"""
Public Finances: budget deficit, public debt, revenue & spending structure.
Sources: Eurostat (gov_10dd_edpt1 — EDP notification data, gov_10a_taxag, gov_10a_main)

Deficit and debt come from the EDP notification tables. Eurostat publishes
these each April and October (the October 2026 notification is due ~21–22 Oct
2026); simply re-running this script picks up the revised figures.
"""

import pandas as pd
import matplotlib.pyplot as plt

from common import (OUTPUT, PEERS, PEER_LABELS, COLORS, save_csv, eurostat_wide,
                    plot_peers, es_url, year_span)

LAST_YEAR = 2025
FIRST_YEAR = 2000

# ---------------------------------------------------------------------------
# 1. General government balance (% GDP) — EDP notification
# ---------------------------------------------------------------------------
print("Fetching government deficit data (gov_10dd_edpt1)...")
deficit = eurostat_wide("gov_10dd_edpt1", {"na_item": "B9", "unit": "PC_GDP", "sector": "S13"},
                        PEERS, FIRST_YEAR, LAST_YEAR)
save_csv(deficit, "02a_govt_balance_pct_gdp",
         "Eurostat gov_10dd_edpt1 — general government net lending (+)/borrowing (-), B9, S13, % of GDP (EDP notification)",
         es_url("gov_10dd_edpt1"),
         ["latest year is from the most recent EDP notification and is revised each April/October"])

fig, ax = plt.subplots(figsize=(13, 5))
plot_peers(ax, deficit)
ax.axhline(-3, color="red", linestyle="--", linewidth=1.2, alpha=0.7, label="Maastricht −3% limit")
ax.axhline(0, color="black", linewidth=0.8)
ro = deficit["RO"]
ax.fill_between(deficit.index, ro, -3, where=ro < -3, alpha=0.12, color="red",
                label="RO breach zone", interpolate=True)
ax.set_title(f"General Government Balance (% of GDP), {year_span(deficit)}",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
ax.legend(ncol=7, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.13), frameon=False)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/02a_deficit.png", dpi=150); plt.close()
print("  saved 02a_deficit.png")

# ---------------------------------------------------------------------------
# 2. Public debt (% GDP) — EDP notification
# ---------------------------------------------------------------------------
print("Fetching public debt data (gov_10dd_edpt1)...")
debt = eurostat_wide("gov_10dd_edpt1", {"na_item": "GD", "unit": "PC_GDP", "sector": "S13"},
                     PEERS, FIRST_YEAR, LAST_YEAR)
save_csv(debt, "02b_public_debt_pct_gdp",
         "Eurostat gov_10dd_edpt1 — general government gross (Maastricht) debt, GD, S13, % of GDP (EDP notification)",
         es_url("gov_10dd_edpt1"),
         ["latest year is from the most recent EDP notification and is revised each April/October"])

