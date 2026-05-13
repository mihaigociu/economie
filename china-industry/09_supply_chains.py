"""
09 — Supply-Chain Leverage

The second pillar of the thesis: even where China isn't yet innovating
at the frontier, it controls upstream chokepoints that give it leverage
over those who do.

The data:
- Rare earths: China ~68% of mining, ~90% of refining (USGS, IEA)
- Lithium: mining diversified (Australia 52%); refining ~70% China
- Cobalt: DRC ~74% of mining; refining ~75% China
- Solar PV: >80% Chinese share at every stage of the value chain
- Shipbuilding: China ~57% of global new-build tonnage (2024), up from
  ~6% in 2000
- Pharma APIs: ~28-40% of US/EU generic-API supply traces to China;
  high "double dependency" via India intermediates
- Critical minerals (refining): gallium 98%, RE 90%, graphite 90%, etc.
- Export-control episodes 2010-2024 (RE 2010, Ga/Ge 2023, graphite 2023,
  RE-tech 2023/2024, antimony 2024) — the leverage being deployed

This script only READS data. Every chart's numbers live in a CSV under
raw-data/ with a `# source:` header. See raw-data/SOURCES.md.
"""

import warnings
warnings.filterwarnings("ignore")

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

OUTPUT   = "charts"
RAW_DATA = "raw-data"
os.makedirs(OUTPUT, exist_ok=True)

COLOR_CN     = "#c0392b"
COLOR_US     = "#2980b9"
COLOR_EU     = "#7f8c8d"
COLOR_JP     = "#8e44ad"
COLOR_KR     = "#e67e22"
COLOR_IN     = "#d4ac0d"
COLOR_AU     = "#16a085"
COLOR_OTHER  = "#bdc3c7"


def load(name, **kwargs):
    return pd.read_csv(f"{RAW_DATA}/{name}.csv", comment="#", **kwargs)


# ---------------------------------------------------------------------------
# 9a. Rare earths — mining vs refining shares
# ---------------------------------------------------------------------------
print("Rare earths — mining and refining shares...")
re = load("09a_rare_earth_mining_refining_pct")
re = re.set_index("country")
# Sort by mining for display
re = re.sort_values("mining", ascending=True)

color_map = {"China": COLOR_CN, "United States": COLOR_US,
             "Australia": COLOR_AU, "Myanmar": "#8e44ad",
             "Vietnam": "#16a085", "Estonia": "#7f8c8d",
             "Malaysia": "#e67e22", "Other": COLOR_OTHER}
bar_colors = [color_map[c] for c in re.index]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

y_pos = range(len(re))
ax1.barh(y_pos, re["mining"], color=bar_colors, edgecolor="white")
ax1.set_yticks(y_pos); ax1.set_yticklabels(re.index)
for i, v in enumerate(re["mining"]):
    if v > 0:
        ax1.text(v + 1, i, f"{v}%", va="center", fontsize=10, color="#222",
                 fontweight="bold")
ax1.set_xlim(0, 80)
ax1.set_xlabel("% of global mine production")
ax1.set_title("Rare-earth mining — geographically diversifying",
              fontsize=12, fontweight="bold")
ax1.grid(axis="x", alpha=0.3)

ax2.barh(y_pos, re["refining"], color=bar_colors, edgecolor="white")
ax2.set_yticks(y_pos); ax2.set_yticklabels(re.index)
for i, v in enumerate(re["refining"]):
    if v > 0:
        ax2.text(v + 1, i, f"{v}%", va="center", fontsize=10, color="#222",
                 fontweight="bold")
ax2.set_xlim(0, 100)
ax2.set_xlabel("% of global refining / separation")
ax2.set_title("Rare-earth refining — the real chokepoint",
              fontsize=12, fontweight="bold")
ax2.grid(axis="x", alpha=0.3)

plt.suptitle("Rare Earths — Mining (left) vs Refining (right), Share by Country, 2023",
             fontsize=13, fontweight="bold", y=1.02)
fig.text(0.5, -0.02,
         "Source: USGS Mineral Commodity Summaries 2024 (mining); IEA Global Critical Minerals Outlook 2024 (refining). "
         "See raw-data/09a_*.csv for URLs.",
         ha="center", fontsize=9, color="#555")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/09a_rare_earths_mining_refining.png", dpi=150,
            bbox_inches="tight")
