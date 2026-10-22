import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from htd.clean import local_end_to_start, runs, impute, full_index
from htd.config import PROCESSED


def test_end_to_start_dst():
    # autumn: logger repeats 02:15..03:00 end labels -> 8 distinct UTC starts
    ends = pd.date_range("2025-10-26 02:15", "2025-10-26 03:00", freq="15min").append(
        pd.date_range("2025-10-26 02:15", "2025-10-26 03:00", freq="15min"))
    st = local_end_to_start(ends, "15min")
    assert st.is_unique and (st[1:] - st[:-1] == pd.Timedelta("15min")).all()
    # spring: end 02:00 then 03:15 -> starts 01:45 CET, 03:00 CEST = 15 min apart
    st = local_end_to_start(pd.DatetimeIndex(["2025-03-30 02:00", "2025-03-30 03:15"]), "15min")
    assert (st[1] - st[0]) == pd.Timedelta("15min")


def test_runs():
    m = pd.Series([0, 1, 1, 0, 1], dtype=bool)
    r = runs(m)
    assert r.n.tolist() == [2, 1] and r.start.tolist() == [1, 4]


def test_impute_short_and_long():
    idx = full_index("2025-01-01", "2025-02-01")
    s = pd.Series(np.tile(np.arange(96, dtype=float), 31), index=idx)  # same daily shape
    bad = pd.Series(False, index=idx)
    bad.iloc[100:102] = True     # short -> linear
    bad.iloc[1500:1530] = True   # long -> weekday profile
    v, how = impute(s, bad, max_interp=4)
    assert (how[bad] != "").all() and how[~bad].eq("").all()
    assert np.allclose(v, s)  # both methods recover a perfectly periodic signal


DATA = PROCESSED / "hala.parquet"


@pytest.mark.skipif(not DATA.exists(), reason="run scripts/01_build_processed.py first")
def test_processed_invariants():
    from htd.loaders import load
    for key in ("hala", "d17", "basen", "ds_profile"):
        d = load(key)
        assert d.kwh.notna().all(), key
        for _, g in d.groupby("meter"):
            assert g.ts.is_unique and g.ts.is_monotonic_increasing
            step = g.ts.diff().dropna().unique()
            assert len(step) == 1, key  # complete regular grid, DST handled
    m = load("ds_monthly")
    assert m.value.notna().all() and not m.duplicated(["month", "site", "carrier", "meter"]).any()
