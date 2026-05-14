"""
Prepend a '#'-prefixed source header to every CSV in raw-data/.

Format of the header:
    # Source: Eurostat — <dataset_code> (<dataset description>)
    # Filters: <key=value pairs>
    # URL: https://ec.europa.eu/eurostat/databrowser/view/<dataset_code>/default/table
    # Notes (optional): <any caveat such as 'derived' or 'snapshot date'>

For derived CSVs (ratios, indices, sums), the header lists every upstream
dataset that feeds the derivation.

This script is idempotent: if a CSV already starts with '# Source:' it skips it.
"""

import os
import sys

RAW = "raw-data"

EUROSTAT_URL = "https://ec.europa.eu/eurostat/databrowser/view/{code}/default/table"

# (sources, filters, notes, friendly_title) — one entry per CSV file in raw-data/
SOURCES = {
    "01b_ict_graduates_tertiary.csv": dict(
        codes=["educ_uoe_grad02"],
        filters="iscedf13=F06 (ICT field), isced11=ED5-8 (tertiary), sex=T, unit=NR",
        title="Tertiary graduates in ICT field of education",
        notes="Eurostat coverage starts ~2013; RO 2013-2014 contains only ED6 (bachelor), ED7 reported as 0 — a known coverage gap (raw values retained).",
    ),
    "01c_engineering_graduates_tertiary.csv": dict(
        codes=["educ_uoe_grad02"],
        filters="iscedf13=F07 (engineering, manufacturing, construction), isced11=ED5-8, sex=T, unit=NR",
        title="Tertiary graduates in engineering, manufacturing & construction",
    ),
    "01d_ict_share_of_grads_pct.csv": dict(
        codes=["educ_uoe_grad02"],
        filters="(iscedf13=F06 / iscedf13=TOTAL) × 100, isced11=ED5-8, sex=T, unit=NR",
        title="ICT graduates as % of all tertiary graduates",
        notes="Derived: ratio of F06 over TOTAL within educ_uoe_grad02.",
    ),
    "02a_ict_gva_meur.csv": dict(
        codes=["nama_10_a64"],
        filters="nace_r2=J62_J63 (computer programming & information services), na_item=B1G (gross value added), unit=CP_MEUR (current prices, million EUR)",
        title="Gross value added in J62_J63, current prices",
    ),
    "02b_ict_gva_share_pct.csv": dict(
        codes=["nama_10_a64"],
        filters="(J62_J63 / TOTAL) × 100, na_item=B1G, unit=CP_MEUR",
        title="J62_J63 GVA as % of total GVA",
        notes="Derived ratio within nama_10_a64.",
    ),
    "02c_ict_employment_ths.csv": dict(
        codes=["nama_10_a64_e"],
        filters="nace_r2=J62_J63, na_item=EMP_DC (total employment, domestic concept), unit=THS_PER (thousand persons)",
        title="Employment in J62_J63, national accounts",
    ),
    "02d_ict_employment_index_2000_100.csv": dict(
        codes=["nama_10_a64_e"],
        filters="J62_J63 employment / 2000 value × 100",
        title="Employment in J62_J63 indexed (2000 = 100)",
        notes="Derived from nama_10_a64_e (THS_PER).",
    ),
    "02e_ict_gva_real_clv15_meur.csv": dict(
        codes=["nama_10_a64"],
        filters="nace_r2=J62_J63, na_item=B1G, unit=CLV15_MEUR (chain-linked volumes, 2015 reference)",
        title="Real (constant 2015 prices) GVA in J62_J63",
    ),
    "02e_ict_productivity_real_keur_per_worker.csv": dict(
        codes=["nama_10_a64", "nama_10_a64_e"],
        filters="(B1G CLV15_MEUR for J62_J63) / (EMP_DC THS_PER for J62_J63)",
        title="Real GVA per worker in J62_J63 (thousand EUR, 2015 prices)",
        notes="Derived: real GVA divided by employment.",
    ),
    "03a_ict_specialists_pct_emp.csv": dict(
        codes=["isoc_sks_itspt"],
        filters="unit=PC_EMP (% of total employment)",
        title="ICT specialists as % of total employment",
    ),
    "03b_telecom_computer_info_exports_eur_bn.csv": dict(
        codes=["bop_its6_det"],
        filters="bop_item=SI (telecommunications, computer & information services), stk_flow=CRE (credits/exports), currency=MIO_EUR, partner=WRL_REST",
        title="Telecom, computer & information services exports (EUR bn)",
        notes="Values converted from million EUR to billion EUR (/1000).",
    ),
    "03c_it_services_trade_balance_eur_bn.csv": dict(
        codes=["bop_its6_det"],
        filters="bop_item=SI, partner=WRL_REST, currency=MIO_EUR; exports = stk_flow=CRE, imports = stk_flow=DEB; balance = exports − imports",
        title="Trade balance in IT services (RO)",
        notes="Derived from bop_its6_det credits and debits.",
    ),
    "03d_it_share_of_services_exports_pct.csv": dict(
        codes=["bop_its6_det"],
        filters="(bop_item=SI / bop_item=S) × 100, stk_flow=CRE, currency=MIO_EUR, partner=WRL_REST",
        title="IT services as % of total services exports",
        notes="Derived ratio within bop_its6_det.",
    ),
    "03e_enterprises_j62_j63.csv": dict(
        codes=["sbs_na_1a_se_r2", "sbs_ovw_act"],
        filters="legacy: indic_sb=V11110 (enterprises) for nace_r2=J62/J63 (2005-2020); new: indic_sbs=ENT_NR for nace_r2=J62/J63 (2021+)",
        title="Active enterprises in J62 and J63",
        notes="Methodology break in 2021 (new SBS Regulation 2019/2152); legacy and new series shown separately.",
    ),
    "04a_ro_compensation_per_employee.csv": dict(
        codes=["nama_10_a64", "nama_10_a64_e"],
        filters="(D1 compensation MEUR for J62_J63 and TOTAL) / (SAL_DC employees THS_PER); premium_x = ict_eur / total_eur",
        title="RO annual compensation per employee — J62_J63 vs whole economy",
        notes="Derived: compensation of employees divided by employees (paid).",
    ),
    "04c_wage_premium_ratio_cee.csv": dict(
        codes=["nama_10_a64", "nama_10_a64_e"],
        filters="(D1/SAL_DC J62_J63) / (D1/SAL_DC TOTAL), per country",
        title="IT wage premium (J62_J63 / whole-economy) across CEE",
        notes="Derived from the same series as 04a, applied per country.",
    ),
    "04d_women_ict_specialists_pct.csv": dict(
        codes=["isoc_sks_itsps"],
        filters="unit=PC, sex=F (women as % of ICT specialists)",
        title="Women as % of ICT specialists",
    ),
    "05a_ict_employment_nuts2_lfs_ths.csv": dict(
        codes=["lfst_r_lfe2en2"],
        filters="nace_r2=J (information & communication), sex=T, age=Y_GE15, unit=THS_PER, geo=RO NUTS2 regions",
        title="NUTS2 employment in NACE J — LFS",
        notes="LFS-sourced — small NUTS2 cells are sample-noisy.",
    ),
    "05b_naceJ_compensation_nuts2_meur.csv": dict(
        codes=["nama_10r_2coe"],
        filters="nace_r2=J, currency=MIO_EUR, geo=RO NUTS2 regions",
        title="NUTS2 compensation of employees in NACE J",
    ),
    "05c_hubs_share_of_naceJ_pct.csv": dict(
        codes=["nama_10r_2coe"],
        filters="Hub NUTS2 compensation / national (sum across RO NUTS2) × 100, nace_r2=J",
        title="Hub share of national NACE-J compensation",
        notes="Derived from nama_10r_2coe.",
    ),
    "05d_hubs_compensation_index_2008_100.csv": dict(
        codes=["nama_10r_2coe"],
        filters="Hub NACE-J compensation / 2008 value × 100",
        title="NACE-J compensation growth by hub (2008 = 100)",
        notes="Derived from nama_10r_2coe.",
    ),
    "05e_population_nuts2.csv": dict(
        codes=["demo_r_pjangrp3"],
        filters="sex=T, age=TOTAL, unit=NR, geo=RO NUTS2 regions and RO",
        title="NUTS2 population (and national total)",
    ),
    "05f_house_price_index_2015_100.csv": dict(
        codes=["prc_hpi_a"],
        filters="purchase=TOTAL, unit=I15_A_AVG (annual average index, 2015 = 100)",
        title="House price index — Romania vs EU27 (2015 = 100)",
    ),
    "06a_business_rd_ro_meur.csv": dict(
        codes=["rd_e_berdindr2"],
        filters="nace_r2 ∈ {J, J62, TOTAL}, unit=MIO_EUR, geo=RO",
        title="Romania business R&D expenditure by NACE",
    ),
    "06b_ict_share_of_business_rd_pct.csv": dict(
        codes=["rd_e_berdindr2"],
        filters="(nace_r2=J / nace_r2=TOTAL) × 100, unit=MIO_EUR",
        title="Information & communication as % of business R&D",
        notes="Derived ratio within rd_e_berdindr2.",
    ),
    "06c_rd_intensity_j62_pct_gva.csv": dict(
        codes=["rd_e_berdindr2", "nama_10_a64"],
        filters="(rd_e_berdindr2 nace_r2=J62 MIO_EUR) / (nama_10_a64 nace_r2=J62_J63 B1G CP_MEUR) × 100",
        title="R&D intensity — J62 business R&D / J62_J63 GVA",
        notes="Derived from two datasets.",
    ),
    "06d_epo_patent_applications.csv": dict(
        codes=["pat_ep_ntot"],
        filters="unit=NR (all technology fields, all IPC sections)",
        title="EPO patent applications (all fields)",
    ),
    "06e_epo_ict_related_patents.csv": dict(
        codes=["pat_ep_ntec"],
        filters="unit=NR, ipc ∈ {CAB, CTE, SMC} summed (computing, communication, semiconductors)",
        title="EPO patent applications in computing/communication/semiconductors",
        notes="Sum of three high-tech IPC subsets within pat_ep_ntec.",
    ),
    "07a_internet_use_pct_individuals.csv": dict(
        codes=["isoc_ci_ifp_iu"],
        filters="indic_is=I_IU3 (used internet last 3 months), ind_type=IND_TOTAL, unit=PC_IND",
        title="% of individuals using internet in last 3 months",
    ),
    "07b_household_internet_access_pct.csv": dict(
        codes=["isoc_ci_in_h"],
        filters="unit=PC_HH (% of households), hhtyp=TOTAL",
        title="% of households with internet access",
    ),
    "07c_digital_skills_basic_plus_pre2021.csv": dict(
        codes=["isoc_sk_dskl_i"],
        filters="indic_is=I_DSK_BAB (basic or above-basic), ind_type=IND_TOTAL, unit=PC_IND",
        title="Individuals with basic+ digital skills — pre-2021 methodology",
        notes="Methodology revised in 2021; companion file *_2021plus uses the new definition.",
    ),
    "07c_digital_skills_basic_plus_2021plus.csv": dict(
        codes=["isoc_sk_dskl_i21"],
        filters="indic_is=I_DSK2_BAB (basic or above-basic, 2021+ definition), ind_type=IND_TOTAL, unit=PC_IND",
        title="Individuals with basic+ digital skills — 2021+ methodology",
        notes="Successor series of isoc_sk_dskl_i (definition change in 2021).",
    ),
    "07d_cloud_adoption_enterprises_pct.csv": dict(
        codes=["isoc_cicce_use"],
        filters="indic_is=E_CC (buy cloud computing services), size_emp=GE10, unit=PC_ENT",
        title="% of enterprises (10+ employees) buying cloud services",
    ),
    "07e_egov_forms_pct_individuals.csv": dict(
        codes=["isoc_ciegi_ac"],
        filters="indic_is=I_IGOV12FM (submitted forms online to public auth., last 12 months), ind_type=IND_TOTAL, unit=PC_IND",
        title="% of individuals submitting forms online to public authorities",
    ),
    "07f_adoption_indicators_latest.csv": dict(
        codes=["isoc_sk_dskl_i21", "isoc_cicce_use", "isoc_ciegi_ac"],
        filters="Latest available value per country for basic+ digital skills, cloud adoption, and e-gov form submission",
        title="Latest digital-adoption indicators (snapshot)",
        notes="Derived: most recent non-NaN value per country from the three datasets above.",
    ),
    "07f_production_indicators_latest.csv": dict(
        codes=["isoc_sks_itspt", "bop_its6_det"],
        filters="Latest available value per country for ICT specialists share (PC_EMP) and IT services share of services exports (SI/S, CRE, WRL_REST)",
        title="Latest IT-production indicators (snapshot)",
        notes="Derived: most recent non-NaN value per country from the two datasets above.",
    ),
    "08a_working_age_pop_projection_persons.csv": dict(
        codes=["proj_23np"],
        filters="projection=BSL (baseline), sex=T, age=Y15-64, unit=PER",
        title="Working-age population (15-64) projection — baseline (proj_23np)",
        notes="Eurostat 2023-based population projections (EUROPOP2023).",
    ),
    "08a_working_age_pop_projection_index2022.csv": dict(
        codes=["proj_23np"],
        filters="As 08a_working_age_pop_projection_persons.csv, indexed to first year (2022) = 100",
        title="Working-age population projection — indexed (2022 = 100)",
        notes="Derived from proj_23np baseline projection.",
    ),
    "08b_young_adult_pop_projection_persons.csv": dict(
        codes=["proj_23np"],
        filters="projection=BSL, sex=T, age ∈ {Y20..Y29} summed, unit=PER",
        title="Young-adult (20-29) population projection — baseline (proj_23np)",
        notes="Derived: sum of single-year age groups Y20 to Y29.",
    ),
    "08b_young_adult_pop_projection_index2022.csv": dict(
        codes=["proj_23np"],
        filters="As 08b_young_adult_pop_projection_persons.csv, indexed to first year (2022) = 100",
        title="Young-adult population projection — indexed (2022 = 100)",
        notes="Derived from proj_23np baseline projection.",
    ),
    "08c_job_vacancy_rate_nace_j_quarterly.csv": dict(
        codes=["jvs_q_nace2"],
        filters="indic_em=JVR, sizeclas=TOTAL, s_adj=NSA, nace_r2=J",
        title="Quarterly job vacancy rate in NACE J (information & communication)",
        notes="First column = fractional year (e.g. 2023.25 = 2023-Q2).",
    ),
    "08d_compensation_per_employee_ict_keur.csv": dict(
        codes=["nama_10_a64", "nama_10_a64_e"],
        filters="(nama_10_a64 D1 CP_MEUR for J62_J63) / (nama_10_a64_e SAL_DC THS_PER for J62_J63); kEUR per employee per year",
        title="Annual compensation per employee in J62_J63 — RO vs CEE peers vs DE/FR",
        notes="Derived: compensation of employees divided by employees (paid).",
    ),
    "08e_ict_specialists_share_emp.csv": dict(
        codes=["isoc_sks_itspt"],
        filters="unit=PC_EMP, geo=PEERS + EU27 + FI + SE",
        title="ICT specialists as % of total employment (including EU leaders)",
        notes="Same dataset as 03a; broader geo set for the headroom comparison.",
    ),
    "08f_ro_ict_gva_history_eurbn.csv": dict(
        codes=["nama_10_a64"],
        filters="nace_r2=J62_J63, na_item=B1G, unit=CP_MEUR, geo=RO; values divided by 1000 (MEUR → EUR bn)",
        title="Romania ICT (J62_J63) GVA history, EUR bn",
        notes="Derived from nama_10_a64 (rescaling).",
    ),
    "08f_scenarios_2030_eurbn.csv": dict(
        codes=[],
        filters="Constant-growth projections from last actual value: stagnation 1%/yr, continuation 9%/yr, acceleration 14%/yr (nominal)",
        title="ILLUSTRATIVE 2030 scenarios for RO ICT GVA — NOT real data",
        notes="Calibrated thumbnails for the narrative, not forecasts. Past anchor (last actual) is from nama_10_a64; future values are author projections at fixed nominal rates.",
    ),
}


