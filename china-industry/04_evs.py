"""
04 — Sectoral Deep Dive: Electric Vehicles

The thesis claim, tested: that China is leading the EV transition not
just on cost but on volume, technology, and exports. The data:

- China alone bought ~11 of the ~17 million EVs sold globally in 2024
- Chinese-brand EVs are ~60-65% of global EV sales
- China became the world's largest auto exporter in 2023
- BYD overtook Tesla on BEV in 2024 and is far ahead on total NEV
- Domestic EV penetration crossed 47% of new passenger cars (BEV+PHEV)

This script only READS data. Every chart's numbers live in a CSV under
raw-data/ with a `# source:` / `# url:` / `# retrieved:` header. See
raw-data/SOURCES.md for the project-wide source index.
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
COLOR_RoW    = "#bdc3c7"


def load(name, **kwargs):
    return pd.read_csv(f"{RAW_DATA}/{name}.csv", comment="#", **kwargs)


# ---------------------------------------------------------------------------
# 4a. Global EV sales by region, 2015–2024
# ---------------------------------------------------------------------------
print("Global EV sales by region...")
ev_sales = load("04a_global_ev_sales_millions", index_col="year")
ev_sales["Global"] = ev_sales.sum(axis=1)

fig, ax = plt.subplots(figsize=(13, 5.5))
ax.stackplot(ev_sales.index, ev_sales["China"], ev_sales["Europe"],
             ev_sales["United States"], ev_sales["Rest of World"],
             labels=["China", "Europe", "United States", "Rest of World"],
             colors=[COLOR_CN, COLOR_EU, COLOR_US, COLOR_RoW],
             alpha=0.88, edgecolor="white", linewidth=0.8)
for x, y in zip(ev_sales.index, ev_sales["Global"]):
    if x % 2 == 0 or x == 2024:
        ax.text(x, y + 0.4, f"{y:.1f}M", ha="center", va="bottom",
                fontsize=9, color="#222", fontweight="bold")
ax.set_title("Global Electric-Vehicle Sales — BEV + PHEV, Millions of Vehicles",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Million vehicles sold")
ax.set_ylim(0, 20)
ax.legend(loc="upper left", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
ax.annotate(
    "China alone accounted for ~11 of ~17 million EVs sold globally in 2024.\n"
    "Source: IEA Global EV Outlook 2024 + 2025.\n"
    "See raw-data/04a_*.csv for URLs.",
    xy=(0.99, 0.05), xycoords="axes fraction",
    fontsize=9, color="#222", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/04a_global_ev_sales.png", dpi=150); plt.close()
print("  saved 04a_global_ev_sales.png")


# ---------------------------------------------------------------------------
# 4b. EV penetration rate — % of new passenger-car sales that are NEV
# ---------------------------------------------------------------------------
print("EV penetration rates by major market...")
penetration = load("04b_ev_penetration_pct_new_car_sales", index_col="year")

fig, ax = plt.subplots(figsize=(13, 5.2))
for col, color in [("China", COLOR_CN), ("Europe", COLOR_EU),
                   ("United States", COLOR_US), ("Japan", COLOR_JP)]:
    lw = 2.8 if col == "China" else 1.5
    ax.plot(penetration.index, penetration[col], label=col, color=color,
            linewidth=lw, marker="o", markersize=6)
    for x, y in zip(penetration.index, penetration[col]):
        if x == 2024:
            ax.text(x + 0.08, y, f"{y:.1f}%", va="center", fontsize=10,
                    color=color, fontweight="bold")
ax.fill_between(penetration.index, penetration["China"], alpha=0.08, color=COLOR_CN)
ax.set_title("Electric-Vehicle Penetration — NEV Share of New Passenger-Car Sales",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of new passenger-car sales (BEV + PHEV)")
ax.set_ylim(0, 55)
ax.legend(loc="upper left", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
ax.annotate(
    "China crossed 47% NEV share in 2024 — almost half of new passenger cars\n"
    "are now BEVs or PHEVs. Europe at ~24%, US ~10%, Japan ~3.5%.\n\n"
    "Source: CPCA (China); ACEA (Europe); IEA (US); JADA (Japan).\n"
    "See raw-data/04b_*.csv for URLs.",
    xy=(0.40, 0.62), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/04b_ev_penetration.png", dpi=150); plt.close()
print("  saved 04b_ev_penetration.png")


# ---------------------------------------------------------------------------
# 4c. China's vehicle exports — total + NEV share, 2018–2024
# ---------------------------------------------------------------------------
print("China vehicle exports trajectory...")
exports = load("04c_china_vehicle_exports_millions", index_col="year")
exports["nev_mn"] = (exports["total_mn"] * exports["nev_share_pct"] / 100).round(2)
exports["ice_mn"] = (exports["total_mn"] - exports["nev_mn"]).round(2)

fig, ax = plt.subplots(figsize=(13, 5.2))
ax.bar(exports.index, exports["ice_mn"],
       color=COLOR_RoW, label="ICE + hybrid (non-plug-in)",
       edgecolor="white", linewidth=0.6)
ax.bar(exports.index, exports["nev_mn"], bottom=exports["ice_mn"],
       color=COLOR_CN, label="NEV (BEV + PHEV)", edgecolor="white", linewidth=0.6)
for x, total in zip(exports.index, exports["total_mn"]):
    ax.text(x, total + 0.10, f"{total:.2f}M", ha="center", va="bottom",
            fontsize=10, color="#222", fontweight="bold")
for x, nev in zip(exports.index, exports["nev_mn"]):
    if nev >= 0.30:
        ax.text(x, exports.loc[x, "ice_mn"] + nev / 2,
                f"NEV\n{nev:.2f}M",
                ha="center", va="center", fontsize=8.5, color="white",
                fontweight="bold")
ax.set_title("China's Vehicle Exports — Total and NEV (BEV + PHEV) Share",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Million vehicles exported")
ax.set_ylim(0, 7)
ax.legend(loc="upper left", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.annotate(
    "2023: China overtook Japan to become the world's largest auto exporter.\n"
    "2024: 5.86 million vehicles exported, of which ~1.2 million NEVs.\n"
    "Top destinations 2024 (units): Russia, Mexico, Belgium, UK, Saudi Arabia.\n\n"
    "Source: CAAM (China Association of Automobile Manufacturers).\n"
    "See raw-data/04c_*.csv for URLs.",
    xy=(0.02, 0.72), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/04c_china_vehicle_exports.png", dpi=150); plt.close()
print("  saved 04c_china_vehicle_exports.png")


# ---------------------------------------------------------------------------
# 4d. BYD vs Tesla — annual sales trajectory
# ---------------------------------------------------------------------------
print("BYD vs Tesla annual sales...")
big_two_auto = load("04d_byd_vs_tesla_sales_millions", index_col="year")
big_two_auto["byd_total_nev"] = big_two_auto["byd_bev"] + big_two_auto["byd_phev"]

fig, ax = plt.subplots(figsize=(13, 5.5))
x = big_two_auto.index
width = 0.36
ax.bar(x - width/2, big_two_auto["tesla_bev"], width=width, color=COLOR_US,
       label="Tesla (BEV)", edgecolor="white", linewidth=0.6)
ax.bar(x + width/2, big_two_auto["byd_bev"], width=width, color=COLOR_CN,
       label="BYD (BEV)", edgecolor="white", linewidth=0.6)
ax.bar(x + width/2, big_two_auto["byd_phev"], width=width,
       bottom=big_two_auto["byd_bev"], color="#e8b4a8",
       label="BYD (PHEV)", edgecolor="white", linewidth=0.6)
for xi, total in zip(x, big_two_auto["byd_total_nev"]):
    ax.text(xi + width/2, total + 0.08, f"{total:.2f}M",
            ha="center", va="bottom", fontsize=9, color="#222", fontweight="bold")
for xi, tesla in zip(x, big_two_auto["tesla_bev"]):
    ax.text(xi - width/2, tesla + 0.08, f"{tesla:.2f}M",
            ha="center", va="bottom", fontsize=9, color="#222", fontweight="bold")
ax.set_title("BYD vs Tesla — Annual Passenger-EV Sales (Million Vehicles)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Million vehicles sold")
ax.set_ylim(0, 5)
ax.legend(loc="upper left", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.annotate(
    "On BEV alone, BYD and Tesla finished 2024 within ~30k units of each other.\n"
    "On total NEV (BEV + PHEV) — BYD's full product line — BYD reached 4.25M\n"
    "in 2024, more than double Tesla's BEV-only total.\n\n"
    "Source: Tesla 10-K filings; BYD annual report and monthly sales releases.\n"
    "See raw-data/04d_*.csv for URLs.",
    xy=(0.02, 0.78), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/04d_byd_vs_tesla.png", dpi=150); plt.close()
print("  saved 04d_byd_vs_tesla.png")


# ---------------------------------------------------------------------------
# 4e. Chinese-brand share of global EV sales
# ---------------------------------------------------------------------------
print("Chinese-brand share of global EV market...")
brand_share = load("04e_china_brand_share_global_ev_pct", index_col="year")

fig, ax = plt.subplots(figsize=(13, 5.0))
ax.fill_between(brand_share.index, 0, brand_share["china_brand_pct"],
                color=COLOR_CN, alpha=0.10)
ax.plot(brand_share.index, brand_share["china_brand_pct"], color=COLOR_CN,
        linewidth=2.8, marker="o", markersize=7)
for x, y in zip(brand_share.index, brand_share["china_brand_pct"]):
    ax.text(x, y + 1.6, f"{y}%", ha="center", va="bottom",
            fontsize=11, color="#222", fontweight="bold")
ax.axhline(50, color="#888", linestyle="--", linewidth=1, alpha=0.7)
ax.text(2018.1, 50.8, "50% line", fontsize=8, color="#666")
ax.set_title("Chinese-Brand Share of Global EV Sales",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of global BEV + PHEV sales")
ax.set_ylim(0, 75)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
ax.annotate(
    "Chinese brands held ~64% of the global EV market in 2024 — including\n"
    "growing share in Europe, Latin America, MENA, and ASEAN. The 2020 dip\n"
    "reflects the temporary cut in Chinese NEV subsidies that year.\n\n"
    "Source: IEA Global EV Outlook 2024+2025; JATO Dynamics public commentary.\n"
    "See raw-data/04e_*.csv for URLs.",
    xy=(0.99, 0.05), xycoords="axes fraction",
    fontsize=9, color="#222", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/04e_china_brand_share.png", dpi=150); plt.close()
print("  saved 04e_china_brand_share.png")


print("\nDone — EV charts saved to", OUTPUT)
