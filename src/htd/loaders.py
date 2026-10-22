"""One loader per raw file -> schema.COLS (long, 15min/1h) or schema.MONTHLY_COLS. Every detected data problem is
appended to ANOMALIES (-> outputs/tables/anomaly_log.csv via scripts/01_build_processed.py).
Meter timestamps in all raw files = interval END, local wall clock -> converted to tz-aware interval START."""
import re
import numpy as np
import pandas as pd
from . import clean
from .config import RAW, PROCESSED, RAW_FILES
from .schema import COLS, MONTHLY_COLS

YEAR = ("2025-01-01", "2026-01-01")  # 15min/1h series cover calendar 2025
ANOMALIES: list[dict] = []


def log(dataset, site, meter, start, end, n, issue, action):
    ANOMALIES.append(dict(dataset=dataset, site=site, meter=meter, start=start, end=end, n=n, issue=issue, action=action))


def anomaly_log() -> pd.DataFrame:
    return pd.DataFrame(ANOMALIES, columns=["dataset", "site", "meter", "start", "end", "n", "issue", "action"])


def save(df: pd.DataFrame, key: str):
    PROCESSED.mkdir(parents=True, exist_ok=True)
    cols = MONTHLY_COLS if "month" in df.columns else COLS
    df[cols].to_parquet(PROCESSED / f"{key}.parquet", index=False)


def load(key: str) -> pd.DataFrame:
    return pd.read_parquet(PROCESSED / f"{key}.parquet")


def wide(key: str, by="site", value="kwh") -> pd.DataFrame:
    """Processed long -> wide (ts x site), meters summed. E.g. wide('hala')['hala'] = whole-site kWh per 15min."""
    return load(key).pivot_table(index="ts", columns=by, values=value, aggfunc="sum", dropna=False)


def raw_path(key: str):
    return RAW / RAW_FILES[key]


# ---------- helpers ----------
def _read_xls_table(key: str) -> pd.DataFrame:
    """Logger exports (hala, d17): banner + gap list + header row 'Znacznik czasowy', then data, then 'ID:' footer.
    Returns data rows with column 0 parsed as naive datetime 't' (rows with seconds kept as-is)."""
    df = pd.read_excel(raw_path(key), header=None)
    hdr = df.index[df[0].astype(str).str.strip() == "Znacznik czasowy"][0]
    names = df.loc[hdr].fillna("").astype(str).str.replace("\n", " ").tolist()
    data = df.loc[hdr + 1:].copy()
    data.columns = names
    data["t"] = pd.to_datetime(data.iloc[:, 0], errors="coerce", format="%Y-%m-%d %H:%M:%S")
    data = data[data.t.notna()].drop(columns=names[0])
    return data.loc[:, [c for c in data.columns if c]].reset_index(drop=True)


def _finish(s: pd.Series, flag: pd.Series, raw: pd.Series, site: str, meter: str, minutes: int) -> pd.DataFrame:
    return pd.DataFrame({"ts": s.index, "site": site, "meter": meter, "kwh": s.to_numpy(),
                         "kw": s.to_numpy() * 60 / minutes, "flag": flag.to_numpy(), "kwh_raw": raw.reindex(s.index).to_numpy()})


def _impute_and_flag(ds, site, meter, s, bad, issue_bad, max_interp=4):
    """Shared: NaN -> missing, bad mask -> anomaly; impute; log runs. Returns (values, flags)."""
    flag = pd.Series("ok", index=s.index)
    val, how = clean.impute(s, bad, max_interp=max_interp)
    for r in clean.runs(s.isna() & ~bad).itertuples():
        log(ds, site, meter, r.start, r.end, r.n, "no data", "interp" if r.n <= max_interp else "gapfill: weekday profile +-1,2 wk")
    for r in clean.runs(bad).itertuples():
        log(ds, site, meter, r.start, r.end, r.n, issue_bad, "replaced: " + ("linear interp" if r.n <= max_interp else "weekday profile +-1,2 wk"))
    flag[how != ""] = how[how != ""]
    flag[bad] = "anomaly"
    flag[val.isna()] = "missing"
    return val, flag


