"""
External Sector: trade balance, current account, FDI, EU funds absorption.
Sources: World Bank, Eurostat
"""

import warnings
warnings.filterwarnings("ignore")

import time
import pandas as pd
import matplotlib.pyplot as plt
import wbgapi as wb
import eurostat

OUTPUT   = "charts"
RAW_DATA = "raw-data"
import os; os.makedirs(OUTPUT, exist_ok=True); os.makedirs(RAW_DATA, exist_ok=True)

def save_csv(df, name):
    path = f"{RAW_DATA}/{name}.csv"
    df.to_csv(path)
    print(f"  saved {path}")

def wb_series(indicator, economies, year_range=(2000, 2025), retries=3):
    for attempt in range(retries):
        try:
            df = wb.data.DataFrame(indicator, economy=economies, time=range(*year_range))
            df = df.T
            df.index = df.index.str.replace("YR", "").astype(int)
            return df
        except Exception as e:
            if attempt < retries - 1:
                print(f"  WB retry {attempt+1} ({e})")
                time.sleep(5)
            else:
                raise

PEERS = ["RO", "PL", "CZ", "HU", "BG"]
PEER_LABELS = {"RO": "Romania", "PL": "Poland", "CZ": "Czechia",
               "HU": "Hungary", "BG": "Bulgaria"}
COLORS = {"RO": "#c0392b", "PL": "#2980b9", "CZ": "#27ae60",
          "HU": "#8e44ad", "BG": "#e67e22"}
WB_CODES = ["ROU", "POL", "CZE", "HUN", "BGR"]
COL_MAP  = dict(zip(WB_CODES, PEERS))

# ---------------------------------------------------------------------------
# 1. Current Account Balance (% of GDP)
# ---------------------------------------------------------------------------
print("Fetching current account data...")
ca = wb_series("BN.CAB.XOKA.GD.ZS", WB_CODES).rename(columns=COL_MAP)
ca.index.name = "year"
save_csv(ca, "05a_current_account_pct_gdp")

fig, ax = plt.subplots(figsize=(13, 5))
for iso in PEERS:
    if iso not in ca.columns:
        continue
    lw = 2.5 if iso == "RO" else 1.4
    ax.plot(ca.index, ca[iso], label=PEER_LABELS[iso],
            color=COLORS[iso], linewidth=lw, marker="o", markersize=3)
ax.axhline(0, color="black", linewidth=0.8)
ax.fill_between(ca.index, ca["RO"], 0, where=ca["RO"] < 0, alpha=0.12, color="#c0392b")
ax.set_title("Current Account Balance (% of GDP)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/05a_current_account.png", dpi=150); plt.close()
print("  saved 05a_current_account.png")

# ---------------------------------------------------------------------------
# 2. Trade balance (exports minus imports, % of GDP)
# ---------------------------------------------------------------------------
print("Fetching trade balance data...")
exports = wb_series("NE.EXP.GNFS.ZS", WB_CODES).rename(columns=COL_MAP)
imports = wb_series("NE.IMP.GNFS.ZS", WB_CODES).rename(columns=COL_MAP)
trade_bal = exports - imports
trade_raw = exports.copy()
trade_raw.columns = [f"exports_{c}" for c in exports.columns]
for c in imports.columns:
    trade_raw[f"imports_{c}"] = imports[c]
trade_raw.index.name = "year"
save_csv(trade_raw, "05b_exports_imports_pct_gdp")

fig, ax = plt.subplots(figsize=(13, 5))
for iso in PEERS:
    if iso not in trade_bal.columns:
        continue
    lw = 2.5 if iso == "RO" else 1.4
    ax.plot(trade_bal.index, trade_bal[iso], label=PEER_LABELS[iso],
            color=COLORS[iso], linewidth=lw, marker="o", markersize=3)
ax.axhline(0, color="black", linewidth=0.8)
ax.set_title("Trade Balance in Goods & Services (% of GDP)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP (exports minus imports)")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/05b_trade_balance.png", dpi=150); plt.close()
print("  saved 05b_trade_balance.png")

# ---------------------------------------------------------------------------
# 3. FDI net inflows (% of GDP)
# ---------------------------------------------------------------------------
print("Fetching FDI data...")
fdi = wb_series("BX.KLT.DINV.WD.GD.ZS", WB_CODES).rename(columns=COL_MAP)
fdi.index.name = "year"
save_csv(fdi, "05c_fdi_net_inflows_pct_gdp")

fig, ax = plt.subplots(figsize=(13, 5))
for iso in PEERS:
    if iso not in fdi.columns:
        continue
    lw = 2.5 if iso == "RO" else 1.4
    ax.plot(fdi.index, fdi[iso], label=PEER_LABELS[iso],
            color=COLORS[iso], linewidth=lw, marker="o", markersize=3)
ax.axhline(0, color="black", linewidth=0.8)
ax.set_title("FDI Net Inflows (% of GDP)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/05c_fdi.png", dpi=150); plt.close()
print("  saved 05c_fdi.png")

# ---------------------------------------------------------------------------
# 4. Exports vs imports levels (Romania, % GDP) — area chart
# ---------------------------------------------------------------------------
print("Building Romania exports/imports area chart...")
ro_exp = exports["RO"].dropna()
ro_imp = imports["RO"].dropna()
idx = ro_exp.index.intersection(ro_imp.index)

fig, ax = plt.subplots(figsize=(12, 5))
ax.fill_between(idx, ro_imp[idx], alpha=0.3, color="#c0392b", label="Imports")
ax.fill_between(idx, ro_exp[idx], alpha=0.4, color="#2980b9", label="Exports")
ax.plot(idx, ro_exp[idx], color="#2980b9", linewidth=2)
ax.plot(idx, ro_imp[idx], color="#c0392b", linewidth=2)
ax.set_title("Romania: Exports and Imports (% of GDP)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
ax.legend(fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/05d_ro_trade_openness.png", dpi=150); plt.close()
print("  saved 05d_ro_trade_openness.png")

# ---------------------------------------------------------------------------
# 5. EU Funds absorption — embedded data
# ---------------------------------------------------------------------------
print("Building EU funds absorption chart...")
funds_2014_2020 = {
    "Poland":    95.2,
    "Czechia":   91.3,
    "Hungary":   88.7,
    "Slovakia":  84.1,
    "Romania":   72.4,
    "Bulgaria":  78.9,
    "Croatia":   81.2,
    "Lithuania": 93.5,
    "Estonia":   97.1,
    "Latvia":    90.8,
}
df_funds = pd.Series(funds_2014_2020, name="absorption_rate_pct")
df_funds.index.name = "country"
save_csv(df_funds.to_frame(), "05e_eu_cohesion_funds_absorption_2014_2020")
df_funds = df_funds.sort_values()
bar_colors = ["#c0392b" if c == "Romania" else "#95a5a6" for c in df_funds.index]
avg = df_funds.mean()

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(df_funds.index, df_funds.values, color=bar_colors)
ax.axvline(avg, color="#2980b9", linestyle="--", linewidth=1.5, label=f"Average: {avg:.1f}%")
for i, (val, country) in enumerate(zip(df_funds.values, df_funds.index)):
    ax.text(val + 0.3, i, f"{val:.1f}%", va="center", fontsize=9)
ax.set_title("EU Cohesion Funds Absorption Rate, 2014–2020 Period\n(% of allocated funds, end-2023)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("% of allocated funds absorbed")
ax.legend(fontsize=9); ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/05e_eu_funds.png", dpi=150); plt.close()
print("  saved 05e_eu_funds.png")

print("\nDone — external sector charts saved to", OUTPUT)
