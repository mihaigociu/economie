"""
06 — Sectoral Deep Dive: Robotics & Industrial Automation

The fourth frontier-leadership case. Robotics sits at the intersection
of China's three earlier strengths (manufacturing scale, EV/battery
components supply chain, applied AI), which makes it the natural next
frontier.

The data:
- China alone took ~54% of global new industrial-robot installations
  in 2023, more than US + EU + Japan + Korea combined
- Robot density in Chinese manufacturing overtook the US in 2021
- Chinese-brand robots have risen from ~30% of the domestic market in
  2015 to ~50% by 2024 — the Big Four (FANUC, Yaskawa, ABB, KUKA) are
  losing share at home
- DJI holds ~70%+ of the global consumer / prosumer drone market
- Chinese humanoid robots reached commercial pilot stage in 2024-25 at
  ~$16k pricing — an order of magnitude below Western equivalents

This script only READS data. Every chart's numbers live in a CSV under
raw-data/ with a `# source:` / `# url:` / `# retrieved:` header. See
raw-data/SOURCES.md for the project-wide source index.

Chart 06f (China's share of installations over time) is computed in this
script from the 06a CSV — no separate CSV is stored to avoid duplicating
the same data twice.
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
COLOR_OTHER  = "#bdc3c7"
COLOR_DE     = "#16a085"


def load(name, **kwargs):
    return pd.read_csv(f"{RAW_DATA}/{name}.csv", comment="#", **kwargs)


# ---------------------------------------------------------------------------
# 6a. Annual industrial-robot installations by country, 2012–2023
# ---------------------------------------------------------------------------
print("Industrial-robot installations by country...")
robots = load("06a_industrial_robot_installations_thousands", index_col="year")
robots["Global"] = robots.sum(axis=1)
robots["China_share_pct"] = (robots["China"] / robots["Global"] * 100).round(1)

fig, ax = plt.subplots(figsize=(13, 5.5))
cols = ["China", "Japan", "Korea", "United States", "Germany", "Rest of World"]
colors = [COLOR_CN, COLOR_JP, COLOR_KR, COLOR_US, COLOR_DE, COLOR_OTHER]
ax.stackplot(robots.index, *[robots[c] for c in cols],
             labels=cols, colors=colors, alpha=0.88,
             edgecolor="white", linewidth=0.7)
for x in robots.index:
    if x in [2015, 2018, 2021, 2023]:
        ax.text(x, robots.loc[x, "Global"] + 12,
                f"{robots.loc[x, 'China_share_pct']:.0f}%\nChina",
                ha="center", va="bottom", fontsize=8.5,
                color=COLOR_CN, fontweight="bold")
ax.set_title("Industrial-Robot Installations Worldwide — Thousands of Units, Annual",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("New robot installations (thousands)")
ax.set_ylim(0, 700)
ax.legend(loc="upper left", fontsize=9, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
ax.annotate(
    "China took ~54% of global new installations in 2023 —\n"
    "more than the US, EU, Japan, and Korea combined.\n\n"
    "Source: IFR World Robotics 2024 (headline figures).\n"
    "See raw-data/06a_*.csv for URLs.",
    xy=(0.02, 0.65), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/06a_industrial_robot_installations.png", dpi=150); plt.close()
print("  saved 06a_industrial_robot_installations.png")


# ---------------------------------------------------------------------------
# 6b. Robot density — industrial robots per 10,000 manufacturing workers
# ---------------------------------------------------------------------------
print("Robot density by country...")
density = load("06b_robot_density_per_10k_workers")
density["change"] = density["density_2023"] - density["density_2018"]
density_sorted = density.sort_values("density_2023", ascending=True)

fig, ax = plt.subplots(figsize=(13, 6.5))
y_pos = range(len(density_sorted))
bar_colors = [COLOR_CN if c == "China" else COLOR_OTHER
              for c in density_sorted["country"]]
ax.barh(y_pos, density_sorted["density_2018"], color=COLOR_OTHER,
        alpha=0.5, edgecolor="white", label="2018")
ax.barh(y_pos, density_sorted["density_2023"], color=bar_colors,
        alpha=0.85, edgecolor="white", label="2023", height=0.5)
ax.set_yticks(y_pos); ax.set_yticklabels(density_sorted["country"])
for i, (d18, d23) in enumerate(zip(density_sorted["density_2018"],
                                     density_sorted["density_2023"])):
    ax.text(d23 + 12, i, f"{d23}", va="center", fontsize=9,
            color="#222", fontweight="bold")
ax.set_xlabel("Robots per 10,000 manufacturing workers")
ax.set_title("Industrial-Robot Density — 2018 vs 2023",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
ax.set_xlim(0, 1100)
ax.annotate(
    "China's robot density tripled from 140 → 470 between 2018 and 2023,\n"
    "overtaking the United States in 2021 and closing on Germany.\n"
    "Korea remains the world leader at 1,012 robots per 10k workers.\n\n"
    "Source: IFR World Robotics 2024 — robot-density tables.\n"
    "See raw-data/06b_*.csv for URLs.",
    xy=(0.98, 0.05), xycoords="axes fraction",
    fontsize=9, color="#222", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/06b_robot_density.png", dpi=150); plt.close()
print("  saved 06b_robot_density.png")


# ---------------------------------------------------------------------------
# 6c. Chinese-brand share of China's domestic industrial-robot market
# ---------------------------------------------------------------------------
print("Chinese vs foreign-brand share of China's robot market...")
domestic_share = load("06c_china_domestic_robot_market_share_pct", index_col="year")

fig, ax = plt.subplots(figsize=(13, 5.0))
ax.fill_between(domestic_share.index, 0, domestic_share["chinese_brand"],
                color=COLOR_CN, alpha=0.85, label="Chinese-brand robots")
ax.fill_between(domestic_share.index, domestic_share["chinese_brand"],
                100, color=COLOR_OTHER, alpha=0.7,
                label="Foreign-brand (FANUC, Yaskawa, ABB, KUKA, etc.)")
for x, y in zip(domestic_share.index, domestic_share["chinese_brand"]):
    ax.text(x, y - 4, f"{y}%", ha="center", va="top", fontsize=10,
            color="white", fontweight="bold")
ax.axhline(50, color="#222", linestyle="--", linewidth=1, alpha=0.7)
ax.set_title("China's Domestic Industrial-Robot Market — Brand Origin Mix",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of robots installed in China")
ax.set_ylim(0, 100)
ax.legend(loc="upper right", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
ax.annotate(
    "Chinese-brand robots crossed 50% of domestic installations in 2024.\n"
    "Estun, Inovance, Siasun, EFORT, Han's Robot lead the domestic challenge.\n\n"
    "Source: Chinese MIIT annual summaries; IFR China-market reports.\n"
    "See raw-data/06c_*.csv for URLs.",
    xy=(0.02, 0.45), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/06c_china_domestic_robot_brands.png", dpi=150); plt.close()
print("  saved 06c_china_domestic_robot_brands.png")


# ---------------------------------------------------------------------------
# 6d. Consumer drone market — DJI dominance
# ---------------------------------------------------------------------------
print("Consumer drone market share snapshot...")
drones = load("06d_consumer_drone_market_share_pct")

color_map = {"China": COLOR_CN, "European Union": COLOR_EU,
             "United States": COLOR_US, "Mixed": COLOR_OTHER}
bar_colors = [color_map[c] for c in drones["country"]]

fig, ax = plt.subplots(figsize=(11, 5))
y_pos = range(len(drones))
ax.barh(y_pos, drones["global_share"], color=bar_colors,
        edgecolor="white")
ax.set_yticks(y_pos); ax.set_yticklabels(drones["maker"])
ax.invert_yaxis()
for i, v in enumerate(drones["global_share"]):
    ax.text(v + 1, i, f"{v}%", va="center", fontsize=10, color="#222",
            fontweight="bold")
ax.set_xlim(0, 85)
ax.set_xlabel("% of global consumer / prosumer drone market (units)")
ax.set_title("Consumer & Prosumer Drone Market — Global Share by Maker",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
ax.annotate(
    "DJI alone holds ~72% of the global consumer / prosumer drone market.\n"
    "Chinese makers combined: ~80% of units.\n"
    "US response: Blue UAS list restricts federal procurement; commercial\n"
    "and consumer markets remain wide open to DJI.\n\n"
    "Source: DJI disclosures; Drone Industry Insights public reports.\n"
    "See raw-data/06d_*.csv for URLs.",
    xy=(0.98, 0.05), xycoords="axes fraction",
    fontsize=9, color="#222", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#fdf2ee",
              edgecolor=COLOR_CN, linewidth=1.0))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/06d_consumer_drone_market.png", dpi=150); plt.close()
print("  saved 06d_consumer_drone_market.png")


# ---------------------------------------------------------------------------
# 6e. Humanoid robots — commercial pricing snapshot, late 2024 / early 2025
# ---------------------------------------------------------------------------
print("Humanoid robot commercial pricing snapshot...")
humanoids = load("06e_humanoid_robot_pricing_usd_k")
humanoids_sorted = humanoids.sort_values("price_usd_k_low", ascending=False)
labels = [f"{m}\n({mk})" for m, mk in zip(humanoids_sorted["model"],
                                            humanoids_sorted["maker"])]
bar_colors = [COLOR_CN if c == "China" else COLOR_US
              for c in humanoids_sorted["country"]]

fig, ax = plt.subplots(figsize=(13, 6.5))
y_pos = range(len(humanoids_sorted))
widths = humanoids_sorted["price_usd_k_high"] - humanoids_sorted["price_usd_k_low"]
ax.barh(y_pos, widths, left=humanoids_sorted["price_usd_k_low"],
        color=bar_colors, alpha=0.7, edgecolor="white", height=0.6)
ax.scatter(humanoids_sorted["price_usd_k_low"], y_pos, color=bar_colors,
           s=80, zorder=3, edgecolor="white", linewidth=1)
ax.scatter(humanoids_sorted["price_usd_k_high"], y_pos, color=bar_colors,
           s=80, zorder=3, edgecolor="white", linewidth=1)
ax.set_yticks(y_pos); ax.set_yticklabels(labels, fontsize=9)
for i, (lo, hi) in enumerate(zip(humanoids_sorted["price_usd_k_low"],
                                   humanoids_sorted["price_usd_k_high"])):
    if lo == hi:
        ax.text(hi + 4, i, f"\\${lo}k", va="center", fontsize=9.5,
                color="#222", fontweight="bold")
    else:
        ax.text(hi + 4, i, f"\\${lo}–\\${hi}k", va="center",
                fontsize=9.5, color="#222", fontweight="bold")
for i, comm in enumerate(humanoids_sorted["commercial"]):
    if not comm:
        ax.text(2, i, "(R&D / not yet at retail)", va="center",
                fontsize=8.5, color="#666", fontstyle="italic")
ax.set_xlim(0, 230)
ax.set_xlabel("Public stated price, USD thousand (per unit)")
ax.set_title("Humanoid Robots — Commercial Pricing Snapshot (late 2024 / early 2025)",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
ax.annotate(
    "Unitree's G1 reached commercial availability at \\$16k —\n"
    "an order of magnitude below the Western humanoid platforms.\n"
    "Most Western entrants (Figure, Optimus) remain R&D / pilot.\n\n"
    "Source: public product announcements and press releases.\n"
    "See raw-data/06e_*.csv for URLs.",
    xy=(0.65, 0.5), xycoords="axes fraction",
    fontsize=9, color="#222", va="center", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/06e_humanoid_robot_pricing.png", dpi=150); plt.close()
print("  saved 06e_humanoid_robot_pricing.png")


# ---------------------------------------------------------------------------
# 6f. China's share of global industrial-robot installations vs peers
#     (derived from 06a — no separate CSV)
# ---------------------------------------------------------------------------
print("China share of global robot installations over time...")
share = pd.DataFrame(index=robots.index)
for col in ["China", "Japan", "Korea", "United States", "Germany"]:
    share[col] = (robots[col] / robots["Global"] * 100).round(1)
share["Rest"] = (robots["Rest of World"] / robots["Global"] * 100).round(1)

fig, ax = plt.subplots(figsize=(13, 5.2))
for col, color, lw in [("China", COLOR_CN, 2.8),
                       ("Japan", COLOR_JP, 1.5),
                       ("Korea", COLOR_KR, 1.5),
                       ("United States", COLOR_US, 1.5),
                       ("Germany", COLOR_DE, 1.5)]:
    ax.plot(share.index, share[col], label=col, color=color,
            linewidth=lw, marker="o", markersize=4)
    if col == "China":
        ax.fill_between(share.index, share[col], alpha=0.08, color=color)
for col in ["China", "Japan", "Korea", "United States", "Germany"]:
    y = share[col].iloc[-1]
    color = {"China": COLOR_CN, "Japan": COLOR_JP, "Korea": COLOR_KR,
             "United States": COLOR_US, "Germany": COLOR_DE}[col]
    ax.text(2023.1, y, f"{y:.0f}%", va="center", fontsize=10,
            color=color, fontweight="bold")
ax.set_title("Share of Global New Industrial-Robot Installations, by Country",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of new installations worldwide")
ax.set_ylim(0, 60)
ax.legend(loc="upper left", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
ax.annotate(
    "Derived from raw-data/06a_industrial_robot_installations_thousands.csv.\n"
    "Source: IFR World Robotics 2024.",
    xy=(0.98, 0.05), xycoords="axes fraction",
    fontsize=8.5, color="#555", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
              edgecolor="#bbb", linewidth=0.6))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/06f_robot_install_share.png", dpi=150); plt.close()
print("  saved 06f_robot_install_share.png")


print("\nDone — robotics charts saved to", OUTPUT)