plt.close()
print("  saved 09a_rare_earths_mining_refining.png")


# ---------------------------------------------------------------------------
# 9b. Lithium & Cobalt — mining vs refining
# ---------------------------------------------------------------------------
print("Lithium & cobalt — mining vs refining...")
lc = load("09b_lithium_cobalt_mining_vs_refining_pct")

fig, axes = plt.subplots(2, 2, figsize=(14, 8))

for row_idx, mineral in enumerate(["Lithium", "Cobalt"]):
    for col_idx, stage in enumerate(["Mining", "Refining"]):
        ax = axes[row_idx, col_idx]
        df = (lc[(lc["mineral"] == mineral) & (lc["stage"] == stage)]
              .sort_values("share", ascending=True))
        bar_colors = []
        for c in df["country"]:
            if c == "China":
                bar_colors.append(COLOR_CN)
            elif c == "Australia":
                bar_colors.append(COLOR_AU)
            elif c == "DR Congo":
                bar_colors.append("#16a085")
            elif c == "Chile":
                bar_colors.append("#e67e22")
            elif c == "Indonesia":
                bar_colors.append("#8e44ad")
            else:
                bar_colors.append(COLOR_OTHER)
        y_pos = range(len(df))
        ax.barh(y_pos, df["share"], color=bar_colors, edgecolor="white")
        ax.set_yticks(y_pos); ax.set_yticklabels(df["country"])
        for i, v in enumerate(df["share"]):
            ax.text(v + 1, i, f"{v}%", va="center", fontsize=10,
                    color="#222", fontweight="bold")
        ax.set_xlim(0, 85)
        ax.set_xlabel(f"% of global {stage.lower()}")
        ax.set_title(f"{mineral} — {stage}", fontsize=12, fontweight="bold")
        ax.grid(axis="x", alpha=0.3)

plt.suptitle("Lithium and Cobalt — Mining (diversified) vs Refining (China-led), 2023",
             fontsize=13, fontweight="bold", y=1.00)
fig.text(0.5, -0.01,
         "Source: USGS Mineral Commodity Summaries 2024; IEA Global Critical Minerals Outlook 2024. "
         "See raw-data/09b_*.csv for URLs.",
         ha="center", fontsize=9, color="#555")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/09b_lithium_cobalt_chain.png", dpi=150,
            bbox_inches="tight")
plt.close()
print("  saved 09b_lithium_cobalt_chain.png")


# ---------------------------------------------------------------------------
# 9c. Solar PV value chain — China share at each stage
# ---------------------------------------------------------------------------
print("Solar PV value chain by stage...")
solar = load("09c_solar_pv_value_chain_pct")

fig, ax = plt.subplots(figsize=(13, 5.0))
y_pos = range(len(solar))
ax.barh(y_pos, solar["china_share"], color=COLOR_CN, alpha=0.85,
        edgecolor="white", label="China")
ax.barh(y_pos, solar["rest_of_world"], left=solar["china_share"],
        color=COLOR_OTHER, edgecolor="white", label="Rest of world")
ax.set_yticks(y_pos); ax.set_yticklabels(solar["stage"])
for i, v in enumerate(solar["china_share"]):
    ax.text(v / 2, i, f"{v}%\nChina", ha="center", va="center",
            fontsize=12, color="white", fontweight="bold")
ax.set_xlim(0, 100)
ax.set_xlabel("% of global manufacturing at each stage")
ax.set_title("Solar PV Manufacturing — China's Share at Each Value-Chain Stage (2023)",
             fontsize=13, fontweight="bold")
