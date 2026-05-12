# Romanian IT Sector — Research Plan

## Objective
Tell the story of Romania's IT industry: how it emerged from a niche post-communist offshoot into one of the largest contributors to the country's economy, the career it opened to a generation of young Romanians, the cities it reshaped, and where it sits today as automation, AI, and the end of long-standing tax incentives change the playing field.

The analysis is narrative-first but evidence-led: every claim is anchored to a public dataset or a publicly-available report, with Python-generated charts produced from raw CSVs committed to `raw-data/`.

Scope: roughly **1990–present**, with the bulk of the data covering 2000 onwards (when comparable Eurostat/INS series become reliable). Where official series are missing for the 1990s, we rely on cited public reports rather than guessed numbers.

---

## Sources — all public

| Source | What it covers | Access |
|--------|---------------|--------|
| **Eurostat** | ICT sector value added, ICT employment (NACE J62/J63), ICT specialists share, services exports, regional employment by NUTS2/3, DESI indicators | `eurostat` Python package / REST API |
| **INS — Tempo Online** (Institutul Național de Statistică) | Domestic detail: enterprises, employment, turnover by CAEN J62/J63; average gross/net wage by activity; regional (județ) breakdown | CSV/XLSX download from `tempo.insse.ro` |
| **BNR** (Banca Națională a României) | Balance of payments — services exports breakdown showing telecom/computer/information services (BPM6) | XLSX from `bnr.ro` interactive database |
| **World Bank Open Data** | ICT service exports (% of services exports, BoP), internet users, fixed broadband | `wbgapi` Python package |
| **OECD** | Digital Economy Outlook, ICT employment shares, R&D intensity | OECD Stats API |
| **European Commission — DESI** (Digital Economy and Society Index) | Human capital, connectivity, digital integration, digital public services | XLSX from `digital-strategy.ec.europa.eu` |
| **Romanian Ministry of Finance** | Public fiscal cost of the IT income-tax exemption (where reported); legislative history (OUG/Legea) | PDF reports, Monitorul Oficial |
| **ANIS** — Romanian Software & Services Association | Annual "Romanian Software & IT Services Industry Study" — published, freely downloadable | PDF |
| **Cluj IT Cluster, ARIES** | Public sectoral reports for regional hubs | PDF |
| **Ministry of Education (Ministerul Educației)** | Enrolment and graduates in IT-related higher-education programmes (informatică, calculatoare, automatică) | Public statistics yearbooks |
| **ANCOM** | Telecom market data, broadband adoption | Public market reports |
| **Stack Overflow Developer Survey, GitHub Octoverse** | Cross-country developer demographics and tooling (public datasets, used sparingly and only where methodology is transparent) | Public CSV/JSON |
| **Press / IPO filings** | UiPath S-1 and 10-K filings (SEC EDGAR) for the marquee case study; only filings, not media commentary | SEC EDGAR |

**Hard rule:** no paid research, no scraped LinkedIn data, no private salary surveys. Where a source is a third-party report (PwC, Deloitte, KPMG, ANIS), we use it only when the PDF is freely published, and we cite the exact document.

---

## Report Structure

### 1. Introduction & Framing
- Why a sector-specific deep dive: IT is one of the few Romanian sectors that **converged with — and in places overtook — Western European norms** on productivity and wages
- Scope, time horizon, methodology note
- Quick orientation: how big is the sector today (GDP share, employment, exports) — the rest of the report unpacks how it got there

---

### 2. Origins (1990–2000)
**Goal:** explain why Romania, of all post-communist economies, ended up with a software industry — not by accident.

#### 2.1 The Engineering Inheritance
- Communist-era investment in technical education: Politehnica București, UTCN Cluj-Napoca, "Gheorghe Asachi" Iași, Politehnica Timișoara — high-volume engineering output predating 1989
- Domestic computer manufacturing of the 1970s–80s (ITC, FEPER, "Felix" mainframes) — created a base of hardware-literate engineers
- Mathematical olympiad tradition and its role in seeding early talent

#### 2.2 The 1990s — First Outsourcing Contracts
- Early companies (Softwin, Siveco, TotalSoft) — domestic origins
- First foreign clients: low wage arbitrage + English/French/German language skills
- Internet arrival and the role of RNC / academic networks

#### 2.3 The First Decisive Policy Choice — IT Income-Tax Exemption (2001)
- Ordinance 94/2004 / earlier Order 1083/2003 lineage (legislative trail)
- What it did: 0% income tax for qualifying IT employees
- Stated rationale at the time and why it was politically durable for 20+ years

