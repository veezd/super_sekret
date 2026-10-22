"""Interactive browser for data/processed/*.parquet. Run: .venv/bin/streamlit run app/dashboard.py
All data logic lives in src/htd/catalog.py; this file is UI only. UI + chart labels in Polish."""
import sys
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
RES = {"Auto": "auto", "Natywna": None, "15 min": "15min", "1 h": "1h", "1 dzień": "1D", "1 tydzień": "W-MON", "1 miesiąc": "MS", "1 rok": "YS"}
RES_H = {"15min": 0.25, "1h": 1, "1D": 24, "W-MON": 168, "MS": 730, "YS": 8760}
NORM = {"none": "brak", "pct_max": "% maksimum serii", "zscore": "z-score (kształt)", "pct_total": "% sumy pokazanych serii"}
MONTHS = ["sty", "lut", "mar", "kwi", "maj", "cze", "lip", "sie", "wrz", "paź", "lis", "gru"]
WDAYS = ["Pn", "Wt", "Śr", "Cz", "Pt", "Sb", "Nd"]
ZONES = {"peak_am": "szczyt przedpołudniowy", "peak_pm": "szczyt popołudniowy", "off": "pozaszczytowa"}
KINDS = ["Linia", "Schodki", "Punkty", "Słupki", "Słupki skumulowane", "Obszar skumulowany"]

theme = st.context.theme.type or "light"
pal, seq = PAL[theme], SEQ[theme]


@st.cache_data(show_spinner="Wczytywanie danych…")
def load(name: str, mtime: float) -> pd.DataFrame:  # mtime -> cache invalidates after rebuild
    return C.add_calendar(C.load(name))


def file_mtime(name):
    return (C.PROCESSED / f"{name}.parquet").stat().st_mtime


# ---------- sidebar: data ----------
sb = st.sidebar
sb.title("⚡ Hack the Dorm")
names = C.discover()
if not names:
    st.error("Brak plików w data/processed/. Uruchom: `.venv/bin/python scripts/01_build_processed.py`")
    st.stop()
sel = sb.multiselect("Zbiory danych (pliki parquet)", names, default=[n for n in ("hala", "d17", "basen") if n in names],
                     help="Możesz łączyć dowolne pliki. Uwaga: sites_2025_15min i ds_profile_15min to wersje zbiorcze "
                          "(szerokie) plików hala/d17/basen i ds_profile – nie sumuj ich z nimi.")
if not sel:
    st.info("Wybierz co najmniej jeden zbiór danych w panelu bocznym.")
    st.stop()
raw = pd.concat([load(n, file_mtime(n)) for n in sel], ignore_index=True)
if {"sites_2025_15min", "hala"} <= set(sel) or {"ds_profile_15min", "ds_profile"} <= set(sel):
    sb.warning("Wybrano plik zbiorczy i jego źródło – te same dane występują dwa razy.")

with sb.expander("Serie i obiekty", expanded=True):
    sites = st.multiselect("Obiekty (puste = wszystkie)", sorted(raw.site.unique()))
    carriers = st.pills("Nośnik", ["el", "heat"], selection_mode="multi", default=sorted(raw.carrier.unique()),
                        format_func={"el": "prąd", "heat": "ciepło"}.get)
    base = raw[(raw.site.isin(sites) if sites else True) & raw.carrier.isin(carriers or [])]
    meters = st.multiselect("Serie źródłowe / liczniki (puste = wszystkie)", sorted(base.series.unique()))
    if meters:
        base = base[base.series.isin(meters)]
    by = st.selectbox("Łącz serie wg", list(DIMS_PL), format_func=DIMS_PL.get,
                      help="Np. 'obiekt' sumuje liczniki ZAS1+ZAS2 w jedną serię D-17.")
if base.empty:
    st.warning("Brak danych dla wybranych obiektów / nośników.")
    st.stop()

# ---------- sidebar: time ----------
tmin, tmax = base.ts.min().date(), base.ts.max().date()
d0 = st.session_state.get("dates")
if not d0 or len(d0) != 2 or d0[0] < tmin or d0[1] > tmax or d0[0] > tmax or d0[1] < tmin:
    st.session_state["dates"] = (tmin, tmax)  # init / clamp when dataset selection changes the range


