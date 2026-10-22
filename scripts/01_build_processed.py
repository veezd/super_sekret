"""Raw -> data/processed/*.parquet (clean, canonical) + cross-checks and anomaly log in outputs/tables/.
Usage: python scripts/01_build_processed.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pandas as pd
from htd import loaders as L
from htd.config import PROCESSED, TAB

TAB.mkdir(parents=True, exist_ok=True)
for key, fn in {"hala": L.load_hala, "d17": L.load_d17, "basen": L.load_basen,
                "ds_profile": L.load_ds_profile, "ds_monthly": L.load_ds_monthly}.items():
    try:
        df = fn()
    except FileNotFoundError as e:
        print(f"{key}: missing raw file ({e.filename})")
        continue
    if key == "basen":
        z = L.basen_zone_check(df)
        print(f"basen: B23 zone mismatches raw 'Strefa' vs tariff.b23_zone = {len(z)}")
        z.to_csv(TAB / "check_basen_zones.csv", index=False)
    L.save(df, key)
    print(f"{key}: {len(df)} rows, flags={df.flag.value_counts().to_dict()}")

kw = L.hala_kw_check()
kw.to_csv(TAB / "check_hala_kw_vs_kwh.csv")
print(f"hala_kw check: {len(kw)} intervals |kW file - 4*kWh| > 1 kW")
d = L.d17_kw_check()
d.to_csv(TAB / "check_d17_kw_vs_counter.csv", index=False)
print("d17 kW check (4*dE - logged kW):", d.round(2).to_dict("records"))

# convenience wide tables (kWh per 15 min, site = sum of meters). Basen hourly -> 4 equal quarters (methodology A10)
w = pd.concat([L.wide("hala"), L.wide("d17")], axis=1)
b = L.wide("basen")["basen"] / 4
w["basen"] = b.reindex(w.index, method="ffill")
w.to_parquet(PROCESSED / "sites_2025_15min.parquet")
L.wide("ds_profile").to_parquet(PROCESSED / "ds_profile_15min.parquet")
print("wide:", {c: round(w[c].sum()) for c in w}, "kWh/2025")

log = L.anomaly_log()
log.to_csv(TAB / "anomaly_log.csv", index=False)
print(f"anomaly log: {len(log)} entries -> {TAB / 'anomaly_log.csv'}")