ax.legend(loc="upper right", fontsize=10, framealpha=0.95)
ax.grid(axis="x", alpha=0.3)
ax.annotate(
    "Polysilicon → wafer → cell → module. China holds >80% at every stage —\n"
    "the highest concentration in wafer (~97%), where polysilicon ingot pulling\n"
    "and slicing capacity took decades to build at scale.\n\n"
    "Source: IEA Solar PV Global Supply Chains 2022; IEA Renewables 2024.\n"
    "See raw-data/09c_*.csv for URLs.",
    xy=(0.62, 0.65), xycoords="axes fraction",
    fontsize=9, color="#222", va="center", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/09c_solar_pv_chain.png", dpi=150); plt.close()
print("  saved 09c_solar_pv_chain.png")


# ---------------------------------------------------------------------------
# 9d. Shipbuilding — China's share of global new-build tonnage
# ---------------------------------------------------------------------------
print("Shipbuilding share over time...")
ship = load("09d_shipbuilding_share_pct", index_col="year")

fig, ax = plt.subplots(figsize=(13, 5.5))
cols = ["China", "South Korea", "Japan", "Other"]
colors = [COLOR_CN, COLOR_KR, COLOR_JP, COLOR_OTHER]
ax.stackplot(ship.index, *[ship[c] for c in cols],
             labels=cols, colors=colors, alpha=0.88,
             edgecolor="white", linewidth=0.8)
for x in [2000, 2010, 2024]:
    if x in ship.index:
        cn = ship.loc[x, "China"]
        ax.text(x, cn / 2, f"{cn}%\nChina",
                ha="center", va="center", fontsize=11, color="white",
                fontweight="bold")
ax.set_title("Global Shipbuilding — Share of New-Build Tonnage by Country, 2000–2024",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of global new-build deliveries (CGT)")
ax.set_ylim(0, 100)
ax.legend(loc="upper right", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
ax.annotate(
    "China's share rose from ~6% in 2000 to ~57% by 2024 —\n"
    "overtaking South Korea around 2009. Maritime infrastructure is\n"
    "the backbone of trade — including LNG carriers, containerships,\n"
    "and increasingly naval platforms (dual-use shipyards).\n\n"
    "Source: UNCTAD Review of Maritime Transport; Clarksons Research.\n"
    "See raw-data/09d_*.csv for URLs.",
    xy=(0.02, 0.95), xycoords="axes fraction",
    fontsize=9, color="white", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#2c3e50",
              edgecolor="white", linewidth=0.8, alpha=0.85))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/09d_shipbuilding_share.png", dpi=150); plt.close()
print("  saved 09d_shipbuilding_share.png")


# ---------------------------------------------------------------------------
# 9e. Pharma API dependency — US and EU
# ---------------------------------------------------------------------------
print("Pharma API dependency...")
api = load("09e_pharma_api_dependency_pct").set_index("market")

fig, ax = plt.subplots(figsize=(13, 5.0))
cols = ["china", "india", "europe", "united_states", "other"]
labels = ["China", "India", "Europe", "United States", "Other"]
colors = [COLOR_CN, COLOR_IN, COLOR_EU, COLOR_US, COLOR_OTHER]
api[cols].plot.barh(stacked=True, ax=ax, color=colors, width=0.55,
                    edgecolor="white", linewidth=0.6)
ax.set_yticklabels(api.index)
for i, market in enumerate(api.index):
    cn = api.loc[market, "china"]
    ax.text(cn / 2, i, f"{cn}%\nChina", ha="center", va="center",
            fontsize=11, color="white", fontweight="bold")
ax.set_xlim(0, 100)
ax.set_xlabel("% of API supply, by origin region")
ax.set_title("Active Pharmaceutical Ingredient (API) Supply — by Origin Region",
             fontsize=13, fontweight="bold")
ax.legend(labels, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.18),
          fontsize=9)
ax.grid(axis="x", alpha=0.3)
ax.annotate(
    "China supplies ~28-40% of US/EU generic-API value directly.\n"
    "India is the largest visible source for finished generic-API forms,\n"
    "but India imports a large share of intermediate APIs from China —\n"
    "the 'double dependency' issue flagged in EU Strategic Dependencies 2021.\n\n"
    "Source: EU Strategic Dependencies report (SWD(2021) 352); US FDA API data.\n"
    "See raw-data/09e_*.csv for URLs.",
    xy=(0.99, 0.95), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/09e_pharma_api_dependency.png", dpi=150,
            bbox_inches="tight")
plt.close()
print("  saved 09e_pharma_api_dependency.png")


# ---------------------------------------------------------------------------
# 9f. Chinese export-control timeline, 2010-2024
# ---------------------------------------------------------------------------
print("Chinese export-control timeline...")
controls = load("09f_china_export_controls_timeline")
# Build a fractional year for plotting
controls["fyear"] = controls["year"] + controls["month"] / 12

fig, ax = plt.subplots(figsize=(14, 5.5))
ax.scatter(controls["fyear"], range(len(controls)),
           color=COLOR_CN, s=160, zorder=3, edgecolor="white", linewidth=1.5)
for i, row in controls.iterrows():
    ax.text(row["fyear"] + 0.15, i, f"{row['event']}",
            va="center", fontsize=9.5, color="#222")
    ax.text(row["fyear"] - 0.2, i, f"{int(row['year'])}",
            va="center", ha="right", fontsize=9, color=COLOR_CN,
            fontweight="bold")
ax.axhline(-0.5, color="#888", linewidth=0.5)
ax.set_xlim(2009, 2026)
ax.set_ylim(-0.7, len(controls) - 0.3)
ax.set_yticks([])
ax.set_xlabel("Year")
ax.set_title("Chinese Export Controls / Embargoes on Critical Minerals & Materials, 2010-2024",
             fontsize=13, fontweight="bold")
for spine in ("top", "right", "left"):
    ax.spines[spine].set_visible(False)
ax.grid(axis="x", alpha=0.3)
ax.invert_yaxis()
ax.annotate(
    "The leverage being deployed — but the WTO 2014 ruling (DS431) shows\n"
    "formal quota systems are challengeable. Recent (2023-2024) controls\n"
    "use export-licensing rather than quotas, which is more legally defensible.\n\n"
    "Source: MOFCOM; WTO DS431; Reuters / FT.\n"
    "See raw-data/09f_*.csv for URLs.",
    xy=(0.55, 0.55), xycoords="axes fraction",
    fontsize=8.5, color="#222", va="center", ha="center",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#fdf2ee",
              edgecolor=COLOR_CN, linewidth=1.0))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/09f_export_controls_timeline.png", dpi=150); plt.close()
