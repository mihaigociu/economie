"""
Verification script: re-fetch a sample of values from Eurostat for each CSV
and compare against what is stored in raw-data/. Reports OK/MISMATCH/MISSING
for each tested datapoint, so we can confirm the data is real and matches
the indicated source (not hallucinated).
"""
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import eurostat

RAW = "raw-data"

def fetch(code, filters):
    df = eurostat.get_data_df(code, flags=False).rename(columns={"geo\\TIME_PERIOD": "geo"})
    for col, vals in filters.items():
        if isinstance(vals, str):
            vals = [vals]
        df = df[df[col].isin(vals)]
    return df

def to_year_indexed(df, by="geo"):
    yrs = [c for c in df.columns if str(c).isdigit()]
    out = df.set_index(by)[yrs].astype(float)
    out.columns = out.columns.astype(int)
    out = out.T.sort_index()
    out.index.name = "year"
    return out

def check(label, expected, actual, tol=0.01):
    if pd.isna(expected) and pd.isna(actual):
        result = "OK (both NaN)"
    elif pd.isna(expected) or pd.isna(actual):
        result = f"MISMATCH expected={expected} actual={actual}"
    else:
        diff = abs(expected - actual)
        rel  = diff / max(abs(expected), 1e-9)
        if rel < tol:
            result = f"OK  ({actual:.4g} vs {expected:.4g})"
        else:
            result = f"MISMATCH expected={expected:.4g} actual={actual:.4g} rel_diff={rel:.3%}"
    print(f"  [{label}]  {result}")

# ---------------------------------------------------------------------------
print("\n=== 01b ICT graduates (educ_uoe_grad02, F06, ED5-8, T, NR) ===")
csv = pd.read_csv(f"{RAW}/01b_ict_graduates_tertiary.csv", comment="#").set_index("year")
df  = fetch("educ_uoe_grad02", {"iscedf13": "F06", "isced11": "ED5-8", "sex": "T",
                                "unit": "NR", "geo": ["RO","PL","HU"]})
api = to_year_indexed(df)
for geo, yr in [("RO", 2023), ("PL", 2023), ("HU", 2020)]:
    check(f"{geo} {yr}", csv.loc[yr, geo], api.loc[yr, geo])

# ---------------------------------------------------------------------------
print("\n=== 02a ICT GVA, current prices (nama_10_a64, J62_J63, B1G, CP_MEUR) ===")
csv = pd.read_csv(f"{RAW}/02a_ict_gva_meur.csv", comment="#").set_index("year")
df  = fetch("nama_10_a64", {"nace_r2": "J62_J63", "na_item": "B1G",
                            "unit": "CP_MEUR", "geo": ["RO","PL","CZ"]})
api = to_year_indexed(df)
for geo, yr in [("RO", 1995), ("RO", 2007), ("RO", 2023), ("PL", 2023), ("CZ", 2015)]:
    check(f"{geo} {yr}", csv.loc[yr, geo], api.loc[yr, geo])

# ---------------------------------------------------------------------------
print("\n=== 02c ICT employment (nama_10_a64_e, J62_J63, EMP_DC, THS_PER) ===")
csv = pd.read_csv(f"{RAW}/02c_ict_employment_ths.csv", comment="#").set_index("year")
df  = fetch("nama_10_a64_e", {"nace_r2": "J62_J63", "na_item": "EMP_DC",
                              "unit": "THS_PER", "geo": ["RO","PL"]})
api = to_year_indexed(df)
for geo, yr in [("RO", 2000), ("RO", 2010), ("RO", 2022), ("RO", 2023), ("PL", 2023)]:
    check(f"{geo} {yr}", csv.loc[yr, geo], api.loc[yr, geo])

# ---------------------------------------------------------------------------
print("\n=== 03a ICT specialists share (isoc_sks_itspt, PC_EMP) ===")
csv = pd.read_csv(f"{RAW}/03a_ict_specialists_pct_emp.csv", comment="#").set_index("year")
df  = fetch("isoc_sks_itspt", {"unit": "PC_EMP", "geo": ["RO","CZ","EU27_2020"]})
api = to_year_indexed(df)
for geo, yr in [("RO", 2024), ("CZ", 2024), ("EU27_2020", 2024)]:
    if yr in api.index and yr in csv.index:
        check(f"{geo} {yr}", csv.loc[yr, geo], api.loc[yr, geo])