**Scripts:** `01_origins.py` — limited quantitative content; mostly produces a single timeline chart (key events 1989–2001) and a chart of engineering-graduate output from public Ministry of Education data where available.

---

### 3. The Outsourcing Boom (2000–2010)
**Goal:** quantify the take-off and show what drove it.

#### 3.1 Sector Size: Value Added & Employment
- ICT sector gross value added (Eurostat `nama_10_a64`, NACE J)
- Employment in J62 (computer programming, consultancy) and J63 (information services), 2000–2010
- Share of total economy employment vs EU average

#### 3.2 The Big-Name Arrivals
- Multinational R&D centres established 2000–2010: Microsoft, Oracle, IBM, HP, Intel, Siemens, Continental, Ericsson — using public press releases / company filings only
- Map: where they landed (Bucharest first, then Cluj, Timișoara, Iași)

#### 3.3 EU Accession Effect (2007)
- Discontinuity in services exports post-accession
- Visa-free movement and the start of "boomerang" return migration in tech roles

**Scripts:** `02_boom.py` — pulls Eurostat ICT GVA, NACE J62/J63 employment; INS Tempo for enterprise counts; plots growth 2000–2010 vs EU27.

---

### 4. Sector Today — Size and Shape
**Goal:** establish current scale in clear, comparable numbers.

#### 4.1 Contribution to GDP
- ICT sector GVA as % GDP (Eurostat)
- Romania vs EU27 vs CEE peers (Poland, Czech, Hungary, Bulgaria)
- Trajectory 2010 → latest

#### 4.2 Employment
- Number of ICT specialists (Eurostat `isoc_sks_itspt`)
- Share of total employment
- Growth rate vs total non-agricultural employment

#### 4.3 Services Exports
- BNR balance-of-payments: computer/telecom/information services exports (EUR bn)
- IT services exports as % of total services exports
- Trade balance in IT services (Romania is a structural net exporter)

#### 4.4 Firm Demography
- INS Tempo: number of active enterprises in J62/J63
- Distribution by size (micro / SME / large)
- Foreign-controlled vs domestic firms (where data permits)

**Scripts:** `03_sector_today.py` — Eurostat + BNR + INS; ~6 charts.

---

### 5. Wages, Careers, and the Generation IT Built
**Goal:** the human story — what the sector actually delivered to people working in it.

#### 5.1 Wage Premium
- Average gross wage in J62/J63 vs national average (INS Tempo, monthly series)
- Multiple of average wage over time — when did it open up, has it narrowed
- Comparison with manufacturing, banking, public sector

#### 5.2 Purchasing Power & Convergence with Western Europe
- IT wages in Romania (PPS, gross) vs Germany, France, UK for comparable roles where Eurostat permits
- The "you can live in Cluj on a Munich-adjacent salary" effect

#### 5.3 Career Pipeline
- Graduates of CS / automation / electronics from Romanian universities (Ministry of Education public data)
- Time-to-first-job, return migration of Romanian engineers (using INS migration data + Eurostat)
- Women in tech share (Eurostat `isoc_sks_itsps`)

#### 5.4 The IT Tax Exemption: Quantifying the Effect
- Estimated number of beneficiaries over time (Ministry of Finance public reports)
- Estimated foregone revenue
- Phase-out timeline (2023 cap, subsequent adjustments) and labour-market response

**Scripts:** `04_wages_careers.py` — INS wage series, Eurostat ICT specialists, Ministry of Education graduates.

---

### 6. The Hubs — How IT Reshaped Cities
**Goal:** show the spillover effects on regional economies. This is the part of the story that does not appear in national aggregates. Equal-weight treatment of the four primary hubs — no single city carries the chapter.

#### 6.1 Geographic Concentration — National Picture
- ICT employment by NUTS2 region (Eurostat `lfst_r_lfe2en2`)
- Bucharest-Ilfov dominance and the rise of the three secondary hubs
- Share-of-national-ICT-employment trajectory 2008 → latest for each hub

#### 6.2 Hub Profiles — Symmetric Treatment
For each of **Bucharest-Ilfov, Cluj-Napoca (Nord-Vest), Timișoara (Vest), Iași (Nord-Est)** we produce the same six measurements so they can be compared like-for-like:
1. ICT employment level and growth (Eurostat NUTS2; INS Tempo by județ where available)
2. ICT share of total regional employment
3. Local university feed — graduate output from the anchor technical university (UPB / UTCN / UPT / TUIASI)
4. Regional average wage trajectory (INS Tempo) — IT wage premium amplified at the regional level
5. Population balance — net migration into the județ (INS), uniquely positive for IT-hub counties in a country with overall demographic decline
6. House price index trend (INS regional series) — the most visible spillover