# ---------- loaders ----------
def load_hala() -> pd.DataFrame:
    """hala_kwh: 2 PPE (…615820 main, …615837 ≈0.17 kWh/15min const). 'Suma' col ignored (recomputable).
    Supply outage detection: const meter …615837 drops to ~0 => whole site without supply (07-04 08:15–15:30,
    incl. partial slots + missing rows). Outage replaced by weekday profile (non-representative for planning).
    hala_kw (= …615820 ×4) only cross-checked in hala_kw_check(); NEVER summed."""
    d = _read_xls_table("hala_kwh")
    cols = [c for c in d.columns if c.startswith("PPE:")]
    d.index = clean.local_end_to_start(d.pop("t"), "15min")
    full = clean.full_index(*YEAR)
    const = d[[c for c in cols if c.endswith("615837")][0]].reindex(full).astype(float)
    outage = const < 0.05  # NaN compares False
    # widen outage to missing rows inside / adjacent to it (data logger also down)
    r = clean.runs(outage | const.isna())
    out_mask = pd.Series(False, index=full)
    for x in r.itertuples():
        if outage[x.start:x.end].any():
            out_mask[x.start:x.end] = True
    for x in clean.runs(out_mask).itertuples():
        log("hala", "hala", "both", x.start, x.end, x.n, "supply outage: both PPE ~0 (+missing rows)", "flag anomaly, replaced by weekday profile")
    frames = []
    for c in cols:
        meter = c.replace("PPE:", "")
        raw = d[c].astype(float).reindex(full)
        val, how = clean.impute(raw, out_mask, max_interp=4)
        f = how.where(how != "", "ok")
        f[out_mask] = "anomaly"
        for x in clean.runs(raw.isna() & ~out_mask).itertuples():
            log("hala", "hala", meter, x.start, x.end, x.n, "no data", how[x.start])
        if meter.endswith("615820"):  # short main-feed interruptions (const meter alive): real events, keep
            low = (raw < 0.1 * raw.rolling("7D", center=True).median()) & ~out_mask
            f[low] = "suspect"
            for x in clean.runs(low).itertuples():
                log("hala", "hala", meter, x.start, x.end, x.n, "main feed <10% of 7D median, const meter alive (switching?)", "kept, flag suspect")
        frames.append(_finish(val, f, raw, "hala", meter, 15))
    return pd.concat(frames, ignore_index=True)


def hala_kw_check() -> pd.DataFrame:
    """Cross-check hala_kw (kW) vs 4×kWh of PPE …615820. Returns per-interval table of mismatches > 1 kW."""
    k = _read_xls_table("hala_kw")
    k.index = clean.local_end_to_start(k.pop("t"), "15min")
    kw = k.iloc[:, 0].astype(float)
    h = load("hala")
    main = h[h.meter.str.endswith("615820")].set_index("ts")
    m = pd.DataFrame({"kw_file": kw, "kw_from_kwh": main.kwh_raw * 4, "flag": main.flag}).dropna(subset=["kw_file"])
    m["diff"] = m.kw_file - m.kw_from_kwh
    for t, r in m[m.kw_file < 0].iterrows():
        log("hala_kw", "hala", "615820", t, t, 1, f"negative power {r.kw_file:.1f} kW (kWh file ok: {r.kw_from_kwh:.1f} kW)", "kW file not used")
    return m[m["diff"].abs() > 1]