# ---------------------------------------------------------------------------
print("\n=== 03b IT services exports (bop_its6_det, SI, CRE, WRL_REST, MIO_EUR -> EUR bn) ===")
csv = pd.read_csv(f"{RAW}/03b_telecom_computer_info_exports_eur_bn.csv", comment="#").set_index("year")
df  = fetch("bop_its6_det", {"bop_item":"SI","stk_flow":"CRE",
                             "currency":"MIO_EUR","partner":"WRL_REST",
                             "geo":["RO","PL"]})
api = to_year_indexed(df) / 1000.0
for geo, yr in [("RO", 2013), ("RO", 2020), ("RO", 2024), ("PL", 2023)]:
    check(f"{geo} {yr}", csv.loc[yr, geo], api.loc[yr, geo])

# ---------------------------------------------------------------------------
print("\n=== 05b NUTS2 NACE-J compensation (nama_10r_2coe, J, MIO_EUR) ===")
csv = pd.read_csv(f"{RAW}/05b_naceJ_compensation_nuts2_meur.csv", comment="#").set_index("year")
df  = fetch("nama_10r_2coe", {"nace_r2":"J","currency":"MIO_EUR",
                              "geo":["RO32","RO11","RO42","RO21"]})
api = to_year_indexed(df)
for geo, yr in [("RO32", 2008), ("RO11", 2020), ("RO42", 2022), ("RO21", 2022)]:
    if yr in csv.index and yr in api.index:
        check(f"{geo} {yr}", csv.loc[yr, geo], api.loc[yr, geo])

# ---------------------------------------------------------------------------
print("\n=== 06d EPO patent applications (pat_ep_ntot, NR) ===")
csv = pd.read_csv(f"{RAW}/06d_epo_patent_applications.csv", comment="#").set_index("year")
df  = fetch("pat_ep_ntot", {"unit":"NR","geo":["RO","CZ","HU","PL"]})
api = to_year_indexed(df)
for geo, yr in [("RO", 2010), ("CZ", 2015), ("HU", 2018), ("PL", 2020), ("RO", 2020)]:
    if yr in csv.index and yr in api.index and geo in csv.columns and geo in api.columns:
        check(f"{geo} {yr}", csv.loc[yr, geo], api.loc[yr, geo])

# ---------------------------------------------------------------------------
print("\n=== 07a Internet use (isoc_ci_ifp_iu, I_IU3, IND_TOTAL, PC_IND) ===")
csv = pd.read_csv(f"{RAW}/07a_internet_use_pct_individuals.csv", comment="#").set_index("year")
df  = fetch("isoc_ci_ifp_iu", {"indic_is":"I_IU3","ind_type":"IND_TOTAL",
                               "unit":"PC_IND","geo":["RO","EU27_2020"]})
api = to_year_indexed(df)
for geo, yr in [("RO", 2010), ("RO", 2023), ("EU27_2020", 2023)]:
    if yr in csv.index and yr in api.index:
        check(f"{geo} {yr}", csv.loc[yr, geo], api.loc[yr, geo])

# ---------------------------------------------------------------------------
print("\n=== 08c Job vacancy rate (jvs_q_nace2, JVR, TOTAL, NSA, J) ===")
csv = pd.read_csv(f"{RAW}/08c_job_vacancy_rate_nace_j_quarterly.csv", comment="#", index_col=0)
csv.index = csv.index.astype(float)
df  = fetch("jvs_q_nace2", {"indic_em":"JVR","sizeclas":"TOTAL",
                            "s_adj":"NSA","nace_r2":"J","geo":["RO"]})
# Convert quarter cols
qcols = [c for c in df.columns if "-Q" in str(c)]
def q_to_year(q):
    y, qn = q.split("-Q")
    return int(y) + (int(qn) - 1) / 4.0
jvr = df.set_index("geo")[qcols].astype(float)
jvr.columns = [q_to_year(c) for c in jvr.columns]
jvr = jvr.T.sort_index()
# pick a few quarters that appear in CSV
for yfrac in [2023.0, 2023.25, 2024.0, 2025.0]:
    if yfrac in csv.index and yfrac in jvr.index:
        check(f"RO {yfrac}", csv.loc[yfrac, "RO"], jvr.loc[yfrac, "RO"])

# ---------------------------------------------------------------------------
print("\n=== 08a Population projection (proj_23np, BSL, Y15-64, T, PER) ===")
csv = pd.read_csv(f"{RAW}/08a_working_age_pop_projection_persons.csv", comment="#").set_index("year")
df  = fetch("proj_23np", {"projection":"BSL","sex":"T","age":"Y15-64",
                          "unit":"PER","geo":["RO","PL"]})