#### 6.3 Cross-Hub Comparison
- Side-by-side charts: who grew fastest, where the wage premium is widest, where the housing-market effect is most pronounced
- Specialisation differences (e.g. Cluj's product/startup tilt vs Bucharest's corporate-services concentration vs Timișoara's automotive-adjacent embedded software vs Iași's outsourcing scale)

#### 6.4 What Does Not Spillover Easily
- Honest counter-evidence: surrounding rural counties have not benefitted comparably (regional disparities widened — overlaps with `romania/07_regional.py` analysis)
- The "ring effect" — spillovers stop sharply at the metro boundary

**Scripts:** `05_hubs.py` — Eurostat regional employment, INS regional wages, INS house price index, INS demographic balance, Ministry of Education graduate counts. The most data-intensive module.

---

### 7. Industry Landscape — What Kind of Sector Is This?
**Goal:** characterise the industry as a whole — types of firms, who owns them, what they actually do, and whether Romania has graduated from pure outsourcing to product creation. No single-company spotlight; the chapter reads the sector laterally.

#### 7.1 Composition — Services vs Product
- Mix of revenue: body-shop outsourcing, captive R&D centres of multinationals, domestic product/SaaS firms (proxied from ANIS public surveys + Eurostat business demography)
- Trajectory over time — has the product share grown?

#### 7.2 Ownership Structure
- Foreign-controlled vs domestically-owned firms by employment and turnover (INS Tempo, Eurostat FATS where available)
- The "captive centre" model: multinationals doing R&D *in* Romania for products sold elsewhere — captured in services exports but not in product ownership

#### 7.3 Sub-Sector Specialisations
- Automotive software (Continental, Bosch, Vitesco — anchored around Sibiu/Timișoara/Cluj)
- Cybersecurity (long-standing Romanian strength — Bitdefender as the canonical example)
- Fintech (Bucharest cluster)
- Enterprise SaaS / RPA — UiPath as the most visible but not the only one
- Gaming and creative tech (Bucharest, Cluj)

For each sub-sector: how big, who the anchor employers are (named from public filings/press), and what fraction of national ICT employment it represents where measurable.

#### 7.4 Maturity Indicators
- R&D intensity in the ICT sector vs total economy (Eurostat `rd_e_berdindr2`)
- Patents / EPO filings with Romanian-resident inventors in computing fields
- Venture funding flowing into Romanian tech (public sources only: EIF annual reports, How To Web public summaries)
- Number of Romanian-origin firms reaching scale (proxy: firms above an employment/revenue threshold in INS data)

**Scripts:** `06_industry_landscape.py` — Eurostat R&D, EPO public statistics, INS Tempo for firm-size distribution. Sub-sector anchor employers cited in `report.md` from public press releases / filings.

---

### 8. The Digital Economy Paradox — DESI and Beyond
**Goal:** standalone chapter contrasting a world-class IT *production* sector with a digitally lagging *general* economy. This is one of the more interesting features of the Romanian case and deserves its own treatment rather than being a footnote in the outlook.

#### 8.1 DESI Headline
- Romania's overall DESI ranking vs EU27 over time
- Component breakdown: Human Capital, Connectivity, Integration of Digital Technology, Digital Public Services

#### 8.2 The Connectivity Paradox
- FTTH / gigabit coverage — Romania at or near the EU top (often top 3)
- Why: late-mover advantage, competitive ISP market, low legacy copper investment
- The "Romania has fast internet" cliché — verifying it from data, not folklore

#### 8.3 The Digital Skills Gap
- Share of population with basic / above-basic digital skills (Eurostat `isoc_sk_dskl_i21`)
- Romania consistently in the bottom 2–3 of EU27
- The gap between ICT specialists (excellent) and digital skills of the general population (poor) is one of the widest in Europe

#### 8.4 Digital Public Services
- e-government use by citizens and businesses
- Why a country that exports billions in IT services has a famously analogue public sector

#### 8.5 Business Digitalisation
- SME adoption of cloud, e-commerce, ERP
- Romanian businesses outside the ICT sector are among the least digitalised in EU

#### 8.6 Interpretation
- The IT sector grew *despite* the rest of the economy's digital state, not because of it
- Implications: domestic demand has not been the growth driver — exports were