def load_d17() -> pd.DataFrame:
    """Cumulative 'Energia Czynna Pobrana' per ZAS -> clean.counter_to_consumption (gaps spread evenly).
    Logger writes stray rows with :01/:59 seconds holding only kW -> merged into nearest 15min slot (kW check only).
    'Moc Czynna Uśred.' kW = cross-check (diff*4) in d17_kw_check()."""
    d = _read_xls_table("d17_el")
    stray = d.t.dt.second != 0
    log("d17", "d17", "ZAS1+ZAS2", d.t[stray].min(), d.t[stray].max(), int(stray.sum()), "stray rows with :01/:59 s timestamps (kW only)", "dropped (kW merged for check)")
    d = d[~stray]
    d.index = clean.local_end_to_start(d.pop("t"), "15min")
    full = clean.full_index(*YEAR)
    frames = []
    for zas in ("ZAS1", "ZAS2"):
        ecol = [c for c in d.columns if zas in c and "Energia" in c][0]
        cum = d[ecol].astype(float)
        cum.index = cum.index + pd.Timedelta("15min")  # reading time = interval END
        cons = clean.counter_to_consumption(cum).reindex(full)
        first = cons.index[0]  # no reading before 2025-01-01 00:00 -> first interval unknown, copy next
        if pd.isna(cons.at[first, "kwh"]):
            cons.loc[first, ["kwh", "flag"]] = [cons.kwh.iloc[1], "interp"]
            log("d17", "d17", zas, first, first, 1, "no counter reading before first interval", "copied next interval")
        cons.loc[cons.kwh.isna() & (cons.flag != "anomaly"), "flag"] = "missing"
        typical = cons.kwh.where(cons.flag == "ok").rolling("1D", center=True).median()
        for x in clean.runs(cons.flag == "gapfill").itertuples():
            ratio = cons.kwh[x.start] / typical[x.start]
            note = f"; rate over gap = {ratio:.0%} of 1D median -> probable outage" if ratio < 0.5 else ""
            log("d17", "d17", zas, x.start, x.end, x.n, "counter readings missing" + note, "meter delta spread evenly (energy kept)")
        for x in clean.runs(cons.flag == "anomaly").itertuples():
            log("d17", "d17", zas, x.start, x.end, x.n, "counter decreased", "NaN")
        raw = cons.kwh.where(cons.flag == "ok")
        out = _finish(cons.kwh, cons.flag, raw, "d17", zas, 15)
        frames.append(out)
    return pd.concat(frames, ignore_index=True)


def d17_kw_check() -> pd.DataFrame:
    """Per ZAS: summary of (4×kWh from counter) − logged mean kW, on 'ok' intervals."""
    d = _read_xls_table("d17_el")
    d["t"] = d.t.dt.round("15min")
    d = d.groupby((d.t != d.t.shift()).cumsum()).first().set_index("t")  # merge stray rows into their slot; DST repeats kept
    d.index = clean.local_end_to_start(d.index, "15min")
    e = load("d17").set_index("ts")
    rows = []
    for zas in ("ZAS1", "ZAS2"):
        kw = d[[c for c in d.columns if zas in c and "Moc" in c][0]].astype(float)
        x = e[(e.meter == zas) & (e.flag == "ok")]
        diff = (x.kw - kw.reindex(x.index)).dropna()
        rows.append(dict(meter=zas, n=len(diff), mean=diff.mean(), mae=diff.abs().mean(), p99_abs=diff.abs().quantile(.99), corr=x.kw.corr(kw.reindex(x.index))))
    return pd.DataFrame(rows)


B23_MAP = {"Reszta dnia": "off", "Szczyt przedpołudniowy": "peak_am", "Szczyt popołudniowy": "peak_pm"}


def load_basen() -> pd.DataFrame:
    """Hourly DSO data, ts = END of hour. 10-26 03:00 = 2 h in one row (completeness 200%) -> split in half
    (2 intervals 02:00 CEST + 02:00 CET). Zeros / robust outliers vs 7D median -> anomaly, interpolated.
    Easter dip is real (kept). 'Strefa' cross-checked against tariff.b23_zone in basen_zone_check()."""
    b = pd.read_csv(raw_path("basen"), sep=";", decimal=",", encoding="cp1250")
    b.columns = ["payer", "ppe", "kind", "t", "zone", "kwh", "compl"]
    b["t"] = pd.to_datetime(b.t, format="%d.%m.%Y %H:%M")
    dbl = b.compl >= 200
    for _, r in b[dbl].iterrows():
        log("basen", "basen", r.ppe, r.t, r.t, 1, f"DST: {r.kwh} kWh = 2 h in 1 row (completeness {r.compl}%)", "split in half -> 2 intervals")
    b = pd.concat([b[~dbl], b[dbl], b[dbl]]).sort_values("t", kind="stable")
    b.loc[b.compl >= 200, "kwh"] /= 2
    b.index = clean.local_end_to_start(b.t, "1h")
    full = clean.full_index(*YEAR, freq="1h")
    raw = b.kwh.reindex(full)
    split = b.compl.reindex(full) >= 200
    bad = (raw <= 0) | clean.flag_outliers(raw, z=8, window="7D")
    val, flag = _impute_and_flag("basen", "basen", b.ppe.iloc[0], raw, bad, "zero / extreme outlier (robust z>8, 7D)", max_interp=3)
    flag[split] = "split"
    out = _finish(val, flag, raw, "basen", b.ppe.iloc[0].replace("PPE:", ""), 60)
    out["zone_raw"] = b.zone.map(B23_MAP).reindex(full).to_numpy()
    return out


