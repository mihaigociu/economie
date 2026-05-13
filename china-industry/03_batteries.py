"""
03 — Sectoral Deep Dive: Lithium-Ion Batteries

The cleanest case for the "selective frontier leadership" thesis:
- China makes ~75-80% of the world's Li-ion cells (concentration)
- Pack prices have fallen 90% since 2010 (cost frontier)
- LFP chemistry — the chemistry-bet China made and which won — now
  ~half of new EV batteries globally
- China dominates the *upstream* processing of every battery material
  (covered properly in §10; we tee up the chart here)

This script only READS data. Every chart's numbers live in a CSV under
raw-data/ with a `# source:` / `# url:` / `# retrieved:` header. To see
where any figure comes from, open the corresponding CSV — or consult
raw-data/SOURCES.md for the project-wide index.
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
COLOR_KR     = "#e67e22"
COLOR_JP     = "#8e44ad"
COLOR_US     = "#2980b9"
COLOR_EU     = "#7f8c8d"
COLOR_OTHER  = "#bdc3c7"


def load(name, **kwargs):
    """Read a CSV from raw-data/, stripping `#`-prefixed source-header lines."""
    return pd.read_csv(f"{RAW_DATA}/{name}.csv", comment="#", **kwargs)


# ---------------------------------------------------------------------------
# 3a. Global Li-ion battery cell production share by country — three snapshots
# ---------------------------------------------------------------------------
print("Battery cell production share by country (3 snapshots)...")
prod = load("03a_battery_cell_production_share_pct", index_col="year")

fig, ax = plt.subplots(figsize=(11, 5.5))
prod.plot.bar(stacked=True, ax=ax,
              color=[COLOR_CN, COLOR_KR, COLOR_JP, COLOR_US, COLOR_EU, COLOR_OTHER],
              width=0.55, edgecolor="white", linewidth=0.6)
ax.set_title("Global Lithium-Ion Battery Cell Production — Share by Country",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year (snapshot)"); ax.set_ylabel("% of global cell production")
ax.set_ylim(0, 100)
ax.set_xticklabels(prod.index, rotation=0)
ax.legend(ncol=6, loc="upper center", bbox_to_anchor=(0.5, -0.10), fontsize=9)
ax.grid(axis="y", alpha=0.3)
for i, year in enumerate(prod.index):
    ax.text(i, prod.loc[year, "China"] / 2,
            f"{prod.loc[year, 'China']}%",
            ha="center", va="center", fontsize=14, color="white",
            fontweight="bold")
ax.annotate(
    "Source: IEA Global EV Outlook 2024 + 2025; SNE Research.\n"
    "See raw-data/03a_battery_cell_production_share_pct.csv for URLs.",
    xy=(0.99, 0.02), xycoords="axes fraction",
    fontsize=8, color="#555", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
              edgecolor="#bbb", linewidth=0.6))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/03a_battery_cell_production_share.png", dpi=150); plt.close()
print("  saved 03a_battery_cell_production_share.png")


# ---------------------------------------------------------------------------
# 3b. Top global battery makers — market share 2024
# ---------------------------------------------------------------------------
print("Top battery makers global share, 2024...")
makers_2024 = load("03b_top_battery_makers_2024_pct")

color_map = {"China": COLOR_CN, "Korea": COLOR_KR, "Japan": COLOR_JP,
             "Mixed": COLOR_OTHER}
bar_colors = [color_map[c] for c in makers_2024["country"]]

fig, ax = plt.subplots(figsize=(11, 5.5))
y_pos = range(len(makers_2024))
ax.barh(y_pos, makers_2024["share"], color=bar_colors, edgecolor="white")
ax.set_yticks(y_pos); ax.set_yticklabels(makers_2024["maker"])
ax.invert_yaxis()
ax.set_xlabel("% of global EV battery installations (kWh, 2024)")
ax.set_title("Top Global EV Battery Makers — Market Share, 2024",
             fontsize=13, fontweight="bold")
for i, (share, country) in enumerate(zip(makers_2024["share"], makers_2024["country"])):
    ax.text(share + 0.4, i, f"{share:.1f}% · {country}",
            va="center", fontsize=9.5, color="#222")
ax.set_xlim(0, 45)
china_total = makers_2024.loc[makers_2024["country"] == "China", "share"].sum()
ax.annotate(
    f"Chinese makers combined: {china_total:.1f}% of global installations\n"
    "(CATL + BYD alone: 55.1%)\n\n"
    "Source: SNE Research (Jan 2025); see raw-data/03b_*.csv for URLs.",
    xy=(0.99, 0.02), xycoords="axes fraction",
    fontsize=9, color="#222", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#fdf2ee",
              edgecolor=COLOR_CN, linewidth=1.0))
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/03b_top_battery_makers_2024.png", dpi=150); plt.close()
print("  saved 03b_top_battery_makers_2024.png")


# ---------------------------------------------------------------------------
# 3c. Lithium-ion battery pack prices ($/kWh, nominal USD)
# ---------------------------------------------------------------------------
print("BNEF battery pack price survey...")
prices = load("03c_battery_pack_price_usd_per_kwh", index_col="year")

fig, ax = plt.subplots(figsize=(13, 5.2))
ax.fill_between(prices.index, 0, prices["usd_per_kwh"], color=COLOR_CN, alpha=0.10)
ax.plot(prices.index, prices["usd_per_kwh"], color=COLOR_CN, linewidth=2.8,
        marker="o", markersize=6)
for x, y in zip(prices.index, prices["usd_per_kwh"]):
    ax.text(x, y + 30, f"\\${y}", ha="center", va="bottom", fontsize=8.5, color="#222")
ax.set_title("Lithium-Ion Battery Pack Price Trajectory — $/kWh, Volume-Weighted Average",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("USD per kWh (nominal)")
ax.set_ylim(0, 1500)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
ax.annotate(
    "2010 → 2024: pack price fell from \\$1,355 → \\$115 per kWh — a 91% drop.\n"
    "2021–22 uptick reflects the lithium price spike; cost decline resumed 2023–24\n"
    "as Chinese LFP scale-up and supply normalised.\n\n"
    "Source: BloombergNEF annual Lithium-Ion Battery Price Survey.\n"
    "See raw-data/03c_*.csv for URLs.",
    xy=(0.55, 0.55), xycoords="axes fraction",
    fontsize=9, color="#222", va="center", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/03c_battery_pack_prices.png", dpi=150); plt.close()
print("  saved 03c_battery_pack_prices.png")


# ---------------------------------------------------------------------------
# 3d. EV battery chemistry share — LFP vs NMC/NCA, 2018–2024
# ---------------------------------------------------------------------------
print("LFP vs NMC chemistry share...")
chem = load("03d_ev_battery_chemistry_share_pct", index_col="year")

fig, ax = plt.subplots(figsize=(13, 5.2))
ax.stackplot(chem.index, chem["LFP"], chem["NMC + NCA"], chem["Other / NaIon"],
             labels=["LFP (lithium iron phosphate)",
                     "NMC / NCA (nickel-based)",
                     "Other / Sodium-ion"],
             colors=[COLOR_CN, COLOR_US, COLOR_OTHER],
             alpha=0.85, edgecolor="white", linewidth=0.8)
ax.set_title("Global EV Battery Chemistry Mix — Share of New Deployments",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of new EV battery deployments")
ax.set_ylim(0, 100)
ax.legend(loc="lower right", fontsize=9, framealpha=0.9)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
ax.annotate(
    "LFP — pioneered to commercial scale by CATL and BYD — rose from\n"
    "~5% of global EV-battery deployments in 2018 to ~48% in 2024.\n"
    "Cheaper, longer cycle life, no cobalt — Chinese makers bet on it\n"
    "while most Western/Korean makers focused on higher-density NMC.\n\n"
    "Source: IEA Global EV Outlook 2024 + 2025.\n"
    "See raw-data/03d_*.csv for URLs.",
    xy=(0.02, 0.95), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/03d_battery_chemistry_share.png", dpi=150); plt.close()
print("  saved 03d_battery_chemistry_share.png")


# ---------------------------------------------------------------------------
# 3e. CATL + BYD combined share of global EV battery market, 2018–2024
# ---------------------------------------------------------------------------
print("CATL+BYD combined share trajectory...")
big_two = load("03e_catl_byd_market_share_pct", index_col="year")
big_two["Combined"] = big_two["CATL"] + big_two["BYD"]

fig, ax = plt.subplots(figsize=(13, 5.2))
ax.bar(big_two.index - 0.18, big_two["CATL"], width=0.36, color=COLOR_CN,
       label="CATL", edgecolor="white", linewidth=0.5)
ax.bar(big_two.index + 0.18, big_two["BYD"], width=0.36, color="#a93226",
       label="BYD", edgecolor="white", linewidth=0.5)
ax.plot(big_two.index, big_two["Combined"], color="#222", linewidth=2.0,
        marker="o", markersize=5, label="CATL + BYD combined", zorder=4)
for x, y in zip(big_two.index, big_two["Combined"]):
    ax.text(x, y + 1.5, f"{y:.1f}%", ha="center", va="bottom",
            fontsize=9, color="#222", fontweight="bold")
ax.set_title("CATL and BYD — Share of Global EV Battery Installations",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of global EV battery installations")
ax.set_ylim(0, 65)
ax.legend(ncol=3, fontsize=10, loc="upper left")
ax.grid(axis="y", alpha=0.3)
ax.annotate(
    "Two Chinese makers, both based in Shenzhen/Ningde, now hold ~55%\n"
    "of the global EV-battery market. CATL passed 30% share alone in 2021;\n"
    "BYD tripled its share over 2020–2024.\n\n"
    "Source: SNE Research annual roundups.\n"
    "See raw-data/03e_*.csv for URLs.",
    xy=(0.99, 0.97), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/03e_catl_byd_share.png", dpi=150); plt.close()
print("  saved 03e_catl_byd_share.png")


# ---------------------------------------------------------------------------
# 3f. China's share of battery-material refining & components, 2023
# ---------------------------------------------------------------------------
print("China's share of battery materials processing...")
materials = load("03f_china_share_battery_materials_pct").sort_values("china_share")

fig, ax = plt.subplots(figsize=(12, 6.5))
y_pos = range(len(materials))
ax.barh(y_pos, materials["china_share"], color=COLOR_CN, alpha=0.85,
        edgecolor="white")
ax.set_yticks(y_pos); ax.set_yticklabels(materials["stage"])
for i, v in enumerate(materials["china_share"]):
    ax.text(v + 1, i, f"{v}%", va="center", fontsize=10, color="#222",
            fontweight="bold")
ax.axvline(50, color="#888", linestyle="--", linewidth=1)
ax.text(50, len(materials) - 0.5, "50% line", fontsize=8, color="#666",
        ha="center", va="bottom")
ax.set_xlim(0, 105)
ax.set_xlabel("% of global processing / production (2023)")
ax.set_title("China's Share of Battery Material Refining and Components — 2023",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
ax.annotate(
    "Cell assembly can be built anywhere in ~2 years.\n"
    "Precursor chemistry and refining took China 20+ years.\n"
    "This is the strategic part — covered in detail in §10.\n\n"
    "Source: IEA Global Critical Minerals Outlook 2024.\n"
    "See raw-data/03f_*.csv for URLs.",
    xy=(0.62, 0.05), xycoords="axes fraction",
    fontsize=9, color="#222", va="bottom", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#fdf2ee",
              edgecolor=COLOR_CN, linewidth=1.0))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/03f_china_battery_materials.png", dpi=150); plt.close()
print("  saved 03f_china_battery_materials.png")


print("\nDone — battery charts saved to", OUTPUT)
