"""
03 — Sectoral Deep Dive: Lithium-Ion Batteries

The cleanest case for the "selective frontier leadership" thesis:
- China makes ~77% (2024 snapshot) and, per the IEA, over 80% (2025) of
  the world's Li-ion cells (concentration)
- Pack prices have fallen >90% since 2010 (cost frontier)
- LFP chemistry — the chemistry-bet China made and which won — is now
  ~half (2024) and, per the IEA, over 55% (2025) of new EV batteries
- China dominates the *upstream* processing of most battery materials
  (covered properly in §10; we tee up the chart here)

This script only READS data. Every chart's numbers live in a CSV under
raw-data/ with a `# source:` / `# url:` / `# retrieved:` header. To see
where any figure comes from, open the corresponding CSV — or consult
raw-data/SOURCES.md for the project-wide index.

Annotations are computed from the latest row of each CSV, so adding a
new year to a CSV updates the chart text automatically.
"""

import warnings
warnings.filterwarnings("ignore")

import glob
import os
import re
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


def latest_snapshot(prefix):
    """Return (name, year) of the newest raw-data/<prefix>_<year>_pct.csv."""
    files = glob.glob(f"{RAW_DATA}/{prefix}_*_pct.csv")
    years = {int(re.search(r"_(\d{4})_pct\.csv$", f).group(1)): f for f in files}
    year = max(years)
    return os.path.basename(years[year])[:-4], year


# ---------------------------------------------------------------------------
# 3a. Global Li-ion battery cell production share by country — snapshots
# ---------------------------------------------------------------------------
print("Battery cell production share by country (snapshots)...")
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
plt.tight_layout()
fig.subplots_adjust(bottom=0.24)
fig.text(
    0.99, 0.015,
    "IEA Global EV Outlook 2026: China produced over 80% of battery cells in 2025\n"
    "(no country split published). Source: IEA Global EV Outlook 2024–2026; SNE Research.\n"
    "See raw-data/03a_battery_cell_production_share_pct.csv for URLs.",
    fontsize=8, color="#555", va="bottom", ha="right")
plt.savefig(f"{OUTPUT}/03a_battery_cell_production_share.png", dpi=150); plt.close()
print("  saved 03a_battery_cell_production_share.png")


# ---------------------------------------------------------------------------
# 3b. Top global battery makers — market share, latest snapshot year
# ---------------------------------------------------------------------------
makers_name, makers_year = latest_snapshot("03b_top_battery_makers")
print(f"Top battery makers global share, {makers_year}...")
makers = load(makers_name)

color_map = {"China": COLOR_CN, "Korea": COLOR_KR, "Japan": COLOR_JP,
             "Mixed": COLOR_OTHER}
bar_colors = [color_map[c] for c in makers["country"]]

fig, ax = plt.subplots(figsize=(11, 5.5))
y_pos = range(len(makers))
ax.barh(y_pos, makers["share"], color=bar_colors, edgecolor="white")
ax.set_yticks(y_pos); ax.set_yticklabels(makers["maker"])
ax.invert_yaxis()
ax.set_xlabel(f"% of global EV battery installations (kWh, {makers_year})")
ax.set_title(f"Top Global EV Battery Makers — Market Share, {makers_year}",
             fontsize=13, fontweight="bold")
for i, (share, country) in enumerate(zip(makers["share"], makers["country"])):
    ax.text(share + 0.4, i, f"{share:.1f}% · {country}",
            va="center", fontsize=9.5, color="#222")
ax.set_xlim(0, max(45, makers["share"].max() * 1.2))
by_country = makers.groupby("country")["share"].sum()
big_two_share = makers.loc[makers["maker"].isin(["CATL", "BYD"]), "share"].sum()
ax.annotate(
    f"Chinese makers in top 10: {by_country.get('China', 0):.1f}% of global installations\n"
    f"(CATL + BYD alone: {big_two_share:.1f}%)\n"
    f"Korean: {by_country.get('Korea', 0):.1f}% · Japanese: {by_country.get('Japan', 0):.1f}%\n\n"
    f"Source: SNE Research, full-year {makers_year}; see raw-data/{makers_name}.csv.",
    xy=(0.99, 0.02), xycoords="axes fraction",
    fontsize=9, color="#222", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#fdf2ee",
              edgecolor=COLOR_CN, linewidth=1.0))
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/03b_top_battery_makers_{makers_year}.png", dpi=150); plt.close()
print(f"  saved 03b_top_battery_makers_{makers_year}.png")


# ---------------------------------------------------------------------------
# 3c. Lithium-ion battery pack prices ($/kWh)
# ---------------------------------------------------------------------------
print("BNEF battery pack price survey...")
prices = load("03c_battery_pack_price_usd_per_kwh", index_col="year")
p = prices["usd_per_kwh"]
p_first_yr, p_last_yr = p.index.min(), p.index.max()
p_drop = (1 - p[p_last_yr] / p[p_first_yr]) * 100

fig, ax = plt.subplots(figsize=(13, 5.2))
ax.fill_between(prices.index, 0, p, color=COLOR_CN, alpha=0.10)
ax.plot(prices.index, p, color=COLOR_CN, linewidth=2.8,
        marker="o", markersize=6)
for x, y in zip(prices.index, p):
    ax.text(x + 0.12, y + 22, f"\\${y:,}", ha="left", va="bottom", fontsize=8.5, color="#222")
