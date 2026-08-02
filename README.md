# Ghana Regional Development & Census Explorer

A portfolio-grade public-data application for examining population change, regional inequality, education, employment, housing, essential services and multidimensional development across Ghana's 16 administrative regions.

## Why this project exists

The project connects mathematical data science with Ghanaian public-sector context. It is designed around the 2021 Population and Housing Census dissemination structure and demonstrates how regional indicators can be transformed into transparent analytical products without presenting a composite index as unquestionable truth.

## Features

- 2010–2021 population comparison and 2030 trend-based projection
- Regional centroid atlas and indicator rankings
- Region profiles with radar comparison and downloadable HTML briefs
- Transparent weighted development index
- Monte Carlo weight-sensitivity analysis
- PCA and K-means regional profiling
- Gini and Theil inequality diagnostics
- CSV/JSON/HTML exports
- Upload pathway for official StatsBank extracts
- Tests, Docker and Streamlit Cloud configuration

## Data boundary

The bundled project runs immediately. Regional population totals reproduce the Ghana 2010/2021 census baseline. The education, employment, service-access, digital, health and poverty indicators are **calibrated demonstration values** and must not be cited as official regional statistics. Replace them with validated Ghana Statistical Service exports for policy or research use.

## Run

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Test

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Deploy

Push the repository to GitHub and deploy `app.py` on Streamlit Community Cloud, or build the included Dockerfile.

## Project structure

- `app.py` — interactive application
- `src/` — data validation, index, clustering and reporting logic
- `data/demo/` — bundled 16-region dataset
- `data/schemas/` — upload contract
- `docs/` — methodology, provenance and integration guidance
- `integration/` — portfolio entry and cover assets
- `tests/` — automated validation