def basen_zone_check(df: pd.DataFrame) -> pd.DataFrame:
    from .tariff import b23_zone
    z = b23_zone(pd.DatetimeIndex(df.ts).tz_localize(None))
    m = pd.DataFrame({"ts": df.ts, "raw": df.zone_raw.to_numpy(), "ours": z.to_numpy()})
    return m[m.raw != m.ours]


DS_SHEETS = {"AGH - DS18": ("ds18", "DS18"), "AGH _ Akropol 50088752": ("akropol", "50088752"),
             "AGH Akropol 50088740": ("akropol", "50088740")}


def load_ds_profile() -> pd.DataFrame:
    """3 sheets, 15min mean kW (2.4 kW quantization), labels = interval END (first = 00:15). Period 2026-07-04 …
    2026-10-02 (summer + start of semester; NOT 2025). Trailing empty rows dropped; common period kept so
    Akropol = sum of 2 meters is complete. Reactive power cols ignored. Zero/robust outliers -> anomaly."""
    x = pd.read_excel(raw_path("ds_profile"), sheet_name=None, header=1)
    series = {}
    for sh, (site, meter) in DS_SHEETS.items():
        df = x[sh].iloc[:, :2].dropna()
        df.columns = ["t", "kw"]
        s = df.set_index(clean.local_end_to_start(pd.to_datetime(df.t), "15min")).kw.astype(float)
        series[(site, meter)] = s
    start = max(s.index.min() for s in series.values())
    end = min(s.index.max() for s in series.values()) + pd.Timedelta("15min")
    full = pd.date_range(start, end, freq="15min", inclusive="left")
    frames = []
    for (site, meter), s in series.items():
        raw = s.reindex(full) / 4
        bad = (raw <= 0) | clean.flag_outliers(raw, z=8, window="7D")
        val, flag = _impute_and_flag("ds_profile", site, meter, raw, bad, "zero / extreme outlier (robust z>8, 7D)")
        frames.append(_finish(val, flag, raw, site, meter, 15))
    return pd.concat(frames, ignore_index=True)


# ---------- monthly dorm data ----------
MONTHS_PL = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]


def _site(label: str) -> str | None:
    s = label.strip().lower()
    if s.startswith("alfa"):
        return "alfa"
    m = re.match(r"ds\D*(\d+)", s)
    return f"ds{int(m.group(1)):02d}" if m else None


def _heat_meter(label: str) -> str:
    s = label.lower().replace(" ", "")
    if "c.o" in s or "co" == s[-2:]:
        return "co"
    if "c.w" in s or s.endswith("cw"):
        return "cw"
    if "ct" in s or "c.t" in s:
        return "ct"
    return "total"


