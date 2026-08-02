from dataclasses import dataclass
from pathlib import Path
import pandas as pd

CORE_COLUMNS = [
    "region","capital","population_2010","population_2021","area_km2","density_2021",
    "growth_2010_2021_percent","latitude","longitude"
]
INDICATOR_COLUMNS = [
    "urban_share_percent","literacy_percent","school_attendance_percent","employed_share_percent",
    "unemployment_rate_percent","improved_water_percent","basic_sanitation_percent",
    "electricity_access_percent","internet_use_percent","avg_household_size","youth_share_percent",
    "female_share_percent","health_insurance_percent","multidimensional_poverty_percent"
]

@dataclass
class RegionalData:
    frame: pd.DataFrame
    source_label: str
    demonstration: bool


def _coerce(frame: pd.DataFrame) -> pd.DataFrame:
    out=frame.copy()
    out.columns=[str(c).strip().lower().replace(" ","_") for c in out.columns]
    missing=[c for c in CORE_COLUMNS if c not in out.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    numeric=[c for c in CORE_COLUMNS+INDICATOR_COLUMNS+["cagr_2010_2021_percent","population_projection_2030"] if c in out.columns and c not in {"region","capital"}]
    for c in numeric: out[c]=pd.to_numeric(out[c],errors="coerce")
    if out[CORE_COLUMNS].isna().any().any():
        raise ValueError("Required fields contain missing or non-numeric values.")
    if out["region"].duplicated().any():
        raise ValueError("Region names must be unique.")
    return out.sort_values("region").reset_index(drop=True)


def load_demo(root: Path) -> RegionalData:
    path=root/"data"/"demo"/"ghana_regional_development_demo.csv"
    return RegionalData(_coerce(pd.read_csv(path)),"Bundled Ghana regional demonstration dataset",True)


def read_uploaded_csv(file) -> RegionalData:
    return RegionalData(_coerce(pd.read_csv(file)),"Uploaded regional dataset",False)
