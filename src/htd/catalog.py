"""Uniform access to every data/processed/*.parquet for the dashboard (app/dashboard.py).
Any file -> NORM long frame: ts (tz, interval START) · dataset · site · meter · carrier · series · kwh · raw · flag · dur_h.
Energy always in kWh (heat GJ converted), power derived as kwh/dur_h. Supported layouts: canonical long (schema.COLS),
monthly (schema.MONTHLY_COLS), wide (DatetimeIndex or datetime column + numeric columns)."""
import numpy as np
import pandas as pd
from .config import PROCESSED, TZ, TAB
from .tariff import is_workday, b23_zone, capacity_fee_applies

NORM = ["ts", "dataset", "site", "meter", "carrier", "series", "kwh", "raw", "flag", "dur_h"]
GJ_KWH = 1000 / 3.6
# worst first: when several intervals are merged, the most severe flag is kept
FLAG_ORDER = ["anomaly", "gapfill", "interp", "split", "suspect", "missing", "ok"]
DIMS = {"series": "seria (licznik)", "site": "obiekt", "carrier": "nośnik", "dataset": "zbiór danych"}


def discover() -> list[str]:
    return sorted(p.stem for p in PROCESSED.glob("*.parquet"))


def layout(df: pd.DataFrame) -> str:
    cols = set(df.columns)
    if {"ts", "kwh", "flag", "site", "meter"} <= cols:
        return "long"
    if {"month", "value", "carrier"} <= cols:
        return "monthly"
    return "wide"


def _dur_h(ts: pd.Series) -> pd.Series:
    """Interval length per row from the regular step of its series (h)."""
    step = ts.drop_duplicates().sort_values().diff().median()
    return pd.Series(step / pd.Timedelta("1h"), index=ts.index)


def load(name: str) -> pd.DataFrame:
    df = pd.read_parquet(PROCESSED / f"{name}.parquet")
    kind = layout(df)
    if kind == "long":
        out = pd.DataFrame({"ts": df.ts, "site": df.site, "meter": df.meter.astype(str), "carrier": "el",
                            "kwh": df.kwh, "raw": df.get("kwh_raw", np.nan), "flag": df.flag})
        out["dur_h"] = out.groupby("meter", group_keys=False).ts.apply(_dur_h)
    elif kind == "monthly":
        f = np.where(df.unit == "GJ", GJ_KWH, 1.0)
        ts = pd.DatetimeIndex(df.month).tz_localize(TZ)
        out = pd.DataFrame({"ts": ts, "site": df.site, "meter": df.carrier + " " + df.meter, "carrier": df.carrier,
                            "kwh": df.value * f, "raw": df.value_raw * f, "flag": df.flag})
        out["dur_h"] = ts.days_in_month * 24.0
    else:
        if not isinstance(df.index, pd.DatetimeIndex):
            tcol = next(c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c]))
            df = df.set_index(tcol)
        idx = df.index if df.index.tz is not None else df.index.tz_localize(TZ, ambiguous="infer", nonexistent="shift_forward")
        num = df.select_dtypes("number")
        out = num.set_axis(idx).rename_axis("ts").reset_index().melt("ts", var_name="site", value_name="kwh")
        out = out.assign(meter=out.site.astype(str), carrier="el", raw=np.nan, flag="ok")
        out["dur_h"] = _dur_h(out.ts)
    out["dataset"] = name
    out["series"] = label(name, out.site.astype(str), out.meter.astype(str))
    return out[NORM].reset_index(drop=True)


def short_meter(m: str) -> str:
    """Long PPE ids -> '…615820' (last 6 digits stay unique within a site)."""
    return "…" + m[-6:] if m.isdigit() and len(m) > 8 else m


def label(dataset: str, site: pd.Series, meter: pd.Series) -> pd.Series:
    """'dataset · site · meter', skipping parts equal to the previous one (e.g. 'hala · …615820')."""
    sm = meter.map(short_meter)
    s = pd.Series(dataset, index=site.index) + (" · " + site).where(site != dataset, "")
    return s + (" · " + sm).where(meter != site, "")


def resolution(df: pd.DataFrame) -> pd.Timedelta:
    return pd.Timedelta(hours=float(df.dur_h.median())) if len(df) else pd.Timedelta("15min")


def add_calendar(df: pd.DataFrame) -> pd.DataFrame:
    ts = pd.DatetimeIndex(df.ts)
    return df.assign(hour=ts.hour + ts.minute / 60, weekday=ts.dayofweek, month=ts.month, year=ts.year,
                     workday=np.asarray(is_workday(ts)), zone=b23_zone(ts).to_numpy(),
                     capacity=np.asarray(capacity_fee_applies(ts)))