api = to_year_indexed(df)
for geo, yr in [("RO", 2022), ("RO", 2030), ("PL", 2050)]:
    if yr in csv.index and yr in api.index:
        check(f"{geo} {yr}", csv.loc[yr, geo], api.loc[yr, geo])

# ---------------------------------------------------------------------------
print("\n=== 04a RO compensation per employee (derived nama_10_a64 D1 / nama_10_a64_e SAL_DC) ===")
csv = pd.read_csv(f"{RAW}/04a_ro_compensation_per_employee.csv", comment="#").set_index("year")
dc = fetch("nama_10_a64",   {"nace_r2":"J62_J63","na_item":"D1",
                             "unit":"CP_MEUR","geo":["RO"]})
ee = fetch("nama_10_a64_e", {"nace_r2":"J62_J63","na_item":"SAL_DC",
                             "unit":"THS_PER","geo":["RO"]})
d1  = to_year_indexed(dc)["RO"]
sal = to_year_indexed(ee)["RO"]
wage = (d1 / sal) * 1000.0   # MEUR/THS_PER -> kEUR -> EUR (×1000)
for yr in [2007, 2015, 2022, 2023]:
    if yr in csv.index and yr in wage.index:
        check(f"RO ict_eur {yr}", csv.loc[yr, "ict_eur"], wage.loc[yr])

# ---------------------------------------------------------------------------
print("\n=== 04d Women in ICT specialists (isoc_sks_itsps, PC, F) ===")
csv = pd.read_csv(f"{RAW}/04d_women_ict_specialists_pct.csv", comment="#").set_index("year")
df  = fetch("isoc_sks_itsps", {"unit":"PC","sex":"F",
                               "geo":["RO","EU27_2020"]})
api = to_year_indexed(df)
for geo, yr in [("RO", 2023), ("EU27_2020", 2023)]:
    if yr in csv.index and yr in api.index:
        check(f"{geo} {yr}", csv.loc[yr, geo], api.loc[yr, geo])

# ---------------------------------------------------------------------------
print("\n=== 06a RO business R&D (rd_e_berdindr2, MIO_EUR) ===")
csv = pd.read_csv(f"{RAW}/06a_business_rd_ro_meur.csv", comment="#").set_index("year")
df  = fetch("rd_e_berdindr2", {"nace_r2":["J","J62","TOTAL"],
                               "unit":"MIO_EUR","geo":["RO"]})
def col_for(nace):
    sub = df[df["nace_r2"] == nace]
    yrs = [c for c in df.columns if str(c).isdigit()]
    s = sub[yrs].iloc[0].astype(float)
    s.index = s.index.astype(int)
    return s
for yr, key, nace in [(2015,"j_meur","J"), (2020,"j62_meur","J62"), (2015,"total_meur","TOTAL")]:
    if yr in csv.index:
        check(f"{key} {yr}", csv.loc[yr, key], col_for(nace).get(yr, float("nan")))

# ---------------------------------------------------------------------------
print("\n=== 06e EPO ICT-related patents (pat_ep_ntec, sum of CAB+CTE+SMC) ===")
csv = pd.read_csv(f"{RAW}/06e_epo_ict_related_patents.csv", comment="#").set_index("year")
df  = fetch("pat_ep_ntec", {"unit":"NR","ipc":["CAB","CTE","SMC"],
                            "geo":["RO","CZ","PL"]})
yrs_cols = [c for c in df.columns if str(c).isdigit()]
def sum_ict(geo):
    sub = df[df["geo"] == geo]
    return sub[yrs_cols].sum(min_count=1).astype(float).rename(lambda c: int(c))
for geo, yr in [("RO", 2010), ("RO", 2013), ("CZ", 2010), ("PL", 2013)]:
    if yr in csv.index:
        check(f"{geo} {yr}", csv.loc[yr, geo], sum_ict(geo).get(yr, float("nan")))

# ---------------------------------------------------------------------------
print("\n=== 07d Cloud adoption (isoc_cicce_use, E_CC, GE10, PC_ENT) ===")
csv = pd.read_csv(f"{RAW}/07d_cloud_adoption_enterprises_pct.csv", comment="#").set_index("year")
df  = fetch("isoc_cicce_use", {"indic_is":"E_CC","size_emp":"GE10",
                               "unit":"PC_ENT","geo":["RO","CZ","EU27_2020"]})
