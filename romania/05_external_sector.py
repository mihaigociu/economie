"""
External Sector: trade balance, current account, FDI, EU funds absorption.
Sources: World Bank (BoP / national accounts), European Commission Cohesion
Open Data platform (EU payments to member states).
"""

import pandas as pd
import requests
import matplotlib.pyplot as plt

from common import (OUTPUT, PEERS, PEER_LABELS, COLORS, WB_CODES, WB_MAP, save_csv,
                    wb_series, plot_peers, wb_url, year_span, TODAY)

LAST_YEAR = 2025
FIRST_YEAR = 2000


def peer_chart(df, title, ylabel, fname, shade_ro=False):
    fig, ax = plt.subplots(figsize=(13, 5))
    plot_peers(ax, df)
    ax.axhline(0, color="black", linewidth=0.8)
    if shade_ro:
        ax.fill_between(df.index, df["RO"], 0, where=df["RO"] < 0, alpha=0.12,
                        color=COLORS["RO"], interpolate=True)
    ax.set_title(f"{title}, {year_span(df)}", fontsize=14, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel(ylabel)
    ax.legend(ncol=5, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.13), frameon=False)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/{fname}", dpi=150); plt.close()
    print(f"  saved {fname}")
    return fig, ax


# ---------------------------------------------------------------------------
# 1. Current Account Balance (% of GDP)
# ---------------------------------------------------------------------------
print("Fetching current account data...")
ca = wb_series("BN.CAB.XOKA.GD.ZS", WB_CODES, FIRST_YEAR, LAST_YEAR, WB_MAP)
save_csv(ca, "05a_current_account_pct_gdp",
         "World Bank WDI BN.CAB.XOKA.GD.ZS — current account balance, % of GDP",
         wb_url("BN.CAB.XOKA.GD.ZS"))
peer_chart(ca, "Current Account Balance (% of GDP)", "% of GDP", "05a_current_account.png",
           shade_ro=True)

# ---------------------------------------------------------------------------
# 2. Trade balance (exports minus imports, % of GDP)
# ---------------------------------------------------------------------------
print("Fetching trade data...")
exports = wb_series("NE.EXP.GNFS.ZS", WB_CODES, FIRST_YEAR, LAST_YEAR, WB_MAP)
imports = wb_series("NE.IMP.GNFS.ZS", WB_CODES, FIRST_YEAR, LAST_YEAR, WB_MAP)
trade_bal = exports - imports
trade_raw = pd.concat([exports.add_prefix("exports_"), imports.add_prefix("imports_")], axis=1)
trade_raw.index.name = "year"
save_csv(trade_raw, "05b_exports_imports_pct_gdp",
         "World Bank WDI NE.EXP.GNFS.ZS / NE.IMP.GNFS.ZS — exports and imports of goods and services, % of GDP",
         wb_url("NE.EXP.GNFS.ZS"))
peer_chart(trade_bal, "Trade Balance in Goods & Services (% of GDP)",
           "% of GDP (exports minus imports)", "05b_trade_balance.png")

# ---------------------------------------------------------------------------
# 3. FDI net inflows (% of GDP)
# ---------------------------------------------------------------------------
print("Fetching FDI data...")
fdi = wb_series("BX.KLT.DINV.WD.GD.ZS", WB_CODES, FIRST_YEAR, LAST_YEAR, WB_MAP)
save_csv(fdi, "05c_fdi_net_inflows_pct_gdp",
         "World Bank WDI BX.KLT.DINV.WD.GD.ZS — foreign direct investment, net inflows, % of GDP",
         wb_url("BX.KLT.DINV.WD.GD.ZS"))