**Scripts:** `07_digital_economy.py` — DESI indicators, Eurostat digital-skills and ICT-adoption series.

---

### 9. Headwinds and Future Prospects
**Goal:** the honest forward-looking section. What could derail or accelerate the next decade.

#### 9.1 Talent Supply
- CS graduate output flattening vs continued demand growth
- Emigration competition: Romanian engineers still recruited westward
- Wage levels eroding cost arbitrage — Romania is no longer cheap

#### 9.2 End of the Tax Exemption Era
- 2023 cap and subsequent tightening — labour-market response
- What replaces the implicit subsidy (if anything)

#### 9.3 AI and Automation
- Risk to entry-level outsourcing/QA roles — public OECD work on AI exposure by occupation
- Opportunity: AI development hubs (local presence of Nvidia, Microsoft AI teams, etc., based on public announcements)

#### 9.4 Geopolitics & Nearshoring
- Post-2022 nearshoring momentum to CEE
- Romania's positioning vs Poland, Czech Republic, Bulgaria

#### 9.5 Scenarios
- Continuation: gradual move up the value chain, sector grows in line with services exports
- Stagnation: outsourcing erodes, product transition does not happen at scale
- Acceleration: AI tooling raises per-engineer productivity, Romania benefits disproportionately

**Scripts:** `08_outlook.py` — OECD AI-exposure measures, demographic projections of working-age STEM cohort, Eurostat ICT-specialist demand-supply indicators.

---

### 10. Synthesis
- The five things that made Romanian IT work (testable claims, each backed by a chart)
- What the sector contributed beyond GDP: a functioning model of meritocratic mobility, real-wage convergence with Western Europe inside Romania, and a regional development pattern unlike anything else in the country
- What the next decade demands

---

## Deliverables

| File | Description |
|------|-------------|
| `plan.md` | This document |
| `01_origins.py` | Timeline + engineering-graduate output chart (1990s qualitative anchor) |
| `02_boom.py` | Sector value-added and employment 2000–2010, EU comparison |
| `03_sector_today.py` | Current GDP share, employment, exports, firm demography |
| `04_wages_careers.py` | Wage premium, women-in-tech share, graduate pipeline, tax-exemption effect |
| `05_hubs.py` | Regional concentration + symmetric Bucharest / Cluj / Timișoara / Iași profiles, spillovers |
| `06_industry_landscape.py` | Services vs product mix, ownership, sub-sector specialisations, R&D / patent maturity |
| `07_digital_economy.py` | DESI headline + components, connectivity paradox, digital-skills gap, business digitalisation |
| `08_outlook.py` | AI exposure, STEM demographic pipeline, nearshoring positioning |
| `report.md` | Narrative report with embedded chart references |
| `raw-data/` | All CSVs as fetched from upstream APIs/portals |
| `charts/` | All generated PNGs |

---

## Python Stack
Same as the parent repo — reuses the shared `.venv/`:

```
pandas, matplotlib, seaborn   — data manipulation & plotting
eurostat                       — Eurostat API wrapper
wbgapi                         — World Bank data
requests                       — raw API calls (BNR, INS Tempo, OECD)
openpyxl                       — read BNR/INS XLSX exports
```

No new heavy dependencies anticipated.

---

## Sequencing
1. Review & approve this plan
2. Build `01_origins.py` and `02_boom.py` together (history block)
3. Build `03_sector_today.py` and `04_wages_careers.py` (current-state block)
4. Build `05_hubs.py` (regional block — most data-intensive, four symmetric hub profiles)
5. Build `06_industry_landscape.py` (sector composition and maturity)
6. Build `07_digital_economy.py` (DESI standalone) and `08_outlook.py` (forward-looking)
7. Write `report.md` chapter by chapter, anchoring each claim to a generated chart
8. Update root `README.md` to register the third analysis folder

---

## Scope Decisions (resolved)
- **Time horizon:** 1990–present. The 1990s get qualitative treatment with cited reports; quantitative charts start ~2000 where Eurostat/INS coverage is solid.
- **Case study approach:** no single-company spotlight. §7 reads the industry laterally — composition, ownership, sub-sector specialisations, maturity.
- **Regional hubs:** equal-weight, symmetric treatment of Bucharest-Ilfov, Cluj-Napoca, Timișoara, Iași — same six measurements per hub.
- **Digital economy / DESI:** standalone chapter (§8), not a footnote in the outlook. The contrast between an excellent IT *production* sector and a digitally lagging *general* economy is one of the more interesting features of the Romanian case.
