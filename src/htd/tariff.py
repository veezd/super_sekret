"""Polish holidays, workdays, B23 zones, capacity-fee hours. All inputs: tz-aware or local-naive timestamps = interval START."""
from datetime import date, timedelta
import pandas as pd
from .config import CAPACITY_HOURS


def _easter(y: int) -> date:  # anonymous Gregorian algorithm
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mo = (h + l - 7 * m + 114) // 31
    da = (h + l - 7 * m + 114) % 31 + 1
    return date(y, mo, da)


def pl_holidays(y: int) -> set[date]:
    e = _easter(y)
    fixed = [(1, 1), (1, 6), (5, 1), (5, 3), (8, 15), (11, 1), (11, 11), (12, 25), (12, 26)]
    s = {date(y, m, d) for m, d in fixed}
    s |= {e, e + timedelta(1), e + timedelta(49), e + timedelta(60)}  # Easter, Mon, Pentecost, Corpus Christi
    if y >= 2025:
        s.add(date(y, 12, 24))  # Wigilia free since 2025
    return s


def is_workday(ts: pd.DatetimeIndex) -> pd.Series:
    ts = pd.DatetimeIndex(ts)
    hol = set().union(*(pl_holidays(y) for y in set(ts.year)))
    d = pd.Series(ts.date, index=ts)
    return (ts.dayofweek < 5) & ~d.isin(hol).to_numpy()


def b23_zone(ts: pd.DatetimeIndex) -> pd.Series:
    """'peak_am' | 'peak_pm' | 'off'. Summer = Apr-Sep (pm 19-22), winter (pm 16-21)."""
    ts = pd.DatetimeIndex(ts)
    wd, h = is_workday(ts), ts.hour
    summer = (ts.month >= 4) & (ts.month <= 9)
    am = wd & (h >= 7) & (h < 13)
    pm = wd & ((summer & (h >= 19) & (h < 22)) | (~summer & (h >= 16) & (h < 21)))
    out = pd.Series("off", index=ts)
    out[am] = "peak_am"
    out[pm] = "peak_pm"
    return out


def capacity_fee_applies(ts: pd.DatetimeIndex):
    ts = pd.DatetimeIndex(ts)
    return is_workday(ts) & ts.hour.isin(list(CAPACITY_HOURS))


def academic_period(ts: pd.DatetimeIndex) -> pd.Series:
    """Rough dorm occupancy label: 'summer' Jul-Sep, 'semester' otherwise. Refine with real AGH calendar if needed."""
    ts = pd.DatetimeIndex(ts)
    return pd.Series(["summer" if m in (7, 8, 9) else "semester" for m in ts.month], index=ts)


# ---------- costs ----------
from .config import PRICE  # noqa: E402


def unit_cost(ts: pd.DatetimeIndex, rdn_pln_kwh: pd.Series | float) -> pd.Series:
    """Full purchase price PLN/kWh for each interval start ts. rdn: spot price PLN/kWh aligned to ts (or scalar)."""
    ts = pd.DatetimeIndex(ts)
    rdn = rdn_pln_kwh.reindex(ts).to_numpy() if isinstance(rdn_pln_kwh, pd.Series) else rdn_pln_kwh
    p = PRICE
    base = rdn + p["margin"] + p["distribution"] + p["quality"] + p["oze_cog_excise"]
    return pd.Series(base + capacity_fee_applies(ts) * p["capacity"], index=ts)


def avoided_cost_selfconsumed(ts: pd.DatetimeIndex, rdn_pln_kwh, in_cooperative=False) -> pd.Series:
    """Value of 1 kWh of own PV consumed behind the meter (internal AGH network) = full unit cost avoided.
    Cooperative variant: see docs/pricing.md (exemptions OZE/mocowa/kog; excise only if <=1 MW; 1:0.6 surplus)."""
    if in_cooperative:
        raise NotImplementedError("model cooperative rules explicitly; document in methodology.md")
    return unit_cost(ts, rdn_pln_kwh)
