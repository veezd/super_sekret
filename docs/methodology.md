# Methodology & assumptions log (→ presentation slide). Append; 1 row per assumption.
| id | assumption | reason/source | impact |
|---|---|---|---|
| A1 | Distribution flat 0.08 PLN/kWh (not B23 zones) | organizers allow | ±0.02–0.03 PLN/kWh |
| A2 | Prices net, VAT ignored | organizers | – |
| A3 | Export surplus priced at PSE RCE, no fees | organizers | export revenue |
| A4 | 1 GJ = 0.2778 MWh | physics | – |
| A5 | Dorm occupancy: Jul–Sep = summer/low, else semester | rough; refine w/ AGH calendar | dorm profile scaling |
| A6 | All series labelled by interval START, tz Europe/Warsaw | convention | alignment |
| A7 | Counter gaps (D17) spread evenly over missing slots | README recommendation | intra-gap shape lost, sum kept |
| A8 | All raw meter timestamps = interval END (first label 00:15 / 01:00) → shifted to START before tz-localize; autumn repeated hour resolved by order | data: every file starts at 00:15, ends 01-01 00:00 | alignment of all series |
| A9 | Hala 2025-07-04 08:15–15:30: both PPE ≈0 incl. const meter → whole-site supply outage, replaced by same-weekday profile (±1, ±2 wk), flag anomaly | non-representative for planning; raw kept in kwh_raw | +0.64 MWh (0.08% of year) |
| A10 | Hala: 13 short (15–45 min) main-feed drops to <10% while const meter alive → real events (switching/tests), kept, flag suspect | const meter proves supply present | none |
| A11 | Basen hourly → 15 min as 4 equal quarters in sites_2025_15min.parquet | no sub-hour data | intra-hour peaks underestimated |
| A12 | Basen 08-04 23:00 = 0 kWh → linear interp; 10-26 02:00 double row halved (CEST+CET) | README + base load never <50 kW | ±0.1 MWh |
| A13 | D17 counter gaps: delta spread evenly (energy kept). 08-01 08:30–10:15 rate ≈20% of normal on both feeds → probable outage, shape inside gap unknown | counter = exact energy | none on energy |
| A14 | D17 first interval 2025-01-01 00:00 (no prior counter reading) = copy of next interval | – | negligible |
| A15 | ds_profile: period 2026-07-04 – 2026-10-02 (not 2025!), labels END; trimmed to common period of 3 meters | data | dorm 15-min shape only for summer/early semester |
| A16 | Monthly dorm data: renovation closures inferred (DS-7 2024-10–2025-11, DS-8 2025-09–12, DS-10 2023-06–2024-09); NaN inside → 0 | el ≪ usual + heat 0/NaN | dorm totals of those years |
| A17 | Monthly el zeros in active buildings (DS-10/11/13 Oct 2025, Alfa) = missing reading → imputed | zero impossible for occupied dorm | ±1% annual |
| A18 | Jan 2025 el < 60% of Feb in 15 DS (systematic, 2023/24 Jan ≥ Feb) → short reading period assumed, imputed (yoy level) | +204 MWh vs raw 2025 | 2025 dorm el total |
| A19 | Monthly imputation: interior → mean(prev,next) × seasonal factor of all other dorms; edges → same month other years × series level | uses common weather/calendar | per-month ±10–20% |
| A20 | Manual monthly corrections (x10 typo, D/N & co/cw swaps, D holds D+N, Alfa bimonthly readings averaged in pairs, heat totals vs co/cw) listed in loaders.MONTHLY_FIXES + outputs/tables/anomaly_log.csv | screening: zeros, ×neighbour, N share, =prev | see log |
| A21 | Heat 'razem' (co+cw together) rows used only where co/cw absent; DS-14 2023 co/cw split implausible → suspect (sum OK) | avoid double count | per-carrier split |
