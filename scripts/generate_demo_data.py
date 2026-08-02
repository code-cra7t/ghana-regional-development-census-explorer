from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/"data"/"demo"/"ghana_regional_development_demo.csv"
df=pd.read_csv(path)
assert len(df)==16
assert int(df.population_2021.sum())==30_832_019
print(f"Validated {path}: {len(df)} regions, population {int(df.population_2021.sum()):,}")
