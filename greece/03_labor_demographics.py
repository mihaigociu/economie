"""
Labor Market & Demographics: employment, unemployment, internal-devaluation wages,
population, brain drain, age dependency, fertility.
Sources: Eurostat (lfsi_emp_a, une_rt_a, lc_lci_r2_a, demo_gind, demo_find), World Bank
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

# Eurostat codes (EL = Greece)
PEERS = ["EL", "PT", "IT", "ES", "CY"]
PEER_LABELS = {"EL": "Greece", "PT": "Portugal", "IT": "Italy",
               "ES": "Spain", "CY": "Cyprus"}
COLORS = {"EL": "#c0392b", "PT": "#e67e22", "IT": "#27ae60",
          "ES": "#2980b9", "CY": "#8e44ad"}
WB_CODES = ["GRC", "PRT", "ITA", "ESP", "CYP"]
WB_TO_EU = dict(zip(WB_CODES, PEERS))

PROG_START, PROG_END = 2010, 2018

def add_programme_shading(ax, label_y_frac=0.92):
    ax.axvspan(PROG_START, PROG_END, alpha=0.06, color="grey")
    ylim = ax.get_ylim()
    y = ylim[0] + (ylim[1] - ylim[0]) * label_y_frac
    ax.text((PROG_START + PROG_END) / 2, y, "Adjustment programmes\n2010-2018",
            ha="center", fontsize=8, color="#555")

def plot_peer_lines(ax, df, title, ylabel, highlight="EL", marker_size=3):
    for iso in PEERS:
        if iso in df.columns:
            lw = 2.5 if iso == highlight else 1.4
            ax.plot(df.index, df[iso], label=PEER_LABELS[iso],
                    color=COLORS[iso], linewidth=lw, marker="o", markersize=marker_size)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel(ylabel)
    ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)

# ---------------------------------------------------------------------------
# 1. Employment rate (15-64)
# ---------------------------------------------------------------------------
print("Fetching employment rates...")
df_emp = eurostat.get_data_df("lfsi_emp_a")
mask = ((df_emp["indic_em"] == "EMP_LFS") & (df_emp["age"] == "Y15-64") &
        (df_emp["unit"] == "PC_POP") & (df_emp["sex"] == "T") &
        (df_emp["geo\\TIME_PERIOD"].isin(PEERS)))
emp = df_emp[mask].set_index("geo\\TIME_PERIOD")
year_cols = sorted([c for c in emp.columns if str(c).isdigit() and 2000 <= int(c) <= 2024])
emp = emp[year_cols].T.astype(float)
emp.index = emp.index.astype(int); emp.index.name = "year"
save_csv(emp, "03a_employment_rate_pct")

fig, ax = plt.subplots(figsize=(12, 5))
plot_peer_lines(ax, emp, "Employment Rate, Ages 15–64 (%)", "%")
add_programme_shading(ax)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/03a_employment_rate.png", dpi=150); plt.close()
print("  saved 03a_employment_rate.png")

# ---------------------------------------------------------------------------
# 2. Unemployment rate (with depression-era spike)
# ---------------------------------------------------------------------------
print("Fetching unemployment rates...")
df_une = eurostat.get_data_df("une_rt_a")

for age_group, suffix, title, csv_name in [
    ("Y15-74", "b_unemployment", "Unemployment Rate (%)",                   "03b_unemployment_rate_pct"),
    ("Y15-24", "c_youth_unemp",  "Youth Unemployment Rate, Ages 15–24 (%)", "03c_youth_unemployment_pct"),
]:
    mask = ((df_une["age"] == age_group) & (df_une["unit"] == "PC_ACT") &
            (df_une["sex"] == "T") & (df_une["geo\\TIME_PERIOD"].isin(PEERS)))
    une = df_une[mask].set_index("geo\\TIME_PERIOD")
    year_cols = sorted([c for c in une.columns if str(c).isdigit() and 2000 <= int(c) <= 2024])
    une = une[year_cols].T.astype(float)
    une.index = une.index.astype(int); une.index.name = "year"
    save_csv(une, csv_name)

    fig, ax = plt.subplots(figsize=(12, 5))
    plot_peer_lines(ax, une, title, "%")
    add_programme_shading(ax, label_y_frac=0.08)
    # Annotate Greek peak — place label below the peak to avoid colliding with title
    if "EL" in une.columns:
        peak = une["EL"].dropna().idxmax()
        peak_val = une["EL"][peak]
        ax.annotate(f"Peak: {peak_val:.0f}% ({int(peak)})",
                    xy=(peak, peak_val), xytext=(peak + 2, peak_val - 4),
                    fontsize=9, ha="left", color=COLORS["EL"], fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=COLORS["EL"], lw=0.8))
    plt.tight_layout(); plt.savefig(f"{OUTPUT}/03{suffix}.png", dpi=150); plt.close()
    print(f"  saved 03{suffix}.png")

# ---------------------------------------------------------------------------
# 3. Labour cost index (internal devaluation chart)
# ---------------------------------------------------------------------------
print("Fetching labour cost index...")
df_lc = eurostat.get_data_df("lc_lci_r2_a")
mask = ((df_lc["nace_r2"] == "B-S") & (df_lc["lcstruct"] == "D11") &
        (df_lc["unit"] == "I20") & (df_lc["geo\\TIME_PERIOD"].isin(PEERS)))
wages = df_lc[mask].set_index("geo\\TIME_PERIOD")
year_cols = sorted([c for c in wages.columns if str(c).isdigit() and 2000 <= int(c) <= 2024])
wages = wages[year_cols].T.astype(float)
wages.index = wages.index.astype(int); wages.index.name = "year"
save_csv(wages, "03d_labour_cost_index_2020_100")

fig, ax = plt.subplots(figsize=(12, 5))
plot_peer_lines(ax, wages, "Labour Cost Index — Wages & Salaries, NACE B-S (2020 = 100)", "Index")
add_programme_shading(ax)
# Annotate Greek peak-to-trough during internal devaluation
if "EL" in wages.columns:
    el = wages["EL"].dropna()
    if not el.empty:
        peak_yr = el.loc[:2012].idxmax()
        trough_yr = el.loc[2010:2018].idxmin()
        drop = (el[peak_yr] - el[trough_yr]) / el[peak_yr] * 100
        ax.annotate(f"Internal devaluation:\n−{drop:.0f}% wages\n({int(peak_yr)}→{int(trough_yr)})",
                    xy=(trough_yr, el[trough_yr]),
                    xytext=(trough_yr + 1, el[trough_yr] - 10),
                    fontsize=9, ha="left", color=COLORS["EL"], fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=COLORS["EL"], lw=0.8))
plt.tight_layout(); plt.savefig(f"{OUTPUT}/03d_wages.png", dpi=150); plt.close()
print("  saved 03d_wages.png")

# ---------------------------------------------------------------------------
# 4. Population trend (peer index + Greek absolute)
# ---------------------------------------------------------------------------
print("Fetching population data...")
pop = wb_series("SP.POP.TOTL", WB_CODES, (2000, 2025)).rename(columns=WB_TO_EU)
pop.index.name = "year"
save_csv(pop, "03e_population_total")

pop_norm = pop.div(pop.iloc[0]) * 100
pop_norm.index.name = "year"
save_csv(pop_norm, "03e_population_index_2000_100")

fig, ax = plt.subplots(figsize=(12, 5))
plot_peer_lines(ax, pop_norm, "Population Index (2000 = 100)", "Index", marker_size=2)
ax.axhline(100, color="black", linestyle="--", linewidth=0.8)
add_programme_shading(ax, label_y_frac=0.05)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/03e_population.png", dpi=150); plt.close()
print("  saved 03e_population.png")

# Greek absolute population in millions — zoomed y-axis to show actual decline
fig, ax = plt.subplots(figsize=(12, 4.5))
el_pop = pop["EL"].dropna() / 1e6
y_min = el_pop.min() - 0.15
y_max = el_pop.max() + 0.15
ax.fill_between(el_pop.index, el_pop.values, y_min, alpha=0.25, color=COLORS["EL"])
ax.plot(el_pop.index, el_pop.values, color=COLORS["EL"], linewidth=2.5, marker="o", markersize=4)
peak = el_pop.idxmax(); last = el_pop.index.max()
decline_pct = (el_pop[peak] - el_pop[last]) / el_pop[peak] * 100
ax.annotate(f"Peak: {el_pop[peak]:.2f}m ({int(peak)})",
            xy=(peak, el_pop[peak]),
            xytext=(peak - 4, el_pop[peak] + 0.03),
            fontsize=9, ha="left", color=COLORS["EL"], fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=COLORS["EL"], lw=0.8))
ax.annotate(f"{int(last)}: {el_pop[last]:.2f}m  (−{decline_pct:.1f}% from peak)",
            xy=(last, el_pop[last]),
            xytext=(last - 7, el_pop[last] - 0.08),
            fontsize=9, ha="left", color=COLORS["EL"], fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=COLORS["EL"], lw=0.8))
ax.set_ylim(y_min, y_max)
ax.set_title("Greece: Total Population (millions)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Millions"); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/03e2_greece_population.png", dpi=150); plt.close()
print("  saved 03e2_greece_population.png")

# ---------------------------------------------------------------------------
# 5. Net migration crude rate (brain drain story)
# ---------------------------------------------------------------------------
print("Fetching net migration data...")
df_mig = eurostat.get_data_df("demo_gind")
mask = ((df_mig["indic_de"] == "CNMIGRATRT") &
        (df_mig["geo\\TIME_PERIOD"].isin(PEERS)))
mig = df_mig[mask].set_index("geo\\TIME_PERIOD")
year_cols = sorted([c for c in mig.columns if str(c).isdigit() and 2000 <= int(c) <= 2024])
mig = mig[year_cols].T.astype(float)
mig.index = mig.index.astype(int); mig.index.name = "year"
save_csv(mig, "03f_net_migration_crude_rate")

fig, ax = plt.subplots(figsize=(12, 5))
for iso in PEERS:
    if iso in mig.columns:
        lw = 2.5 if iso == "EL" else 1.4
        ax.plot(mig.index, mig[iso], label=PEER_LABELS[iso],
                color=COLORS[iso], linewidth=lw, marker="o", markersize=3)
ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax.fill_between(mig.index, mig.get("EL", pd.Series()), 0,
                where=mig.get("EL", pd.Series()) < 0,
                alpha=0.12, color=COLORS["EL"], label="Greek net outflow")
add_programme_shading(ax, label_y_frac=0.08)
ax.set_title("Crude Rate of Net Migration (per 1,000 inhabitants)",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("per 1,000")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/03f_net_migration.png", dpi=150); plt.close()
print("  saved 03f_net_migration.png")

# ---------------------------------------------------------------------------
# 6. Age dependency ratio
# ---------------------------------------------------------------------------
print("Fetching age dependency ratio...")
dep = wb_series("SP.POP.DPND", WB_CODES, (2000, 2025)).rename(columns=WB_TO_EU)
dep.index.name = "year"
save_csv(dep, "03g_age_dependency_ratio_pct")

fig, ax = plt.subplots(figsize=(12, 5))
plot_peer_lines(ax, dep, "Age Dependency Ratio (% of working-age population)", "%", marker_size=2)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/03g_dependency_ratio.png", dpi=150); plt.close()
print("  saved 03g_dependency_ratio.png")

# ---------------------------------------------------------------------------
# 7. Total fertility rate
# ---------------------------------------------------------------------------
print("Fetching fertility rate...")
df_fer = eurostat.get_data_df("demo_find")
mask = ((df_fer["indic_de"] == "TOTFERRT") &
        (df_fer["geo\\TIME_PERIOD"].isin(PEERS + ["EU27_2020"])))
fer = df_fer[mask].set_index("geo\\TIME_PERIOD")
year_cols = sorted([c for c in fer.columns if str(c).isdigit() and 2000 <= int(c) <= 2024])
fer = fer[year_cols].T.astype(float)
fer.index = fer.index.astype(int); fer.index.name = "year"
save_csv(fer, "03h_total_fertility_rate")

fig, ax = plt.subplots(figsize=(12, 5))
for iso in PEERS:
    if iso in fer.columns:
        lw = 2.5 if iso == "EL" else 1.4
        ax.plot(fer.index, fer[iso], label=PEER_LABELS[iso],
                color=COLORS[iso], linewidth=lw, marker="o", markersize=3)
if "EU27_2020" in fer.columns:
    ax.plot(fer.index, fer["EU27_2020"], label="EU27",
            color="#7f8c8d", linewidth=1.4, linestyle="--", marker="o", markersize=3)
ax.axhline(2.1, color="red", linestyle=":", linewidth=1.0, alpha=0.6, label="Replacement rate (2.1)")
ax.set_title("Total Fertility Rate (live births per woman)",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Births per woman")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/03h_fertility.png", dpi=150); plt.close()
print("  saved 03h_fertility.png")

print("\nDone — labor & demographics charts and CSVs saved.")