def set_window(days):
    end = st.session_state.get("dates", (tmin, tmax))[-1]
    st.session_state["dates"] = (tmin, tmax) if days is None else (max(tmin, end - pd.Timedelta(days=days - 1)), end)


with sb.expander("Czas", expanded=True):
    st.segmented_control("Szybki zakres (od końca wybranego)", ["Całość", "30 dni", "7 dni", "Doba"], key="preset",
                         on_change=lambda: st.session_state.preset and set_window({"Całość": None, "30 dni": 30, "7 dni": 7, "Doba": 1}.get(st.session_state.preset)))
    dates = st.date_input("Zakres dat", min_value=tmin, max_value=tmax, key="dates", format="DD.MM.YYYY")
    if len(dates) != 2:
        dates = (dates[0], dates[0]) if dates else (tmin, tmax)
    months = st.multiselect("Miesiące (puste = wszystkie)", list(range(1, 13)), format_func=lambda m: MONTHS[m - 1])
    overlay = st.toggle("Nałóż lata na jeden rok (porównanie sezonowe)",
                        help="Każdy rok staje się osobną serią przesuniętą na rok referencyjny, np. ds_monthly 2023–2025.")
    years = sorted(base.ts.dt.year.unique())
    ref_year = st.selectbox("Rok referencyjny", years, index=len(years) - 1) if overlay else None
    st.caption("Poniższe filtry działają tylko na danych 15-min / 1-h (nie na miesięcznych).")
    wd = st.pills("Dni tygodnia", list(range(7)), selection_mode="multi", default=list(range(7)), format_func=lambda i: WDAYS[i])
    daytype = st.segmented_control("Typ dnia", ["all", "workday", "free"], default="all",
                                   format_func={"all": "wszystkie", "workday": "robocze", "free": "wolne + święta"}.get)
    hours = st.slider("Godziny doby", 0, 24, (0, 24))
    zones = st.multiselect("Strefa taryfy B23 (puste = wszystkie)", list(ZONES), format_func=ZONES.get)
    capacity_only = st.toggle("Tylko godziny opłaty mocowej (dni rob. 7–22)")

with sb.expander("Jakość danych"):
    flags = st.multiselect("Uwzględnij punkty z flagą", C.FLAG_ORDER, default=C.FLAG_ORDER, format_func=FLAG_PL.get)
    show_raw = st.toggle("Pokaż dane surowe (przed czyszczeniem)", help="Linia przerywana tego samego koloru.")
    mark_flags = st.toggle("Zaznacz punkty z flagą", value=True)

with sb.expander("Agregacja i jednostki", expanded=True):
    res_lab = st.selectbox("Rozdzielczość", list(RES), help="Auto: najdrobniejsza dająca ≤ 4000 punktów na serię (przegląd). Szczegóły: zawęź zakres dat lub wybierz rozdzielczość.")
    measure = st.selectbox("Wielkość", list(C.MEASURES), index=1, format_func=C.MEASURES.get,
                           help="Moc średnia jest porównywalna między rozdzielczościami; energia = suma w okresie.")
    mega = st.segmented_control("Skala", ["k", "M"], default="k", format_func={"k": "kWh / kW", "M": "MWh / MW"}.get)
    norm = st.selectbox("Normalizacja", list(NORM), format_func=NORM.get)
    win = st.slider("Wygładzanie (średnia krocząca, punkty)", 1, 48, 1)

with sb.expander("Widok", expanded=True):
    mode = st.segmented_control("Układ", ["one", "grid", "stack"], default="one",
                                format_func={"one": "jeden wykres", "grid": "obok siebie", "stack": "pod sobą"}.get)
    split = st.selectbox("Rozdziel wykresy wg", ["dataset", "site", "carrier", "series"],
                         format_func={"dataset": "zbiór danych", "site": "obiekt", "carrier": "nośnik", "series": "seria"}.get,
                         disabled=mode == "one")
    ncols = st.slider("Kolumn (obok siebie)", 1, 4, 2, disabled=mode != "grid")
    kind = st.selectbox("Typ wykresu", KINDS)
    height = st.slider("Wysokość wykresu [px]", 250, 1000, 450, step=50)
    shared_y = st.toggle("Wspólna skala Y", value=True)
    rangeslider = st.toggle("Suwak zakresu czasu pod wykresem")

