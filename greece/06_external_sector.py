"""
External Sector: current account, goods vs services balance (the distinctive
Greek pattern), tourism & shipping receipts, FDI, RRF disbursement.
Sources: World Bank (CA, FDI), Eurostat (bop_c6_a), EC RRF Scoreboard (hardcoded)
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import eurostat
import wbgapi as wb

OUTPUT   = "charts"
RAW_DATA = "raw-data"
import os; os.makedirs(OUTPUT, exist_ok=True); os.makedirs(RAW_DATA, exist_ok=True)

def save_csv(df, name):
    path = f"{RAW_DATA}/{name}.csv"
    df.to_csv(path)
    print(f"  saved {path}")

def wb_series(indicator, economies, year_range=(2000, 2025)):
    df = wb.data.DataFrame(indicator, economy=economies, time=range(*year_range))
    df = df.T
    df.index = df.index.str.replace("YR", "").astype(int)
    return df

PEERS_WB = ["GRC", "PRT", "ITA", "ESP", "CYP"]
WB_TO_LBL = {"GRC":"GR","PRT":"PT","ITA":"IT","ESP":"ES","CYP":"CY"}
PEER_LABELS = {"GR":"Greece","PT":"Portugal","IT":"Italy","ES":"Spain","CY":"Cyprus"}
COLORS = {"GR":"#c0392b","PT":"#e67e22","IT":"#27ae60","ES":"#2980b9","CY":"#8e44ad"}
PROG_START, PROG_END = 2010, 2018

def add_programme_shading(ax, label_y_frac=0.92):
    ax.axvspan(PROG_START, PROG_END, alpha=0.06, color="grey")
    ylim = ax.get_ylim()
    y = ylim[0] + (ylim[1] - ylim[0]) * label_y_frac
    ax.text((PROG_START + PROG_END) / 2, y, "Adjustment programmes\n2010-2018",
            ha="center", fontsize=8, color="#555")

def plot_peer_lines(ax, df, highlight="GR"):
    for iso in ["GR","PT","IT","ES","CY"]:
        if iso in df.columns:
            lw = 2.5 if iso == highlight else 1.4
            ax.plot(df.index, df[iso], label=PEER_LABELS[iso],
                    color=COLORS[iso], linewidth=lw, marker="o", markersize=3)

# ---------------------------------------------------------------------------
# 1. Current Account Balance (% of GDP)
# ---------------------------------------------------------------------------
print("Fetching current account...")
ca = wb_series("BN.CAB.XOKA.GD.ZS", PEERS_WB).rename(columns=WB_TO_LBL)
ca.index.name = "year"
save_csv(ca, "06a_current_account_pct_gdp")

fig, ax = plt.subplots(figsize=(13, 5))
plot_peer_lines(ax, ca)
ax.axhline(0, color="black", linewidth=0.8)
ax.fill_between(ca.index, ca["GR"], 0, where=ca["GR"] < 0, alpha=0.12, color=COLORS["GR"])
add_programme_shading(ax, label_y_frac=0.92)
if "GR" in ca.columns:
    el = ca["GR"].dropna()
    trough = el.idxmin()
    ax.annotate(f"Pre-crisis deficit\n{int(trough)}: {el[trough]:.0f}%",
                xy=(trough, el[trough]),
                xytext=(trough + 2, el[trough] - 1),
                fontsize=9, ha="left", color=COLORS["GR"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["GR"], lw=0.8))
ax.set_title("Current Account Balance (% of GDP)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/06a_current_account.png", dpi=150); plt.close()
print("  saved 06a_current_account.png")

# ---------------------------------------------------------------------------
# 2. Greek BoP: Goods vs Services balance — the distinctive Greek pattern
# ---------------------------------------------------------------------------
print("Fetching Greek BoP (goods vs services)...")
df_bop = eurostat.get_data_df("bop_c6_a")
common = ((df_bop["stk_flow"]=="BAL") & (df_bop["partner"]=="WRL_REST") &
          (df_bop["currency"]=="MIO_EUR") & (df_bop["geo\\TIME_PERIOD"]=="EL") &
          (df_bop["sectpart"]=="S1") & (df_bop["sector10"]=="S1"))
year_cols = sorted([c for c in df_bop.columns if str(c).isdigit() and 2000 <= int(c) <= 2024])

components = {}
for item in ["G", "S", "IN1", "IN2", "CA"]:
    sub = df_bop[common & (df_bop["bop_item"] == item)]
    if not sub.empty:
        s = sub[year_cols].iloc[0].astype(float)
        s.index = s.index.astype(int)
        components[item] = s / 1000  # to € bn

bop_df = pd.DataFrame(components)
bop_df.index.name = "year"
bop_df.columns = ["Goods", "Services", "Primary income", "Secondary income", "Current account"]
save_csv(bop_df, "06b_greek_bop_components_bn_eur")

fig, ax = plt.subplots(figsize=(13, 5))
ax.bar(bop_df.index, bop_df["Goods"], label="Goods balance",
       color="#c0392b", alpha=0.85, width=0.7)
ax.bar(bop_df.index, bop_df["Services"], label="Services balance",
       color="#27ae60", alpha=0.85, width=0.7,
       bottom=bop_df["Goods"].clip(upper=0))  # stack above the negative goods
ax.plot(bop_df.index, bop_df["Current account"], label="Current account (total)",
        color="black", linewidth=2.5, marker="o", markersize=4)
ax.axhline(0, color="black", linewidth=0.8)
add_programme_shading(ax, label_y_frac=0.92)
ax.set_title("Greece: Balance of Payments Components (€ billions)\n"
             "Services surplus (tourism + shipping) partly offsets the goods deficit",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("€ billions")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"€{x:.0f}bn"))
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/06b_goods_vs_services.png", dpi=150); plt.close()
print("  saved 06b_goods_vs_services.png")

# ---------------------------------------------------------------------------
# 3. Tourism (SD travel) and Shipping (SC transport) services credits — the two pillars
# ---------------------------------------------------------------------------
print("Fetching tourism & shipping receipts...")
service_data = {}
for code, label in [("SC", "Transport (mainly shipping)"), ("SD", "Travel (tourism)")]:
    sub = df_bop[(df_bop["bop_item"]==code) & (df_bop["stk_flow"]=="CRE") &
                 (df_bop["partner"]=="WRL_REST") & (df_bop["currency"]=="MIO_EUR") &
                 (df_bop["geo\\TIME_PERIOD"]=="EL") & (df_bop["sectpart"]=="S1") &
                 (df_bop["sector10"]=="S1")]
    if not sub.empty:
        s = sub[year_cols].iloc[0].astype(float)
        s.index = s.index.astype(int)
        service_data[label] = s / 1000

svc_df = pd.DataFrame(service_data)
svc_df.index.name = "year"
save_csv(svc_df, "06c_tourism_shipping_credits_bn_eur")

fig, ax = plt.subplots(figsize=(13, 5))
ax.stackplot(svc_df.index,
             svc_df["Transport (mainly shipping)"].fillna(0),
             svc_df["Travel (tourism)"].fillna(0),
             labels=["Transport (mainly shipping)", "Travel (tourism)"],
             colors=["#2980b9", "#e67e22"], alpha=0.85)
add_programme_shading(ax, label_y_frac=0.92)
# Mark COVID 2020
ax.axvline(2020, color="black", linestyle=":", linewidth=0.7, alpha=0.6)
ax.text(2020, svc_df.sum(axis=1).max() * 0.98, "COVID",
        rotation=90, va="top", ha="right", fontsize=8, color="#333")
ax.set_title("Greece: Tourism + Shipping Services Receipts (€ billions, gross credits)",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("€ billions")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"€{x:.0f}bn"))
ax.legend(loc="upper left", fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/06c_tourism_shipping.png", dpi=150); plt.close()
print("  saved 06c_tourism_shipping.png")

# ---------------------------------------------------------------------------
# 4. FDI net inflows (% of GDP)
# ---------------------------------------------------------------------------
print("Fetching FDI data...")
fdi = wb_series("BX.KLT.DINV.WD.GD.ZS", PEERS_WB).rename(columns=WB_TO_LBL)
fdi.index.name = "year"
save_csv(fdi, "06d_fdi_net_inflows_pct_gdp")

fig, ax = plt.subplots(figsize=(13, 5))
# Drop Cyprus from chart only — its SPV pass-through flows swing ±300-400% of GDP
# and dominate the y-axis. Data remains in the CSV.
fdi_plot = fdi.drop(columns=[c for c in ["CY"] if c in fdi.columns])
plot_peer_lines(ax, fdi_plot)
ax.axhline(0, color="black", linewidth=0.8)
add_programme_shading(ax, label_y_frac=0.92)
ax.set_title("FDI Net Inflows (% of GDP)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
fig.text(0.5, -0.01,
         "Cyprus excluded from chart: SPV pass-through flows produce extreme values (e.g. +432% 2019, −296% 2020). Data retained in CSV.",
         ha="center", fontsize=8, color="#555", style="italic")
plt.tight_layout(); plt.savefig(f"{OUTPUT}/06d_fdi.png", dpi=150, bbox_inches="tight"); plt.close()
print("  saved 06d_fdi.png")

# ---------------------------------------------------------------------------
# 5. RRF disbursement progress — hardcoded from EC Recovery & Resilience Scoreboard
# ---------------------------------------------------------------------------
# Allocation (grants + loans) and disbursements as of ~mid-2025.
# Sources: EC Recovery & Resilience Scoreboard; figures rounded.
print("Building RRF disbursement chart...")
rrf = {
    # country: (total allocation €bn, disbursed €bn, allocation % 2023 GDP)
    "Greece":    {"alloc": 36.0, "disb": 22.3, "alloc_pct_gdp": 16.5},
    "Italy":     {"alloc": 194.4, "disb": 122.0, "alloc_pct_gdp": 9.3},
    "Spain":     {"alloc": 163.0, "disb": 60.5, "alloc_pct_gdp": 11.0},
    "Portugal":  {"alloc": 22.2, "disb": 7.6, "alloc_pct_gdp": 8.4},
    "Romania":   {"alloc": 28.5, "disb": 9.7, "alloc_pct_gdp": 9.4},
    "Croatia":   {"alloc": 10.0, "disb": 5.7, "alloc_pct_gdp": 13.5},
    "Cyprus":    {"alloc": 1.2, "disb": 0.5, "alloc_pct_gdp": 4.0},
}
rrf_df = pd.DataFrame(rrf).T
rrf_df["disb_pct"] = (rrf_df["disb"] / rrf_df["alloc"]) * 100
rrf_df.index.name = "country"
save_csv(rrf_df, "06e_rrf_progress")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: Disbursement progress %
ax = axes[0]
order = rrf_df.sort_values("disb_pct")
bar_colors = ["#c0392b" if c == "Greece" else "#95a5a6" for c in order.index]
ax.barh(order.index, order["disb_pct"], color=bar_colors)
for i, v in enumerate(order["disb_pct"]):
    ax.text(v + 1, i, f"{v:.0f}%", va="center", fontsize=9)
ax.axvline(order["disb_pct"].mean(), color="#2980b9", linestyle="--", linewidth=1.2,
           label=f"Avg: {order['disb_pct'].mean():.0f}%")
ax.set_title("RRF Disbursement Rate (% of allocation, ~mid-2025)",
             fontsize=12, fontweight="bold")
ax.set_xlabel("% disbursed"); ax.legend(fontsize=9); ax.grid(axis="x", alpha=0.3)

# Right: Allocation size in % of 2023 GDP — emphasises Greece as a top per-capita recipient
ax2 = axes[1]
order2 = rrf_df.sort_values("alloc_pct_gdp")
bar_colors2 = ["#c0392b" if c == "Greece" else "#95a5a6" for c in order2.index]
ax2.barh(order2.index, order2["alloc_pct_gdp"], color=bar_colors2)
for i, v in enumerate(order2["alloc_pct_gdp"]):
    ax2.text(v + 0.2, i, f"{v:.1f}%", va="center", fontsize=9)
ax2.set_title("RRF Total Allocation (% of 2023 GDP)",
              fontsize=12, fontweight="bold")
ax2.set_xlabel("% of 2023 GDP"); ax2.grid(axis="x", alpha=0.3)

fig.suptitle("Greece is one of the largest per-capita RRF recipients in the EU",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/06e_rrf.png", dpi=150); plt.close()
print("  saved 06e_rrf.png")

print("\nDone — external sector charts saved to", OUTPUT)