def _local_bounds(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Naive local interval start/end (wall clock, so a monthly row ends at 00:00 of the next month despite DST)."""
    t0 = df.ts.dt.tz_localize(None)
    return t0, t0 + pd.to_timedelta(df.dur_h, unit="h").where(df.dur_h < 24 * 27, pd.to_timedelta(t0.dt.days_in_month, unit="D"))


def span(df: pd.DataFrame) -> tuple:
    """(first, last) calendar day covered by df; last includes the end of the final interval (monthly -> month end)."""
    t0, t1 = _local_bounds(df)
    return t0.min().date(), (t1.max() - pd.Timedelta("1s")).date()


def merge_options(df: pd.DataFrame) -> list[str]:
    """`group` dimensions that actually merge something; options giving the same partition as an earlier one dropped."""
    meta = df[["series", "dataset", "site", "carrier"]].drop_duplicates("series")
    out, seen = [], set()
    for by in ("series", "site", "dataset", "carrier"):
        part = frozenset(meta.groupby(series_key(meta, by)).series.agg(frozenset))
        if part not in seen:
            out.append(by)
            seen.add(part)
    return out


def filter_df(df, start=None, end=None, months=None, weekdays=None, daytype="all", hours=(0, 24),
              zones=None, capacity_only=False, flags=None) -> pd.DataFrame:
    """Calendar filters (hour/weekday/day type/zone/capacity) only apply to sub-daily rows; months/dates to all.
    Date range keeps every interval overlapping [start, end] (a monthly row counts if the range touches its month)."""
    m = pd.Series(True, index=df.index)
    if start is not None or end is not None:
        t0, t1 = _local_bounds(df)
        if start is not None:
            m &= t1 > pd.Timestamp(start)
        if end is not None:
            m &= t0 < pd.Timestamp(end) + pd.Timedelta("1D")
    if months:
        m &= df.month.isin(months)
    if flags is not None:
        m &= df.flag.isin(flags)
    sub = df.dur_h < 24
    c = pd.Series(True, index=df.index)
    if weekdays:
        c &= df.weekday.isin(weekdays)
    if daytype == "workday":
        c &= df.workday
    elif daytype == "free":
        c &= ~df.workday
    c &= (df.hour >= hours[0]) & (df.hour < hours[1])
    if zones is not None:
        c &= df.zone.isin(zones)
    if capacity_only:
        c &= df.capacity
    return df[m & (c | ~sub)]


def overlay_years(df: pd.DataFrame, ref_year: int) -> pd.DataFrame:
    """Seasonal comparison: move every row to ref_year (same month/day/time), series suffixed with its year."""
    loc = df.ts.dt.tz_localize(None)
    yrs = loc.dt.year
    moved = pd.to_datetime({"year": ref_year, "month": loc.dt.month, "day": loc.dt.day, "hour": loc.dt.hour,
                            "minute": loc.dt.minute}, errors="coerce")  # 29.02 -> NaT
    ts = pd.DatetimeIndex(moved).tz_localize(TZ, ambiguous="NaT", nonexistent="NaT")
    tag = " (" + yrs.astype(str) + ")"
    out = df.assign(ts=ts, tag=tag, series=df.series + tag)
    return out[out.ts.notna()]


CAL = ["hour", "weekday", "month", "year", "workday", "zone", "capacity"]


def series_key(df: pd.DataFrame, by: str) -> pd.Series:
    """Series label after merging meters by `by` (series = finest, no merge)."""
    if by == "series":
        return df.series
    sfx = df["tag"] if "tag" in df else ""  # year suffix from overlay_years
    if by == "dataset":
        return df.dataset.astype(str) + sfx
    return df.dataset + (" · " + df[by].astype(str)).where(df[by].astype(str) != df.dataset, "") + sfx


def group(df: pd.DataFrame, by: str) -> pd.DataFrame:
    """Sum meters into coarser series (site / carrier / dataset). Flag = worst of merged rows."""
    if by == "series":
        return df
    sev = df.flag.map({f: i for i, f in enumerate(FLAG_ORDER)}).fillna(len(FLAG_ORDER) - 1).astype(int)
    d = df.assign(series=series_key(df, by), sev=sev)
    g = d.groupby(["series", "ts"], sort=False)
    keep = ["dur_h", "dataset", "site", "carrier"] + [c for c in CAL if c in d]
    out = g[keep].first()
    out["kwh"] = g.kwh.sum()
    out["raw"] = g.raw.sum(min_count=1)
    out["flag"] = np.array(FLAG_ORDER)[g.sev.min().to_numpy()]
    out = out.reset_index()
    out["meter"] = out.series
    return out


MEASURES = {"energy": "Energia", "p_mean": "Moc średnia", "p_max": "Moc maks.", "p_min": "Moc min."}


def aggregate(df: pd.DataFrame, rule: str | None, measure: str) -> pd.DataFrame:
    """Per series: resample to rule (None = native) and compute measure. Returns ts · series · value · raw · flag.
    energy = sum kWh · p_mean = sum kWh / sum h · p_max/p_min = extreme of native interval power."""
    d = df.assign(p=df.kwh / df.dur_h, praw=df.raw / df.dur_h,
                  sev=df.flag.map({f: i for i, f in enumerate(FLAG_ORDER)}).fillna(len(FLAG_ORDER) - 1))
    if rule is None:
        val = {"energy": d.kwh, "p_mean": d.p, "p_max": d.p, "p_min": d.p}[measure]
        raw = {"energy": d.raw}.get(measure, d.praw)
        return pd.DataFrame({"ts": d.ts, "series": d.series, "value": val, "raw": raw, "flag": d.flag})
    out = []
    for s, g in d.groupby("series", sort=False):
        kw = {"label": "left", "closed": "left"} if rule.startswith("W") else {}
        r = g.set_index("ts").resample(rule, **kw)
        a = pd.DataFrame({"kwh": r.kwh.sum(min_count=1), "raw": r.raw.sum(min_count=1), "h": r.dur_h.sum(),
                          "pmax": r.p.max(), "pmin": r.p.min(), "rmax": r.praw.max(), "rmin": r.praw.min(), "sev": r.sev.min()})
        a = a[a.h > 0]
        val = {"energy": a.kwh, "p_mean": a.kwh / a.h, "p_max": a.pmax, "p_min": a.pmin}[measure]
        raw = {"energy": a.raw, "p_mean": a.raw / a.h, "p_max": a.rmax, "p_min": a.rmin}[measure]
        out.append(pd.DataFrame({"ts": a.index, "series": s, "value": val.to_numpy(), "raw": raw.to_numpy(),
                                 "flag": [FLAG_ORDER[int(i)] for i in a.sev]}))
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame(columns=["ts", "series", "value", "raw", "flag"])


def normalize(a: pd.DataFrame, how: str) -> pd.DataFrame:
    if how == "none":
        return a
    g = a.groupby("series").value
    if how == "pct_max":
        f = 100 / g.transform("max")
        return a.assign(value=a.value * f, raw=a.raw * f)
    if how == "zscore":
        mu, sd = g.transform("mean"), g.transform("std")
        return a.assign(value=(a.value - mu) / sd, raw=(a.raw - mu) / sd)
    if how == "pct_total":  # share of each series in the sum of all shown series at that time
        tot = a.groupby("ts").value.transform("sum")
        return a.assign(value=100 * a.value / tot, raw=np.nan)
    raise ValueError(how)


def smooth(a: pd.DataFrame, window: int) -> pd.DataFrame:
    if window <= 1:
        return a
    f = lambda x: x.rolling(window, center=True, min_periods=1).mean()  # noqa: E731
    return a.assign(value=a.groupby("series").value.transform(f), raw=a.groupby("series").raw.transform(f))


def stats(df: pd.DataFrame) -> pd.DataFrame:
    """Per series on filtered native data: energy, mean/max/min power, capacity-hour share, flagged share."""
    d = df.assign(p=df.kwh / df.dur_h)
    if "capacity" not in d:
        d = add_calendar(d)
    g = d.groupby("series")
    out = pd.DataFrame({
        "od": g.ts.min().dt.strftime("%Y-%m-%d"), "do": g.ts.max().dt.strftime("%Y-%m-%d"), "n": g.size(),
        "energia_MWh": g.kwh.sum() / 1000, "moc_sr_kW": g.kwh.sum() / g.dur_h.sum(), "moc_max_kW": g.p.max(),
        "moc_min_kW": g.p.min(),
        "udzial_godz_mocowych_%": 100 * d[d.capacity & (d.dur_h < 24)].groupby("series").kwh.sum() / g.kwh.sum(),
        "flagowane_%": 100 * g.flag.apply(lambda x: (x != "ok").mean()),
    })
    return out.round(2)


def anomaly_log() -> pd.DataFrame:
    p = TAB / "anomaly_log.csv"
    return pd.read_csv(p) if p.exists() else pd.DataFrame()
