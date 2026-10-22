# Data notes (condensed from data_readme_orig.md – read orig only if detail missing)
All times local CET/CEST → DST visible (end Mar, end Oct). Raw, uncleaned. Not all anomalies documented: detect + handle (30% criterion). Duplicate file "Zużycie mediów 2023r.,2024r.,2025r..xlsx" == MS_AGH_...xlsx → ignore it.

## hala – Nowa Hala Sportowa 2025.xls | 15min kWh | 2025
- PPE …615820 main; …615837 small constant ≈0.17 kWh/15min (≈0.7 kW). "Suma zużycia" = both.
- "Profil mocy Hala Sportowa 2025.xls" = SAME as …615820, as kW (=kWh×4). NEVER add to kWh file. Gap 2025-07-04 ~10:00–14:30 (listed in header).

## d17 – Dane D-17 2025.xls | 15min | 2025
- Two feeds ZAS1 + ZAS2; building = sum.
- "Energia Czynna Pobrana" = CUMULATIVE meter state → diff = consumption. Gap → diff covers whole gap → spread over missing slots (clean.counter_to_consumption).
- "Moc Czynna Uśred." kW = check (diff×4 ≈ kW). Gap lists in header, differ for E vs P.
- LV sub-meters (RG_D17_nn) inside AGH network, not DSO billing meters.
- Shape: ZAS2 flat ~85–90 kW 24/7; ZAS1 ~22–30 kW night, 70–90 kW workdays.

## basen – Basen 2025.csv | 1h kWh | 2025 | PPE …049120 (DSO read)
- cp1250, sep ';', decimal ','. Timestamp = END of hour (01:00 = 00–01). Range 2025-01-01 01:00 … 2026-01-01 00:00.
- "Strefa" = B23 zone: am peak workdays 7–13; pm peak workdays 16–21 (Oct–Mar) / 19–22 (Apr–Sep); rest = off incl. weekends/holidays.
- DST: 2025-03-30 03:00 missing (correct). 2025-10-26 03:00 = 247.8 @ completeness 200% → 2 h in 1 row, split.
- Anomaly: 2025-08-05 00:00 = 0. Easter 19–21.04 drop = REAL.
- Night base load ~70–100 kW (filtration, water heating).

## ds_profile – Profil poboru - AGH MS.xlsx | 15min kW | 2026-07-04 … 2026-10-02
- Sheets: "AGH - DS18", "AGH _ Akropol 50088752", "AGH Akropol 50088740". Akropol = sum of 2 meters.
- Delivered .xlsx has real datetimes (openpyxl); labels = interval END (first 00:15) – verified. Akropol 50088752 has empty tail after 10-02 16:15. No DST change inside period.
- Summer = low occupancy → shape ≠ academic year; calibrate with monthly data (summer vs winter ratio).
- Power resolution 2.4 kW (meter constant) → steps are quantization.
- Also reactive power cols (inductive, capacitive).

## ds_monthly – MS_AGH_energia_ele_i_cieplna_2023-2025.xlsx | monthly | 2023–2025
- Sheets el (kWh) + heat (GJ) per year. Dorms DS-1…DS-19 + Alfa.
- El: 2 rows per DS: D (day) / N (night) meter zones. Alfa split bl.1–bl.5.
- Heat: per DS c.o. (space heating), c.w. (DHW), sometimes CT (tech heat for AHU heaters).
- Summary col order c.o./c.w. differs 2023 vs 2024/2025!

## d17_heat – Dane D17 ciepło.xlsx | monthly 2024 | GJ, MW, PLN
- NOT in delivered package (2026-10-21) – loader stub.

## Glossary
c.o. space heating · c.w./c.w.u. DHW · CT AHU heat · D/N day/night zone · PPE DSO metering point · nn LV · 1 GJ = 0.2778 MWh
Note: orig README has no section 7 (numbering gap) – maybe something omitted; ask organizers if relevant.

## Findings from cleaning (2026-10-21, full list: outputs/tables/anomaly_log.csv)
- ALL 15min/1h files label interval END. Autumn DST: hala/d17 repeat 02:15–03:00 labels in order; basen packs 2 h in one row.
- hala: kW file = 4×kWh(…615820) exactly (13 slots differ >1 kW; 07-15 12:45 kW=−9.3 glitch). Outage 07-04 08:15–15:30 (both PPE 0, logger gaps). 13 short midday main-feed dips (~monthly) with const meter alive → real.
- d17: 7 stray rows with :01/:59 s timestamps (kW only). Counter never decreases. kW col vs 4·ΔE: corr 0.96 (ZAS1) / 0.99 (ZAS2). 08-01 08:30–10:15 probable outage.
- basen: B23 'Strefa' == tariff.b23_zone for all 8760 h (tariff module validated).
- ds_monthly el: x10 typo DS-9 N 11/2024; DS-1 D/N swap 12/2023; N too low DS-2 01/2023, DS-3 10/2025; DS-13 01/2024 D=D+N; Jan 2025 short for 15 DS; Oct 2025 zeros DS-10/11/13; DS-14…19 Jan 2024 == Feb 2024 (copy); Alfa only total 2024–25, bimonthly-like readings, Nov–Dec 2025 missing.
- ds_monthly heat: text cells = meter replacements (DS-5 07/2024, DS-8 01/2024, DS-14 01/2024 'Stan po'); DS-5 cw 03+05/2024 = merged/state; DS-11 CT 265 GJ ×2 01–02/2024; DS-16 co/cw swap 12/2024; DS-14 2023 co/cw implausible; DS-3, DS-16 (I–III 2023), DS-7 (2023–24) only co+cw totals.
- Closures (renovation): DS-7 10/2024–11/2025, DS-8 from 09/2025, DS-10 06/2023–09/2024.
