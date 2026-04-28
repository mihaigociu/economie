# Romanian Economy Analysis — Report Plan

## Objective
Produce a data-driven report on Romania's economic trajectory over the past two decades, with a sharp focus on current structural challenges. All analysis will be grounded in public statistical sources, supplemented by Python-generated charts.

---

## Data Sources
| Source | What it covers | Access |
|--------|---------------|--------|
| **Eurostat** | GDP, employment, trade, public finances, regional data | `eurostat` Python package / REST API |
| **World Bank Open Data** | Long-run macro series, poverty, governance | `wbgapi` Python package |
| **IMF WEO / IFS** | Fiscal forecasts, current account, external debt | CSV / SDMX |
| **Romanian INS** (institutul national de statistica) | Granular domestic data, regional breakdown | manual CSV download |
| **National Bank of Romania (BNR)** | Monetary aggregates, exchange rate, credit | CSV / Excel |
| **OECD** | Productivity, FDI, education | OECD Stats API |

---

## Report Structure

### 1. Introduction & Context
- Why Romania matters: EU member since 2007, largest non-euro-zone eastern economy
- Scope: 2000–present, with forecasts where available
- Key data sources and methodology note

---

### 2. Macroeconomic Overview
**Goal:** establish the long-run growth story and where Romania stands vs peers.

#### 2.1 GDP Growth
- Real GDP growth rate (annual %) vs EU27 average and regional peers (Poland, Czech Republic, Hungary, Bulgaria)
- GDP at PPP per capita — convergence path toward EU average
- Pre-crisis (pre-2008), post-crisis, post-pandemic trajectory

#### 2.2 GDP Structure (by sector)
- Agriculture / Industry / Services share over time
- Shift in economic composition — deindustrialisation or reindustrialisation?

#### 2.3 GDP per capita — Convergence Analysis
- Romania vs EU average (PPS)
- "Convergence trap" risk — has growth been translating into catching-up?

**Scripts:** `01_gdp_overview.py` — pulls Eurostat / World Bank data, plots growth rates, convergence chart, sector composition.

---

### 3. Public Finances & Fiscal Health
**Goal:** quantify the fiscal deterioration that is Romania's most acute current crisis.

#### 3.1 Budget Deficit
- General government balance (% GDP) 2000–present
- Romania vs Maastricht 3% ceiling; breach history
- 2024–2025 situation: deficit in the 7–8% GDP range, EDP (Excessive Deficit Procedure) status

#### 3.2 Public Debt
- Gross public debt (% GDP) trajectory
- Debt composition: currency, maturity, domestic vs foreign holders
- Debt sustainability outlook (IMF/EC projections)

#### 3.3 Spending & Revenue Structure
- Tax revenue as % GDP — one of the lowest in EU
- VAT gap — large informal economy effect
- Public spending efficiency — health, education, infrastructure

#### 3.4 Pension System Pressure
- Aging demographics + generous pension reform (2019 law)
- Pension expenditure as % GDP vs EU

**Scripts:** `02_public_finances.py`

---

### 4. Labor Market & Demographics
**Goal:** understand the demographic time bomb and its economic consequences.

#### 4.1 Employment & Unemployment
- Employment rate, unemployment rate (ILO) over time
- Youth unemployment — persistent problem
- NEET rate (Not in Employment, Education or Training)

#### 4.2 Wages
- Average gross/net wages in EUR — trajectory
- Minimum wage evolution and policy
- Wage competitiveness vs regional peers

#### 4.3 Brain Drain & Emigration
- Romania's population decline: ~19M → ~16–17M
- Emigration patterns post-EU accession (2007 spike)
- Skilled labour shortage — sectors affected
- Remittances as share of GDP

#### 4.4 Demographic Outlook
- Age dependency ratio trajectory
- Population projections to 2050

**Scripts:** `03_labor_demographics.py`

---

### 5. Inflation & Monetary Policy
**Goal:** contextualise the recent high-inflation episode and BNR's response.

#### 5.1 CPI History
- Hyperinflation of the 1990s → disinflation → EU-era moderate inflation → 2021-2023 surge
- Romania vs Euro area inflation

#### 5.2 BNR Policy Rate
- Policy rate cycle vs inflation
- Exchange rate (RON/EUR) — managed float dynamics

#### 5.3 Euro Adoption — The Perpetually Deferred Goal
- Convergence criteria status
- Political economy of euro reluctance

**Scripts:** `04_inflation_monetary.py`

