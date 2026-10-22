# CLAUDE.md — Hack the Dorm (MS AGH energy hackathon)
Reply to user in Polish. Code/comments/docs EN (fewer tokens). Chart labels + presentation PL.

## Goal
Raise energy self-sufficiency of AGH student campus (MS AGH) + optimize electricity & heat mgmt. Score: data use 30% (incl. anomaly handling) · feasibility tech+legal 20% · efficiency+economics 20% · presentation 20% · innovation 10%. Detail: docs/task.md

## Layout
```
data/raw/        original files, READ-ONLY, never modify
data/interim/    scratch
data/processed/  clean parquet, canonical schema (src/htd/schema.py)
data/external/   RDN/RCE prices, PVGIS, weather
src/htd/         config.py (paths, prices, file names) · loaders.py · clean.py · tariff.py (holidays, B23, costs) · pv.py · viz.py · schema.py
scripts/         runnable pipeline steps (NN_name.py) + inspect_raw.py
app/             dashboard.py – Streamlit browser for data/processed (UI only; logic in src/htd/catalog.py)
notebooks/       exploration only; reusable logic → src/htd
outputs/figures|tables   deliverables (png 150dpi, csv)
presentation/    final deck material
docs/            task, pricing, data_notes, methodology (assumption log), sources, data_inventory (auto)
```

## Agent rules (token economy)
- Don't open raw binaries. Read docs/data_inventory.md (regen: `python scripts/inspect_raw.py`).
- Read docs/* only when task needs it; data_readme_orig.md only if data_notes.md lacks detail.
- Never print whole DataFrames: use .shape/.head()/.describe()/aggregates. Summarize results in ≤10 lines.
- Write results to files (outputs/, data/processed/); report paths + key numbers, not dumps.
- Reuse src/htd; don't duplicate logic in scripts/notebooks. Python = `.venv/bin/python` (system python has no pandas). Run with `PYTHONPATH=src` (scripts also self-insert src).
- Every assumption/simplification → 1 row in docs/methodology.md. Every external dataset → docs/sources.md.
- On task finish: update "Status" below (1 line). Run `python -m pytest -q tests` after touching src/.

## Canonical schema (processed, long) – src/htd/schema.py
`ts` tz Europe/Warsaw, interval START · `site` hala|d17|basen|ds18|akropol · `meter` (site = sum of meters, no total rows) · `kwh` clean · `kw` · `flag` ok|interp|gapfill|split|anomaly(replaced)|suspect(kept)|missing · `kwh_raw` as delivered.
Files data/processed/: hala, d17, basen (1h, +zone_raw), ds_profile (2026-07-04…10-02!), ds_monthly (`month site carrier[el|heat] meter[D|N|total|co|cw|ct] value unit flag value_raw note`), wide: sites_2025_15min (hala,d17,basen kWh/15min), ds_profile_15min.
Load: `from htd.loaders import load, wide, ds_monthly_wide`. Rebuild: `python scripts/01_build_processed.py`. Anomalies: outputs/tables/anomaly_log.csv.

## Raw data cheat sheet (full: docs/data_notes.md)
| key | file | res | period | gotchas |
|---|---|---|---|---|
| hala_kwh | Nowa Hala Sportowa 2025.xls | 15m kWh | 2025 | PPE …615820 main + …615837 const ≈0.7kW |
| hala_kw | Profil mocy Hala Sportowa 2025.xls | 15m kW | 2025 | = …615820 ×4 → check only, NEVER sum with hala_kwh; gap 07-04 10:00–14:30 |
| d17_el | Dane D-17 2025.xls | 15m | 2025 | ZAS1+ZAS2; energy = CUMULATIVE → diff; gaps in header; kW col = check; LV submeters |
| basen | Basen 2025.csv | 1h kWh | 2025 | cp1250 ; , · ts = hour END · 10-26 03:00 double row (247.8, 200%) split · 08-05 00:00 =0 anomaly · Easter dip real |
| ds_profile | Profil poboru - AGH MS.xlsx | 15m kW | 2026-07-04…10-02 | sheets DS18, Akropol×2 (sum) · ts = END · 2.4kW quantization · SUMMER = low occupancy |
| ds_monthly | MS_AGH_energia_ele_i_cieplna_2023-2025.xlsx | month | 2023–25 | DS-1…19 + Alfa(bl.1–5) · el D/N rows · heat c.o./c.w./CT GJ · 2023 col order differs |
| d17_heat | Dane D17 ciepło.xlsx | month | 2024 | GJ, MW, PLN · NOT DELIVERED yet |
Ignore duplicate "Zużycie mediów 2023r.,2024r.,2025r..xlsx". Times local → DST in data. Undocumented anomalies exist: detect (clean.flag_outliers, clean.gaps).

## Economics (PLN/kWh net, docs/pricing.md)
unit = RDN + 0.05 margin + 0.08 distr(flat) + 0.0332 quality + 0.015 OZE/kog/excise + 0.2194 capacity (workdays 07–21:59 only) → `tariff.unit_cost`.
- Capacity fee = biggest adder → shifting load out of workday 7–22 / covering it with PV+storage is high value.
- Export surplus → PSE RCE price, no fees. Behind-the-meter flows inside AGH network allowed w/o coop → self-consumption avoids full unit price.
- Coop: exempts OZE+capacity+kog (excise only if ≤1MW); BUT AGH = 1 member (needs several), ≥70% self-gen rule from 2026, surplus 1:0.6, distr partly exempt → feasibility risk.
- B23 zones (tariff.b23_zone): am 7–13 workdays; pm 16–21 Oct–Mar / 19–22 Apr–Sep; else off. PL holidays incl. 24.12 from 2025.

## PV givens
Zaścianek 40.6 kWp. Straszny Dwór 121 modules, >200 m² → kWp estimate needed (pv.kwp_from_area/modules; ~20% eff ≈ 40 kWp) + method in methodology.md. Yield profile: PVGIS Kraków (todo).

## Status
- [x] skeleton, docs, tariff/clean helpers + tests
- [x] raw files → data/raw (read-only), inspect_raw.py run
- [x] loaders + cleaning → data/processed/*.parquet, anomaly_log.csv, cross-checks (d17_heat file missing)
- [x] dashboard: `.venv/bin/streamlit run app/dashboard.py` (any new parquet in data/processed appears automatically)
- [ ] fetch external: RDN, RCE, PVGIS
- [ ] EDA: campus peak coincidence, base loads, seasonal dorm scaling
- [ ] pick solution concept(s) + ROI

## Open questions
- Solution concept not chosen yet.
- d17_heat file ("Dane D17 ciepło.xlsx") missing from delivered package – ask organizers.
- Jan 2025 dorm el ≈45% of Feb in 15 DS → imputed (A18); confirm with organizers if possible.
- Orig README skips section 7 – missing info?