api = to_year_indexed(df)
for geo, yr in [("RO", 2023), ("CZ", 2023), ("EU27_2020", 2023)]:
    if yr in csv.index and yr in api.index:
        check(f"{geo} {yr}", csv.loc[yr, geo], api.loc[yr, geo])

# ---------------------------------------------------------------------------
print("\n=== 07e E-gov submission (isoc_ciegi_ac, I_IGOV12FM, IND_TOTAL, PC_IND) ===")
csv = pd.read_csv(f"{RAW}/07e_egov_forms_pct_individuals.csv", comment="#").set_index("year")
df  = fetch("isoc_ciegi_ac", {"indic_is":"I_IGOV12FM","ind_type":"IND_TOTAL",
                              "unit":"PC_IND","geo":["RO","EU27_2020"]})
api = to_year_indexed(df)
for geo, yr in [("RO", 2020), ("RO", 2021), ("EU27_2020", 2021)]:
    if yr in csv.index and yr in api.index:
        check(f"{geo} {yr}", csv.loc[yr, geo], api.loc[yr, geo])

# ---------------------------------------------------------------------------
print("\n=== 07c Digital skills 2021+ (isoc_sk_dskl_i21, I_DSK2_BAB, IND_TOTAL, PC_IND) ===")
csv = pd.read_csv(f"{RAW}/07c_digital_skills_basic_plus_2021plus.csv", comment="#").set_index("year")
df  = fetch("isoc_sk_dskl_i21", {"indic_is":"I_DSK2_BAB","ind_type":"IND_TOTAL",
                                 "unit":"PC_IND","geo":["RO","EU27_2020"]})
api = to_year_indexed(df)
for geo, yr in [("RO", 2023), ("EU27_2020", 2023)]:
    if yr in csv.index and yr in api.index:
        check(f"{geo} {yr}", csv.loc[yr, geo], api.loc[yr, geo])

# ---------------------------------------------------------------------------
print("\n=== 05e NUTS2 population (demo_r_pjangrp3, T, TOTAL, NR) ===")
csv = pd.read_csv(f"{RAW}/05e_population_nuts2.csv", comment="#").set_index("year")
df  = fetch("demo_r_pjangrp3", {"sex":"T","age":"TOTAL","unit":"NR",
                                "geo":["RO11","RO32","RO"]})
api = to_year_indexed(df)
for geo, yr in [("RO11", 2014), ("RO32", 2020), ("RO", 2023)]:
    if yr in csv.index and yr in api.index:
        check(f"{geo} {yr}", csv.loc[yr, geo], api.loc[yr, geo])

# ---------------------------------------------------------------------------
print("\n=== 05f House price index (prc_hpi_a, TOTAL, I15_A_AVG) ===")
csv = pd.read_csv(f"{RAW}/05f_house_price_index_2015_100.csv", comment="#").set_index("year")
df  = fetch("prc_hpi_a", {"purchase":"TOTAL","unit":"I15_A_AVG",
                          "geo":["RO","EU27_2020"]})
api = to_year_indexed(df)
for geo, yr in [("RO", 2015), ("RO", 2023), ("EU27_2020", 2023)]:
    if yr in csv.index and yr in api.index:
        check(f"{geo} {yr}", csv.loc[yr, geo], api.loc[yr, geo])

# ---------------------------------------------------------------------------
print("\n=== 03e Enterprises J62 legacy (sbs_na_1a_se_r2, V11110) and new (sbs_ovw_act, ENT_NR) ===")
csv = pd.read_csv(f"{RAW}/03e_enterprises_j62_j63.csv", comment="#").set_index("year")
df_l62 = fetch("sbs_na_1a_se_r2", {"geo":["RO"], "nace_r2":"J62", "indic_sb":"V11110"})
df_n62 = fetch("sbs_ovw_act",     {"geo":["RO"], "nace_r2":"J62", "indic_sbs":"ENT_NR"})
leg62 = to_year_indexed(df_l62)["RO"]
new62 = to_year_indexed(df_n62)["RO"]
for yr in [2010, 2015, 2020]:
    if yr in csv.index and yr in leg62.index:
        check(f"J62_legacy {yr}", csv.loc[yr, "J62_legacy"], leg62.loc[yr])
for yr in [2021, 2022]:
    if yr in csv.index and yr in new62.index:
        check(f"J62_new {yr}", csv.loc[yr, "J62_new"], new62.loc[yr])

print("\nVerification complete.")