fig, ax = plt.subplots(figsize=(13, 5))
plot_peers(ax, debt)
ax.axhline(60, color="red", linestyle="--", linewidth=1.2, alpha=0.7, label="Maastricht 60% limit")
ax.set_title(f"General Government Gross Debt (% of GDP), {year_span(debt)}",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
ax.legend(ncol=3, fontsize=9, loc="upper left"); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/02b_debt.png", dpi=150); plt.close()
print("  saved 02b_debt.png")

# ---------------------------------------------------------------------------
# 3. Tax revenue (incl. social contributions) as % GDP — Romania vs EU
# ---------------------------------------------------------------------------
print("Fetching tax revenue data (gov_10a_taxag)...")
TAX_GEOS = ["RO", "PL", "CZ", "HU", "BG", "SK", "AT", "DE", "FR", "SE", "EU27_2020"]
labels_map = {"RO": "Romania", "PL": "Poland", "CZ": "Czechia", "HU": "Hungary",
              "BG": "Bulgaria", "SK": "Slovakia", "AT": "Austria", "DE": "Germany",
              "FR": "France", "SE": "Sweden", "EU27_2020": "EU27"}
tax_ts = eurostat_wide("gov_10a_taxag",
                       {"na_item": "D2_D5_D91_D61_M_D995", "unit": "PC_GDP", "sector": "S13"},
                       TAX_GEOS, FIRST_YEAR, LAST_YEAR)
save_csv(tax_ts, "02c_tax_revenue_pct_gdp",
         "Eurostat gov_10a_taxag — total receipts from taxes and social contributions after deduction of amounts assessed but unlikely to be collected (D2_D5_D91_D61_M_D995), S13, % of GDP",
         es_url("gov_10a_taxag"))

# latest year with at least 8 of the 11 countries reported
latest = max(y for y in tax_ts.index if tax_ts.loc[y].notna().sum() >= 8)
tax_latest = tax_ts.loc[latest].dropna().sort_values()
bar_colors = ["#c0392b" if i == "RO" else "#7f8c8d" if i == "EU27_2020" else "#95a5a6"
              for i in tax_latest.index]
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.barh([labels_map.get(i, i) for i in tax_latest.index], tax_latest.values, color=bar_colors)
for b, v in zip(bars, tax_latest.values):
    ax.text(v + 0.3, b.get_y() + b.get_height() / 2, f"{v:.1f}", va="center", fontsize=9)
ax.set_xlim(0, tax_latest.max() * 1.1)
ax.set_title(f"Taxes and Social Contributions (% of GDP), {latest}", fontsize=14, fontweight="bold")
ax.set_xlabel("% of GDP"); ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/02c_tax_revenue.png", dpi=150); plt.close()
print(f"  saved 02c_tax_revenue.png (year {latest})")

# ---------------------------------------------------------------------------
# 4. Government expenditure vs revenue (Romania)
# ---------------------------------------------------------------------------
print("Fetching revenue/expenditure for Romania (gov_10a_main)...")
items = {"TE": "Total Expenditure", "TR": "Total Revenue"}
rev_exp = pd.DataFrame({
    label: eurostat_wide("gov_10a_main", {"na_item": code, "unit": "PC_GDP", "sector": "S13"},
                         ["RO"], FIRST_YEAR, LAST_YEAR)["RO"]
    for code, label in items.items()
})
rev_exp.index.name = "year"
save_csv(rev_exp, "02d_romania_revenue_expenditure_pct_gdp",
         "Eurostat gov_10a_main — Romania general government total expenditure (TE) and total revenue (TR), S13, % of GDP",
         es_url("gov_10a_main"))

fig, ax = plt.subplots(figsize=(13, 5))
ax.plot(rev_exp.index, rev_exp["Total Expenditure"], label="Total Expenditure",
        color="#c0392b", linewidth=2, marker="o", markersize=3)
ax.plot(rev_exp.index, rev_exp["Total Revenue"], label="Total Revenue",
        color="#27ae60", linewidth=2, marker="o", markersize=3)
ax.fill_between(rev_exp.index, rev_exp["Total Revenue"], rev_exp["Total Expenditure"],
                where=rev_exp["Total Expenditure"] > rev_exp["Total Revenue"],
                alpha=0.15, color="red", label="Deficit area", interpolate=True)
ax.set_title(f"Romania: Government Revenue vs Expenditure (% of GDP), {year_span(rev_exp)}",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
ax.legend(fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/02d_rev_vs_exp.png", dpi=150); plt.close()
print("  saved 02d_rev_vs_exp.png")

# ---------------------------------------------------------------------------
# 5. Old-age (pension) expenditure, COFOG GF1002 — data only, used in text
# ---------------------------------------------------------------------------
print("Fetching old-age expenditure (gov_10a_exp, GF1002)...")
old_age = eurostat_wide("gov_10a_exp", {"cofog99": "GF1002", "na_item": "TE", "unit": "PC_GDP",
                                        "sector": "S13"},
                        PEERS + ["EU27_2020"], FIRST_YEAR, LAST_YEAR)
save_csv(old_age, "02e_old_age_expenditure_pct_gdp",
         "Eurostat gov_10a_exp — general government total expenditure on old age (COFOG GF1002), % of GDP",
         es_url("gov_10a_exp"))

print("\nDone — public finance charts and CSVs saved.")