def parse_ds_monthly() -> pd.DataFrame:
    """Raw monthly workbook -> long [month, site, carrier, meter, value_raw, note]. No cleaning.
    El: rows 'DS.-n D/N' (cols = I..XII), Alfa = 'RAZEM ALFA' (2023 blocks bl.1-5 checked against it).
    Heat: rows 'DS.-n c.o/c.w/CT' or '-razem'/'DS.-7' (=total) ; columns 1..12. Summary columns ignored."""
    book = pd.read_excel(raw_path("ds_monthly"), sheet_name=None, header=None)
    rows = []
    for name, df in book.items():
        year = 2000 + int(re.search(r"(\d\d)r", name).group(1))
        carrier = "el" if "elektr" in name else "heat"
        if carrier == "el":
            hdr = df.index[df.apply(lambda r: "I" in r.astype(str).str.strip().tolist(), axis=1)][0]
            cols = [df.columns[(df.loc[hdr].astype(str).str.strip() == mo).to_numpy()][0] for mo in MONTHS_PL]
        else:
            hdr = df.index[df.apply(lambda r: "m-c" in r.astype(str).str.strip().tolist(), axis=1)][0]
            lab = df.loc[hdr]
            cols = [c for c in df.columns if str(lab[c]).strip() in {str(i) for i in range(1, 13)} | {f"{i}.0" for i in range(1, 13)}][:12]
        labcol = min(cols) - 1  # label column directly left of month 1
        blocks = {}
        for i in df.index[df.index > hdr]:
            label = str(df.at[i, labcol]) if pd.notna(df.at[i, labcol]) else ""
            lab = label.strip()
            if not lab:
                continue
            if carrier == "el":
                if re.match(r"^(alfa\s*)?bl\.\s*\d", lab, re.I):
                    blocks[lab] = pd.to_numeric(df.loc[i, cols], errors="coerce").to_numpy()
                    continue
                if lab.upper().startswith("RAZEM ALFA"):
                    site, meter = "alfa", "total"
                else:
                    m = re.match(r"^DS\D*(\d+)\s*([DN])$", lab, re.I)
                    if not m:
                        continue
                    site, meter = f"ds{int(m.group(1)):02d}", m.group(2).upper()
            else:
                site = _site(lab)
                if site is None or "odczyt" in lab.lower():
                    continue
                meter = _heat_meter(lab)
            for mo, c in enumerate(cols, start=1):
                v = df.at[i, c]
                num = pd.to_numeric(v, errors="coerce")
                note = str(v).strip() if (pd.notna(v) and pd.isna(num)) else ""
                rows.append(dict(month=pd.Timestamp(year, mo, 1), site=site, carrier=carrier, meter=meter,
                                 value_raw=float(num) if pd.notna(num) else np.nan, note=note, label=lab))
        if blocks and not np.isnan(np.vstack(list(blocks.values()))).all():
            tot = np.nansum(np.vstack(list(blocks.values())), axis=0)
            alfa = [r for r in rows if r["site"] == "alfa" and r["carrier"] == "el" and r["month"].year == year]
            dev = max(abs(r["value_raw"] - tot[r["month"].month - 1]) for r in alfa)
            if dev > 1:
                log("ds_monthly", "alfa", "el", year, year, 12, f"blocks bl.1-5 sum != RAZEM ALFA (max dev {dev:.0f} kWh)", "RAZEM used")
    out = pd.DataFrame(rows)
    out["unit"] = np.where(out.carrier == "el", "kWh", "GJ")
    return out


# Building closures (renovation) inferred from data: el << usual, heat 0/NaN. NaN inside -> 0, low values not anomalies.
CLOSED = {"ds07": ("2024-10", "2025-11"), "ds08": ("2025-09", "2025-12"), "ds10": ("2023-06", "2024-09")}

