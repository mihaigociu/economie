"""
Inflation & Monetary Policy: CPI history, BNR policy rate, RON/EUR exchange rate,
euro adoption convergence criteria.
Sources: World Bank, Eurostat, BNR (embedded series)
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

def wb_series(indicator, economies, year_range=(1995, 2025), retries=3):
    for attempt in range(retries):
        try:
            df = wb.data.DataFrame(indicator, economy=economies, time=range(*year_range))
            df = df.T
            df.index = df.index.str.replace("YR", "").astype(int)
            return df
        except Exception as e:
            if attempt < retries - 1:
                print(f"  WB API error ({e}), retrying in 5s...")
                time.sleep(5)
            else:
                raise

PEERS = ["RO", "PL", "CZ", "HU", "BG"]
PEER_LABELS = {"RO": "Romania", "PL": "Poland", "CZ": "Czechia",
               "HU": "Hungary", "BG": "Bulgaria"}
COLORS = {"RO": "#c0392b", "PL": "#2980b9", "CZ": "#27ae60",
          "HU": "#8e44ad", "BG": "#e67e22"}
WB_CODES = ["ROU", "POL", "CZE", "HUN", "BGR", "EMU"]
COL_MAP  = {"ROU":"RO","POL":"PL","CZE":"CZ","HUN":"HU","BGR":"BG","EMU":"EA"}

# ---------------------------------------------------------------------------
# 1. CPI / HICP annual inflation — Eurostat primary, WB fallback
# ---------------------------------------------------------------------------
print("Fetching CPI/HICP inflation data...")
cpi = None
try:
    df_hicp = eurostat.get_data_df("prc_hicp_aind")
    geo_col = [c for c in df_hicp.columns if "geo" in c.lower()][0]
    eurostat_peers = PEERS + ["EA20"]
    mask = (
        (df_hicp["unit"] == "RCH_A_AVG") &  # annual rate of change, annual avg
        (df_hicp["coicop"] == "CP00") &      # all items
        (df_hicp[geo_col].isin(eurostat_peers))
    )
    hicp = df_hicp[mask].set_index(geo_col)
    year_cols = sorted([c for c in hicp.columns if str(c).isdigit() and int(c) >= 1995])
    hicp = hicp[year_cols].T.astype(float)
    hicp.index = hicp.index.astype(int)
    hicp = hicp.rename(columns={"EA20": "EA"})
    cpi = hicp
    print("  Using Eurostat HICP data")
except Exception as e:
    print(f"  Eurostat HICP failed ({e}), falling back to World Bank")

if cpi is None:
    cpi = wb_series("FP.CPI.TOTL.ZG", WB_CODES).rename(columns=COL_MAP)

cpi.index.name = "year"
save_csv(cpi, "04a_hicp_inflation_pct")

fig, axes = plt.subplots(2, 1, figsize=(13, 9))

# top: full history
ax = axes[0]
for iso, label in {**PEER_LABELS, "EA": "Euro Area"}.items():
    if iso not in cpi.columns:
        continue
    lw = 2.5 if iso == "RO" else 1.2
    ls = "--" if iso == "EA" else "-"
    color = COLORS.get(iso, "#7f8c8d")
    ax.plot(cpi.index, cpi[iso], label=label, color=color, linewidth=lw, linestyle=ls)
ax.axhline(2, color="grey", linestyle=":", linewidth=1, alpha=0.7, label="2% reference")
ax.set_title("CPI Inflation (%), 1995–2024 — Full History", fontsize=13, fontweight="bold")
ax.set_ylabel("Annual %"); ax.legend(ncol=3, fontsize=8); ax.grid(axis="y", alpha=0.3)
ax.set_ylim(-5, None)

# bottom: 2015-2024 zoom
ax2 = axes[1]
recent = cpi[cpi.index >= 2015]
for iso, label in {**PEER_LABELS, "EA": "Euro Area"}.items():
    if iso not in recent.columns:
        continue
    lw = 2.5 if iso == "RO" else 1.2
    ls = "--" if iso == "EA" else "-"
    color = COLORS.get(iso, "#7f8c8d")
    ax2.plot(recent.index, recent[iso], label=label, color=color, linewidth=lw, linestyle=ls)
ax2.axhline(2, color="grey", linestyle=":", linewidth=1, alpha=0.7, label="2% target")
ax2.set_title("CPI Inflation (%), 2015–2024 — Recent Surge", fontsize=13, fontweight="bold")
ax2.set_xlabel("Year"); ax2.set_ylabel("Annual %")
ax2.legend(ncol=3, fontsize=8); ax2.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig(f"{OUTPUT}/04a_inflation.png", dpi=150); plt.close()
print("  saved 04a_inflation.png")

# ---------------------------------------------------------------------------
# 2. BNR Policy Rate vs CPI Romania
# ---------------------------------------------------------------------------
print("Building BNR policy rate series...")
bnr_rate = {
    2000: 35.0, 2001: 35.0, 2002: 25.0, 2003: 21.25, 2004: 17.0,
    2005: 8.5,  2006: 8.75, 2007: 7.5,  2008: 10.25, 2009: 8.0,
    2010: 6.25, 2011: 6.0,  2012: 5.25, 2013: 4.0,   2014: 2.75,
    2015: 1.75, 2016: 1.75, 2017: 1.75, 2018: 2.5,   2019: 2.5,
    2020: 1.5,  2021: 1.75, 2022: 6.75, 2023: 7.0,   2024: 6.5,
}
bnr_s = pd.Series(bnr_rate, name="policy_rate_pct")
bnr_s.index.name = "year"
save_csv(bnr_s.to_frame(), "04b_bnr_policy_rate_pct")
cpi_ro = cpi["RO"].dropna()
cpi_ro = cpi_ro[cpi_ro.index >= 2000]

fig, ax = plt.subplots(figsize=(13, 5))
ax.plot(bnr_s.index, bnr_s.values, color="#c0392b", linewidth=2.5,
        marker="o", markersize=4, label="BNR Policy Rate")
ax.fill_between(bnr_s.index, bnr_s.values, alpha=0.1, color="#c0392b")

ax2 = ax.twinx()
ax2.plot(cpi_ro.index, cpi_ro.values, color="#e67e22", linewidth=1.8,
         linestyle="--", marker="s", markersize=3, label="CPI Inflation (RHS)")
ax2.set_ylabel("CPI %", color="#e67e22")
ax2.tick_params(axis="y", labelcolor="#e67e22")

ax.set_title("Romania: BNR Policy Rate vs CPI Inflation", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Policy Rate %", color="#c0392b")
ax.tick_params(axis="y", labelcolor="#c0392b"); ax.grid(axis="y", alpha=0.3)
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, fontsize=9)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/04b_policy_rate.png", dpi=150); plt.close()
print("  saved 04b_policy_rate.png")

# ---------------------------------------------------------------------------
# 3. RON/EUR Exchange Rate
# ---------------------------------------------------------------------------
print("Building RON/EUR exchange rate series...")
ron_eur = {
    1999: 1.866, 2000: 1.993, 2001: 2.601, 2002: 3.128, 2003: 3.756,
    2004: 4.051, 2005: 3.621, 2006: 3.526, 2007: 3.337, 2008: 3.683,
    2009: 4.239, 2010: 4.212, 2011: 4.239, 2012: 4.456, 2013: 4.419,
    2014: 4.444, 2015: 4.445, 2016: 4.490, 2017: 4.569, 2018: 4.654,
    2019: 4.745, 2020: 4.839, 2021: 4.921, 2022: 4.931, 2023: 4.953,
    2024: 4.975,
}
try:
    df_fx = eurostat.get_data_df("ert_bil_eur_a")
    mask = (df_fx["currency"] == "RON") & (df_fx["statinfo"] == "AVG")
    geo_col = [c for c in df_fx.columns if "geo" in c.lower()][0]
    fx_eur = df_fx[mask & (df_fx[geo_col] == "RO")]
    if not fx_eur.empty:
        year_cols = [c for c in fx_eur.columns if str(c).isdigit()]
        fx_s = fx_eur[year_cols].iloc[0].astype(float).dropna()
        fx_s.index = fx_s.index.astype(int)
        ron_eur.update(fx_s.to_dict())
        print("  RON/EUR: Eurostat data merged")
except Exception as e:
    print(f"  RON/EUR Eurostat skipped ({e}), using embedded series")

fx_series = pd.Series(ron_eur, name="RON_per_EUR").sort_index()
fx_series.index.name = "year"
save_csv(fx_series.to_frame(), "04c_ron_eur_exchange_rate")

fig, ax = plt.subplots(figsize=(13, 4))
ax.plot(fx_series.index, fx_series.values, color="#2980b9", linewidth=2.5, marker="o", markersize=3)
ax.axvline(2007, color="green", linestyle="--", linewidth=1.2, alpha=0.7)
ax.text(2007.2, fx_series.max() * 0.97, "EU accession", fontsize=8, color="green")
ax.set_title("RON / EUR Exchange Rate (Annual Average)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("RON per 1 EUR")
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/04c_ron_eur.png", dpi=150); plt.close()
print("  saved 04c_ron_eur.png")

# ---------------------------------------------------------------------------
# 4. Euro adoption convergence criteria dashboard
# ---------------------------------------------------------------------------
print("Building euro criteria dashboard...")
criteria = {
    "Inflation (≤ ~3.3%)":        {"ro": 5.9,  "limit": 3.3},
    "LT Interest Rate (≤ ~4.8%)": {"ro": 6.8,  "limit": 4.8},
    "Budget Deficit (≤ 3% GDP)":  {"ro": 7.9,  "limit": 3.0},
    "Public Debt (≤ 60% GDP)":    {"ro": 52.0, "limit": 60.0},
}
criteria_df = pd.DataFrame(criteria, index=["Romania_value", "limit"]).T
criteria_df["pass"] = criteria_df["Romania_value"] <= criteria_df["limit"]
criteria_df.index.name = "criterion"
save_csv(criteria_df, "04d_euro_maastricht_criteria")

# reformat labels for the chart
criteria_chart = {
    "Inflation\n(≤ ~3.3%)":        {"ro": 5.9,  "limit": 3.3},
    "LT Interest Rate\n(≤ ~4.8%)": {"ro": 6.8,  "limit": 4.8},
    "Budget Deficit\n(≤ 3% GDP)":  {"ro": 7.9,  "limit": 3.0},
    "Public Debt\n(≤ 60% GDP)":    {"ro": 52.0, "limit": 60.0},
}

fig, axes = plt.subplots(1, 4, figsize=(14, 5))
for ax, (label, vals) in zip(axes, criteria_chart.items()):
    ro_val = vals["ro"]
    limit  = vals["limit"]
    ok = ro_val <= limit
    color = "#27ae60" if ok else "#c0392b"
    ax.bar(["Romania", "Limit"], [ro_val, limit], color=[color, "#95a5a6"])
    ax.set_title(label, fontsize=9, fontweight="bold")
    ax.set_ylabel("Value")
    for x, v in zip([0, 1], [ro_val, limit]):
        ax.text(x, v + limit * 0.02, f"{v:.1f}", ha="center", fontsize=9, fontweight="bold")
    status = "PASS ✓" if ok else "FAIL ✗"
    ax.text(0.5, 0.96, status, transform=ax.transAxes, ha="center",
            fontsize=12, fontweight="bold", color=color, va="top")
    ax.grid(axis="y", alpha=0.3)

fig.suptitle("Romania: Euro Adoption Maastricht Criteria (~2024)",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/04d_euro_criteria.png", dpi=150); plt.close()
print("  saved 04d_euro_criteria.png")

print("\nDone — inflation & monetary charts saved to", OUTPUT)