# ---------- pipeline ----------
f = C.filter_df(base, start=dates[0], end=dates[1], months=months or None, weekdays=wd, daytype=daytype or "all",
                hours=hours, zones=zones or None, capacity_only=capacity_only, flags=flags)
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

with sb.expander("Widoczność serii (wygaszanie)", expanded=False):
    present = [s for s in order if s in set(g.series)]
    focus = st.selectbox("Wyróżnij serię (pozostałe wygaszone)", ["—"] + present)
    dimmed = st.multiselect("Wygaszone (półprzezroczyste)", present)
    hidden = st.multiselect("Ukryte (włączysz klikając w legendę)", present)
    dim_op = st.slider("Krycie wygaszonych", 0.05, 0.6, 0.2, 0.05)
    st.caption("W legendzie: klik = ukryj/pokaż, dwuklik = tylko ta seria.")

native_h = g.groupby("series").dur_h.median()
mixed = native_h.nunique() > 1
rule = RES[res_lab]
if rule == "auto":
    span_h = (g.ts.max() - g.ts.min()) / pd.Timedelta("1h") + 1
    rule = None
    if span_h / native_h.min() > 4000:
        rule = next((r for r, h in RES_H.items() if h >= native_h.min() and span_h / h <= 4000), "MS")
a = C.aggregate(g, rule, measure)
a = C.smooth(C.normalize(a, norm), win)
scale = 1000 if (mega == "M" and norm == "none") else 1
a["value"], a["raw"] = a.value / scale, a.raw / scale
unit = NORM[norm] if norm != "none" else ("MWh" if scale > 1 else "kWh") if measure == "energy" else ("MW" if scale > 1 else "kW")
ylab = f"{C.MEASURES[measure]} [{unit}]"
res_txt = next((k for k, v in RES.items() if v == rule), "natywna") if rule else "natywna"

# ---------- header ----------
st.subheader("Przegląd danych energetycznych MS AGH")
with st.container(horizontal=True, gap="medium"):
    for lab, val in [("Serie", a.series.nunique()), ("Zakres", f"{g.ts.min():%d.%m.%y} – {g.ts.max():%d.%m.%y}"),
                     ("Punkty na wykresie", f"{len(a):,}".replace(",", " ")),
                     ("Energia w filtrze", f"{g.kwh.sum() / 1000:,.1f} MWh".replace(",", " ")),
                     ("Punkty z flagą", f"{(g.flag != 'ok').mean():.2%}")]:
        st.metric(lab, val, width="content")
if mixed and measure == "energy" and (rule is None or RES_H[rule] < native_h.max()):
    st.info("Serie mają różne rozdzielczości (np. 15 min i miesiąc) – energii w punkcie nie da się porównać. "
            "Wybierz 'Moc średnia' albo wspólną rozdzielczość.")
if kind.startswith("Słupki") and len(a) > 20000:
    st.warning("Dużo słupków – wykres może działać wolno. Zwiększ rozdzielczość (np. 1 dzień).")


# ---------- chart builders ----------
def trace_style(s):
    color, dash = style.get(s, (pal[0], "solid"))
    vis = "legendonly" if s in hidden else True
    op = dim_op if (s in dimmed or (focus != "—" and s != focus)) else 1.0
    return color, dash, vis, op


