# Economie

Data-driven economic analyses using public sources (Eurostat, World Bank, ECB, European Commission).

## Structure

| Folder | Description |
|--------|-------------|
| [`romania/`](romania/) | Romanian economy: trajectory, structural challenges, and current state |
| [`greece/`](greece/) | Greek economy: debt crisis, adjustment programmes, and the slow reconstruction |
| [`it-romania/`](it-romania/) | Romanian IT sector deep dive: origins, take-off, hubs, the digital paradox, and outlook |

## Romania

A full analysis of the Romanian economy from 2000 to 2024, covering GDP convergence, public finances, labour market, demographics, inflation, external sector, industry, regional disparities, and social indicators.

- **[Report](romania/report.md)** — narrative analysis
- **[Charts](romania/charts/)** — 40 charts generated from live data
- **[Raw data](romania/raw-data/)** — underlying CSVs from Eurostat and World Bank
- **Scripts** — `01_gdp_overview.py` through `08_social.py`

## Greece

A full analysis of the Greek economy from 2000 to 2025, covering the debt crisis (2010–2018 adjustment programmes), banking near-collapse, internal devaluation, tourism and shipping dominance, regional divergence, and the post-RRF recovery.

- **[Report](greece/report.md)** — narrative analysis
- **[Plan](greece/plan.md)** — research plan
- **[Charts](greece/charts/)** — 49 charts generated from live data
- **[Raw data](greece/raw-data/)** — 50 underlying CSVs from Eurostat, World Bank and ECB SDW
- **Scripts** — `01_gdp_overview.py` through `09_social.py`

## Romanian IT Sector

A focused deep dive into the Romanian IT industry from 1990 to 2025: how it emerged from a post-communist engineering inheritance, how it grew into 5.6% of GDP and €11.5bn in annual services exports, how it reshaped four hub cities (Bucharest, Cluj, Timișoara, Iași), the paradox of being a top IT *producer* but a digital-adoption laggard, and the outlook as cost-arbitrage and demographic tailwinds fade.

- **[Report](it-romania/report.md)** — narrative analysis
- **[Plan](it-romania/plan.md)** — research plan
- **[Charts](it-romania/charts/)** — 42 charts generated from live data
- **[Raw data](it-romania/raw-data/)** — 45 underlying CSVs from Eurostat and EPO
- **Scripts** — `01_origins.py` through `08_outlook.py`

## Running the scripts

A single shared virtual environment lives at the repo root (`.venv/`) and is used by all three projects.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r romania/requirements.txt
# regenerate Romanian charts
cd romania && python 01_gdp_overview.py   # ... through 08_social.py
# regenerate Greek charts
cd ../greece && python 01_gdp_overview.py # ... through 09_social.py
# regenerate Romanian IT-sector charts
cd ../it-romania && python 01_origins.py  # ... through 08_outlook.py
```

Each script fetches fresh data from the upstream APIs, writes a CSV to `raw-data/`, and saves PNG charts to `charts/`.
