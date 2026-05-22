# SAFE — EU Security Action for Europe & Romania

An objective assessment of the EU's €150 bn Security Action for Europe (SAFE) defence-financing instrument, with emphasis on costs and benefits for Romania. Covers the contracts ledger of all 21 Romanian SAFE-funded programmes, the controversies around German-prime concentration, transparency, and the Hanwha (Korean) exclusion on the Lynx KF41 IFV programme, the macro/fiscal layer, and the "auto-to-defence pivot" thesis.

Research conducted 2026-05-22, **8 days before the 30 May 2026 SAFE single-MS contracting deadline**.

## Where to start

**Read [`synthesis.md`](synthesis.md) first** — the Romania-centric TL;DR, the three controversies separately, and what to watch in the deadline week.

Then, if you want the structured verdicts: [`hypothesis_scorecard.md`](hypothesis_scorecard.md) — five pre-committed hypotheses tested against pre-set falsification thresholds.

The five thread files underneath are the underlying research; dip in by topic.

## File index

| File | Lines | Purpose |
|---|---:|---|
| [`synthesis.md`](synthesis.md) | 215 | **Main deliverable.** Bottom-line cost-benefit for Romania, three separate verdicts on the three conflated controversies, deadline-week watch list, open documentary gaps |
| [`hypothesis_scorecard.md`](hypothesis_scorecard.md) | 93 | H1–H5 verdicts against pre-committed thresholds (German prime share, single-source share, Korean exclusion grounds, auto-pivot, net NPV) |
| [`01_foundation_and_ledger.md`](01_foundation_and_ledger.md) | 433 | SAFE regulation summary, Law 4/2026 summary, walkthrough of all 21 Romanian programmes, aggregations |
| [`02_ifv_skynex_briefs.md`](02_ifv_skynex_briefs.md) | 470 | Deep-dives on the two highest-value German wins: Lynx KF41 IFV (€3.34 bn, Hanwha excluded at RFI) and Skynex VSHORAD (€476 m, benchmarked against Italian price) |
| [`03_political_transparency_briefs.md`](03_political_transparency_briefs.md) | 818 | PSD influence-peddling accusations; Defence Minister Miruță's "30% price hike at signature" complaint; OUG 62/2025 → Law 4/2026 → OUG 21/2026 → OUG 38/2026 legal stack (last one challenged at the Constitutional Court); Romanian industrial participation |
| [`04_german_pivot.md`](04_german_pivot.md) | 834 | Test of H4 — whether German defence primes are absorbing automotive-sector capacity. Verdict: pivot is real but a minority mechanism; the dominant mechanism is the 65% EU/EEA/Ukraine content rule plus the scale of incumbent German primes |
| [`05_macro_fiscal.md`](05_macro_fiscal.md) | 721 | SAFE loan economics (~3% / 45y / 10y grace, €5–8 bn PV subsidy), Romania's fiscal context (BBB-/Negative across all three agencies), opportunity-cost analysis (A8 was originally in PNRR), comparator data for Poland / France / Italy / Hungary |
| [`contracts_ledger.csv`](contracts_ledger.csv) | 22 | The 21-programme ledger with prime, value, country, procedure type, status, source — the empirical spine of the whole analysis |
| [`_aggregate.py`](_aggregate.py) | — | Reproducible pandas aggregation script (uses the repo-root `.venv/`) for the headline shares (German prime %, single-source %, etc.) |
| [`research_plan.md`](research_plan.md) | 176 | The original plan: research questions, the five hypotheses with pre-committed falsification thresholds, source taxonomy, working order |

## Headline findings (one-paragraph version)

SAFE is a **net-positive €3–6 bn NPV** deal for Romania, dominated by a 250–350 bps financing subsidy (~3 % SAFE rate vs Romania's 5.5–6.5 % EUR sovereign curve), worth **€5–8 bn in present value** over the 45-year loan life. Romania receives €16.68 bn now and pays back roughly €32 bn nominal across 45 years. But the procurement governance is **structurally opaque**: ~65 % of the €9.80 bn military pool is awarded under negotiated procedure without prior publication, authorised by a four-ordinance legal stack (OUG 62/2025 → Law 4/2026 → OUG 21/2026 → OUG 38/2026), the last of which is contested at the Constitutional Court. The "German bailout" charge is **mostly wrong as literally stated** (Germany itself doesn't draw SAFE money — it uses its own €600 bn Sondervermögen; the iconic VW Osnabrück–Rheinmetall auto-pivot deal collapsed in March 2026) **but partially right in a way that matters**: Romania sends ~61 % of MApN SAFE value to German primes and ~54 % to Rheinmetall alone — the highest single-firm concentration in the SAFE pool, because Romania lacks a domestic prime-contractor champion. The Hanwha exclusion on Lynx is real and not defended via published evaluation; the silent +12 % unit-price hike on Lynx (after a 22 % quantity cut) is the most quantifiable single governance loss.

## Methodology

- All five thread files were produced by parallel research agents using primary documents (Romanian Monitorul Oficial, EU Commission press releases, MApN notices, IMF Article IV, rating-agency reports) where available, and trade press plus Romanian-language coverage for items where primary documents are not public.
- Falsification thresholds for H1–H5 were set in `research_plan.md` **before** the data was tallied. The scorecard reads each hypothesis against its pre-committed threshold.
- Press-estimated vs contract-confirmed values are flagged programme-by-programme in `contracts_ledger.csv`.
- Largest residual uncertainty: the full SAFE loan-agreement text for Romania is not yet public, so the ~3 % rate / 45-year / 10-year-grace structure is triangulated rather than confirmed. If the effective lifetime cost is closer to 3.3–3.5 %, the PV subsidy shrinks from €5–8 bn toward €4–6 bn but remains comfortably positive.

## Reproducing the ledger aggregations

```bash
cd /Users/2346263/projects/economie
source .venv/bin/activate
python SAFE/_aggregate.py
```

The script reads `contracts_ledger.csv` and prints the headline shares (total value, German-prime share, Rheinmetall share, single-source share, joint-EU vs national split).
