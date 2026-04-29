# Economie

Data-driven economic analyses using public sources (Eurostat, World Bank).

## Structure

| Folder | Description |
|--------|-------------|
| [`romania/`](romania/) | Romanian economy: trajectory, structural challenges, and current state |

## Romania

A full analysis of the Romanian economy from 2000 to 2024, covering GDP convergence, public finances, labour market, demographics, inflation, external sector, industry, regional disparities, and social indicators.

- **[Report](romania/report.md)** — narrative analysis
- **[Charts](romania/charts/)** — 38 charts generated from live data
- **[Raw data](romania/raw-data/)** — underlying CSVs from Eurostat and World Bank
- **Scripts** — `01_gdp_overview.py` through `08_social.py`

### Running the scripts

```bash
cd romania
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python 01_gdp_overview.py
# ... repeat for 02 through 08
```
