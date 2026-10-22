"""PV estimation. Sources/assumptions must go to docs/methodology.md + docs/sources.md."""
import pandas as pd


def kwp_from_area(area_m2: float, module_eff: float = 0.20) -> float:
    """STC: 1000 W/m2 * area * efficiency. 200 m2 @ 20% ≈ 40 kWp."""
    return area_m2 * module_eff


def kwp_from_modules(n: int, wp_per_module: float) -> float:
    return n * wp_per_module / 1000


def scale_profile(kwp: float, profile_kw_per_kwp: pd.Series) -> pd.Series:
    """profile_kw_per_kwp: e.g. PVGIS hourly output for 1 kWp Kraków (data/external/). Returns kW."""
    return profile_kw_per_kwp * kwp
