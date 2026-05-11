"""
Public Finances: budget balance, public debt, primary balance, debt composition,
tax revenue, revenue vs expenditure.
Sources: Eurostat (gov_10dd_edpt1, gov_10a_main, gov_10a_taxag)

Note: Eurostat uses "EL" for Greece (not the ISO "GR" used by the World Bank).
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import matplotlib.pyplot as plt
import eurostat

OUTPUT   = "charts"
RAW_DATA = "raw-data"
import os; os.makedirs(OUTPUT, exist_ok=True); os.makedirs(RAW_DATA, exist_ok=True)

def save_csv(df, name):
    path = f"{RAW_DATA}/{name}.csv"
    df.to_csv(path)
    print(f"  saved {path}")

# Eurostat country codes (note: Greece = EL, not GR)
PEERS = ["EL", "PT", "IT", "ES", "CY"]
PEER_LABELS = {"EL": "Greece", "PT": "Portugal", "IT": "Italy",
               "ES": "Spain", "CY": "Cyprus"}
COLORS = {"EL": "#c0392b", "PT": "#e67e22", "IT": "#27ae60",
          "ES": "#2980b9", "CY": "#8e44ad"}

# Programme period shading bounds (approx: first MoU May 2010 → exit August 2018)
PROG_START, PROG_END = 2010, 2018

def add_programme_shading(ax, label_y_frac=0.92):
    ax.axvspan(PROG_START, PROG_END, alpha=0.06, color="grey")
    ylim = ax.get_ylim()
    y = ylim[0] + (ylim[1] - ylim[0]) * label_y_frac
    ax.text((PROG_START + PROG_END) / 2, y, "Adjustment programmes\n2010-2018",
            ha="center", fontsize=8, color="#555")

def fetch_edp(na_item, geos, unit="PC_GDP", sector="S13"):
    df = eurostat.get_data_df("gov_10dd_edpt1")
    mask = ((df["na_item"] == na_item) & (df["unit"] == unit) &
            (df["sector"] == sector) & (df["geo\\TIME_PERIOD"].isin(geos)))
    sub = df[mask].set_index("geo\\TIME_PERIOD")
    year_cols = [c for c in sub.columns if str(c).isdigit() and 2000 <= int(c) <= 2024]
    out = sub[year_cols].T.astype(float)
    out.index = out.index.astype(int)
    out.index.name = "year"
    return out

# ---------------------------------------------------------------------------
# 1. General government balance (% GDP) — Greece vs southern peers
# ---------------------------------------------------------------------------
print("Fetching government balance...")
balance = fetch_edp("B9", PEERS)
save_csv(balance, "02a_govt_balance_pct_gdp")

fig, ax = plt.subplots(figsize=(13, 5))
for iso in PEERS:
    if iso in balance.columns:
        lw = 2.5 if iso == "EL" else 1.4
        ax.plot(balance.index, balance[iso], label=PEER_LABELS[iso],
                color=COLORS[iso], linewidth=lw, marker="o", markersize=3)
ax.axhline(-3, color="red", linestyle="--", linewidth=1.2, alpha=0.7, label="Maastricht −3% limit")
ax.axhline(0, color="black", linewidth=0.8)
add_programme_shading(ax)
ax.set_title("General Government Balance (% of GDP)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
ax.legend(ncol=3, fontsize=9, loc="lower right"); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/02a_deficit.png", dpi=150); plt.close()
print("  saved 02a_deficit.png")

# ---------------------------------------------------------------------------
# 2. Public debt (% GDP) — Greece vs peers
# ---------------------------------------------------------------------------
print("Fetching public debt...")
debt = fetch_edp("GD", PEERS)
save_csv(debt, "02b_public_debt_pct_gdp")

fig, ax = plt.subplots(figsize=(13, 5))
for iso in PEERS:
    if iso in debt.columns:
        lw = 2.5 if iso == "EL" else 1.4
        ax.plot(debt.index, debt[iso], label=PEER_LABELS[iso],
                color=COLORS[iso], linewidth=lw, marker="o", markersize=3)
ax.axhline(60, color="red", linestyle="--", linewidth=1.2, alpha=0.7, label="Maastricht 60% limit")
add_programme_shading(ax, label_y_frac=0.05)
# Annotate PSI 2012 on Greek line
if "EL" in debt.columns:
    el_series = debt["EL"].dropna()
    if 2012 in el_series.index:
        ax.annotate("PSI haircut\n(2012)", xy=(2012, el_series[2012]),
                    xytext=(2009, el_series[2012] + 25),
                    fontsize=8, ha="center", color=COLORS["EL"],
                    arrowprops=dict(arrowstyle="->", color=COLORS["EL"], lw=0.8))
    peak_year = el_series.idxmax()
    ax.annotate(f"Peak: {el_series[peak_year]:.0f}% ({int(peak_year)})",
                xy=(peak_year, el_series[peak_year]),
                xytext=(peak_year + 1.5, el_series[peak_year] + 5),
                fontsize=8, ha="left", color=COLORS["EL"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["EL"], lw=0.8))
ax.set_title("General Government Gross Debt (% of GDP)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
ax.legend(ncol=3, fontsize=9, loc="lower right"); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/02b_debt.png", dpi=150); plt.close()
print("  saved 02b_debt.png")

# ---------------------------------------------------------------------------
# 3. Primary vs headline balance for Greece — the austerity story
# ---------------------------------------------------------------------------
# Primary balance = headline balance + interest payments. D41PAY is interest paid.
print("Fetching primary balance components...")
balance_el = fetch_edp("B9", ["EL"])["EL"]
interest_el = fetch_edp("D41PAY", ["EL"])["EL"]
primary_el = (balance_el + interest_el).dropna()

prim_df = pd.DataFrame({
    "Headline balance": balance_el,
    "Interest paid":    interest_el,
    "Primary balance":  primary_el,
})
prim_df.index.name = "year"
save_csv(prim_df, "02c_primary_balance_greece")

fig, ax = plt.subplots(figsize=(13, 5))
ax.plot(balance_el.index, balance_el.values, label="Headline balance",
        color="#c0392b", linewidth=2.5, marker="o", markersize=3)
ax.plot(primary_el.index, primary_el.values, label="Primary balance",
        color="#27ae60", linewidth=2.5, marker="o", markersize=3)
ax.fill_between(primary_el.index, primary_el.values, 0,
                where=primary_el.values > 0, alpha=0.15, color="#27ae60",
                label="Primary surplus zone")
ax.axhline(0, color="black", linewidth=0.8)
ax.axhline(-3, color="red", linestyle="--", linewidth=1.0, alpha=0.6, label="Maastricht −3% (headline)")
add_programme_shading(ax, label_y_frac=0.02)
ax.set_title("Greece: Primary vs Headline Government Balance (% of GDP)",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
ax.legend(ncol=2, fontsize=9, loc="lower right"); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/02c_primary_balance.png", dpi=150); plt.close()
print("  saved 02c_primary_balance.png")

# ---------------------------------------------------------------------------
# 4. Debt composition by instrument — Greece's distinctive structure
# ---------------------------------------------------------------------------
# F2: currency and deposits | F3: debt securities (market) | F4: loans (official sector)
print("Fetching debt composition...")
comp_codes = {"Currency & deposits": "GD_F2",
              "Debt securities (market)": "GD_F3",
              "Loans (mainly official sector)": "GD_F4"}
comp_data = {}
for label, code in comp_codes.items():
    s = fetch_edp(code, ["EL"])["EL"]
    comp_data[label] = s
comp_df = pd.DataFrame(comp_data).dropna(how="all")
comp_df.index.name = "year"
save_csv(comp_df, "02d_debt_composition_greece")

fig, ax = plt.subplots(figsize=(13, 5))
ax.stackplot(comp_df.index,
             comp_df["Currency & deposits"].fillna(0),
             comp_df["Debt securities (market)"].fillna(0),
             comp_df["Loans (mainly official sector)"].fillna(0),
             labels=["Currency & deposits", "Debt securities (market)", "Loans (official sector)"],
             colors=["#95a5a6", "#2980b9", "#c0392b"], alpha=0.85)
# Mark PSI 2012 and end of programmes 2018
ax.axvline(2012, color="black", linestyle=":", linewidth=0.8, alpha=0.6)
ax.text(2012, comp_df.sum(axis=1).max() * 0.98, "PSI 2012",
        rotation=90, va="top", ha="right", fontsize=8, color="#333")
ax.axvline(2018, color="black", linestyle=":", linewidth=0.8, alpha=0.6)
ax.text(2018, comp_df.sum(axis=1).max() * 0.98, "Programme exit 2018",
        rotation=90, va="top", ha="right", fontsize=8, color="#333")
ax.set_title("Greece: Public Debt by Instrument (% of GDP)\nLoans = EFSF/ESM/IMF/GLF official-sector debt",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
ax.legend(loc="upper left", fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/02d_debt_composition.png", dpi=150); plt.close()
print("  saved 02d_debt_composition.png")

# ---------------------------------------------------------------------------
# 5. Tax revenue as % GDP — Greece vs broader EU set (latest available year)
# ---------------------------------------------------------------------------
print("Fetching tax revenue cross-country...")
try:
    df_tax = eurostat.get_data_df("gov_10a_taxag")
    eu_set = ["EL","PT","IT","ES","CY","DE","FR","NL","AT","SE","DK","FI","IE","BE","EU27_2020"]
    mask = ((df_tax["na_item"] == "D2_D5_D91_D61_M_D995") &
            (df_tax["unit"] == "PC_GDP") &
            (df_tax["sector"] == "S13") &
            (df_tax["geo\\TIME_PERIOD"].isin(eu_set)))
    tax = df_tax[mask].set_index("geo\\TIME_PERIOD")
    year_cols = sorted([c for c in tax.columns if str(c).isdigit()], reverse=True)
    latest = None
    for y in year_cols:
        col = tax[y].dropna()
        if len(col) >= 10:
            latest = y; break

    if latest:
        tax_ts = tax[[c for c in tax.columns if str(c).isdigit()]].T.astype(float)
        tax_ts.index = tax_ts.index.astype(int)
        tax_ts.index.name = "year"
        save_csv(tax_ts, "02e_tax_revenue_pct_gdp")

        tax_latest = tax[latest].dropna().sort_values()
        labels_map = {"EL":"Greece","PT":"Portugal","IT":"Italy","ES":"Spain","CY":"Cyprus",
                      "DE":"Germany","FR":"France","NL":"Netherlands","AT":"Austria",
                      "SE":"Sweden","DK":"Denmark","FI":"Finland","IE":"Ireland",
                      "BE":"Belgium","EU27_2020":"EU27"}
        bar_colors = ["#c0392b" if i == "EL" else ("#7f8c8d" if i == "EU27_2020" else "#95a5a6")
                      for i in tax_latest.index]
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh([labels_map.get(i, i) for i in tax_latest.index],
                tax_latest.values, color=bar_colors)
        for i, v in enumerate(tax_latest.values):
            ax.text(v + 0.2, i, f"{v:.1f}", va="center", fontsize=8)
        ax.set_title(f"Tax Revenue (% of GDP), {latest}",
                     fontsize=14, fontweight="bold")
        ax.set_xlabel("% of GDP"); ax.grid(axis="x", alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{OUTPUT}/02e_tax_revenue.png", dpi=150); plt.close()
        print("  saved 02e_tax_revenue.png")
except Exception as e:
    print(f"  tax revenue chart skipped: {e}")

# ---------------------------------------------------------------------------
# 6. Government revenue vs expenditure (Greece) — area chart with deficit shading
# ---------------------------------------------------------------------------
print("Fetching revenue/expenditure split for Greece...")
try:
    df_main = eurostat.get_data_df("gov_10a_main")
    items = {"TE": "Total Expenditure", "TR": "Total Revenue"}
    el_data = {}
    for code, label in items.items():
        mask = ((df_main["na_item"] == code) & (df_main["unit"] == "PC_GDP") &
                (df_main["sector"] == "S13") & (df_main["geo\\TIME_PERIOD"] == "EL"))
        sub = df_main[mask]
        if not sub.empty:
            year_cols = [c for c in sub.columns if str(c).isdigit() and 2000 <= int(c) <= 2024]
            s = sub[year_cols].iloc[0].astype(float)
            s.index = s.index.astype(int)
            el_data[label] = s

    if len(el_data) == 2:
        rev_exp_df = pd.DataFrame(el_data)
        rev_exp_df.index.name = "year"
        save_csv(rev_exp_df, "02f_greece_revenue_expenditure_pct_gdp")

        fig, ax = plt.subplots(figsize=(13, 5))
        rev = el_data["Total Revenue"]; exp = el_data["Total Expenditure"]
        ax.plot(rev.index, rev.values, label="Total Revenue",
                color="#27ae60", linewidth=2.5, marker="o", markersize=3)
        ax.plot(exp.index, exp.values, label="Total Expenditure",
                color="#c0392b", linewidth=2.5, marker="o", markersize=3)
        idx = rev.index.intersection(exp.index)
        ax.fill_between(idx, rev[idx], exp[idx],
                        where=exp[idx] > rev[idx], alpha=0.15, color="red",
                        label="Deficit area")
        ax.fill_between(idx, rev[idx], exp[idx],
                        where=exp[idx] <= rev[idx], alpha=0.15, color="green",
                        label="Surplus area")
        add_programme_shading(ax, label_y_frac=0.95)
        ax.set_title("Greece: Government Revenue vs Expenditure (% of GDP)",
                     fontsize=14, fontweight="bold")
        ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
        ax.legend(fontsize=9, loc="lower right"); ax.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{OUTPUT}/02f_rev_vs_exp.png", dpi=150); plt.close()
        print("  saved 02f_rev_vs_exp.png")
except Exception as e:
    print(f"  revenue/expenditure chart skipped: {e}")

print("\nDone — public finance charts and CSVs saved.")
