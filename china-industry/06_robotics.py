"""
06 — Sectoral Deep Dive: Robotics & Industrial Automation

The fourth frontier-leadership case. Robotics sits at the intersection
of China's three earlier strengths (manufacturing scale, EV/battery
components supply chain, applied AI), which makes it the natural next
frontier.

The data:
- China installed ~59% of the world's new industrial robots in 2025
  (354k of 603k; IFR World Robotics 2026), up from 51% in 2023
- Robot density: IFR re-based China on NBS employment data in 2026 —
  China is 166 robots per 10k workers (2024, 22nd), well below the US
  (307), Germany (449) and Japan (446); not comparable with the old 470
- Chinese-brand robots rose from ~30% of the domestic market (2019–21)
  to 57% in 2024, slipping to 55% in 2025
- DJI holds ~70%+ of the global consumer / prosumer drone market
- Chinese humanoids lead on price: Unitree R1 from ~$5.6k (2025)

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


def fmt_k(v):
    """Price label in USD thousands: integer if whole, else one decimal."""
    return f"{v:.0f}" if float(v).is_integer() else f"{v:.1f}"


# ---------------------------------------------------------------------------
# 6a. Annual industrial-robot installations by country
# ---------------------------------------------------------------------------
print("Industrial-robot installations by country...")
robots = load("06a_industrial_robot_installations_thousands", index_col="year")
cols = ["China", "Japan", "Korea", "United States", "Germany", "Rest of World"]
robots["Global"] = robots[cols].sum(axis=1)
robots["China_share_pct"] = (robots["China"] / robots["Global"] * 100).round(1)
y0, y1 = robots.index.min(), robots.index.max()
# Pre-2021 Rest-of-World values are known to understate IFR global totals
FIRST_RECONCILED = 2021

fig, ax = plt.subplots(figsize=(13, 5.8))
colors = [COLOR_CN, COLOR_JP, COLOR_KR, COLOR_US, COLOR_DE, COLOR_OTHER]
ax.stackplot(robots.index, *[robots[c] for c in cols],
             labels=cols, colors=colors, alpha=0.88,
             edgecolor="white", linewidth=0.7)
label_years = sorted({y for y in range(y1, y0 - 1, -3)} | {y1})
for x in label_years:
    ax.text(x, robots.loc[x, "Global"] + 12,
            f"{robots.loc[x, 'China_share_pct']:.0f}%\nChina",
            ha="center", va="bottom", fontsize=8.5,
            color=COLOR_CN, fontweight="bold")
ax.set_title(f"Industrial-Robot Installations Worldwide — Thousands of Units, "
             f"Annual {y0}–{y1}", fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("New robot installations (thousands)")
ax.set_ylim(0, robots["Global"].max() * 1.2)
ax.set_xlim(y0 - 0.3, y1 + 0.5)
ax.legend(loc="upper left", fontsize=9, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
last = robots.loc[y1]
ax.annotate(
    f"{y1}: China installed {last['China']:.0f}k of {last['Global']:.0f}k "
    f"robots worldwide ({last['China_share_pct']:.0f}%) —\n"
    f"vs {last['Global'] - last['China']:.0f}k for the rest of the "
    "world combined.\n"
    f"Pre-{FIRST_RECONCILED} 'Rest of World' understates IFR totals, so\n"
    "China's share is overstated for those years.\n\n"
    "Source: IFR World Robotics 2022–2026 (headline figures).\n"
    "See raw-data/06a_*.csv for URLs.",
    xy=(0.24, 0.97), xycoords="axes fraction",
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
DCOL = "density_2024"
density = density.dropna(subset=[DCOL]).copy()
density[DCOL] = density[DCOL].astype(int)
density_sorted = density.sort_values(DCOL, ascending=True)

fig, ax = plt.subplots(figsize=(13, 6.0))
y_pos = range(len(density_sorted))
bar_colors = [COLOR_CN if c == "China" else COLOR_US if c == "United States"
              else COLOR_OTHER for c in density_sorted["country"]]
ax.barh(y_pos, density_sorted[DCOL], color=bar_colors,
        alpha=0.9, edgecolor="white", height=0.6)
ax.set_yticks(y_pos); ax.set_yticklabels(density_sorted["country"])
for i, v in enumerate(density_sorted[DCOL]):
    ax.text(v + 12, i, f"{v:,}", va="center", fontsize=10,
            color="#222", fontweight="bold")
ax.set_xlabel("Robots per 10,000 manufacturing workers (2024)")
ax.set_title("Industrial-Robot Density, 2024 — IFR World Robotics 2025",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
ax.set_xlim(0, density_sorted[DCOL].max() * 1.12)
d = density.set_index("country")[DCOL]
ax.annotate(
    "2024 figures use IFR's re-based employment denominator for China\n"
    "(updated National Bureau of Statistics labour data) and are NOT\n"
    "comparable with earlier editions (old basis: China 470 in 2023).\n\n"
    f"On the new basis China is {d['China']} (22nd worldwide, +17% y/y),\n"
    f"below the US ({d['United States']}), Japan ({d['Japan']}) and "
    f"Germany ({d['Germany']}).\n"
    f"Korea leads at {d['South Korea']:,}; world average 132.\n\n"
    "Source: IFR press release, 8 April 2026 (World Robotics 2025).\n"
    "See raw-data/06b_*.csv for URLs.",
    xy=(0.98, 0.05), xycoords="axes fraction",
    fontsize=9, color="#222", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#fdf2ee",
              edgecolor=COLOR_CN, linewidth=1.0))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/06b_robot_density.png", dpi=150); plt.close()
print("  saved 06b_robot_density.png")


# ---------------------------------------------------------------------------
# 6c. Chinese-brand share of China's domestic industrial-robot market
# ---------------------------------------------------------------------------
print("Chinese vs foreign-brand share of China's robot market...")
domestic_share = load("06c_china_domestic_robot_market_share_pct", index_col="year")
peak_year = domestic_share["chinese_brand"].idxmax()
last_year = domestic_share.index.max()

fig, ax = plt.subplots(figsize=(13, 5.0))
ax.fill_between(domestic_share.index, 0, domestic_share["chinese_brand"],
                color=COLOR_CN, alpha=0.85, label="Chinese-brand robots")
ax.fill_between(domestic_share.index, domestic_share["chinese_brand"],
                100, color=COLOR_OTHER, alpha=0.7,
                label="Foreign-brand (FANUC, Yaskawa, ABB, KUKA, etc.)")
xs = list(domestic_share.index)
for x, y in zip(xs, domestic_share["chinese_brand"]):
    # keep edge labels inside the filled area
    xt = x + 0.3 if x == xs[0] else x - 0.3 if x == xs[-1] else x
    ax.text(xt, y / 2, f"{y}%", ha="center", va="center", fontsize=10,
            color="white", fontweight="bold")
ax.axhline(50, color="#222", linestyle="--", linewidth=1, alpha=0.7)
ax.set_title("China's Domestic Industrial-Robot Market — Brand Origin Mix",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of robots installed in China")
ax.set_ylim(0, 100)
ax.set_xlim(domestic_share.index.min() - 0.5, domestic_share.index.max() + 0.5)
ax.legend(loc="upper right", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
ax.annotate(
    f"Chinese brands passed 50% of domestic installations in 2024, peaking\n"
    f"at {domestic_share.loc[peak_year, 'chinese_brand']}% ({peak_year}); "
    f"{domestic_share.loc[last_year, 'chinese_brand']}% in {last_year} as "
    "foreign-brand installs grew faster.\n"
    "Caveat: IFR puts the 2019–21 share at ~30%; earlier points unverified.\n\n"
    "Source: IFR World Robotics 2024–2026; Chinese MIIT summaries.\n"
    "See raw-data/06c_*.csv for URLs.",
    xy=(0.02, 0.97), xycoords="axes fraction",
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
bar_colors = [color_map.get(c, COLOR_OTHER) for c in drones["country"]]
dji = drones.loc[drones["maker"].str.startswith("DJI"), "global_share"].iloc[0]
cn_total = drones.loc[drones["country"] == "China", "global_share"].sum()

fig, ax = plt.subplots(figsize=(11, 5))
y_pos = range(len(drones))
ax.barh(y_pos, drones["global_share"], color=bar_colors,
        edgecolor="white")
ax.set_yticks(y_pos); ax.set_yticklabels(drones["maker"])
ax.invert_yaxis()
for i, v in enumerate(drones["global_share"]):
    ax.text(v + 1, i, f"{v}%", va="center", fontsize=10, color="#222",
            fontweight="bold")
ax.set_xlim(0, drones["global_share"].max() * 1.18)
ax.set_xlabel("% of global consumer / prosumer drone market (units)")
ax.set_title("Consumer & Prosumer Drone Market — Global Share by Maker",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
ax.annotate(
    f"DJI alone holds ~{dji}% of the global consumer / prosumer market;\n"
    f"Chinese makers combined ~{cn_total}% of units (pre-2026 estimate).\n"
    "US response: since Dec 2025 the FCC Covered List blocks\n"
    "authorisation of NEW foreign-made drone models (incl. DJI, Autel);\n"
    "previously authorised models can still be sold and flown.\n\n"
    "Source: DJI disclosures; Drone Industry Insights; FCC.\n"
    "See raw-data/06d_*.csv for URLs.",
    xy=(0.98, 0.05), xycoords="axes fraction",
    fontsize=9, color="#222", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#fdf2ee",
              edgecolor=COLOR_CN, linewidth=1.0))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/06d_consumer_drone_market.png", dpi=150); plt.close()
print("  saved 06d_consumer_drone_market.png")


# ---------------------------------------------------------------------------
# 6e. Humanoid robots — commercial pricing snapshot
# ---------------------------------------------------------------------------
print("Humanoid robot commercial pricing snapshot...")
humanoids = load("06e_humanoid_robot_pricing_usd_k")
humanoids_sorted = humanoids.sort_values("price_usd_k_low", ascending=False)
labels = [f"{m}\n({mk})" for m, mk in zip(humanoids_sorted["model"],
                                            humanoids_sorted["maker"])]
bar_colors = [COLOR_CN if c == "China" else COLOR_US
              for c in humanoids_sorted["country"]]
cheapest = humanoids.loc[humanoids["price_usd_k_low"].idxmin()]

fig, ax = plt.subplots(figsize=(13, 7.0))
y_pos = range(len(humanoids_sorted))
widths = humanoids_sorted["price_usd_k_high"] - humanoids_sorted["price_usd_k_low"]
ax.barh(y_pos, widths, left=humanoids_sorted["price_usd_k_low"],
        color=bar_colors, alpha=0.7, edgecolor="white", height=0.6)
ax.scatter(humanoids_sorted["price_usd_k_low"], y_pos, color=bar_colors,
           s=80, zorder=3, edgecolor="white", linewidth=1)
ax.scatter(humanoids_sorted["price_usd_k_high"], y_pos, color=bar_colors,
           s=80, zorder=3, edgecolor="white", linewidth=1)
ax.set_yticks(y_pos); ax.set_yticklabels(labels, fontsize=9)
xmax = humanoids_sorted["price_usd_k_high"].max() * 1.42
for i, (lo, hi, comm) in enumerate(zip(humanoids_sorted["price_usd_k_low"],
                                        humanoids_sorted["price_usd_k_high"],
                                        humanoids_sorted["commercial"])):
    txt = f"\\${fmt_k(lo)}k" if lo == hi else f"\\${fmt_k(lo)}–\\${fmt_k(hi)}k"
    if not comm:
        txt += "  (R&D / target, not at retail)"
    ax.text(hi + xmax * 0.015, i, txt, va="center", fontsize=9.5,
            color="#222", fontweight="bold" if comm else "normal",
            fontstyle="normal" if comm else "italic")
ax.set_xlim(0, xmax)
ax.set_xlabel("Public stated price, USD thousand (per unit)")
ax.set_title("Humanoid Robots — Public Pricing Snapshot (2024–2026)",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
ax.annotate(
    f"Cheapest listed: {cheapest['model']} at \\${fmt_k(cheapest['price_usd_k_low'])}k "
    "(July 2025).\n"
    "1X NEO (\\$20k) is a pre-order price; deliveries unconfirmed.\n"
    "IFR: ~7,000 full-size humanoids sold worldwide in 2025;\n"
    "most remain prototypes or pilots. Figure 03, Optimus V3 and\n"
    "UBTech Walker S2 have no public unit price.\n\n"
    "Source: vendor announcements; Reuters; Business Wire; IFR.\n"
    "See raw-data/06e_*.csv for URLs.",
    xy=(0.98, 0.97), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="right",
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
peers = ["China", "Japan", "Korea", "United States", "Germany"]
for col in peers:
    share[col] = (robots[col] / robots["Global"] * 100).round(1)
peer_colors = {"China": COLOR_CN, "Japan": COLOR_JP, "Korea": COLOR_KR,
               "United States": COLOR_US, "Germany": COLOR_DE}

fig, ax = plt.subplots(figsize=(13, 5.2))
ax.axvspan(y0 - 0.5, FIRST_RECONCILED - 0.5, color="#f2f2f2", zorder=0)
ax.text(y0 - 0.3, share["China"].max() * 1.12,
        f"{y0}–{FIRST_RECONCILED - 1}: China share overstated\n"
        "(Rest of World not reconciled to IFR totals)",
        fontsize=8.5, color="#666", va="top", ha="left", fontstyle="italic")
for col in peers:
    lw = 2.8 if col == "China" else 1.5
    ax.plot(share.index, share[col], label=col, color=peer_colors[col],
            linewidth=lw, marker="o", markersize=4)
    if col == "China":
        ax.fill_between(share.index, share[col], alpha=0.08,
                        color=peer_colors[col])
# End-of-line labels, nudged apart so close values do not overlap
ends = sorted(((share[c].iloc[-1], c) for c in peers))
min_gap = share["China"].max() * 0.045
placed = []
for v, c in ends:
    y = v if not placed else max(v, placed[-1] + min_gap)
    placed.append(y)
    ax.text(y1 + 0.15, y, f"{c.split()[-1] if c != 'United States' else 'US'}"
            f" {v:.0f}%", va="center", fontsize=9.5, color=peer_colors[c],
            fontweight="bold")
ax.set_title("Share of Global New Industrial-Robot Installations, by Country",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of new installations worldwide")
ax.set_ylim(0, share["China"].max() * 1.18)
ax.set_xlim(y0 - 0.5, y1 + 1.6)
ax.legend(loc="center left", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.set_xticks(range(y0, y1 + 1))
ax.annotate(
    "Derived from raw-data/06a_industrial_robot_installations_thousands.csv.\n"
    "Source: IFR World Robotics 2022–2026.",
    xy=(0.98, 0.42), xycoords="axes fraction",
    fontsize=8.5, color="#555", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
              edgecolor="#bbb", linewidth=0.6))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/06f_robot_install_share.png", dpi=150); plt.close()
print("  saved 06f_robot_install_share.png")


print("\nDone — robotics charts saved to", OUTPUT)