def add_series(fig, d, s, row=None, legend=True):
    color, dash, vis, op = trace_style(s)
    kw = dict(name=s, legendgroup=s, showlegend=legend, visible=vis, opacity=op, legendrank=order.index(s) if s in order else 999)
    x, y = d.ts, d.value
    hov = "%{x|%d.%m.%Y %H:%M}<br>%{y:,.2f} " + unit + "<extra>" + s + "</extra>"
    if kind in ("Linia", "Schodki", "Punkty"):
        tr = go.Scattergl(x=x, y=y, mode="markers" if kind == "Punkty" else "lines", hovertemplate=hov,
                          line=dict(color=color, width=2, dash=dash, shape="hv" if kind == "Schodki" else "linear"),
                          marker=dict(color=color, size=5), **kw)
    elif kind.startswith("Słupki"):
        tr = go.Bar(x=x, y=y, marker=dict(color=color, line=dict(width=0)), hovertemplate=hov, **kw)
    else:
        tr = go.Scatter(x=x, y=y, mode="lines", stackgroup="one", line=dict(color=color, width=1), hovertemplate=hov, **kw)
    fig.add_trace(tr, row=row, col=1 if row else None)
    if show_raw and d.raw.notna().any() and not kind.endswith("skumulowany"):
        fig.add_trace(go.Scattergl(x=x, y=d.raw, mode="lines", name=f"{s} (surowe)", legendgroup=s, showlegend=False,
                                   visible=vis, opacity=op * 0.9, line=dict(color=color, width=1, dash="dot"),
                                   hovertemplate="%{x|%d.%m.%Y %H:%M}<br>surowe: %{y:,.2f}<extra>" + s + "</extra>"),
                      row=row, col=1 if row else None)
    if mark_flags:
        bad = d[d.flag != "ok"]
        for fl, b in bad.groupby("flag"):
            sym, col, lab = FLAG_STYLE.get(fl, ("circle", "#d03b3b", fl))
            fig.add_trace(go.Scattergl(x=b.ts, y=b.value, mode="markers", name=lab, legendgroup="flag_" + fl, legendrank=2000,
                                       showlegend=fl not in seen_flags, visible=vis,
                                       marker=dict(symbol=sym, color=col, size=9, line=dict(width=2, color=col)),
                                       hovertemplate="%{x|%d.%m.%Y %H:%M}<br>" + lab + "<extra>" + s + "</extra>"),
                          row=row, col=1 if row else None)
            seen_flags.add(fl)


def finish(fig, h, title=None, yrange=None):
    sub_daily = rule is None and native_h.min() < 24 or (rule is not None and RES_H[rule] < 24)
    fig.update_layout(height=h, margin=dict(l=10, r=10, t=40 if title else 10, b=10), title=title,
                      hovermode="x unified" if len(a.series.unique()) <= 8 else "closest",
                      legend=dict(orientation="h", yanchor="top", y=-0.12 if not rangeslider else -0.25, x=0),
                      barmode="stack" if kind == "Słupki skumulowane" else "group", bargap=0.1,
                      uirevision="keep")  # keep zoom when toggling options
    fig.update_yaxes(title_text=ylab, gridcolor="rgba(128,128,128,0.15)", zeroline=False, range=yrange)
    fig.update_xaxes(gridcolor="rgba(128,128,128,0.15)")
    last = [k for k in fig.layout if k.startswith("xaxis")][-1] if any(k.startswith("xaxis") for k in fig.layout) else "xaxis"
    fig.layout[last].rangeslider = dict(visible=rangeslider, thickness=0.06)
    if sub_daily:
        fig.layout[last].rangeselector = dict(buttons=[dict(count=1, label="1 d", step="day", stepmode="backward"),
                                                       dict(count=7, label="7 d", step="day", stepmode="backward"),
                                                       dict(count=1, label="1 m", step="month", stepmode="backward"),
                                                       dict(step="all", label="całość")])
    return fig


def yrange_all(d):
    if not shared_y or norm == "pct_total" or kind.endswith("skumulowane") or kind.endswith("skumulowany"):
        return None
    v = pd.concat([d.value, d.raw if show_raw else d.value]).dropna()
    if v.empty:
        return None
    lo, hi = float(v.min()), float(v.max())
    pad = (hi - lo) * 0.05 or 1
    return [min(lo - pad, 0) if lo >= 0 else lo - pad, hi + pad]


def panels():
    """series -> panel label for grid/stack modes."""
    meta = g.groupby("series")[["dataset", "site", "carrier"]].first()
    if split == "series":
        return {s: s for s in meta.index}
    if split == "dataset":
        return meta.dataset.to_dict()
    return (meta.dataset + " · " + meta[split].astype(str)).to_dict()


# ---------- tabs ----------
tabs = st.tabs(["Przebieg czasowy", "Profil dobowy", "Mapa cieplna", "Krzywa uporządkowana", "Statystyki", "Dane", "Log anomalii"])