print("  saved 09f_export_controls_timeline.png")


# ---------------------------------------------------------------------------
# 9g. Critical minerals overview — China's refining share by mineral
# ---------------------------------------------------------------------------
print("Critical minerals — China's refining share...")
cm = load("09g_critical_minerals_china_share_pct").sort_values("china_share")

fig, ax = plt.subplots(figsize=(13, 6.5))
y_pos = range(len(cm))
bar_colors = [COLOR_CN if v >= 50 else COLOR_OTHER
              for v in cm["china_share"]]
ax.barh(y_pos, cm["china_share"], color=bar_colors, alpha=0.85,
        edgecolor="white")
ax.set_yticks(y_pos); ax.set_yticklabels(cm["mineral"])
for i, v in enumerate(cm["china_share"]):
    ax.text(v + 1, i, f"{v}%", va="center", fontsize=10,
            color="#222", fontweight="bold")
ax.axvline(50, color="#888", linestyle="--", linewidth=1)
ax.text(50.5, len(cm) - 0.5, "50% line", fontsize=8, color="#666")
ax.set_xlim(0, 105)
ax.set_xlabel("China's share of global refining / processing capacity (%)")
ax.set_title("China's Share of Global Critical-Mineral Refining — 2023",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
ax.annotate(
    "Refining concentration is the leverage point, not mining.\n"
    "China refines >80% of supply for graphite, rare earths,\n"
    "tungsten, manganese, magnesium, gallium — and 60-75% for\n"
    "antimony, lithium, cobalt, germanium.\n"
    "Nickel is the outlier — refined mostly in Indonesia, Russia, Japan.\n\n"
    "Source: IEA Global Critical Minerals Outlook 2024.\n"
    "See raw-data/09g_*.csv for URLs.",
    xy=(0.45, 0.45), xycoords="axes fraction",
    fontsize=9, color="#222", va="center", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/09g_critical_minerals_overview.png", dpi=150); plt.close()
print("  saved 09g_critical_minerals_overview.png")


print("\nDone — supply-chain charts saved to", OUTPUT)