fig, ax = peer_chart(fdi, "FDI Net Inflows (% of GDP)", "% of GDP", "05c_fdi.png")
# re-draw with a clipped axis: Hungary's SPE-driven swings would flatten every other line
fig, ax = plt.subplots(figsize=(13, 5))
plot_peers(ax, fdi)
ax.axhline(0, color="black", linewidth=0.8)
ax.set_ylim(-10, 35)
hu = fdi["HU"].dropna()
off = hu[(hu > 35) | (hu < -10)]
ax.text(0.01, 0.97, "Hungary off-scale in " + ", ".join(f"{y} ({v:+.0f})" for y, v in off.items())
        + " — SPE/holding-company flows, not comparable", transform=ax.transAxes,
        fontsize=8, color=COLORS["HU"], va="top", zorder=5,
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.9))
ax.set_title(f"FDI Net Inflows (% of GDP), {year_span(fdi)}", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
ax.legend(ncol=5, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.13), frameon=False)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/05c_fdi.png", dpi=150); plt.close()
print("  saved 05c_fdi.png (clipped axis)")

# ---------------------------------------------------------------------------
# 4. Exports vs imports levels (Romania, % GDP) — area chart
# ---------------------------------------------------------------------------
print("Building Romania exports/imports area chart...")
ro = pd.DataFrame({"exp": exports["RO"], "imp": imports["RO"]}).dropna()
fig, ax = plt.subplots(figsize=(12, 5))
ax.fill_between(ro.index, ro["imp"], alpha=0.3, color="#c0392b", label="Imports")
ax.fill_between(ro.index, ro["exp"], alpha=0.4, color="#2980b9", label="Exports")
ax.plot(ro.index, ro["exp"], color="#2980b9", linewidth=2)
ax.plot(ro.index, ro["imp"], color="#c0392b", linewidth=2)
ax.set_title(f"Romania: Exports and Imports of Goods & Services (% of GDP), {year_span(ro)}",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
ax.legend(fontsize=9, loc="upper left"); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/05d_ro_trade_openness.png", dpi=150); plt.close()
print("  saved 05d_ro_trade_openness.png")

# ---------------------------------------------------------------------------
# 5. EU funds absorption — EU payments as % of planned EU amount
# ---------------------------------------------------------------------------
print("Fetching EU funds payment rates (Cohesion Open Data)...")
COH = "https://cohesiondata.ec.europa.eu/resource/{}.json?$limit=5000"
FUND_COUNTRIES = {"PL": "Poland", "CZ": "Czechia", "HU": "Hungary", "SK": "Slovakia",
                  "RO": "Romania", "BG": "Bulgaria", "HR": "Croatia", "LT": "Lithuania",
                  "EE": "Estonia", "LV": "Latvia"}


def coh(dataset_id):
    r = requests.get(COH.format(dataset_id), timeout=120)
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    if df.empty:
        raise RuntimeError(f"Cohesion dataset {dataset_id} returned no rows")
    return df


# (a) 2014-2020 ESIF (excl. REACT-EU): programme-level cumulative EU payments by year,
#     aggregated to member state (dataset gayr-92qh)
r = requests.get("https://cohesiondata.ec.europa.eu/resource/gayr-92qh.json",
                 params={"$select": "ms,year,fund,sum(total_net_payments) as pay,"
                                    "sum(net_planned_eu_amount) as plan",
                         "$group": "ms,year,fund", "$limit": "50000"}, timeout=120)
r.raise_for_status()
ts = pd.DataFrame(r.json())
if ts.empty:
    raise RuntimeError("Cohesion dataset gayr-92qh returned no rows")
ts = ts[ts["ms"].isin(FUND_COUNTRIES) & ~ts["fund"].str.contains("REACT", case=False)]
ts[["pay", "plan"]] = ts[["pay", "plan"]].astype(float)
ts = ts.groupby(["year", "ms"])[["pay", "plan"]].sum()
rate_ts = (ts["pay"] / ts["plan"] * 100).unstack().round(1)
rate_ts.index = rate_ts.index.astype(int); rate_ts.index.name = "year"
rate_ts = rate_ts.rename(columns=FUND_COUNTRIES)
save_csv(rate_ts, "05e2_eu_funds_2014_2020_payment_rate_timeseries_pct",
         "European Commission Cohesion Open Data, dataset gayr-92qh (ESIF 2014-2020 EU payments, programme level) — "
         "cumulative EU payments as % of net planned EU amount, aggregated by member state, excl. REACT-EU",
         "https://cohesiondata.ec.europa.eu/resource/gayr-92qh",
         ["year = position at end of year (current year = latest available)"])
latest_1420 = int(rate_ts.index.max())
p1420_2023 = rate_ts.loc[2023].rename(index={v: k for k, v in FUND_COUNTRIES.items()})
p1420_now = rate_ts.loc[latest_1420].rename(index={v: k for k, v in FUND_COUNTRIES.items()})
# (c) 2021-2027 cohesion programmes, latest cumulative EU payments
c = coh("ue97-5sq6")
c = c[c["fund"].isin(FUND_COUNTRIES)].set_index("fund")   # 'fund' column holds the MS code here
p2127_now = c["total_net_payments"].astype(float) / c["actual_plan_eu_amt_latest_adop"].astype(float) * 100

funds = pd.DataFrame({"p2014_2020_end2023": p1420_2023,
                      "p2014_2020_latest": p1420_now,
                      "p2021_2027_latest": p2127_now}).round(1)
if funds.isna().any().any():
    raise RuntimeError(f"EU funds: missing values\n{funds}")
funds.index = funds.index.map(FUND_COUNTRIES)
funds.index.name = "country"
save_csv(funds, "05e_eu_funds_payment_rates_pct",
         "European Commission Cohesion Open Data — EU payments as % of planned EU amount: "
         "2014-2020 ESIF excl. REACT-EU (dataset gayr-92qh, end-2023 and latest year); "
         "2021-2027 (ue97-5sq6, latest)",
         "https://cohesiondata.ec.europa.eu/",
         ["2014-2020 'latest' is effectively the closure position (programmes closed 2024-2026)",
          f"latest values as published on the platform on {TODAY}"])

order = funds.sort_values("p2014_2020_end2023").index
f = funds.loc[order]
fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
y = range(len(f))
ax = axes[0]
ax.barh([i + 0.2 for i in y], f["p2014_2020_end2023"], height=0.4,
        color=["#c0392b" if c == "Romania" else "#95a5a6" for c in f.index], label="End-2023")
ax.barh([i - 0.2 for i in y], f["p2014_2020_latest"], height=0.4,
        color=["#e6a59e" if c == "Romania" else "#d5dbdb" for c in f.index], label=f"{latest_1420} (closure phase)")
for i, (v1, v2) in enumerate(zip(f["p2014_2020_end2023"], f["p2014_2020_latest"])):
    ax.text(v1 + 0.3, i + 0.2, f"{v1:.1f}", va="center", fontsize=8)
    ax.text(v2 + 0.3, i - 0.2, f"{v2:.1f}", va="center", fontsize=8, color="#555")
ax.set_yticks(list(y)); ax.set_yticklabels(f.index)
ax.set_xlim(70, 104)
ax.set_title("2014–2020 programmes: EU payments\n(% of planned EU amount)", fontsize=11, fontweight="bold")
ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=2, frameon=False)
ax.grid(axis="x", alpha=0.3)
ax = axes[1]
ax.barh(list(y), f["p2021_2027_latest"],
        color=["#c0392b" if c == "Romania" else "#95a5a6" for c in f.index])
for i, v in enumerate(f["p2021_2027_latest"]):
    ax.text(v + 0.5, i, f"{v:.1f}", va="center", fontsize=8)
ax.set_xlim(0, f["p2021_2027_latest"].max() * 1.15)
ax.set_title(f"2021–2027 programmes: EU payments to date\n(% of planned EU amount, {TODAY})",
             fontsize=11, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
fig.suptitle("EU Cohesion Funds Absorption — Romania vs CEE peers", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/05e_eu_funds.png", dpi=150); plt.close()
print("  saved 05e_eu_funds.png")

print("\nDone — external sector charts saved to", OUTPUT)
