import sys
from datetime import date
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from htd.tariff import pl_holidays, b23_zone, capacity_fee_applies, unit_cost
from htd.clean import counter_to_consumption, localize


def test_holidays_2025():
    h = pl_holidays(2025)
    assert date(2025, 4, 21) in h and date(2025, 6, 19) in h and date(2025, 12, 24) in h


def test_zones():
    ts = pd.DatetimeIndex(["2025-01-15 08:00", "2025-01-15 17:00", "2025-07-15 17:00",
                           "2025-07-15 20:00", "2025-01-18 08:00", "2025-04-21 08:00"])
    assert b23_zone(ts).tolist() == ["peak_am", "peak_pm", "off", "peak_pm", "off", "off"]
    assert capacity_fee_applies(ts).tolist() == [True, True, True, True, False, False]


def test_unit_cost():
    ts = pd.DatetimeIndex(["2025-01-15 08:00", "2025-01-18 08:00"])
    c = unit_cost(ts, 0.5)
    assert abs(c.iloc[0] - c.iloc[1] - 0.2194) < 1e-9


def test_counter_gap():
    idx = localize(pd.DatetimeIndex(["2025-01-01 00:00", "2025-01-01 00:15", "2025-01-01 01:00"]))
    r = counter_to_consumption(pd.Series([100.0, 110.0, 140.0], index=idx))
    assert len(r) == 4 and abs(r.kwh.sum() - 40) < 1e-9
    assert r.flag.tolist() == ["ok", "gapfill", "gapfill", "gapfill"]
