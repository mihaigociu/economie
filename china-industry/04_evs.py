"""
04 — Sectoral Deep Dive: Electric Vehicles

The thesis claim, tested: that China is leading the EV transition not
just on cost but on volume, technology, and exports. The data:

- China alone bought ~13 of the ~20.7 million EVs sold globally in 2025
- Chinese automakers supplied ~60% of global EV sales in 2025 (IEA);
  Chinese brands ~64% in 2024 on the brand-of-origin series charted here
- China became the world's largest auto exporter in 2023; exports passed
  7 million in 2025, 37% of them NEVs
- BYD overtook Tesla on BEV volume in 2025 and is far ahead on total NEV
- Domestic EV penetration reached ~54% of new passenger cars (BEV+PHEV)

This script only READS data. Every chart's numbers live in a CSV under
raw-data/ with a `# source:` / `# url:` / `# retrieved:` header. See
raw-data/SOURCES.md for the project-wide source index.

Annotations are computed from the latest row of each CSV, so adding a
new year to a CSV updates the chart text automatically.
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
# 4a. Global EV sales by region
# ---------------------------------------------------------------------------
print("Global EV sales by region...")
ev_sales = load("04a_global_ev_sales_millions", index_col="year")
ev_sales["Global"] = ev_sales.sum(axis=1)
s_first, s_last = ev_sales.index.min(), ev_sales.index.max()

fig, ax = plt.subplots(figsize=(13, 5.5))
ax.stackplot(ev_sales.index, ev_sales["China"], ev_sales["Europe"],
             ev_sales["United States"], ev_sales["Rest of World"],
             labels=["China", "Europe", "United States", "Rest of World"],
             colors=[COLOR_CN, COLOR_EU, COLOR_US, COLOR_RoW],
             alpha=0.88, edgecolor="white", linewidth=0.8)
for x, y in zip(ev_sales.index, ev_sales["Global"]):
    if x % 2 == 0 or x == s_last:
        ax.text(x, y + 0.4, f"{y:.1f}M", ha="center", va="bottom",
                fontsize=9, color="#222", fontweight="bold")
ax.set_title("Global Electric-Vehicle Sales — BEV + PHEV, Millions of Vehicles",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Million vehicles sold")
ax.set_ylim(0, ev_sales["Global"].max() * 1.15)
ax.set_xlim(s_first - 0.3, s_last + 0.3)
ax.legend(loc="upper left", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
last = ev_sales.loc[s_last]
ax.annotate(
    f"China alone accounted for ~{last['China']:.0f} of ~{last['Global']:.1f} million "
    f"EVs sold globally in {s_last}.\n"
    "2025 values are the IEA's rounded figures (China: \"more than 13 million\").\n"
    "Source: IEA Global EV Outlook 2024, 2025 + 2026.\n"
    "See raw-data/04a_*.csv for URLs.",
    xy=(0.30, 0.62), xycoords="axes fraction",
    fontsize=9, color="#222", va="bottom", ha="left",
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
pen_last = penetration.index.max()

fig, ax = plt.subplots(figsize=(13, 5.2))
latest = {}
for col, color in [("China", COLOR_CN), ("Europe", COLOR_EU),
                   ("United States", COLOR_US), ("Japan", COLOR_JP)]:
    series = penetration[col].dropna()
    lw = 2.8 if col == "China" else 1.5
    ax.plot(series.index, series, label=col, color=color,
            linewidth=lw, marker="o", markersize=6)
    x_end, y_end = series.index.max(), series.iloc[-1]
    latest[col] = (x_end, y_end)
    ax.text(x_end + 0.08, y_end, f"{y_end:.1f}%", va="center", fontsize=10,
            color=color, fontweight="bold")
ax.fill_between(penetration.index, penetration["China"], alpha=0.08, color=COLOR_CN)
ax.set_title("Electric-Vehicle Penetration — NEV Share of New Passenger-Car Sales",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of new passenger-car sales (BEV + PHEV)")
ax.set_ylim(0, penetration.max().max() * 1.15)
ax.set_xlim(penetration.index.min() - 0.3, pen_last + 0.6)
ax.legend(loc="upper left", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(1))


def _fmt(col):
    yr, v = latest[col]
    return f"{v:.1f}%" + ("" if yr == pen_last else f" ({yr})")


ax.annotate(
    f"{pen_last}: China {_fmt('China')} of new passenger cars were BEVs or PHEVs.\n"
    f"Europe {_fmt('Europe')}, US {_fmt('United States')}, Japan {_fmt('Japan')}.\n"
    "Japan 2025: no exact figure published (IEA: \"less than 3%\").\n\n"
    "Source: CPCA (China); IEA/ACEA (Europe); Argonne/IEA (US); JADA (Japan).\n"
    "See raw-data/04b_*.csv for URLs.",
    xy=(0.02, 0.68), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/04b_ev_penetration.png", dpi=150); plt.close()
print("  saved 04b_ev_penetration.png")


# ---------------------------------------------------------------------------
# 4c. China's vehicle exports — total + NEV share
# ---------------------------------------------------------------------------
print("China vehicle exports trajectory...")
exports = load("04c_china_vehicle_exports_millions", index_col="year")
exports["nev_mn"] = (exports["total_mn"] * exports["nev_share_pct"] / 100).round(2)
exports["ice_mn"] = (exports["total_mn"] - exports["nev_mn"]).round(2)
e_last = exports.index.max()

fig, ax = plt.subplots(figsize=(13, 5.2))
ax.bar(exports.index, exports["ice_mn"],
       color=COLOR_RoW, label="ICE + hybrid (non-plug-in)",
       edgecolor="white", linewidth=0.6)
ax.bar(exports.index, exports["nev_mn"], bottom=exports["ice_mn"],
       color=COLOR_CN, label="NEV (BEV + PHEV)", edgecolor="white", linewidth=0.6)
for x, total in zip(exports.index, exports["total_mn"]):
    ax.text(x, total + 0.10, f"{total:.2f}M", ha="center", va="bottom",
            fontsize=10, color="#222", fontweight="bold")
for x, nev, share in zip(exports.index, exports["nev_mn"], exports["nev_share_pct"]):
    if nev >= 0.30:
        ax.text(x, exports.loc[x, "ice_mn"] + nev / 2,
                f"NEV\n{share}%",
                ha="center", va="center", fontsize=8.5, color="white",
                fontweight="bold")
ax.set_title("China's Vehicle Exports — Total and NEV (BEV + PHEV) Share",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Million vehicles exported")
ax.set_ylim(0, exports["total_mn"].max() * 1.15)
ax.legend(loc="upper left", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.annotate(
    "2023: China overtook Japan as the world's largest auto exporter.\n"
    f"{e_last}: {exports.loc[e_last, 'total_mn']:.2f}M vehicles exported, "
    f"{exports.loc[e_last, 'nev_share_pct']}% of them NEVs (by units).\n"
    "NEVs ship at ~2x the per-unit FOB price of ICE exports, so\n"
    "their share by export value is well above their unit share.\n\n"
    "Source: CAAM (China Association of Automobile Manufacturers).\n"
    "See raw-data/04c_*.csv for URLs.",
    xy=(0.02, 0.80), xycoords="axes fraction",
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
d_last = big_two_auto.index.max()
dl = big_two_auto.loc[d_last]

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
ax.set_ylim(0, big_two_auto["byd_total_nev"].max() * 1.18)
ax.legend(loc="upper left", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
bev_gap = dl["byd_bev"] - dl["tesla_bev"]
if abs(bev_gap) < 0.05:
    bev_line = f"On BEV alone, BYD and Tesla were roughly level in {d_last}."
elif bev_gap > 0:
    bev_line = (f"On BEV alone, BYD outsold Tesla in {d_last}: "
                f"{dl['byd_bev']:.2f}M vs {dl['tesla_bev']:.2f}M.")
else:
    bev_line = (f"On BEV alone, Tesla outsold BYD in {d_last}: "
                f"{dl['tesla_bev']:.2f}M vs {dl['byd_bev']:.2f}M.")
ax.annotate(
    f"{bev_line}\n"
    f"On total NEV (BEV + PHEV), BYD sold {dl['byd_total_nev']:.2f}M passenger cars,\n"
    f"{dl['byd_total_nev'] / dl['tesla_bev']:.1f}x Tesla's BEV-only total.\n\n"
    "Source: Tesla delivery releases / 10-K; BYD HKEX monthly sales filings.\n"
    "See raw-data/04d_*.csv for URLs.",
    xy=(0.02, 0.80), xycoords="axes fraction",
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
b_first, b_last = brand_share.index.min(), brand_share.index.max()

fig, ax = plt.subplots(figsize=(13, 5.0))
ax.fill_between(brand_share.index, 0, brand_share["china_brand_pct"],
                color=COLOR_CN, alpha=0.10)
ax.plot(brand_share.index, brand_share["china_brand_pct"], color=COLOR_CN,
        linewidth=2.8, marker="o", markersize=7)
for x, y in zip(brand_share.index, brand_share["china_brand_pct"]):
    ax.text(x, y + 1.6, f"{y}%", ha="center", va="bottom",
            fontsize=11, color="#222", fontweight="bold")
ax.axhline(50, color="#888", linestyle="--", linewidth=1, alpha=0.7)
ax.text(b_first + 0.5, 50.8, "50% line", fontsize=8, color="#666", ha="center")
ax.set_title("Chinese-Brand Share of Global EV Sales",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of global BEV + PHEV sales")
ax.set_ylim(0, max(75, brand_share["china_brand_pct"].max() * 1.15))
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
ax.annotate(
    f"Chinese brands held ~{brand_share.loc[b_last, 'china_brand_pct']}% of the "
    f"global EV market in {b_last}.\n"
    "The 2020 dip reflects the temporary cut in Chinese NEV subsidies that year.\n"
    "IEA GEVO 2026 (different method): Chinese automakers supplied ~60% of\n"
    "global EV sales in 2025 — not appended, as the series are not comparable.\n\n"
    "Source: IEA Global EV Outlook 2024–2026; JATO Dynamics public commentary.\n"
    "See raw-data/04e_*.csv for URLs.",
    xy=(0.99, 0.05), xycoords="axes fraction",
    fontsize=9, color="#222", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/04e_china_brand_share.png", dpi=150); plt.close()
print("  saved 04e_china_brand_share.png")


print("\nDone — EV charts saved to", OUTPUT)
