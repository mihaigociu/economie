"""
Public Finances: budget deficit, public debt, revenue & spending structure.
Sources: Eurostat (gov_10a_main, gov_10dd_edpt1), World Bank
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

def save_csv(df, name):
    path = f"{RAW_DATA}/{name}.csv"
    df.to_csv(path)
    print(f"  saved {path}")

PEERS = ["RO", "PL", "CZ", "HU", "BG"]
PEER_LABELS = {"RO": "Romania", "PL": "Poland", "CZ": "Czechia",
               "HU": "Hungary", "BG": "Bulgaria"}
COLORS = {"RO": "#c0392b", "PL": "#2980b9", "CZ": "#27ae60",
          "HU": "#8e44ad", "BG": "#e67e22"}

# ---------------------------------------------------------------------------
# 1. General government deficit (% GDP)
# ---------------------------------------------------------------------------
print("Fetching government deficit data...")
try:
    df_def = eurostat.get_data_df("gov_10dd_edpt1")
    mask = (
        (df_def["na_item"] == "B9") &
        (df_def["unit"] == "PC_GDP") &
        (df_def["sector"] == "S13") &
        (df_def["geo\\TIME_PERIOD"].isin(PEERS))
    )
    deficit = df_def[mask].set_index("geo\\TIME_PERIOD")
    year_cols = [c for c in deficit.columns if str(c).isdigit() and 2000 <= int(c) <= 2024]
    deficit = deficit[year_cols].T.astype(float)
    deficit.index = deficit.index.astype(int)
    deficit.index.name = "year"
    save_csv(deficit, "02a_govt_balance_pct_gdp")

    fig, ax = plt.subplots(figsize=(13, 5))
    for iso in PEERS:
        if iso in deficit.columns:
            lw = 2.5 if iso == "RO" else 1.4
            ax.plot(deficit.index, deficit[iso], label=PEER_LABELS[iso],
                    color=COLORS[iso], linewidth=lw, marker="o", markersize=3)
    ax.axhline(-3, color="red", linestyle="--", linewidth=1.2, alpha=0.7, label="Maastricht −3% limit")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.fill_between(deficit.index, deficit.get("RO", pd.Series()), -3,
                    where=deficit.get("RO", pd.Series()) < -3,
                    alpha=0.12, color="red", label="RO breach zone")
    ax.set_title("General Government Balance (% of GDP)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
    ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/02a_deficit.png", dpi=150); plt.close()
    print("  saved 02a_deficit.png")
except Exception as e:
    print(f"  deficit via Eurostat failed ({e}), falling back to World Bank")
    df_wb = wb.data.DataFrame("GC.BAL.CASH.GD.ZS", economy=["ROU","POL","CZE","HUN","BGR"],
                               time=range(2000, 2025))
    df_wb = df_wb.T
    df_wb.index = df_wb.index.str.replace("YR", "").astype(int)
    df_wb.columns = ["RO", "PL", "CZ", "HU", "BG"]
    df_wb.index.name = "year"
    save_csv(df_wb, "02a_govt_balance_pct_gdp")
    fig, ax = plt.subplots(figsize=(13, 5))
    for iso in PEERS:
        lw = 2.5 if iso == "RO" else 1.4
        ax.plot(df_wb.index, df_wb[iso], label=PEER_LABELS[iso],
                color=COLORS[iso], linewidth=lw, marker="o", markersize=3)
    ax.axhline(-3, color="red", linestyle="--", linewidth=1.2, label="Maastricht −3%")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title("Government Cash Surplus/Deficit (% of GDP)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
    ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/02a_deficit.png", dpi=150); plt.close()
    print("  saved 02a_deficit.png (WB fallback)")

# ---------------------------------------------------------------------------
# 2. Public debt (% GDP)
# ---------------------------------------------------------------------------
print("Fetching public debt data...")
try:
    df_debt = eurostat.get_data_df("gov_10dd_edpt1")
    mask = (
        (df_debt["na_item"] == "GD") &
        (df_debt["unit"] == "PC_GDP") &
        (df_debt["sector"] == "S13") &
        (df_debt["geo\\TIME_PERIOD"].isin(PEERS))
    )
    debt = df_debt[mask].set_index("geo\\TIME_PERIOD")
    year_cols = [c for c in debt.columns if str(c).isdigit() and 2000 <= int(c) <= 2024]
    debt = debt[year_cols].T.astype(float)
    debt.index = debt.index.astype(int)
    debt.index.name = "year"
    save_csv(debt, "02b_public_debt_pct_gdp")

    fig, ax = plt.subplots(figsize=(13, 5))
    for iso in PEERS:
        if iso in debt.columns:
            lw = 2.5 if iso == "RO" else 1.4
            ax.plot(debt.index, debt[iso], label=PEER_LABELS[iso],
                    color=COLORS[iso], linewidth=lw, marker="o", markersize=3)
    ax.axhline(60, color="red", linestyle="--", linewidth=1.2, alpha=0.7, label="Maastricht 60% limit")
    ax.set_title("General Government Gross Debt (% of GDP)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
    ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/02b_debt.png", dpi=150); plt.close()
    print("  saved 02b_debt.png")
except Exception as e:
    print(f"  debt via Eurostat failed ({e}), using World Bank")
    debt_wb = wb.data.DataFrame("GC.DOD.TOTL.GD.ZS", economy=["ROU","POL","CZE","HUN","BGR"],
                                 time=range(2000, 2025))
    debt_wb = debt_wb.T
    debt_wb.index = debt_wb.index.str.replace("YR", "").astype(int)
    debt_wb.columns = ["RO", "PL", "CZ", "HU", "BG"]
    debt_wb.index.name = "year"
    save_csv(debt_wb, "02b_public_debt_pct_gdp")
    fig, ax = plt.subplots(figsize=(13, 5))
    for iso in PEERS:
        lw = 2.5 if iso == "RO" else 1.4
        ax.plot(debt_wb.index, debt_wb[iso], label=PEER_LABELS[iso],
                color=COLORS[iso], linewidth=lw, marker="o", markersize=3)
    ax.axhline(60, color="red", linestyle="--", linewidth=1.2, label="Maastricht 60%")
    ax.set_title("Public Debt (% of GDP)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
    ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/02b_debt.png", dpi=150); plt.close()
    print("  saved 02b_debt.png (WB fallback)")

# ---------------------------------------------------------------------------
# 3. Tax revenue as % GDP — Romania vs EU peers
# ---------------------------------------------------------------------------
print("Fetching tax revenue data...")
try:
    df_tax = eurostat.get_data_df("gov_10a_taxag")
    eu_countries = ["RO","PL","CZ","HU","BG","SK","AT","DE","FR","SE","EU27_2020"]
    mask = (
        (df_tax["na_item"] == "D2_D5_D91_D61_M_D995") &
        (df_tax["unit"] == "PC_GDP") &
        (df_tax["sector"] == "S13") &
        (df_tax["geo\\TIME_PERIOD"].isin(eu_countries))
    )
    tax = df_tax[mask].set_index("geo\\TIME_PERIOD")
    year_cols = sorted([c for c in tax.columns if str(c).isdigit()], reverse=True)
    latest = None
    for y in year_cols:
        col = tax[y].dropna()
        if len(col) >= 5:
            latest = y
            break
    if latest:
        # save full time series
        tax_ts = tax[[c for c in tax.columns if str(c).isdigit()]].T.astype(float)
        tax_ts.index = tax_ts.index.astype(int)
        tax_ts.index.name = "year"
        save_csv(tax_ts, "02c_tax_revenue_pct_gdp")

        tax_latest = tax[latest].dropna().sort_values()
        labels_map = {"RO":"Romania","PL":"Poland","CZ":"Czechia","HU":"Hungary",
                      "BG":"Bulgaria","SK":"Slovakia","AT":"Austria","DE":"Germany",
                      "FR":"France","SE":"Sweden","EU27_2020":"EU27"}
        bar_colors = ["#c0392b" if i == "RO" else "#95a5a6" for i in tax_latest.index]
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.barh([labels_map.get(i, i) for i in tax_latest.index],
                tax_latest.values, color=bar_colors)
        ax.set_title(f"Tax Revenue (% of GDP), {latest}", fontsize=14, fontweight="bold")
        ax.set_xlabel("% of GDP"); ax.grid(axis="x", alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{OUTPUT}/02c_tax_revenue.png", dpi=150); plt.close()
        print("  saved 02c_tax_revenue.png")
except Exception as e:
    print(f"  tax revenue chart skipped: {e}")

# ---------------------------------------------------------------------------
# 4. Government expenditure vs revenue (Romania only)
# ---------------------------------------------------------------------------
print("Fetching revenue/expenditure split for Romania...")
try:
    df_main = eurostat.get_data_df("gov_10a_main")
    items = {"TE": "Total Expenditure", "TR": "Total Revenue"}
    ro_data = {}
    for code, label in items.items():
        mask = (
            (df_main["na_item"] == code) &
            (df_main["unit"] == "PC_GDP") &
            (df_main["sector"] == "S13") &
            (df_main["geo\\TIME_PERIOD"] == "RO")
        )
        sub = df_main[mask]
        if not sub.empty:
            year_cols = [c for c in sub.columns if str(c).isdigit() and 2000 <= int(c) <= 2024]
            s = sub[year_cols].iloc[0].astype(float)
            s.index = s.index.astype(int)
            ro_data[label] = s

    if ro_data:
        rev_exp_df = pd.DataFrame(ro_data)
        rev_exp_df.index.name = "year"
        save_csv(rev_exp_df, "02d_romania_revenue_expenditure_pct_gdp")

        fig, ax = plt.subplots(figsize=(13, 5))
        for label, series in ro_data.items():
            color = "#c0392b" if "Expenditure" in label else "#27ae60"
            ax.plot(series.index, series.values, label=label, color=color,
                    linewidth=2, marker="o", markersize=3)
        if len(ro_data) == 2:
            rev = ro_data["Total Revenue"]
            exp = ro_data["Total Expenditure"]
            idx = rev.index.intersection(exp.index)
            ax.fill_between(idx, rev[idx], exp[idx],
                            where=exp[idx] > rev[idx], alpha=0.15, color="red",
                            label="Deficit area")
        ax.set_title("Romania: Government Revenue vs Expenditure (% of GDP)",
                     fontsize=14, fontweight="bold")
        ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
        ax.legend(fontsize=9); ax.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{OUTPUT}/02d_rev_vs_exp.png", dpi=150); plt.close()
        print("  saved 02d_rev_vs_exp.png")
except Exception as e:
    print(f"  revenue/expenditure chart skipped: {e}")

print("\nDone — public finance charts and CSVs saved.")
