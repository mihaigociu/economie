"""
Labor Market & Demographics: employment, wages, brain drain, population.
Sources: Eurostat, World Bank
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import matplotlib.pyplot as plt
import eurostat
import wbgapi as wb

OUTPUT   = "charts"
RAW_DATA = "raw-data"
import os; os.makedirs(OUTPUT, exist_ok=True); os.makedirs(RAW_DATA, exist_ok=True)

def wb_series(indicator, economies, year_range=(2000, 2025)):
    df = wb.data.DataFrame(indicator, economy=economies, time=range(*year_range))
    df = df.T
    df.index = df.index.str.replace("YR", "").astype(int)
    return df

def save_csv(df, name):
    path = f"{RAW_DATA}/{name}.csv"
    df.to_csv(path)
    print(f"  saved {path}")

PEERS = ["RO", "PL", "CZ", "HU", "BG"]
PEER_LABELS = {"RO": "Romania", "PL": "Poland", "CZ": "Czechia",
               "HU": "Hungary", "BG": "Bulgaria"}
COLORS = {"RO": "#c0392b", "PL": "#2980b9", "CZ": "#27ae60",
          "HU": "#8e44ad", "BG": "#e67e22"}
WB_CODES = ["ROU", "POL", "CZE", "HUN", "BGR"]
COL_MAP  = dict(zip(WB_CODES, PEERS))

# ---------------------------------------------------------------------------
# 1. Employment rate (15-64), annual
# ---------------------------------------------------------------------------
print("Fetching employment rates...")
try:
    df_emp = eurostat.get_data_df("lfsi_emp_a")
    mask = (
        (df_emp["indic_em"] == "EMP_LFS") &
        (df_emp["age"] == "Y15-64") &
        (df_emp["unit"] == "PC_POP") &
        (df_emp["sex"] == "T") &
        (df_emp["geo\\TIME_PERIOD"].isin(PEERS))
    )
    emp = df_emp[mask].set_index("geo\\TIME_PERIOD")
    year_cols = sorted([c for c in emp.columns if str(c).isdigit() and 2000 <= int(c) <= 2024])
    emp = emp[year_cols].T.astype(float)
    emp.index = emp.index.astype(int)
    emp.index.name = "year"
    save_csv(emp, "03a_employment_rate_pct")

    fig, ax = plt.subplots(figsize=(12, 5))
    for iso in PEERS:
        if iso in emp.columns:
            lw = 2.5 if iso == "RO" else 1.4
            ax.plot(emp.index, emp[iso], label=PEER_LABELS[iso],
                    color=COLORS[iso], linewidth=lw, marker="o", markersize=3)
    ax.set_title("Employment Rate, Ages 15–64 (%)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel("%")
    ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/03a_employment_rate.png", dpi=150); plt.close()
    print("  saved 03a_employment_rate.png")
except Exception as e:
    print(f"  employment chart error: {e}")

# ---------------------------------------------------------------------------
# 2. Unemployment rate + youth unemployment
# ---------------------------------------------------------------------------
print("Fetching unemployment rates...")
try:
    df_une = eurostat.get_data_df("une_rt_a")
    for age_group, suffix, title, csv_name in [
        ("Y15-74", "b_unemployment", "Unemployment Rate (%)",                 "03b_unemployment_rate_pct"),
        ("Y15-24", "c_youth_unemp",  "Youth Unemployment Rate, Ages 15–24 (%)", "03c_youth_unemployment_pct"),
    ]:
        mask = (
            (df_une["age"] == age_group) &
            (df_une["unit"] == "PC_ACT") &
            (df_une["sex"] == "T") &
            (df_une["geo\\TIME_PERIOD"].isin(PEERS))
        )
        une = df_une[mask].set_index("geo\\TIME_PERIOD")
        year_cols = sorted([c for c in une.columns if str(c).isdigit() and 2000 <= int(c) <= 2024])
        une = une[year_cols].T.astype(float)
        une.index = une.index.astype(int)
        une.index.name = "year"
        save_csv(une, csv_name)

        fig, ax = plt.subplots(figsize=(12, 5))
        for iso in PEERS:
            if iso in une.columns:
                lw = 2.5 if iso == "RO" else 1.4
                ax.plot(une.index, une[iso], label=PEER_LABELS[iso],
                        color=COLORS[iso], linewidth=lw, marker="o", markersize=3)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel("Year"); ax.set_ylabel("%")
        ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{OUTPUT}/03{suffix}.png", dpi=150); plt.close()
        print(f"  saved 03{suffix}.png")
except Exception as e:
    print(f"  unemployment chart error: {e}")

# ---------------------------------------------------------------------------
# 3. Labour cost index
# ---------------------------------------------------------------------------
print("Fetching wage/labour cost data...")
try:
    df_lc = eurostat.get_data_df("lc_lci_r2_a")
    mask = (
        (df_lc["nace_r2"] == "B-S") &
        (df_lc["lcstruct"] == "D11") &
        (df_lc["unit"] == "I20") &
        (df_lc["geo\\TIME_PERIOD"].isin(PEERS))
    )
    wages = df_lc[mask].set_index("geo\\TIME_PERIOD")
    year_cols = sorted([c for c in wages.columns if str(c).isdigit() and 2000 <= int(c) <= 2024])
    wages = wages[year_cols].T.astype(float)
    wages.index = wages.index.astype(int)
    wages.index.name = "year"
    save_csv(wages, "03d_labour_cost_index_2020_100")

    fig, ax = plt.subplots(figsize=(12, 5))
    for iso in PEERS:
        if iso in wages.columns:
            lw = 2.5 if iso == "RO" else 1.4
            ax.plot(wages.index, wages[iso], label=PEER_LABELS[iso],
                    color=COLORS[iso], linewidth=lw, marker="o", markersize=3)
    ax.set_title("Labour Cost Index (2020=100)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel("Index")
    ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/03d_wages.png", dpi=150); plt.close()
    print("  saved 03d_wages.png")
except Exception as e:
    print(f"  wages via Eurostat failed ({e}), using World Bank GNI proxy")
    gni = wb_series("NY.GNP.PCAP.CD", WB_CODES).rename(columns=COL_MAP)
    gni.index.name = "year"
    save_csv(gni, "03d_gni_per_capita_usd")
    fig, ax = plt.subplots(figsize=(12, 5))
    for iso in PEERS:
        if iso in gni.columns:
            lw = 2.5 if iso == "RO" else 1.4
            ax.plot(gni.index, gni[iso], label=PEER_LABELS[iso],
                    color=COLORS[iso], linewidth=lw, marker="o", markersize=3)
    ax.set_title("GNI per Capita, nominal USD (wage proxy)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel("USD")
    ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/03d_wages.png", dpi=150); plt.close()
    print("  saved 03d_wages.png (WB fallback)")

# ---------------------------------------------------------------------------
# 4. Population trend (index 1990=100) + absolute Romania
# ---------------------------------------------------------------------------
print("Fetching population data...")
pop = wb_series("SP.POP.TOTL", WB_CODES, (1990, 2025)).rename(columns=COL_MAP)
pop.index.name = "year"
save_csv(pop, "03e_population_total")

pop_norm = pop.div(pop.iloc[0]) * 100
pop_norm.index.name = "year"
save_csv(pop_norm, "03e_population_index_1990_100")

fig, ax = plt.subplots(figsize=(12, 5))
for iso in PEERS:
    if iso in pop_norm.columns:
        lw = 2.5 if iso == "RO" else 1.4
        ax.plot(pop_norm.index, pop_norm[iso], label=PEER_LABELS[iso],
                color=COLORS[iso], linewidth=lw, marker="o", markersize=2)
ax.axhline(100, color="black", linestyle="--", linewidth=0.8)
ax.set_title("Population Index (1990 = 100)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Index")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/03e_population.png", dpi=150); plt.close()
print("  saved 03e_population.png")

fig, ax = plt.subplots(figsize=(12, 4))
ro_pop = pop["RO"].dropna() / 1e6
ax.fill_between(ro_pop.index, ro_pop.values, alpha=0.3, color="#c0392b")
ax.plot(ro_pop.index, ro_pop.values, color="#c0392b", linewidth=2.5)
ax.set_title("Romania: Total Population (millions)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Millions")
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/03e2_romania_population.png", dpi=150); plt.close()
print("  saved 03e2_romania_population.png")

# ---------------------------------------------------------------------------
# 5. Remittances as % of GDP
# ---------------------------------------------------------------------------
print("Fetching remittances data...")
rem_codes = ["ROU", "POL", "BGR", "MDA", "PHL"]
rem_map   = {"ROU":"RO","POL":"PL","BGR":"BG","MDA":"MD","PHL":"PH"}
rem = wb_series("BX.TRF.PWKR.DT.GD.ZS", rem_codes).rename(columns=rem_map)
rem.index.name = "year"
save_csv(rem, "03f_remittances_pct_gdp")

labels_r = {"RO":"Romania","PL":"Poland","BG":"Bulgaria","MD":"Moldova","PH":"Philippines"}
colors_r = {"RO":"#c0392b","PL":"#2980b9","BG":"#e67e22","MD":"#8e44ad","PH":"#27ae60"}

fig, ax = plt.subplots(figsize=(12, 5))
for iso in rem.columns:
    if iso in labels_r:
        lw = 2.5 if iso == "RO" else 1.4
        ax.plot(rem.index, rem[iso], label=labels_r[iso],
                color=colors_r[iso], linewidth=lw, marker="o", markersize=3)
ax.set_title("Remittances Received (% of GDP)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/03f_remittances.png", dpi=150); plt.close()
print("  saved 03f_remittances.png")

# ---------------------------------------------------------------------------
# 6. Age dependency ratio
# ---------------------------------------------------------------------------
print("Fetching age dependency data...")
dep = wb_series("SP.POP.DPND", WB_CODES, (1990, 2025)).rename(columns=COL_MAP)
dep.index.name = "year"
save_csv(dep, "03g_age_dependency_ratio_pct")

fig, ax = plt.subplots(figsize=(12, 5))
for iso in PEERS:
    if iso in dep.columns:
        lw = 2.5 if iso == "RO" else 1.4
        ax.plot(dep.index, dep[iso], label=PEER_LABELS[iso],
                color=COLORS[iso], linewidth=lw, marker="o", markersize=2)
ax.set_title("Age Dependency Ratio (% of working-age population)",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("%")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/03g_dependency_ratio.png", dpi=150); plt.close()
print("  saved 03g_dependency_ratio.png")

print("\nDone — labor & demographics charts and CSVs saved.")