with tabs[0]:
    st.caption(f"Rozdzielczość: {res_txt} · {C.MEASURES[measure]} · łączenie: {DIMS_PL[by]}")
    seen_flags = set()
    present = [s for s in order if s in set(a.series)]
    yr = yrange_all(a)
    if mode == "one":
        fig = go.Figure()
        for s in present:
            add_series(fig, a[a.series == s], s)
        st.plotly_chart(finish(fig, height), width="stretch", config={"displaylogo": False})
    else:
        pmap = panels()
        groups = {}
        for s in present:
            groups.setdefault(pmap[s], []).append(s)
        if mode == "stack":
            fig = make_subplots(rows=len(groups), cols=1, shared_xaxes=True, vertical_spacing=0.04,
                                subplot_titles=list(groups))
            done = set()
            for i, (p, ss) in enumerate(groups.items(), start=1):
                for s in ss:
                    add_series(fig, a[a.series == s], s, row=i, legend=s not in done)
                    done.add(s)
            fig = finish(fig, max(height, 220 * len(groups)))
            if yr:
                fig.update_yaxes(range=yr)
            st.plotly_chart(fig, width="stretch", config={"displaylogo": False})
        else:
            items = list(groups.items())
            ncols = min(ncols, len(items))
            for r0 in range(0, len(items), ncols):
                cols = st.columns(ncols)
                for col, (p, ss) in zip(cols, items[r0:r0 + ncols]):
                    fig = go.Figure()
                    for s in ss:
                        add_series(fig, a[a.series == s], s)
                    col.plotly_chart(finish(fig, height, title=p, yrange=yr), width="stretch", config={"displaylogo": False})

# native-resolution, sub-daily rows for shape analyses
fine = g[g.dur_h < 24].assign(kw=lambda x: x.kwh / x.dur_h / scale)
punit = "MW" if scale > 1 else "kW"

with tabs[1]:
    if fine.empty:
        st.info("Profil dobowy wymaga danych 15-min lub 1-h.")
    else:
        c1, c2, c3 = st.columns(3)
        psplit = c1.selectbox("Podział", ["none", "daytype", "season", "month", "zone"],
                              format_func={"none": "brak", "daytype": "dzień roboczy / wolny", "season": "pora roku",
                                           "month": "miesiąc", "zone": "strefa B23"}.get)
        pstat = c2.selectbox("Statystyka", ["mean", "median", "max", "min", "p90"],
                             format_func={"mean": "średnia", "median": "mediana", "max": "maksimum", "min": "minimum", "p90": "90. percentyl"}.get)
        pcols = c3.slider("Kolumn", 1, 4, 2, key="pcols")
        lab = {"none": lambda d: pd.Series("wszystkie dni", index=d.index),
               "daytype": lambda d: d.workday.map({True: "robocze", False: "wolne + święta"}),
               "season": lambda d: d.month.map(lambda x: ["zima", "wiosna", "lato", "jesień"][(x % 12) // 3]),
               "month": lambda d: d.month.map(lambda x: f"{x:02d} {MONTHS[x - 1]}"),
               "zone": lambda d: d.zone.map(ZONES)}[psplit]
        fp = fine.assign(part=lab(fine), hb=(fine.hour * 4).round() / 4)
        agg = (lambda x: x.quantile(0.9)) if pstat == "p90" else pstat
        prof = fp.groupby(["part", "series", "hb"]).kw.agg(agg).reset_index()
        ylim = [0, prof.kw.max() * 1.05] if shared_y else None
        parts = sorted(prof.part.unique())
        pcols = min(pcols, len(parts))
        for r0 in range(0, len(parts), pcols):
            cols = st.columns(pcols)
            for col, p in zip(cols, parts[r0:r0 + pcols]):
                fig = go.Figure()
                for s in [s for s in order if s in set(prof.series)]:
                    d = prof[(prof.part == p) & (prof.series == s)]
                    color, dash, vis, op = trace_style(s)
                    fig.add_trace(go.Scatter(x=d.hb, y=d.kw, name=s, mode="lines", visible=vis, opacity=op,
                                             line=dict(color=color, dash=dash, width=2, shape="hv"),
                                             hovertemplate="%{x:.2f} h: %{y:,.1f} " + punit + "<extra>" + s + "</extra>"))
                fig.update_layout(height=max(300, height * 0.8), title=p, margin=dict(l=10, r=10, t=40, b=10),
                                  legend=dict(orientation="h", y=-0.2), hovermode="x unified")
                fig.update_xaxes(title_text="godzina", dtick=2, range=[0, 24])
                fig.update_yaxes(title_text=f"moc [{punit}]", range=ylim, gridcolor="rgba(128,128,128,0.15)")
                col.plotly_chart(fig, width="stretch", config={"displaylogo": False})

with tabs[2]:
    if fine.empty:
        st.info("Mapa cieplna wymaga danych 15-min lub 1-h.")
    else:
        s = st.selectbox("Seria", [x for x in order if x in set(fine.series)], key="hm_series")
        d = fine[fine.series == s]
        hm = d.assign(date=d.ts.dt.date, hb=(d.hour * 4).round() / 4).pivot_table(index="hb", columns="date", values="kw", aggfunc="mean")
        fig = go.Figure(go.Heatmap(z=hm.values, x=hm.columns, y=hm.index, colorscale=[[i / 4, c] for i, c in enumerate(seq)],
                                   colorbar=dict(title=punit), hovertemplate="%{x}<br>%{y:.2f} h<br>%{z:,.1f} " + punit + "<extra></extra>"))
        fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10))
        fig.update_yaxes(title_text="godzina", autorange="reversed", dtick=2)
        st.plotly_chart(fig, width="stretch", config={"displaylogo": False})
        st.caption("Jasne = niska moc, ciemne = wysoka. Pionowe pasy = dni nietypowe (święta, awarie).")