---

### 6. External Sector
**Goal:** assess Romania's external vulnerabilities.

#### 6.1 Trade Balance & Current Account
- Trade in goods deficit — import dependency
- Current account deficit as % GDP (structural or cyclical?)
- Main trading partners and export composition

#### 6.2 Foreign Direct Investment
- FDI inflows over time
- Sectoral breakdown of FDI
- Romania vs regional peers in attracting investment

#### 6.3 EU Funds Absorption
- Cohesion & structural funds allocation vs absorption rate
- Why Romania historically underperforms on EU fund absorption
- 2021-2027 NRRP (National Recovery and Resilience Plan) progress

**Scripts:** `05_external_sector.py`

---

### 7. Sectoral Deep Dives
**Goal:** understand which sectors drive growth and which are lagging.

#### 7.1 Industry & Manufacturing
- Automotive sector (Dacia/Renault — flagship)
- IT & software — Romania as a regional tech hub
- Energy sector: oil, gas, renewables, energy transition

#### 7.2 Agriculture
- Arable land potential vs productivity gap
- Subsistence vs commercial farming
- Food trade balance

#### 7.3 Real Estate & Construction
- Housing price growth — affordability concerns
- Infrastructure deficit (highways, rail)

**Scripts:** `06_sectors.py`

---

### 8. Regional Disparities
**Goal:** show the stark urban-rural and Bucharest-rest-of-country divide.

- GDP per capita by NUTS2 region vs EU average
- Bucharest at ~170% EU average; Nord-Est at ~35%
- Divergence or convergence within Romania?
- Population movement and regional depopulation

**Scripts:** `07_regional.py`

---

### 9. Social Indicators
**Goal:** assess whether economic growth translated into social progress.

#### 9.1 Poverty & Inequality
- At-risk-of-poverty rate (AROPE) — Romania consistently highest/near-highest in EU
- Gini coefficient trend
- Material deprivation

#### 9.2 Education
- PISA results, early school leaving rate
- Tertiary education participation
- Skills mismatch

#### 9.3 Healthcare
- Health expenditure per capita
- Infant mortality, life expectancy vs EU
- Healthcare system capacity and emigration of medical staff

**Scripts:** `08_social.py`

---

### 10. Structural Problems & Current Crisis
**Goal:** synthesise the systemic issues holding Romania back.

1. **Fiscal imbalance** — chronic deficit driven by rigid spending and weak revenue collection
2. **Demographic decline** — emigration + low birth rate + aging
3. **Infrastructure gap** — lowest highway density in EU, unreliable rail
4. **Institutional weaknesses** — rule of law, corruption, state capacity
5. **Convergence trap** — growth without catch-up in quality of life
6. **Euro adoption limbo** — monetary sovereignty costs vs benefits
7. **Energy transition** — coal dependency vs renewable potential
8. **2024-2025 political uncertainty** — fiscal consolidation political resistance

---

### 11. Outlook & Scenarios
- IMF / EC baseline projections
- Optimistic scenario: fiscal consolidation, EU fund absorption, demographic stabilisation
- Pessimistic scenario: continued deficit, emigration acceleration, credit downgrade risk
- Policy recommendations (comparative — what worked for peers)

---

## Deliverables
| File | Description |
|------|-------------|
| `plan.md` | This document |
| `01_gdp_overview.py` | GDP growth, convergence, sector composition charts |
| `02_public_finances.py` | Deficit, debt, revenue/spending charts |
| `03_labor_demographics.py` | Employment, wages, emigration, demographics |
| `04_inflation_monetary.py` | CPI, policy rate, exchange rate charts |
| `05_external_sector.py` | Trade, CA, FDI, EU funds charts |
| `06_sectors.py` | Sectoral analysis charts |
| `07_regional.py` | NUTS2 regional maps and charts |
| `08_social.py` | Poverty, inequality, education, health charts |
| `report.md` | Final narrative report with embedded chart references |

---

## Suggested Python Stack
```
pandas, matplotlib, seaborn   — data manipulation & plotting
eurostat                       — Eurostat API wrapper
wbgapi                         — World Bank data
requests                       — raw API calls (IMF, BNR)
geopandas + folium             — regional maps
plotly                         — interactive charts (optional)
```

---

## Sequencing
1. Review & approve this plan
2. Set up Python environment + data fetching scripts
3. Run each analysis module, review outputs
4. Write narrative sections chapter by chapter
5. Assemble final `report.md`
