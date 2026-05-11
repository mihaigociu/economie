# Greek Economy Analysis — Report Plan

## Objective
Produce a data-driven report on Greece's economic trajectory over the past two and a half decades, with a sharp focus on the legacy of the sovereign debt crisis, the post-bailout recovery, and current structural challenges. All analysis grounded in public statistical sources, supplemented by Python-generated charts.

The Greek case is distinctive: a euro-area member since 2001, subject of the largest sovereign rescue programmes in IMF history (2010, 2012, 2015), three lost decades of convergence reversed, and — since 2018 — a contested recovery story. This report aims to separate genuine structural change from cyclical rebound.

---

## Data Sources
| Source | What it covers | Access |
|--------|---------------|--------|
| **Eurostat** | GDP, employment, trade, public finances, regional data | `eurostat` Python package / REST API |
| **World Bank Open Data** | Long-run macro series, governance | `wbgapi` Python package |
| **IMF WEO / IFS / Article IV** | Fiscal series, current account, programme history | CSV / SDMX |
| **ELSTAT** (Hellenic Statistical Authority) | Granular domestic data, regional/sectoral detail | CSV / XLSX download |
| **Bank of Greece (BoG)** | Banking stability, NPL ratios, balance of payments, credit | XLSX / PDF |
| **ECB / SDW** | Euro-area monetary context, ECB holdings of Greek debt | SDMX |
| **OECD** | Productivity, FDI, education, pensions | OECD Stats API |
| **AMECO** (EC) | Cyclically-adjusted balances, output gap, forecasts | XLSX |
| **PDMA** (Public Debt Management Agency) | Debt composition, maturity profile, issuance | PDF reports |

---

## Report Structure

### 1. Introduction & Context
- Why Greece matters: euro-area member, crisis epicentre 2010-2018, geopolitical hinge of SE Europe
- Scope: 2000–present, with emphasis on pre-crisis (2000-2008), crisis & programmes (2009-2018), recovery (2019-present)
- Key data sources and methodology note
- Note on data quality: ELSTAT credibility crisis of 2009-2010 and subsequent reforms

---

### 2. Macroeconomic Overview
**Goal:** establish the boom-bust-recovery arc and Greece's position vs euro-area peers.

#### 2.1 GDP Growth
- Real GDP growth (annual %) vs Euro area, EU27, and southern peers (Portugal, Italy, Spain, Cyprus)
- The pre-crisis boom (2000-2007), the depression (2008-2016, peak-to-trough ~26%), the recovery (2017-present)
- Comparison with US Great Depression and other historical contractions in magnitude and duration

#### 2.2 GDP Structure (by sector)
- Agriculture / Industry / Services share over time
- Deindustrialisation: long-term decline of manufacturing share
- Tourism and shipping weight in GVA — sector concentration risk

#### 2.3 GDP per capita — Convergence Reversal
- Greece vs EU average (PPS): from ~95% (2008) to ~67% (2013) to gradual recovery
- The only EU member to *diverge* materially from EU average over 2000-2024
- Productivity gap vs core euro area

**Scripts:** `01_gdp_overview.py` — pulls Eurostat / World Bank data, plots growth rates, convergence chart, sector composition.

---

### 3. The Debt Crisis & Programme Legacy
**Goal:** anchor the narrative in the defining episode of modern Greek economic history.

#### 3.1 Run-up to the Crisis (2000-2009)
- Pre-euro convergence and ELSTAT data revisions of 2009-2010
- Fiscal slippage hidden by accounting practices
- Current account deficit driven by credit boom and lost competitiveness

#### 3.2 The Three Programmes (2010, 2012, 2015)
- Timeline of the three Memoranda of Understanding (IMF/ECB/EC "Troika")
- PSI 2012: the largest sovereign debt restructuring in history (~€100bn haircut)
- Capital controls (June 2015 – September 2019) — context and effects
- Programme conditionality: fiscal targets, structural reforms, privatisations

