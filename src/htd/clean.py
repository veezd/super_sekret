"""Generic cleaning: DST, cumulative counters, gaps, flags. Flags (schema.FLAGS):
ok measured · interp short gap/bad value linearly interpolated · gapfill long gap filled (counter spread / typical profile)
· split value split from a combined reading · anomaly measured value rejected + replaced (raw kept in kwh_raw)
· suspect kept as-is but questionable · missing no value."""
import numpy as np
import pandas as pd
from .config import TZ


def localize(naive: pd.Series | pd.DatetimeIndex, ambiguous="infer") -> pd.DatetimeIndex:
    """Naive local CET/CEST -> tz-aware. Spring gap shifted; autumn duplicate inferred from order."""
    idx = pd.DatetimeIndex(naive)
    return idx.tz_localize(TZ, ambiguous=ambiguous, nonexistent="shift_forward")


def local_end_to_start(naive_end, freq: str) -> pd.DatetimeIndex:
    """Naive local END labels (as logged by meters, autumn hour repeated in order) -> tz-aware interval START.
    Shift first: end labels '03:00' twice become starts '02:45' twice, which 'infer' resolves CEST then CET."""
    return localize(pd.DatetimeIndex(naive_end) - pd.Timedelta(freq))


def excel_serial_to_dt(x) -> pd.Series:
    """Excel serial (e.g. 46207.0104) -> naive datetime rounded to minute."""
    return (pd.to_datetime(pd.Series(x, dtype=float), unit="D", origin="1899-12-30")).dt.round("min")


def end_to_start(idx: pd.DatetimeIndex, freq: str) -> pd.DatetimeIndex:
    """Timestamps marking interval END -> interval START."""
    return idx - pd.Timedelta(freq)


def full_index(start: str, end: str, freq="15min") -> pd.DatetimeIndex:
    """Complete tz-aware grid of interval starts, local [start, end)."""
    return pd.date_range(pd.Timestamp(start, tz=TZ), pd.Timestamp(end, tz=TZ), freq=freq, inclusive="left")


def counter_to_consumption(cum: pd.Series, freq="15min") -> pd.DataFrame:
    """Cumulative meter reading -> per-interval kWh. Gaps: delta spread evenly over missing slots (flag 'gapfill').
    Negative deltas (meter reset/rollback) -> NaN + flag 'anomaly'. Input index = tz-aware reading time (interval END)."""
    s = cum.dropna().sort_index()
    s = s[~s.index.duplicated()]
    step = pd.Timedelta(freq)
    full = pd.date_range(s.index[0], s.index[-1], freq=freq)
    n = (s.index.to_series().diff() / step).to_numpy()
    rate = s.diff().to_numpy() / n
    per = pd.DataFrame({"rate": rate, "n": n}, index=s.index).reindex(full).bfill()  # slot ending at t takes next reading's rate
    out = pd.DataFrame(index=full, data={"kwh": per["rate"], "flag": "ok"})
    out.loc[per["n"] > 1, "flag"] = "gapfill"
    neg = per["rate"] < 0
    out.loc[neg, ["kwh", "flag"]] = [np.nan, "anomaly"]
    out = out.iloc[1:]
    out.index = end_to_start(out.index, freq)  # reading at t = end of interval -> label by start
    return out


def split_double_row(df: pd.DataFrame, when, col="kwh") -> pd.DataFrame:
    """Autumn DST: one row holding 2 hours (completeness 200%). Halve and duplicate."""
    row = df.loc[[when]].copy()
    row[col] = row[col] / 2
    return pd.concat([df.drop(index=when), row, row]).sort_index()


def flag_outliers(s: pd.Series, z=4.0, window="7D") -> pd.Series:
    """Robust rolling z-score (median/MAD). True = suspicious. Use for flagging, not auto-delete."""
    med = s.rolling(window, center=True, min_periods=10).median()
    mad = (s - med).abs().rolling(window, center=True, min_periods=10).median() * 1.4826
    return ((s - med).abs() / mad.replace(0, np.nan)) > z


def gaps(idx: pd.DatetimeIndex, freq="15min") -> pd.DataFrame:
    """List gaps in a time index (start, end, n_missing)."""
    idx = pd.DatetimeIndex(idx).sort_values()
    step = pd.Timedelta(freq)
    d = idx.to_series().diff()
    g = d[d > step]
    return pd.DataFrame({"start": (g.index - g + step), "end": g.index - step, "n_missing": (g / step - 1).astype(int)}).reset_index(drop=True)


def runs(mask: pd.Series) -> pd.DataFrame:
    """Consecutive True runs in a boolean series -> (start, end, n) with index labels."""
    m = mask.fillna(False).astype(bool).to_numpy()
    if not m.any():
        return pd.DataFrame(columns=["start", "end", "n"])
    edges = np.diff(np.r_[0, m.astype(int), 0])
    st, en = np.flatnonzero(edges == 1), np.flatnonzero(edges == -1) - 1
    return pd.DataFrame({"start": mask.index[st], "end": mask.index[en], "n": en - st + 1})


def profile_fill(s: pd.Series, mask: pd.Series, weeks=(1, 2)) -> pd.Series:
    """Estimate masked values from same local wall-clock time on same weekday +-1..n weeks (mean of valid donors).
    Donors that are themselves masked/NaN are skipped. Index tz-aware. Returns estimates for masked points only."""
    loc = s.index.tz_localize(None)
    val = s.where(~mask)
    lookup = pd.Series(val.to_numpy(), index=loc)
    lookup = lookup[~lookup.index.duplicated()]
    tgt = loc[mask.to_numpy()]
    donors = [lookup.reindex(tgt + pd.Timedelta(days=7 * w * sgn)).to_numpy() for w in weeks for sgn in (-1, 1)]
    est = np.nanmean(np.vstack(donors), axis=0)
    return pd.Series(est, index=s.index[mask.to_numpy()])


def impute(s: pd.Series, mask: pd.Series, max_interp: int = 4) -> tuple[pd.Series, pd.Series]:
    """Replace masked/NaN points: runs <= max_interp slots -> linear interpolation ('interp'), longer -> profile_fill
    ('gapfill'). Returns (values, method) where method is '' for untouched points."""
    bad = mask | s.isna()
    out, how = s.where(~bad), pd.Series("", index=s.index)
    for _, r in runs(bad).iterrows():
        sl = slice(r.start, r.end)
        how[sl] = "interp" if r.n <= max_interp else "gapfill"
    lin = out.interpolate(limit_area="inside")
    short = how == "interp"
    out[short] = lin[short]
    long_ = how == "gapfill"
    if long_.any():
        out[long_] = profile_fill(s, bad).reindex(s.index)[long_]
    return out, how