# Manual corrections found by scripts/02_check_monthly.py-style screening (zeros, x neighbours, N share, =prev).
# (carrier, site, meter, months, action, reason). Actions: set:<v> | swap:<meter> | dn_split | n_share | pair_avg | drop | suspect
MONTHLY_FIXES = [
    ("el", "ds09", "N", ["2024-11"], "set:4888", "x10 typo (48880; D=8720, N share 0.39 expected)"),
    ("el", "ds01", "D", ["2023-12"], "swap:N", "D/N swapped (N share 0.64 vs median 0.37)"),
    ("el", "ds02", "N", ["2023-01"], "n_share", "N far too low (share 0.15 vs 0.37)"),
    ("el", "ds03", "N", ["2025-10"], "n_share", "N far too low (share 0.18 vs 0.37)"),
    ("el", "ds13", "D", ["2024-01"], "dn_split", "N=0, D holds D+N (D=2.4x Feb)"),
    ("el", "alfa", "total", ["2024-07", "2024-08"], "pair_avg", "irregular reading dates: 76220 + 0"),
    ("el", "alfa", "total", ["2024-09", "2024-10"], "pair_avg", "irregular reading dates: 23660 + 71430"),
    ("el", "alfa", "total", ["2024-11", "2024-12"], "pair_avg", "irregular reading dates: 31720 + 63930"),
    ("el", "alfa", "total", ["2025-07", "2025-08"], "pair_avg", "irregular reading dates: 0 + 80930"),
    ("heat", "ds16", "co", ["2024-12"], "swap:cw", "co/cw swapped (co 71, cw 188 in Dec)"),
    ("heat", "ds05", "cw", ["2024-03", "2024-05"], "drop", "cw 348/331 while co empty: co+cw merged or meter state"),
    ("heat", "ds11", "ct", ["2024-01", "2024-02"], "drop", "CT 265 GJ twice (=prev), 10x other years"),
    ("heat", "ds14", "co", ["2023-12"], "drop", "partial month before meter replacement (81 vs ~500)"),
    ("heat", "ds14", "cw", ["2023-12"], "drop", "partial month before meter replacement (87 vs ~220)"),
    ("heat", "ds14", "co", [f"2023-{m:02d}" for m in range(1, 12)], "suspect", "co/cw split implausible in 2023 (cw > co in winter); total OK"),
    ("heat", "ds14", "cw", [f"2023-{m:02d}" for m in range(1, 12)], "suspect", "co/cw split implausible in 2023 (cw > co in winter); total OK"),
    ("heat", "ds11", "cw", ["2025-04"], "suspect", "cw 26 vs ~60-75 neighbours"),
    ("heat", "ds12", "cw", ["2023-08"], "suspect", "cw 4 vs 26/49 neighbours"),
    ("heat", "ds17", "cw", ["2023-07"], "suspect", "cw 4 vs 77/34 neighbours"),
]


def _months(ms):
    return [pd.Timestamp(m + "-01") for m in ms]


def _closed(site, month) -> bool:
    if site not in CLOSED:
        return False
    a, b = CLOSED[site]
    return pd.Timestamp(a + "-01") <= month <= pd.Timestamp(b + "-01")


def _impute_monthly(v: pd.DataFrame) -> pd.Series:
    """Fill NaN values. Interior: mean(prev, next) x seasonal factor of peers (all other series of same carrier
    and co/non-co group valid in the 3 months). Edges/longer gaps: mean of same calendar month in other years x
    level ratio of this series (this year vs others on commonly valid months)."""
    val = v.value.copy()
    wide = val.unstack("month")
    car, mtr = wide.index.get_level_values("carrier"), wide.index.get_level_values("meter")
    gwide = pd.Series(car + np.where(mtr == "co", ":co", ":x"), index=wide.index)
    est = {}
    for key, s in wide.iterrows():
        peers = wide[(gwide == gwide[key]).to_numpy()].drop(index=key)
        for i, m in enumerate(s.index):
            if pd.notna(s[m]):
                continue
            e = np.nan
            if 0 < i < len(s) - 1 and pd.notna(s.iloc[i - 1]) and pd.notna(s.iloc[i + 1]):
                p = peers.iloc[:, i - 1:i + 2].dropna()
                nb = (p.iloc[:, 0] + p.iloc[:, 2]).sum() / 2
                f = p.iloc[:, 1].sum() / nb if nb > 0 else 1.0
                e = (s.iloc[i - 1] + s.iloc[i + 1]) / 2 * f
            if pd.isna(e):
                same = s[(s.index.month == m.month) & (s.index != m)].dropna()
                yr = s[s.index.year == m.year].dropna()
                oth = s[(s.index.year != m.year) & s.index.month.isin(yr.index.month)].dropna()
                lvl = yr.sum() / oth.groupby(oth.index.year).sum().mean() if len(yr) and len(oth) and oth.sum() > 0 else 1.0
                e = same.mean() * lvl if len(same) else np.nan
            est[key + (m,)] = e
    return pd.Series(est, dtype=float)