with tabs[3]:
    if fine.empty:
        st.info("Krzywa uporządkowana wymaga danych 15-min lub 1-h.")
    else:
        fig = go.Figure()
        for s in [x for x in order if x in set(fine.series)]:
            v = np.sort(fine[fine.series == s].kw.dropna().to_numpy())[::-1]
            color, dash, vis, op = trace_style(s)
            fig.add_trace(go.Scattergl(x=np.linspace(0, 100, len(v)), y=v, name=s, mode="lines", visible=vis, opacity=op,
                                       line=dict(color=color, dash=dash, width=2),
                                       hovertemplate="%{x:.1f}% czasu ≥ %{y:,.1f} " + punit + "<extra>" + s + "</extra>"))
        fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=1.05))
        fig.update_xaxes(title_text="% czasu (w filtrze)")
        fig.update_yaxes(title_text=f"moc [{punit}]", gridcolor="rgba(128,128,128,0.15)")
        st.plotly_chart(fig, width="stretch", config={"displaylogo": False})

with tabs[4]:
    stt = C.stats(g)
    st.dataframe(stt, width="stretch")
    st.download_button("Pobierz CSV", stt.to_csv().encode("utf-8"), "statystyki.csv", "text/csv")
    st.caption("Liczone na danych natywnych po filtrach. Moc min/maks. z interwałów natywnych (dla danych miesięcznych = średnia miesiąca).")

with tabs[5]:
    wide_t = st.toggle("Tabela szeroka (czas × seria)", value=True)
    tbl = a.pivot_table(index="ts", columns="series", values="value") if wide_t else a
    st.dataframe(tbl, width="stretch", height=500)
    st.download_button("Pobierz CSV (dane z wykresu)", tbl.to_csv().encode("utf-8"), "dane.csv", "text/csv")

with tabs[6]:
    log = C.anomaly_log()
    if log.empty:
        st.info("Brak outputs/tables/anomaly_log.csv – uruchom scripts/01_build_processed.py")
    else:
        c1, c2 = st.columns([1, 2])
        ds = c1.multiselect("Zbiór", sorted(log.dataset.unique()), default=[d for d in sorted(log.dataset.unique()) if d in sel or d.split("_")[0] in sel])
        q = c2.text_input("Szukaj (obiekt, opis, akcja)")
        lg = log[log.dataset.isin(ds)] if ds else log
        if q:
            lg = lg[lg.astype(str).apply(lambda r: r.str.contains(q, case=False)).any(axis=1)]
        st.dataframe(lg, width="stretch", height=500, hide_index=True)
        st.caption(f"{len(lg)} z {len(log)} wpisów. Pełne zasady: docs/methodology.md")