def build_header(meta, fname):
    lines = []
    title = meta.get("title", "")
    if title:
        lines.append(f"# {title}")
    codes = meta.get("codes", [])
    if codes:
        if len(codes) == 1:
            lines.append(f"# Source: Eurostat dataset {codes[0]}")
            lines.append(f"# URL: {EUROSTAT_URL.format(code=codes[0])}")
        else:
            lines.append(f"# Source: Eurostat datasets {', '.join(codes)}")
            for c in codes:
                lines.append(f"# URL: {EUROSTAT_URL.format(code=c)}")
    else:
        lines.append("# Source: author calculation (no Eurostat dataset)")
    filt = meta.get("filters", "")
    if filt:
        lines.append(f"# Filters: {filt}")
    notes = meta.get("notes")
    if notes:
        lines.append(f"# Notes: {notes}")
    lines.append("# Generated by the Python scripts in this directory's parent (01_origins.py .. 08_outlook.py).")
    return "\n".join(lines) + "\n"


def main():
    files = sorted(os.listdir(RAW))
    n_updated = 0
    n_skipped_existing = 0
    n_missing_meta = 0
    for f in files:
        if not f.endswith(".csv"):
            continue
        path = os.path.join(RAW, f)
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
        if content.startswith("# "):
            n_skipped_existing += 1
            print(f"  skip (already has header): {f}")
            continue
        if f not in SOURCES:
            n_missing_meta += 1
            print(f"  MISSING metadata for: {f}")
            continue
        header = build_header(SOURCES[f], f)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(header + content)
        n_updated += 1
        print(f"  updated: {f}")
    print(f"\nUpdated {n_updated} files, skipped {n_skipped_existing} (already had header), "
          f"missing metadata for {n_missing_meta}.")
    if n_missing_meta > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