def load_ds_monthly() -> pd.DataFrame:
    """Clean monthly dorm data -> MONTHLY_COLS (long). Steps: drop empty/leading-NaN rows (meter not existing yet);
    heat 'total' rows kept only where co/cw missing (else dropped, no double count); CLOSED periods NaN -> 0;
    el zeros outside closures -> anomaly; D and N both equal to previous month -> suspect (copied reading);
    Jan 2025 <60% of Feb 2025 (systematic, 16 DS) -> anomaly (short reading period); MONTHLY_FIXES; then
    _impute_monthly for every NaN (flag interp if absent in raw, anomaly if rejected)."""
    r = parse_ds_monthly()
    k = ["carrier", "site", "meter", "month"]
    r = r.set_index(k).sort_index()
    r["value"], r["flag"] = r.value_raw, "ok"
    # meter not existing yet / empty series
    first = r.value_raw.notna().groupby(level=[0, 1, 2]).cummax() | r.note.ne("").groupby(level=[0, 1, 2]).cummax()
    r = r[first]
    # heat totals vs components
    h = r.xs("heat", drop_level=False)
    comp = h[h.index.get_level_values("meter").isin(["co", "cw"])].value.notna().groupby(level=["site", "month"]).sum()
    drop = []
    for idx in h[h.index.get_level_values("meter") == "total"].index:
        _, site, _, m = idx
        if comp.get((site, m), 0) == 2 or pd.isna(r.at[idx, "value_raw"]) and comp.get((site, m), 0) > 0:
            drop.append(idx)
        elif pd.notna(r.at[idx, "value_raw"]):
            for mt in ("co", "cw"):
                j = ("heat", site, mt, m)
                if j in r.index:
                    drop.append(j)
            r.at[idx, "note"] = "co+cw reported together"
    for (_, site, mt), g in pd.Series(1, index=pd.MultiIndex.from_tuples(sorted(set(drop)), names=k)).groupby(level=[0, 1, 2]):
        log("ds_monthly", site, f"heat {mt}", g.index[0][3].date(), g.index[-1][3].date(), len(g), "heat total row overlaps co/cw rows", "dropped (no double count)")
    r = r.drop(index=list(set(drop)))
    # closures
    closed = np.array([_closed(s, m) for _, s, _, m in r.index])
    r.loc[closed, "note"] = r.loc[closed, "note"].where(r.loc[closed, "note"] != "", "building closed (renovation)")
    na_closed = closed & r.value.isna().to_numpy()
    r.loc[na_closed, ["value", "flag"]] = [0.0, "interp"]
    for (c, s), g in r[na_closed].groupby(level=[0, 1]):
        log("ds_monthly", s, c, g.index.get_level_values("month").min().date(), g.index.get_level_values("month").max().date(), len(g), "no data while building closed", "set 0")
    # el zeros
    el = r.index.get_level_values("carrier") == "el"
    fixed = {(c, si, mt, m) for c, si, mt, ms, act, _ in MONTHLY_FIXES if act != "suspect" for m in _months(ms)}
    fixed |= {(c, si, o, m) for c, si, mt, m in list(fixed) for o in ("D", "N") if c == "el"}  # D/N pair fixes
    z = el & (r.value == 0).to_numpy() & ~closed & ~r.index.isin(list(fixed))
    r.loc[z, ["value", "flag"]] = [np.nan, "anomaly"]
    for idx in r.index[z]:
        log("ds_monthly", idx[1], f"el {idx[2]}", idx[3].date(), idx[3].date(), 1, "zero reading in active building", "imputed")
    # D and N both copied from previous month
    dn = r.xs("el").value_raw.unstack("meter")[["D", "N"]].dropna()
    same = dn.groupby(level="site").transform(lambda x: x.eq(x.shift()))
    for site, m in same.index[same.all(axis=1)]:
        for mt in ("D", "N"):
            r.loc[("el", site, mt, m), "flag"] = "suspect"
            r.loc[("el", site, mt, m), "note"] = "D and N identical to previous month (copied reading?)"
        log("ds_monthly", site, "el D+N", m.date(), m.date(), 2, "D and N identical to previous month", "kept, flag suspect")
    # systematic short Jan 2025
    tot = r.xs("el").value_raw.groupby(level=["site", "month"]).sum()
    jan, feb = pd.Timestamp("2025-01-01"), pd.Timestamp("2025-02-01")
    short = [s for s in tot.index.get_level_values(0).unique() if s != "alfa" and not _closed(s, jan)
             and tot.get((s, jan), np.nan) < 0.6 * tot.get((s, feb), np.nan)]
    for s in short:
        for mt in ("D", "N"):
            r.loc[("el", s, mt, jan), ["value", "flag", "note"]] = [np.nan, "anomaly", "Jan 2025 <60% of Feb (short reading period?)"]
    log("ds_monthly", ",".join(short), "el", jan.date(), jan.date(), len(short), "Jan 2025 < 60% of Feb 2025 in many DS (systematic)", "imputed (yoy level)")
    # manual fixes
    for c, s, mt, ms, act, why in MONTHLY_FIXES:
        for m in _months(ms):
            i = (c, s, mt, m)
            if i not in r.index:
                continue
            v = r.at[i, "value_raw"]
            if act.startswith("set:"):
                r.loc[i, ["value", "flag"]] = [float(act[4:]), "anomaly"]
            elif act.startswith("swap:"):
                j = (c, s, act[5:], m)
                r.loc[i, "value"], r.loc[j, "value"] = r.at[j, "value_raw"], v
                r.loc[[i, j], "flag"] = "anomaly"
                r.loc[j, "note"] = why
            elif act in ("n_share", "dn_split"):
                sh = r.xs(("el", s)).value_raw.unstack("meter")
                med = (sh.N / (sh.D + sh.N)).median()
                d = r.at[("el", s, "D", m), "value_raw"]
                if act == "n_share":
                    r.loc[i, ["value", "flag"]] = [d * med / (1 - med), "anomaly"]
                else:
                    r.loc[("el", s, "D", m), "value"], r.loc[("el", s, "N", m), "value"] = d * (1 - med), d * med
                    r.loc[[("el", s, "D", m), ("el", s, "N", m)], "flag"] = "split"
                    r.loc[("el", s, "N", m), "note"] = why
            elif act == "pair_avg":
                pair = [(c, s, mt, x) for x in _months(ms)]
                r.loc[pair, ["value", "flag"]] = [np.nanmean(r.loc[pair, "value_raw"].fillna(0)), "split"]
            elif act == "drop":
                r.loc[i, ["value", "flag"]] = [np.nan, "anomaly"]
            elif act == "suspect":
                r.loc[i, "flag"] = "suspect"
            r.loc[i, "note"] = why
        if act != "suspect" or ms[0] == ms[-1]:
            log("ds_monthly", s, f"{c} {mt}", ms[0], ms[-1], len(ms), why, act)
    log("ds_monthly", "ds14", "heat co+cw", "2023-01", "2023-11", 11, "co/cw split implausible (cw > co in winter)", "kept, flag suspect")
    # impute remaining NaN
    miss = r.value.isna()
    est = _impute_monthly(r)
    r.loc[miss, "value"] = est.reindex(r.index[miss]).to_numpy()
    r.loc[miss & (r.flag == "ok"), "flag"] = "interp"
    for idx in r.index[miss & r.value_raw.isna() & ~closed]:
        if r.at[idx, "flag"] == "interp":
            r.at[idx, "note"] = r.at[idx, "note"] or "no data"
    n_int = int((miss & r.value_raw.isna()).sum())
    log("ds_monthly", "*", "*", "", "", n_int, "empty / text cells (meter change notes, missing readings)", "imputed: peer-seasonal / yoy level")
    r["flag"] = r.flag.where(r.value.notna(), "missing")
    return r.reset_index()[MONTHLY_COLS]


def ds_monthly_wide(carrier="el") -> pd.DataFrame:
    """month x site, meters summed (el kWh / heat GJ)."""
    d = load("ds_monthly")
    return d[d.carrier == carrier].pivot_table(index="month", columns="site", values="value", aggfunc="sum")


def load_d17_heat() -> pd.DataFrame:
    """Monthly 2024: GJ, MW (ordered capacity?), zł. Raw file not delivered yet (2026-10-21)."""
    if not raw_path("d17_heat").exists():
        raise FileNotFoundError(2, "not delivered", str(raw_path("d17_heat")))
    raise NotImplementedError