#### 3.3 Post-Programme Period (2018–present)
- Enhanced Surveillance framework (2018-2022)
- Return to investment grade: timeline of upgrades (DBRS, S&P, Fitch, Moody's 2023-2024)
- Primary surplus targets and their easing

**Scripts:** discussed in `02_public_finances.py` and a separate narrative chapter; no dedicated script needed — uses series from §4.

---

### 4. Public Finances & Fiscal Health
**Goal:** quantify the fiscal trajectory and assess sustainability of the current consolidation.

#### 4.1 Budget Balance
- General government balance (% GDP) 2000–present
- Primary balance — the headline metric of programme years
- Excessive Deficit Procedure history (Greece was in EDP almost continuously 2004-2017)

#### 4.2 Public Debt
- Gross public debt (% GDP) trajectory: ~100% (2000) → 180%+ (peak) → declining
- Debt composition: official sector loans (EFSF/ESM/IMF/GLF) vs market debt — favourable structure
- Maturity profile, weighted average cost, cash buffer
- Debt sustainability — the gap between headline ratio and effective risk

#### 4.3 Spending & Revenue Structure
- Tax revenue and tax mix (high indirect tax reliance)
- VAT gap and tax compliance — historical weakness, recent gains
- Pension expenditure as % GDP — historically among the highest in EU
- Public wage bill consolidation under the programmes

#### 4.4 Pension System
- Pre-crisis pension generosity and demographic pressures
- 2010-2016 reforms: parametric changes, retirement age increases
- Current sustainability outlook

**Scripts:** `02_public_finances.py`

---

### 5. Banking Sector & Financial Stability
**Goal:** trace the banking crisis and its incomplete resolution — distinctive to Greece's story.

#### 5.1 The NPL Crisis
- Non-performing loan ratio: peak >45% (2016), now in single digits
- Hercules securitisation scheme — state guarantee mechanism for NPL disposal
- Four systemic banks: Alpha, Eurobank, NBG, Piraeus — recapitalisations and ownership changes
- HFSF (Hellenic Financial Stability Fund) stakes and divestment

#### 5.2 Credit and Deposits
- Deposit flight episodes (2010, 2012, 2015) and the capital controls era
- Credit-to-GDP gap and the deleveraging cycle
- Re-emergence of credit growth post-2022

#### 5.3 Capital Markets
- Sovereign bond yields: from default-grade to sub-Italian spreads
- Athens Exchange (ATHEX) trajectory
- Inclusion in major bond indices following investment-grade restoration

**Scripts:** `05_banking.py` (new vs Romania structure — banking is distinctive enough to warrant its own module)

---

### 6. Labor Market & Demographics
**Goal:** assess the human cost of the crisis and the demographic constraint on recovery.

#### 6.1 Employment & Unemployment
- Unemployment rate: pre-crisis ~8% → peak ~28% (2013) → recovery to single digits (~10%)
- Youth unemployment: peak >60%, structural elevation
- Long-term unemployment share
- Employment rate vs EU target

#### 6.2 Wages
- Real wage compression during the programmes (internal devaluation strategy)
- Minimum wage: abolition of automatic indexation, recent restorations
- Real wage recovery gap vs pre-crisis peak

#### 6.3 Brain Drain & Emigration
- Net emigration during the crisis years (estimated 400-500k Greeks left)
- Skill composition of emigrants — disproportionately tertiary-educated
- Return migration trends and policy responses (e.g. tax incentives for repatriates)

#### 6.4 Demographic Outlook
- Population decline: ~11.1m (2010) → ~10.4m (current) and projections
- One of the lowest fertility rates in EU
- Age dependency ratio trajectory — among the most adverse in EU
- Implications for pension system and labour supply

**Scripts:** `03_labor_demographics.py`

---

### 7. Inflation & the Euro Membership
**Goal:** contextualise inflation within the euro-area framework and assess the costs and benefits of euro membership.

#### 7.1 CPI History
- Pre-euro inflation differentials and convergence
- The deflation episode of 2013-2015 (the unique Greek case in the euro area)
- 2021-2023 inflation surge: drivers, comparison to euro-area average
- Wage-price dynamics in the recovery

#### 7.2 The Cost of Euro Membership
- No monetary policy lever during the crisis — internal devaluation as the only adjustment channel
- ECB programmes Greece accessed (SMP, OMT eligibility, PEPP)
- The 2015 ELA episode and the brink of Grexit
- Counterfactual debate: would devaluation have been better?

#### 7.3 Real Effective Exchange Rate
- Competitiveness loss 2000-2009, regaining 2010-2017
- Comparison with peripheral peers

**Scripts:** `04_inflation_monetary.py`

---

### 8. External Sector
**Goal:** assess external rebalancing and remaining vulnerabilities.

#### 8.1 Current Account
- Pre-crisis current account deficit of ~15% GDP — among the largest in EU
- Adjustment to near balance by 2015-2016
- Recent re-widening — tourism boom vs energy import bill

#### 8.2 Trade in Goods & Services
- Persistent goods deficit, surplus on services (tourism + transport)
- Export base narrowness and concentration
- Energy import dependence and the 2022 gas shock

#### 8.3 Foreign Direct Investment
- Historically low FDI inflows relative to peers
- Recent uptick: real estate (Golden Visa), energy, infrastructure
- Privatisation receipts under HRADF

#### 8.4 EU Funds — NSRF and RRF
- Cohesion fund absorption history
- Greece as one of the largest per-capita beneficiaries of the Recovery and Resilience Facility (~€36bn)
- RRF disbursement progress and milestones

**Scripts:** `06_external_sector.py`

---

### 9. Sectoral Deep Dives
**Goal:** understand the engines of the recovery and the structural specialisation.

#### 9.1 Tourism
- Arrivals and receipts trajectory — pre-crisis, crisis-era, post-2022 boom
- Tourism share of GDP and employment — among the highest in OECD
- Spatial concentration and seasonality
- Over-tourism debate (Santorini, Mykonos, Athens short-term rentals)

#### 9.2 Shipping
- Greek-owned merchant fleet: largest in the world by tonnage
- Onshore contribution: shipping cluster in Piraeus/Athens
- Tax regime for shipping (constitutionally protected tonnage tax)
- COSCO and the Piraeus port investment

#### 9.3 Energy
- From lignite dependence to renewables push
- Greece as SE European gas hub: Revithoussa LNG, Alexandroupolis FSRU, IGB pipeline
- Electricity interconnectors (Greece-Bulgaria, planned Greece-Egypt, Greece-Cyprus-Israel)
- Renewables capacity growth and grid constraints

#### 9.4 Manufacturing & Industry
- Long-run decline in industrial share — structural deindustrialisation
- Surviving clusters: refining, food and beverages, building materials, pharma
- Reindustrialisation prospects under RRF

#### 9.5 Real Estate & Construction
- House price collapse 2008-2017 (-40%+) and recovery (2018-present)
- Golden Visa programme and foreign demand
- Affordability concerns in Athens and on islands
- Construction recovery and infrastructure pipeline

**Scripts:** `07_sectors.py`

---

### 10. Regional Disparities
**Goal:** show the Attica-vs-periphery and mainland-vs-islands divides.

- GDP per capita by NUTS2 region vs EU average
- Attica concentration: hosts ~40% of population and produces close to half of GDP
- Island economies: tourism-dependent prosperity vs structural fragility
- Northern Greece (Central Macedonia, Eastern Macedonia & Thrace): industrial legacy and lagging indicators
- Population dynamics by region: depopulation of interior and northern border regions

**Scripts:** `08_regional.py`

---

### 11. Social Indicators
**Goal:** assess whether the macro recovery has translated into welfare gains.

#### 11.1 Poverty & Inequality
- At-risk-of-poverty-or-social-exclusion rate (AROPE) — elevated since the crisis
- Gini coefficient and income share ratios
- Severe material deprivation — sharp rise during the crisis, slow decline
- In-work poverty

#### 11.2 Education
- PISA results — declining trend, below EU average
- Tertiary attainment and field-of-study mix
- Skills mismatch and graduate unemployment paradox
- Public education spending share

#### 11.3 Healthcare
- Health expenditure per capita — cut sharply during the programmes
- Out-of-pocket payment share — among the highest in EU
- Outcomes vs spending: life expectancy, avoidable mortality
- Pandemic-era pressures and current capacity

**Scripts:** `09_social.py`

---

### 12. Structural Problems & Current Challenges
**Goal:** synthesise the systemic issues holding Greece back despite the macro recovery.

1. **Debt overhang** — sustainability dependent on growth, ECB holdings rolloff, and political continuity
2. **Demographic decline** — emigration legacy + ultra-low fertility + aging
3. **Investment gap** — gross fixed capital formation still well below pre-crisis levels
4. **Productivity gap** — TFP growth weak, capital stock erosion during the crisis
5. **Sector concentration** — heavy reliance on tourism, real estate, shipping; thin tradable manufacturing base
6. **Institutional quality** — judicial efficiency, public administration, rule-of-law indicators
7. **Pension and healthcare sustainability** — adverse demographics + recovered spending pressure
8. **Climate exposure** — wildfires, water stress, tourism vulnerability to extreme heat
9. **Geopolitical exposure** — Turkey relations, migration flows, energy transit role

---

### 13. Outlook & Scenarios
- IMF / EC / OECD baseline projections
- Optimistic scenario: sustained RRF implementation, demographic stabilisation via return migration and immigration, FDI in tradables
- Pessimistic scenario: stalled reforms, growth deceleration before debt ratio falls to safe range, external shock
- Policy comparison: what worked for Portugal, Cyprus, Ireland (fellow programme countries)

---

## Deliverables
| File | Description |
|------|-------------|
| `plan.md` | This document |
| `01_gdp_overview.py` | GDP growth, convergence reversal, sector composition charts |
| `02_public_finances.py` | Deficit, debt, debt composition, revenue/spending charts |
| `03_labor_demographics.py` | Employment, wages, emigration, demographics |
| `04_inflation_monetary.py` | CPI, REER, euro-area context |
| `05_banking.py` | NPL ratios, deposits, credit, sovereign yields |
| `06_external_sector.py` | Current account, trade, FDI, EU funds |
| `07_sectors.py` | Tourism, shipping, energy, real estate, industry |
| `08_regional.py` | NUTS2 regional maps and charts |
| `09_social.py` | Poverty, inequality, education, health charts |
| `report.md` | Final narrative report with embedded chart references |

---

## Suggested Python Stack
```
pandas, matplotlib, seaborn   — data manipulation & plotting
eurostat                       — Eurostat API wrapper
wbgapi                         — World Bank data
requests                       — raw API calls (IMF, BoG, ELSTAT)
geopandas + folium             — regional maps
plotly                         — interactive charts (optional)
```

---

## Differences vs the Romania Plan
- Banking sector merits a dedicated module (§5) — the NPL crisis and recapitalisations are central to the Greek story in a way they are not for Romania
- Debt crisis & programme history (§3) is a dedicated narrative chapter — the defining episode of the period
- No "Euro adoption" section — Greece has been in since 2001; instead, §7 examines the *costs* of membership
- Tourism and shipping get expanded treatment in §9 — they are dominant in a way comparable sectors are not in Romania
- "Convergence reversal" framing in §2.3 — Greece is the rare EU member that *lost ground* over the period
- No central-bank policy chapter — monetary policy is ECB; instead BoG appears as a financial stability and statistics source

---

## Sequencing
1. Review & approve this plan
2. Set up Python environment + data fetching scripts (likely shared `requirements.txt` with Romania project)
3. Run each analysis module, review outputs
4. Write narrative sections chapter by chapter
5. Assemble final `report.md`
