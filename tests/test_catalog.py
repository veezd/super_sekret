import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from htd import catalog as C
from htd.clean import full_index


def _df(n_days=14, meters=("A", "B")):
    idx = full_index("2025-03-24", str((pd.Timestamp("2025-03-24") + pd.Timedelta(days=n_days)).date()))  # spans DST
    rows = [pd.DataFrame({"ts": idx, "dataset": "x", "site": "s", "meter": m, "carrier": "el", "series": f"x · s · {m}",
                          "kwh": 1.0, "raw": 1.0, "flag": "ok", "dur_h": 0.25}) for m in meters]
    d = pd.concat(rows, ignore_index=True)
    d.loc[5, "flag"] = "anomaly"
    return C.add_calendar(d)


def test_group_sums_meters_and_keeps_worst_flag():
    g = C.group(_df(), "site")
    assert g.series.nunique() == 1 and (g.kwh == 2.0).all()
    assert (g.flag == "anomaly").sum() == 1


def test_aggregate_energy_and_power_consistent():
    d = C.group(_df(), "site")
    e = C.aggregate(d, "1D", "energy")
    p = C.aggregate(d, "1D", "p_mean")
    assert np.isclose(e.value.sum(), d.kwh.sum())
    assert np.allclose(p.value, 8.0)  # 2 kWh / 0.25 h on every interval, incl. 23 h DST day
    assert len(e) == 14


def test_filter_calendar_only_subdaily():
    d = _df()
    m = d.iloc[:1].assign(dur_h=744.0, ts=pd.Timestamp("2025-03-01", tz=C.TZ))  # monthly row survives hour filter
    f = C.filter_df(pd.concat([d, m]), hours=(7, 8), daytype="workday")
    assert (f[f.dur_h < 24].hour.between(7, 7.75)).all() and (f.dur_h == 744).sum() == 1


def test_overlay_years_and_normalize():
    d = _df(3)
    d2 = d.assign(ts=d.ts + pd.DateOffset(years=-1))
    o = C.overlay_years(pd.concat([d, d2]), 2025)
    assert o.ts.dt.year.eq(2025).all() and o.series.str.endswith(("(2024)", "(2025)")).all()
    a = C.normalize(C.aggregate(C.group(d, "site"), "1h", "p_mean"), "pct_max")
    assert np.isclose(a.value.max(), 100)


@pytest.mark.skipif(not C.discover(), reason="no processed data")
def test_every_processed_file_loads():
    for n in C.discover():
        d = C.load(n)
        assert list(d.columns) == C.NORM and d.ts.dt.tz is not None and (d.dur_h > 0).all(), n
