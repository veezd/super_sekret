"""Single source of truth: paths, constants, prices, raw file names."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW, INTERIM, PROCESSED, EXTERNAL = (DATA / d for d in ("raw", "interim", "processed", "external"))
OUT = ROOT / "outputs"
FIG, TAB = OUT / "figures", OUT / "tables"

TZ = "Europe/Warsaw"
GJ_TO_MWH = 1 / 3.6  # 0.2778

# Raw files (names exactly as delivered). key -> filename
RAW_FILES = {
    "hala_kwh": "Nowa Hala Sportowa 2025.xls",           # kWh/15min, 2 PPE + suma
    "hala_kw": "Profil mocy Hala Sportowa 2025.xls",     # kW = PPE ...615820 x4. DO NOT ADD to hala_kwh
    "d17_el": "Dane D-17 2025.xls",                      # cumulative kWh + kW, ZAS1+ZAS2
    "basen": "Basen 2025.csv",                           # kWh/h, cp1250, ';', ',' ; ts = END of hour
    "ds_profile": "Profil poboru - AGH MS.xlsx",          # kW/15min from 2026-07-04, sheets DS18, Akropol x2
    "ds_monthly": "MS_AGH_energia_ele_i_cieplna_2023-2025.xlsx",  # kWh D/N, GJ
    "d17_heat": "Dane D17 ciepło.xlsx",                  # monthly 2024 GJ, MW, zł
}

# Prices, PLN/kWh net (docs/pricing.md)
PRICE = {
    "margin": 0.05,          # added to RDN spot
    "capacity": 0.2194,      # workdays 07:00-21:59 only
    "distribution": 0.08,    # simplified flat B23 (real 0.05-0.10 by zone)
    "quality": 0.0332,       # always
    "oze_cog_excise": 0.015, # always
}
CAPACITY_HOURS = range(7, 22)  # hours 7..21 inclusive

# PV on dorm roofs
PV = {
    "zascianek_kwp": 40.6,
    "straszny_dwor_modules": 121,     # >200 m2 total, kWp to estimate (docs/methodology.md)
    "straszny_dwor_area_m2": 200,
}