ax.axhline(100, color="#888", linestyle="--", linewidth=1)
ax.text(p_first_yr - 0.3, 108, "\\$100/kWh", fontsize=8, color="#666",
        ha="left", va="bottom")
ax.set_title("Lithium-Ion Battery Pack Price Trajectory — $/kWh, Volume-Weighted Average",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year")
ax.set_ylabel("USD per kWh (survey-year dollars)")
ax.set_ylim(0, max(1500, p.max() * 1.1))
ax.set_xlim(p_first_yr - 0.6, p_last_yr + 0.9)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
ax.tick_params(axis="x", labelsize=9)
ax.annotate(
    f"{p_first_yr} → {p_last_yr}: average pack price fell from "
    f"\\${p[p_first_yr]:,} → \\${p[p_last_yr]:,} per kWh — a {p_drop:.0f}% drop.\n"
    "2021–22 uptick reflects the lithium price spike; the decline resumed\n"
    f"in 2023–{p_last_yr} on Chinese LFP scale-up and cell overcapacity.\n\n"
    "Each point is BNEF's headline for that survey year (dollars of that year).\n"
    "Source: BloombergNEF annual Lithium-Ion Battery Price Survey.\n"
    "See raw-data/03c_*.csv for URLs.",
    xy=(0.45, 0.62), xycoords="axes fraction",
    fontsize=9, color="#222", va="center", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/03c_battery_pack_prices.png", dpi=150); plt.close()
print("  saved 03c_battery_pack_prices.png")


# ---------------------------------------------------------------------------
# 3d. EV battery chemistry share — LFP vs NMC/NCA
# ---------------------------------------------------------------------------
print("LFP vs NMC chemistry share...")
chem = load("03d_ev_battery_chemistry_share_pct", index_col="year")
c_first, c_last = chem.index.min(), chem.index.max()

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
    f"~{chem.loc[c_first, 'LFP']}% of global EV-battery deployments in {c_first} "
    f"to ~{chem.loc[c_last, 'LFP']}% in {c_last}.\n"
    "Cheaper, longer cycle life, no cobalt — Chinese makers bet on it\n"
    "while most Western/Korean makers focused on higher-density NMC.\n"
    "IEA GEVO 2026: LFP was over 55% of EV batteries deployed in 2025\n"
    "(no full chemistry split published, so not plotted).\n\n"
    "Source: IEA Global EV Outlook 2024, 2025 + 2026.\n"
    "See raw-data/03d_*.csv for URLs.",
    xy=(0.02, 0.95), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/03d_battery_chemistry_share.png", dpi=150); plt.close()
print("  saved 03d_battery_chemistry_share.png")


# ---------------------------------------------------------------------------
# 3e. CATL + BYD combined share of global EV battery market
# ---------------------------------------------------------------------------
print("CATL+BYD combined share trajectory...")
big_two = load("03e_catl_byd_market_share_pct", index_col="year")
big_two["Combined"] = big_two["CATL"] + big_two["BYD"]
b_first, b_last = big_two.index.min(), big_two.index.max()
peak_byd_yr = big_two["BYD"].idxmax()

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
ax.set_ylim(0, max(80, big_two["Combined"].max() * 1.45))
ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
ax.legend(ncol=3, fontsize=10, loc="upper left")
ax.grid(axis="y", alpha=0.3)
byd_note = (f"BYD's share peaked in {peak_byd_yr} ({big_two.loc[peak_byd_yr, 'BYD']:.1f}%)"
            f" and was {big_two.loc[b_last, 'BYD']:.1f}% in {b_last}."
            if peak_byd_yr != b_last else
            f"BYD's share reached a high of {big_two.loc[b_last, 'BYD']:.1f}% in {b_last}.")
ax.annotate(
    f"Two Chinese makers held {big_two.loc[b_last, 'Combined']:.1f}% of the global "
    f"EV-battery market in {b_last}.\n"
    f"CATL alone: {big_two.loc[b_first, 'CATL']:.0f}% ({b_first}) → "
    f"{big_two.loc[b_last, 'CATL']:.1f}% ({b_last}).\n"
    f"{byd_note}\n\n"
    "Source: SNE Research annual roundups.\n"
    "See raw-data/03e_*.csv for URLs.",
    xy=(0.01, 0.86), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/03e_catl_byd_share.png", dpi=150); plt.close()
print("  saved 03e_catl_byd_share.png")


# ---------------------------------------------------------------------------
# 3f. China's share of battery-material refining & components, ca. 2023
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
ax.set_xlabel("% of global processing / production (ca. 2023)")
ax.set_title("China's Share of Battery Material Refining and Components — ca. 2023",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
fig.subplots_adjust(bottom=0.22)
fig.text(
    0.99, 0.015,
    "Cell assembly can be built anywhere in ~2 years; precursor chemistry and refining\n"
    "took China 20+ years. This is the strategic part — covered in detail in §10.\n"
    "IEA GEVO 2026 (2025 data): ~85% of cathode and >90% of anode active material.\n"
    "Source: IEA Global Critical Minerals Outlook 2024. See raw-data/03f_*.csv for URLs.",
    fontsize=9, color="#222", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#fdf2ee",
              edgecolor=COLOR_CN, linewidth=1.0))
plt.savefig(f"{OUTPUT}/03f_china_battery_materials.png", dpi=150); plt.close()
print("  saved 03f_china_battery_materials.png")


print("\nDone — battery charts saved to", OUTPUT)
