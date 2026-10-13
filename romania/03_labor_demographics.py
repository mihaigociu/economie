"""
Labor Market & Demographics: employment, wages, brain drain, population.
Sources: Eurostat (lfsi_emp_a, une_rt_a, lc_lci_r2_a), World Bank (population,
remittances, dependency ratio, agricultural employment share)
"""

import matplotlib.pyplot as plt

from common import (OUTPUT, PEERS, PEER_LABELS, COLORS, WB_CODES, WB_MAP, save_csv,
                    wb_series, eurostat_wide, plot_peers, es_url, wb_url, year_span)

LAST_YEAR = 2025
FIRST_YEAR = 2000


def line_chart(df, title, ylabel, fname, ms=3):
    fig, ax = plt.subplots(figsize=(12, 5))
    plot_peers(ax, df, markersize=ms)
    ax.set_title(f"{title}, {year_span(df)}", fontsize=14, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel(ylabel)
    ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/{fname}", dpi=150); plt.close()
    print(f"  saved {fname}")
    return ax


# ---------------------------------------------------------------------------
# 1. Employment rate (15-64), annual
# ---------------------------------------------------------------------------
print("Fetching employment rates...")
emp = eurostat_wide("lfsi_emp_a", {"indic_em": "EMP_LFS", "age": "Y15-64", "unit": "PC_POP",
                                   "sex": "T"}, PEERS, FIRST_YEAR, LAST_YEAR)
save_csv(emp, "03a_employment_rate_pct",
         "Eurostat lfsi_emp_a — employment rate, ages 15-64, % of population (LFS)", es_url("lfsi_emp_a"))
line_chart(emp, "Employment Rate, Ages 15–64 (%)", "%", "03a_employment_rate.png")

# ---------------------------------------------------------------------------
# 2. Unemployment rate + youth unemployment
# ---------------------------------------------------------------------------
print("Fetching unemployment rates...")
for age_group, fname, title, csv_name in [
    ("Y15-74", "03b_unemployment.png", "Unemployment Rate, Ages 15–74 (%)", "03b_unemployment_rate_pct"),
    ("Y15-24", "03c_youth_unemp.png", "Youth Unemployment Rate, Ages 15–24 (%)", "03c_youth_unemployment_pct"),
]:
    une = eurostat_wide("une_rt_a", {"age": age_group, "unit": "PC_ACT", "sex": "T"},
                        PEERS, FIRST_YEAR, LAST_YEAR)
    save_csv(une, csv_name,
             f"Eurostat une_rt_a — unemployment rate, ages {age_group}, % of active population",
             es_url("une_rt_a"))
    line_chart(une, title, "%", fname)

# ---------------------------------------------------------------------------
# 3. Labour cost index (wages and salaries)
# ---------------------------------------------------------------------------
print("Fetching labour cost index...")
wages = eurostat_wide("lc_lci_r2_a", {"nace_r2": "B-S", "lcstruct": "D11", "unit": "I20"},
                      PEERS, FIRST_YEAR, LAST_YEAR)
save_csv(wages, "03d_labour_cost_index_2020_100",
         "Eurostat lc_lci_r2_a — labour cost index, wages and salaries (D11), business economy B-S, 2020=100, nominal national currency",
         es_url("lc_lci_r2_a"))
line_chart(wages, "Labour Cost Index, Wages & Salaries (2020 = 100, national currency)",
           "Index", "03d_wages.png")

# ---------------------------------------------------------------------------
# 4. Population trend (index 1990=100) + absolute Romania
# ---------------------------------------------------------------------------
print("Fetching population data...")
pop = wb_series("SP.POP.TOTL", WB_CODES, 1990, LAST_YEAR, WB_MAP)
save_csv(pop, "03e_population_total",
         "World Bank WDI SP.POP.TOTL — population, total (mid-year)", wb_url("SP.POP.TOTL"))

pop_norm = pop.div(pop.loc[1990]) * 100
save_csv(pop_norm, "03e_population_index_1990_100",
         "Derived from World Bank WDI SP.POP.TOTL — population index, 1990 = 100",
         wb_url("SP.POP.TOTL"))
line_chart(pop_norm, "Population Index (1990 = 100)", "Index", "03e_population.png", ms=2)

fig, ax = plt.subplots(figsize=(12, 4))
ro_pop = pop["RO"].dropna() / 1e6
ax.fill_between(ro_pop.index, ro_pop.values, alpha=0.3, color="#c0392b")
ax.plot(ro_pop.index, ro_pop.values, color="#c0392b", linewidth=2.5)
for y in (ro_pop.index[0], ro_pop.index[-1]):
    ax.annotate(f"{ro_pop[y]:.2f}m", (y, ro_pop[y]), xytext=(0, 6), textcoords="offset points",
                ha="left" if y == ro_pop.index[0] else "right", fontsize=9, fontweight="bold")
ax.set_ylim(0, ro_pop.max() * 1.12)
ax.set_title(f"Romania: Total Population (millions), {year_span(ro_pop)}",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Millions")
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/03e2_romania_population.png", dpi=150); plt.close()
print("  saved 03e2_romania_population.png")

# ---------------------------------------------------------------------------
# 5. Remittances as % of GDP
# ---------------------------------------------------------------------------
print("Fetching remittances data...")
rem_map = {"ROU": "RO", "POL": "PL", "BGR": "BG", "MDA": "MD", "PHL": "PH"}
rem = wb_series("BX.TRF.PWKR.DT.GD.ZS", list(rem_map), FIRST_YEAR, LAST_YEAR, rem_map)
save_csv(rem, "03f_remittances_pct_gdp",
         "World Bank WDI BX.TRF.PWKR.DT.GD.ZS — personal remittances received, % of GDP",
         wb_url("BX.TRF.PWKR.DT.GD.ZS"))
labels_r = {"RO": "Romania", "PL": "Poland", "BG": "Bulgaria", "MD": "Moldova", "PH": "Philippines"}
colors_r = {"RO": "#c0392b", "PL": "#2980b9", "BG": "#e67e22", "MD": "#8e44ad", "PH": "#27ae60"}
fig, ax = plt.subplots(figsize=(12, 5))
plot_peers(ax, rem, labels=labels_r, colors=colors_r)
ax.set_title(f"Personal Remittances Received (% of GDP), {year_span(rem)}",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/03f_remittances.png", dpi=150); plt.close()
print("  saved 03f_remittances.png")

# ---------------------------------------------------------------------------
# 6. Age dependency ratio
# ---------------------------------------------------------------------------
print("Fetching age dependency data...")
dep = wb_series("SP.POP.DPND", WB_CODES, 1990, LAST_YEAR, WB_MAP)
save_csv(dep, "03g_age_dependency_ratio_pct",
         "World Bank WDI SP.POP.DPND — age dependency ratio, % of working-age population (15-64)",
         wb_url("SP.POP.DPND"))
line_chart(dep, "Age Dependency Ratio (% of working-age population)", "%",
           "03g_dependency_ratio.png", ms=2)

# ---------------------------------------------------------------------------
# 7. Employment in agriculture (% of total employment) — data only, used in text
# ---------------------------------------------------------------------------
print("Fetching agricultural employment share...")
agr = wb_series("SL.AGR.EMPL.ZS", WB_CODES + ["EUU"], FIRST_YEAR, LAST_YEAR,
                {**WB_MAP, "EUU": "EU"})
save_csv(agr, "03h_agriculture_employment_pct",
         "World Bank WDI SL.AGR.EMPL.ZS — employment in agriculture, % of total employment (modeled ILO estimate)",
         wb_url("SL.AGR.EMPL.ZS"))

print("\nDone — labor & demographics charts and CSVs saved.")
