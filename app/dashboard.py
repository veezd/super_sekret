"""Interactive browser for data/processed/*.parquet. Run: .venv/bin/streamlit run app/dashboard.py
All data logic lives in src/htd/catalog.py; this file is UI only. UI + chart labels in Polish.
Every control is shown only when it can change something for the current selection (others use neutral defaults);
conditional widgets use persist_state="page" so their value survives being hidden."""
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots
from htd import catalog as C

st.set_page_config(page_title="Hack the Dorm – dane", page_icon="⚡", layout="wide")

# ---------- palette (dataviz reference instance, validated light/dark) ----------
PAL = {"light": ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"],
       "dark": ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"]}
DASHES = ["solid", "dash", "dot", "dashdot", "longdash", "longdashdot"]  # 9th+ series: same hues, new dash
SEQ = {"light": ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#104281"],
       "dark": ["#104281", "#256abf", "#3987e5", "#86b6ef", "#cde2fb"]}
FLAG_STYLE = {  # status colors reserved for data quality; always symbol + label, never color alone
    "anomaly": ("x", "#d03b3b", "anomalia (zastąpiona)"), "missing": ("circle-open", "#d03b3b", "brak danych"),
    "gapfill": ("diamond", "#ec835a", "luka uzupełniona"), "interp": ("diamond-open", "#ec835a", "interpolacja"),
    "split": ("square-open", "#fab219", "podział odczytu"), "suspect": ("triangle-up", "#fab219", "podejrzana (bez zmian)")}
FLAG_PL = {"ok": "ok", **{k: v[2] for k, v in FLAG_STYLE.items()}}
DIMS_PL = {"series": "nie łącz (każdy licznik osobno)", "site": "obiekt (suma liczników)", "carrier": "nośnik (prąd/ciepło)", "dataset": "zbiór danych"}
SPLIT_PL = {"dataset": "zbiór danych", "site": "obiekt", "carrier": "nośnik", "series": "seria"}
RES = {"Auto": "auto", "Natywna": None, "15 min": "15min", "1 h": "1h", "1 dzień": "1D", "1 tydzień": "W-MON", "1 miesiąc": "MS", "1 rok": "YS"}
RES_H = {"15min": 0.25, "1h": 1, "1D": 24, "W-MON": 168, "MS": 730, "YS": 8760}
NORM = {"none": "brak", "pct_max": "% maksimum serii", "zscore": "z-score (kształt)", "pct_total": "% sumy pokazanych serii"}
MONTHS = ["sty", "lut", "mar", "kwi", "maj", "cze", "lip", "sie", "wrz", "paź", "lis", "gru"]
WDAYS = ["Pn", "Wt", "Śr", "Cz", "Pt", "Sb", "Nd"]
ZONES = {"peak_am": "szczyt przedpołudniowy", "peak_pm": "szczyt popołudniowy", "off": "pozaszczytowa"}
SEASONS = ["zima", "wiosna", "lato", "jesień"]
KINDS = ["Linia", "Schodki", "Punkty", "Słupki", "Słupki skumulowane", "Obszar skumulowany"]
WINDOWS = {"Rok": 365, "Miesiąc": 30, "Tydzień": 7, "Doba": 1}
V_TS, V_PROF, V_HEAT, V_DUR, V_STATS, V_DATA, V_LOG = ("Przebieg czasowy", "Profil dobowy", "Mapa cieplna",
                                                      "Krzywa uporządkowana", "Statystyki", "Dane", "Log anomalii")
SUB_DAILY_VIEWS = {V_PROF, V_HEAT, V_DUR}
P = {"persist_state": "page"}
PLOT_CFG = {"displaylogo": False}

theme = st.context.theme.type or "light"
pal, seq = PAL[theme], SEQ[theme]
ss = st.session_state


@st.cache_data(show_spinner="Wczytywanie danych…")
def load(name: str, mtime: float) -> pd.DataFrame:  # mtime -> cache invalidates after rebuild
    return C.add_calendar(C.load(name))


def file_mtime(name):
    return (C.PROCESSED / f"{name}.parquet").stat().st_mtime


def res_name(h: float) -> str:
    return {0.25: "15 min", 1.0: "1 h", 24.0: "1 dzień"}.get(round(h, 2), "miesiąc" if h >= 24 * 27 else f"{h:g} h")


def keep(items, col: pd.Series) -> list:
    """Items present in col, in items' order. Build the set once: iterating arrow-backed columns row by row is slow."""
    u = set(col.unique())
    return [x for x in items if x in u]


def partitions(meta: pd.DataFrame, keys: dict[str, pd.Series]) -> list[str]:
    """Options whose grouping of series is non-trivial (>1 group) and differs from earlier options."""
    out, seen = [], set()
    for k, key in keys.items():
        part = frozenset(meta.groupby(key.to_numpy()).series.agg(frozenset))
        if len(part) > 1 and part not in seen:
            out.append(k)
            seen.add(part)
    return out


# ---------- time-window state (date_input key "dates"; last complete range in "dates_ok") ----------
def sync_dates(lo, hi):
    """On data bounds change: follow full range if it was untouched, else clamp the user's range."""
    prev, cur = ss.get("bounds"), ss.get("dates_ok")
    if prev == (lo, hi):
        return
    if cur is None or prev is None or cur == prev:
        new = (lo, hi)
    else:
        a, b = max(cur[0], lo), min(cur[1], hi)
        new = (a, b) if a <= b else (lo, hi)
    ss.dates = ss.dates_ok = new
    ss.bounds = (lo, hi)


def current_dates(lo, hi):
    d = ss.get("dates")
    d = tuple(d) if d is not None and len(d) == 2 else ss.get("dates_ok", (lo, hi))
    a, b = max(d[0], lo), min(d[1], hi)
    return (a, b) if a <= b else (lo, hi)


def set_window(days, lo, hi):
    end = current_dates(lo, hi)[1]
    ss.dates = ss.dates_ok = (lo, hi) if days is None else (max(lo, end - timedelta(days=days - 1)), end)


def shift_window(step, lo, hi):
    a, b = current_dates(lo, hi)
    n = b - a + timedelta(days=1)
    if step > 0:
        b = min(hi, b + n)
        a = max(lo, b - n + timedelta(days=1))
    else:
        a = max(lo, a - n)
        b = min(hi, a + n - timedelta(days=1))
    ss.dates = ss.dates_ok = (a, b)


# ---------- sidebar: data ----------
sb = st.sidebar
sb.title("⚡ Hack the Dorm")
names = C.discover()
if not names:
    st.error("Brak plików w data/processed/. Uruchom: `.venv/bin/python scripts/01_build_processed.py`")
    st.stop()
sel = sb.multiselect("Zbiory danych (pliki parquet)", names, default=[n for n in ("hala", "d17", "basen") if n in names],
                     key="sel", help="Możesz łączyć dowolne pliki. Uwaga: sites_2025_15min i ds_profile_15min to wersje "
                                     "zbiorcze (szerokie) plików hala/d17/basen i ds_profile – nie sumuj ich z nimi.")
if not sel:
    st.info("Wybierz co najmniej jeden zbiór danych w panelu bocznym.")
    st.stop()
raw = pd.concat([load(n, file_mtime(n)) for n in sel], ignore_index=True)
if {"sites_2025_15min", "hala"} <= set(sel) or {"ds_profile_15min", "ds_profile"} <= set(sel):
    sb.warning("Wybrano plik zbiorczy i jego źródło – te same dane występują dwa razy.")

base, by = raw, "series"
if raw.series.nunique() > 1:
    with sb.expander("Obiekty i serie", expanded=True):
        site_opts = sorted(raw.site.unique())
        sites = st.multiselect("Obiekty (puste = wszystkie)", site_opts, key="sites", **P) if len(site_opts) > 1 else []
        if sites:
            base = base[base.site.isin(sites)]
        car_opts = sorted(base.carrier.unique())
        if len(car_opts) > 1:
            carriers = st.pills("Nośnik (puste = wszystkie)", car_opts, selection_mode="multi", key="carriers",
                                format_func={"el": "prąd", "heat": "ciepło"}.get, **P)
            if carriers:
                base = base[base.carrier.isin(carriers)]
        ser_opts = sorted(base.series.unique())
        if len(ser_opts) > 1:
            meters = st.multiselect("Serie źródłowe / liczniki (puste = wszystkie)", ser_opts, key="meters", **P)
            if meters:
                base = base[base.series.isin(meters)]
        by_opts = C.merge_options(base)
        if len(by_opts) > 1:
            by = st.selectbox("Łącz serie wg", by_opts, format_func=DIMS_PL.get, key="by", **P,
                              help="Np. 'obiekt' sumuje liczniki ZAS1+ZAS2 w jedną serię D-17.")
if base.empty:
    st.warning("Brak danych dla wybranych obiektów / nośników.")
    st.stop()

# ---------- sidebar: time ----------
lo, hi = C.span(base)
sync_dates(lo, hi)
cur = current_dates(lo, hi)
span_days = (hi - lo).days + 1
native_min = float(base.dur_h.min())
with sb.expander("Zakres czasu", expanded=True):
    wins = [k for k, n in WINDOWS.items() if n < span_days and n * 24 >= 4 * native_min]
    with st.container(horizontal=True, gap="small"):
        st.button("Całość", on_click=set_window, args=(None, lo, hi), disabled=cur == (lo, hi))
        for k in wins:
            st.button(k, on_click=set_window, args=(WINDOWS[k], lo, hi), help=f"Ostatnie {WINDOWS[k]} dni wybranego zakresu")
    if cur != (lo, hi):
        with st.container(horizontal=True, gap="small"):
            st.button("Wcześniej", icon=":material/chevron_left:", on_click=shift_window, args=(-1, lo, hi),
                      disabled=cur[0] <= lo, width="stretch")
            st.button("Później", icon=":material/chevron_right:", on_click=shift_window, args=(1, lo, hi),
                      disabled=cur[1] >= hi, width="stretch")
    dates = st.date_input("Zakres dat", min_value=lo, max_value=hi, key="dates", format="DD.MM.YYYY")
    if len(dates) == 2:
        ss.dates_ok = tuple(dates)
    else:
        st.caption("Wybierz datę końcową – do tego czasu obowiązuje poprzedni zakres.")
    d0, d1 = current_dates(lo, hi)
    in_range = C.filter_df(base, start=d0, end=d1)
    if (in_range.dur_h >= 24 * 27).any() and (d0.day != 1 or (d1 + timedelta(days=1)).day != 1):
        st.caption("Dane miesięczne: miesiąc przecięty zakresem jest uwzględniony w całości.")
    mo_opts = sorted(in_range.month.unique())
    months = st.multiselect("Miesiące (puste = wszystkie)", mo_opts, format_func=lambda m: MONTHS[m - 1],
                            key="months", **P) if len(mo_opts) > 1 else []
    years = sorted(in_range.year.unique())
    overlay = len(years) > 1 and st.toggle("Nałóż lata na jeden rok (porównanie sezonowe)", key="overlay", **P,
                                           help="Każdy rok staje się osobną serią przesuniętą na rok referencyjny.")
    ref_year = st.selectbox("Rok referencyjny", years, index=len(years) - 1, key="ref_year", **P) if overlay else None
if in_range.empty:
    st.warning("Brak danych w wybranym zakresie dat.")
    st.stop()

# calendar filters: only sub-daily rows, only controls that can split the data in range
sub = in_range[in_range.dur_h < 24]
wd, daytype, hours, zones, capacity_only = [], "all", (0, 24), [], False
if not sub.empty:
    with sb.expander("Dni i godziny"):
        if (in_range.dur_h >= 24).any():
            st.caption("Dotyczy tylko serii 15 min / 1 h – serie miesięczne pozostają bez zmian.")
        wd_opts = sorted(sub.weekday.unique())
        if len(wd_opts) > 1:
            wd = st.pills("Dni tygodnia (puste = wszystkie)", wd_opts, selection_mode="multi",
                          format_func=lambda i: WDAYS[i], key="wd", **P)
        if sub.workday.nunique() > 1:
            daytype = st.segmented_control("Typ dnia", ["all", "workday", "free"], default="all", key="daytype", **P,
                                           format_func={"all": "wszystkie", "workday": "robocze", "free": "wolne + święta"}.get) or "all"
        hours = st.slider("Godziny doby", 0, 24, (0, 24), key="hours", **P)
        z_opts = keep(ZONES, sub.zone)
        if len(z_opts) > 1:
            zones = st.multiselect("Strefa taryfy B23 (puste = wszystkie)", z_opts, format_func=ZONES.get, key="zones", **P)
        if sub.capacity.nunique() > 1:
            capacity_only = st.toggle("Tylko godziny opłaty mocowej (dni rob. 7–22)", key="capacity_only", **P)

fl_present = keep([fl for fl in C.FLAG_ORDER if fl != "ok"], in_range.flag)
excl = []
if fl_present:
    with sb.expander("Jakość danych"):
        excl = st.multiselect("Wyklucz punkty z flagą", fl_present, format_func=FLAG_PL.get, key="excl_flags", **P,
                              help="Domyślnie pokazywane są wszystkie punkty (też poprawione).")

# ---------- pipeline ----------
f = C.filter_df(in_range, months=months or None, weekdays=wd, daytype=daytype, hours=hours, zones=zones or None,
                capacity_only=capacity_only, flags=[x for x in C.FLAG_ORDER if x not in excl] if excl else None)
if overlay:
    f = C.overlay_years(f, ref_year)
    base_keys = C.series_key(C.overlay_years(base, ref_year), by)
else:
    base_keys = C.series_key(base, by)
if f.empty:
    st.warning("Filtry nie zostawiły żadnych danych.")
    st.stop()
g = C.group(f, by)
order = sorted(base_keys.unique())  # colour follows entity, independent of filters
style = {s: (pal[i % 8], DASHES[(i // 8) % len(DASHES)]) for i, s in enumerate(order)}
present = keep(order, g.series)
native_h = g.groupby("series").dur_h.median()
fine = g[g.dur_h < 24]

# ---------- main: header + view tabs ----------
st.subheader("Przegląd danych energetycznych MS AGH")
hdr = st.container()
log = C.anomaly_log()
# fixed tab list: a changing list would reset the selected tab; inapplicable views explain why instead of vanishing
views = [V_TS, V_PROF, V_HEAT, V_DUR, V_STATS, V_DATA, V_LOG]
tabs = dict(zip(views, st.tabs(views, key="view", on_change="rerun")))
view = next((v for v, t in tabs.items() if t.open), views[0])
blocked = None
if view in SUB_DAILY_VIEWS and fine.empty:
    if (raw.dur_h < 24).any():
        blocked = "Filtry (zakres dat, obiekty, dni i godziny, flagi) usunęły wszystkie serie 15 min / 1 h."
    else:
        alt = [n for n in names if n not in sel and (load(n, file_mtime(n)).dur_h < 24).any()]
        blocked = ("Ten widok wymaga danych 15 min / 1 h, a wybrane zbiory mają tylko dane miesięczne. "
                   f"Dodaj w panelu bocznym np.: {', '.join(alt)}.")
elif view == V_LOG and log.empty:
    blocked = "Brak outputs/tables/anomaly_log.csv – uruchom scripts/01_build_processed.py"
if blocked:
    tabs[view].info(blocked, icon=":material/info:")
    view = None  # nothing to configure or draw

with hdr:
    with st.container(horizontal=True, gap="medium"):
        res_txt = res_name(native_h.min()) + ("" if native_h.nunique() == 1 else f" … {res_name(native_h.max())}")
        st.metric("Serie", len(present), width="content")
        st.metric("Zakres danych", "{:%d.%m.%y} – {:%d.%m.%y}".format(*C.span(f)), width="content")
        st.metric("Rozdzielczość natywna", res_txt, width="content")
        st.metric("Energia w filtrze", f"{g.kwh.sum() / 1000:,.1f} MWh".replace(",", " "), width="content")
        if (g.flag != "ok").any():
            st.metric("Punkty z flagą", f"{(g.flag != 'ok').mean():.2%}", width="content")
    if overlay:
        st.caption(f"Lata nałożone na rok {ref_year} – zakres dat dotyczy dat oryginalnych.")

# ---------- sidebar: settings of the active view only ----------
chart_views = {V_TS, V_PROF, V_HEAT, V_DUR}
rule, measure, norm, win, a = None, "p_mean", "none", 1, None
mode, split, ncols, kind, shared_y, rangeslider, show_raw, mark_flags = "one", None, 1, "Linia", False, False, False, False
psplit, pstat, pcols, hm_series = "none", "mean", 1, None
mega, height = "k", 450
if view in chart_views | {V_DATA}:
    with sb.expander(f"Ustawienia: {view.lower()}", expanded=True):
        if view in (V_TS, V_DATA):
            span_h = (g.ts.max() - g.ts.min()) / pd.Timedelta("1h") + native_h.min()
            coarse = [r for r, h in RES_H.items() if h > native_h.min() and span_h / h >= 2]
            res_opts = ["Auto", "Natywna"] + [k for k, v in RES.items() if v in coarse]
            res_lab = st.selectbox("Rozdzielczość", res_opts, key="res", **P,
                                   help="Auto: najdrobniejsza dająca ≤ 4000 punktów na serię.") if coarse else "Natywna"
            rule = RES[res_lab]
            if rule == "auto":
                rule = None
                if span_h / native_h.min() > 4000:
                    rule = next((r for r, h in RES_H.items() if h >= native_h.min() and span_h / h <= 4000), "MS")
            m_opts = ["energy", "p_mean"] + (["p_max", "p_min"] if rule and RES_H[rule] > native_h.min() else [])
            measure = st.selectbox("Wielkość", m_opts, index=1, format_func=C.MEASURES.get, key="measure", **P,
                                   help="Moc średnia jest porównywalna między rozdzielczościami; energia = suma w okresie. "
                                        "Moc maks./min. dostępna po agregacji do grubszej rozdzielczości.")
            n_opts = [k for k in NORM if k != "pct_total" or len(present) > 1]
            norm = st.selectbox("Normalizacja", n_opts, format_func=NORM.get, key="norm", **P)
            a = C.aggregate(g, rule, measure)
            if a.groupby("series").size().max() >= 10:
                win = st.slider("Wygładzanie (średnia krocząca, punkty)", 1, 48, 1, key="win", **P)
            a = C.smooth(C.normalize(a, norm), win)
        if norm == "none":
            mega = st.segmented_control("Skala", ["k", "M"], default="k", key="mega", **P,
                                        format_func={"k": "kWh / kW", "M": "MWh / MW"}.get) or "k"
        if view == V_TS:
            kinds = KINDS if len(present) > 1 else KINDS[:4]
            kind = st.selectbox("Typ wykresu", kinds, key="kind", **P)
            meta = g.drop_duplicates("series").set_index("series", drop=False)
            pkeys = {"dataset": meta.dataset, "site": meta.dataset + " · " + meta.site.astype(str),
                     "carrier": meta.dataset + " · " + meta.carrier, "series": meta.series}
            split_opts = partitions(meta, pkeys)
            if split_opts:
                mode = st.segmented_control("Układ", ["one", "grid", "stack"], default="one", key="mode", **P,
                                            format_func={"one": "jeden wykres", "grid": "obok siebie", "stack": "pod sobą"}.get) or "one"
            if mode != "one":
                split = st.selectbox("Rozdziel wykresy wg", split_opts, format_func=SPLIT_PL.get, key="split", **P) \
                    if len(split_opts) > 1 else split_opts[0]
                pmap = pkeys[split].to_dict()
                n_panels = len(set(pmap.values()))
                if mode == "grid" and n_panels > 2:
                    ncols = st.slider("Kolumn (obok siebie)", 1, min(4, n_panels), min(2, n_panels), key="ncols", **P)
                else:
                    ncols = min(2, n_panels)
                shared_y = st.toggle("Wspólna skala Y", value=True, key="shared_y", **P)
            rangeslider = st.toggle("Suwak zakresu czasu pod wykresem", key="rangeslider", **P)
            if (g.flag != "ok").any():
                mark_flags = st.toggle("Zaznacz punkty z flagą", value=True, key="mark_flags", **P)
            if norm != "pct_total" and (g.raw.notna() & ~np.isclose(g.raw, g.kwh)).any():
                show_raw = st.toggle("Pokaż dane surowe (przed czyszczeniem)", key="show_raw", **P,
                                     help="Linia kropkowana tego samego koloru.")
        if view == V_PROF:
            part_opts = ["none"] + [k for k, col in (("daytype", fine.workday), ("season", fine.month % 12 // 3),
                                                     ("month", fine.month), ("zone", fine.zone)) if col.nunique() > 1]
            psplit = st.selectbox("Podział", part_opts, key="psplit", **P,
                                  format_func={"none": "brak", "daytype": "dzień roboczy / wolny", "season": "pora roku",
                                               "month": "miesiąc", "zone": "strefa B23"}.get)
            pstat = st.selectbox("Statystyka", ["mean", "median", "max", "min", "p90"], key="pstat", **P,
                                 format_func={"mean": "średnia", "median": "mediana", "max": "maksimum", "min": "minimum", "p90": "90. percentyl"}.get)
        if view == V_HEAT:
            hm_opts = keep(order, fine.series)
            hm_series = st.selectbox("Seria", hm_opts, key="hm_series", **P) if len(hm_opts) > 1 else hm_opts[0]
        if view in chart_views:
            height = st.slider("Wysokość wykresu [px]", 250, 1000, 450, step=50, key="height", **P)

focus, dimmed, hidden, dim_op = "—", [], [], 0.2
if view in {V_TS, V_PROF, V_DUR} and len(present) > 1:
    with sb.expander("Widoczność serii"):
        focus = st.selectbox("Wyróżnij serię (pozostałe wygaszone)", ["—"] + present, key="focus", **P)
        dimmed = st.multiselect("Wygaszone (półprzezroczyste)", present, key="dimmed", **P)
        hidden = st.multiselect("Ukryte (włączysz klikając w legendę)", present, key="hidden", **P)
        if focus != "—" or dimmed:
            dim_op = st.slider("Krycie wygaszonych", 0.05, 0.6, 0.2, 0.05, key="dim_op", **P)
        st.caption("W legendzie: klik = ukryj/pokaż, dwuklik = tylko ta seria.")

scale = 1000 if mega == "M" else 1
punit = "MW" if scale > 1 else "kW"
if a is not None:
    a["value"], a["raw"] = a.value / scale, a.raw / scale
unit = NORM[norm] if norm != "none" else ("MWh" if scale > 1 else "kWh") if measure == "energy" else punit
ylab = f"{C.MEASURES[measure]} [{unit}]"
# reset zoom whenever the data window changes; keep it for pure styling changes
uirev = str((d0, d1, tuple(sel), by, rule, measure, norm, overlay, ref_year, mode, split))


# ---------- chart builders ----------
def trace_style(s):
    color, dash = style.get(s, (pal[0], "solid"))
    vis = "legendonly" if s in hidden else True
    op = dim_op if (s in dimmed or (focus != "—" and s != focus)) else 1.0
    return color, dash, vis, op


def add_series(fig, d, s, seen_flags, row=None, legend=True):
    color, dash, vis, op = trace_style(s)
    kw = dict(name=s, legendgroup=s, showlegend=legend, visible=vis, opacity=op, legendrank=order.index(s) if s in order else 999)
    x, y = d.ts, d.value
    hov = "%{x|%d.%m.%Y %H:%M}<br>%{y:,.2f} " + unit + "<extra>" + s + "</extra>"
    pos = dict(row=row, col=1 if row else None)
    if kind in ("Linia", "Schodki", "Punkty"):
        tr = go.Scattergl(x=x, y=y, mode="markers" if kind == "Punkty" else "lines", hovertemplate=hov,
                          line=dict(color=color, width=2, dash=dash, shape="hv" if kind == "Schodki" else "linear"),
                          marker=dict(color=color, size=5), **kw)
    elif kind.startswith("Słupki"):
        tr = go.Bar(x=x, y=y, marker=dict(color=color, line=dict(width=0)), hovertemplate=hov, **kw)
    else:
        tr = go.Scatter(x=x, y=y, mode="lines", stackgroup="one", line=dict(color=color, width=1), hovertemplate=hov, **kw)
    fig.add_trace(tr, **pos)
    if show_raw and d.raw.notna().any() and not kind.endswith("skumulowany"):
        fig.add_trace(go.Scattergl(x=x, y=d.raw, mode="lines", name=f"{s} (surowe)", legendgroup=s, showlegend=False,
                                   visible=vis, opacity=op * 0.9, line=dict(color=color, width=1, dash="dot"),
                                   hovertemplate="%{x|%d.%m.%Y %H:%M}<br>surowe: %{y:,.2f}<extra>" + s + "</extra>"), **pos)
    if mark_flags:
        for fl, b in d[d.flag != "ok"].groupby("flag"):
            sym, col, lab = FLAG_STYLE.get(fl, ("circle", "#d03b3b", fl))
            fig.add_trace(go.Scattergl(x=b.ts, y=b.value, mode="markers", name=lab, legendgroup="flag_" + fl, legendrank=2000,
                                       showlegend=fl not in seen_flags, visible=vis,
                                       marker=dict(symbol=sym, color=col, size=9, line=dict(width=2, color=col)),
                                       hovertemplate="%{x|%d.%m.%Y %H:%M}<br>" + lab + "<extra>" + s + "</extra>"), **pos)
            seen_flags.add(fl)


def finish(fig, h, title=None, yrange=None):
    fig.update_layout(height=h, margin=dict(l=10, r=10, t=40 if title else 10, b=10), title=title,
                      hovermode="x unified" if len(present) <= 8 else "closest",
                      legend=dict(orientation="h", yanchor="top", y=-0.12 if not rangeslider else -0.25, x=0),
                      barmode="stack" if kind == "Słupki skumulowane" else "group", bargap=0.1, uirevision=uirev)
    fig.update_yaxes(title_text=ylab, gridcolor="rgba(128,128,128,0.15)", zeroline=False, range=yrange)
    fig.update_xaxes(gridcolor="rgba(128,128,128,0.15)")
    last = sorted((k for k in fig.layout if k.startswith("xaxis")), key=lambda k: int(k[5:] or 1))
    fig.layout[last[-1] if last else "xaxis"].rangeslider = dict(visible=rangeslider, thickness=0.06)
    return fig


def yrange_all(d):
    if not shared_y or norm == "pct_total" or kind in ("Słupki skumulowane", "Obszar skumulowany"):
        return None
    v = pd.concat([d.value, d.raw if show_raw else d.value]).dropna()
    if v.empty:
        return None
    lo_, hi_ = float(v.min()), float(v.max())
    pad = (hi_ - lo_) * 0.05 or 1
    return [min(lo_ - pad, 0) if lo_ >= 0 else lo_ - pad, hi_ + pad]


# ---------- views (only the open tab is computed) ----------
if view == V_TS:
    with tabs[V_TS]:
        rtxt = res_name(RES_H[rule]) if rule else "natywna"
        st.caption(f"Rozdzielczość: {rtxt} · {C.MEASURES[measure]} · łączenie: {DIMS_PL[by]} · "
                   f"{len(a):,} punktów".replace(",", " "))
        if native_h.nunique() > 1 and measure == "energy" and (rule is None or RES_H[rule] < native_h.max()):
            st.info("Serie mają różne rozdzielczości (np. 15 min i miesiąc) – energii w punkcie nie da się porównać. "
                    "Wybierz 'Moc średnia' albo wspólną rozdzielczość.")
        if kind.startswith("Słupki") and len(a) > 20000:
            st.warning("Dużo słupków – wykres może działać wolno. Zwiększ rozdzielczość (np. 1 dzień).")
        seen = set()
        shown = keep(present, a.series)
        if mode == "one":
            fig = go.Figure()
            for s in shown:
                add_series(fig, a[a.series == s], s, seen)
            st.plotly_chart(finish(fig, height), width="stretch", config=PLOT_CFG)
        else:
            groups = {}
            for s in shown:
                groups.setdefault(pmap[s], []).append(s)
            yr = yrange_all(a)
            if mode == "stack":
                fig = make_subplots(rows=len(groups), cols=1, shared_xaxes=True, vertical_spacing=0.04,
                                    subplot_titles=list(groups))
                done = set()
                for i, ss_ in enumerate(groups.values(), start=1):
                    for s in ss_:
                        add_series(fig, a[a.series == s], s, seen, row=i, legend=s not in done)
                        done.add(s)
                fig = finish(fig, max(height, 220 * len(groups)), yrange=yr)
                st.plotly_chart(fig, width="stretch", config=PLOT_CFG)
            else:
                items = list(groups.items())
                for r0 in range(0, len(items), ncols):
                    cols = st.columns(ncols)
                    for col, (p, ss_) in zip(cols, items[r0:r0 + ncols]):
                        fig = go.Figure()
                        for s in ss_:
                            add_series(fig, a[a.series == s], s, seen)
                        col.plotly_chart(finish(fig, height, title=p, yrange=yr), width="stretch", config=PLOT_CFG)

elif view in SUB_DAILY_VIEWS:
    fine = fine.assign(kw=fine.kwh / fine.dur_h / scale)
    if (g.dur_h >= 24).any():
        tabs[view].caption("Widok liczony tylko z serii 15 min / 1 h (serie miesięczne pominięte).")

if view == V_PROF:
    with tabs[V_PROF]:
        lab = {"none": lambda d: pd.Series("wszystkie dni", index=d.index),
               "daytype": lambda d: d.workday.map({True: "robocze", False: "wolne + święta"}),
               "season": lambda d: d.month.map(lambda x: SEASONS[(x % 12) // 3]),
               "month": lambda d: d.month.map(lambda x: f"{x:02d} {MONTHS[x - 1]}"),
               "zone": lambda d: d.zone.map(ZONES)}[psplit]
        fp = fine.assign(part=lab(fine), hb=(fine.hour * 4).round() / 4)
        agg = (lambda x: x.quantile(0.9)) if pstat == "p90" else pstat
        prof = fp.groupby(["part", "series", "hb"]).kw.agg(agg).reset_index()
        parts = sorted(prof.part.unique())
        if len(parts) > 1:
            c1, c2 = st.columns(2)
            pcols = c1.slider("Kolumn", 1, min(4, len(parts)), min(2, len(parts)), key="pcols", **P)
            shared_y = c2.toggle("Wspólna skala Y", value=True, key="p_shared_y", **P)
        ylim = [0, prof.kw.max() * 1.05] if shared_y else None
        for r0 in range(0, len(parts), pcols):
            cols = st.columns(pcols)
            for col, p in zip(cols, parts[r0:r0 + pcols]):
                fig = go.Figure()
                for s in keep(order, prof.series):
                    d = prof[(prof.part == p) & (prof.series == s)]
                    color, dash, vis, op = trace_style(s)
                    fig.add_trace(go.Scatter(x=d.hb, y=d.kw, name=s, mode="lines", visible=vis, opacity=op,
                                             line=dict(color=color, dash=dash, width=2, shape="hv"),
                                             hovertemplate="%{x:.2f} h: %{y:,.1f} " + punit + "<extra>" + s + "</extra>"))
                fig.update_layout(height=max(300, height * 0.8), title=p if len(parts) > 1 else None,
                                  margin=dict(l=10, r=10, t=40 if len(parts) > 1 else 10, b=10),
                                  legend=dict(orientation="h", y=-0.2), hovermode="x unified")
                fig.update_xaxes(title_text="godzina", dtick=2, range=[0, 24])
                fig.update_yaxes(title_text=f"moc [{punit}]", range=ylim, gridcolor="rgba(128,128,128,0.15)")
                col.plotly_chart(fig, width="stretch", config=PLOT_CFG)

elif view == V_HEAT:
    with tabs[V_HEAT]:
        d = fine[fine.series == hm_series]
        hm = d.assign(date=d.ts.dt.date, hb=(d.hour * 4).round() / 4).pivot_table(index="hb", columns="date", values="kw", aggfunc="mean")
        fig = go.Figure(go.Heatmap(z=hm.values, x=hm.columns, y=hm.index, colorscale=[[i / 4, c] for i, c in enumerate(seq)],
                                   colorbar=dict(title=punit), hovertemplate="%{x}<br>%{y:.2f} h<br>%{z:,.1f} " + punit + "<extra></extra>"))
        fig.update_layout(height=height, margin=dict(l=10, r=10, t=30, b=10), title=hm_series)
        fig.update_yaxes(title_text="godzina", autorange="reversed", dtick=2)
        st.plotly_chart(fig, width="stretch", config=PLOT_CFG)
        st.caption("Jasne = niska moc, ciemne = wysoka. Pionowe pasy = dni nietypowe (święta, awarie).")

elif view == V_DUR:
    with tabs[V_DUR]:
        fig = go.Figure()
        for s in keep(order, fine.series):
            v = np.sort(fine[fine.series == s].kw.dropna().to_numpy())[::-1]
            color, dash, vis, op = trace_style(s)
            fig.add_trace(go.Scattergl(x=np.linspace(0, 100, len(v)), y=v, name=s, mode="lines", visible=vis, opacity=op,
                                       line=dict(color=color, dash=dash, width=2),
                                       hovertemplate="%{x:.1f}% czasu ≥ %{y:,.1f} " + punit + "<extra>" + s + "</extra>"))
        fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=1.05))
        fig.update_xaxes(title_text="% czasu (w filtrze)")
        fig.update_yaxes(title_text=f"moc [{punit}]", gridcolor="rgba(128,128,128,0.15)")
        st.plotly_chart(fig, width="stretch", config=PLOT_CFG)

elif view == V_STATS:
    with tabs[V_STATS]:
        stt = C.stats(g)
        if fine.empty:
            stt = stt.drop(columns="udzial_godz_mocowych_%")
        st.dataframe(stt, width="stretch")
        st.download_button("Pobierz CSV", stt.to_csv().encode("utf-8"), "statystyki.csv", "text/csv")
        st.caption("Liczone na danych natywnych po filtrach. Moc min/maks. z interwałów natywnych (dla danych miesięcznych = średnia miesiąca).")

elif view == V_DATA:
    with tabs[V_DATA]:
        wide_t = len(present) > 1 and st.toggle("Tabela szeroka (czas × seria)", value=True, key="wide_t", **P)
        tbl = a.pivot_table(index="ts", columns="series", values="value") if wide_t else a
        st.caption(f"{ylab} · rozdzielczość: {res_name(RES_H[rule]) if rule else 'natywna'}")
        st.dataframe(tbl, width="stretch", height=500)
        st.download_button("Pobierz CSV (dane z wykresu)", tbl.to_csv().encode("utf-8"), "dane.csv", "text/csv")

elif view == V_LOG:
    with tabs[V_LOG]:
        ds_opts = sorted(log.dataset.unique())
        c1, c2 = st.columns([1, 2])
        ds = c1.multiselect("Zbiór (puste = wszystkie)", ds_opts, key="log_ds", **P,
                            default=[d for d in ds_opts if d in sel or d.split("_")[0] in sel])
        q = c2.text_input("Szukaj (obiekt, opis, akcja)", key="log_q", **P)
        lg = log[log.dataset.isin(ds)] if ds else log
        if q:
            lg = lg[lg.astype(str).apply(lambda r: r.str.contains(q, case=False, regex=False)).any(axis=1)]
        st.dataframe(lg, width="stretch", height=500, hide_index=True)
        st.caption(f"{len(lg)} z {len(log)} wpisów. Pełne zasady: docs/methodology.md")
