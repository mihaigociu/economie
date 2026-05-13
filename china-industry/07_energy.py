"""
07 — Energy: The AI-Era Strategic Asset

China's electricity build-out as a strategic asset, particularly in the
era where AI is becoming energy-bound rather than purely chip-bound.

The data:
- China generates more electricity than the US + EU27 combined; gap widening
- China installed more solar PV capacity in 2024 than the rest of the world
- China has the world's largest pipeline of nuclear reactors under
  construction (~26 vs ~30 total under construction worldwide outside China)
- Industrial electricity prices are materially below the EU, somewhat below US
- Western data-centre electricity bottlenecks (NoVa, Ireland) well-documented;
  China has spare generation in western provinces

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
COLOR_IN     = "#e67e22"
COLOR_OTHER  = "#bdc3c7"

# Generation-mix colours
COLOR_COAL    = "#2c3e50"
COLOR_GAS     = "#7f8c8d"
COLOR_HYDRO   = "#3498db"
COLOR_NUCLEAR = "#9b59b6"
COLOR_WIND    = "#27ae60"
COLOR_SOLAR   = "#f1c40f"
COLOR_BIO     = "#d35400"


def load(name, **kwargs):
    return pd.read_csv(f"{RAW_DATA}/{name}.csv", comment="#", **kwargs)


# ---------------------------------------------------------------------------
# 7a. Total electricity generation by country, 1990–2024 (TWh)
# ---------------------------------------------------------------------------
print("Total electricity generation by country...")
gen = load("07a_electricity_generation_twh", index_col="year")

fig, ax = plt.subplots(figsize=(13, 5.5))
for col, color, lw in [("China", COLOR_CN, 2.8),
                       ("United States", COLOR_US, 2.0),
                       ("EU27", COLOR_EU, 1.8),
                       ("India", COLOR_IN, 1.5),
                       ("Japan", COLOR_JP, 1.5)]:
    ax.plot(gen.index, gen[col], label=col, color=color,
            linewidth=lw, marker="o", markersize=5)
ax.fill_between(gen.index, gen["China"], alpha=0.08, color=COLOR_CN)
us_eu = gen["United States"] + gen["EU27"]
ax.plot(gen.index, us_eu, color="#222", linewidth=1.5, linestyle="--",
        label="US + EU27 combined", alpha=0.6)
for col, color in [("China", COLOR_CN), ("United States", COLOR_US),
                   ("EU27", COLOR_EU), ("India", COLOR_IN)]:
    y = gen[col].iloc[-1]
    ax.text(2024.3, y, f"{y:,}", va="center", fontsize=9.5,
            color=color, fontweight="bold")
ax.set_title("Electricity Generation by Country — TWh per Year",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Generation (TWh per year)")
ax.set_ylim(0, 11500)
ax.legend(loc="upper left", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
ax.annotate(
    "China's 2024 generation (~10,250 TWh) exceeds the US + EU27 combined (~6,960 TWh).\n"
    "The gap has been widening every year since ~2018.\n\n"
    "Source: Ember Global Electricity Review; IEA Electricity Report.\n"
    "See raw-data/07a_*.csv for URLs.",
    xy=(0.02, 0.55), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/07a_electricity_generation.png", dpi=150); plt.close()
print("  saved 07a_electricity_generation.png")


# ---------------------------------------------------------------------------
# 7b. China's electricity generation mix by source, 2010–2024
# ---------------------------------------------------------------------------
print("China generation mix by source...")
mix = load("07b_china_generation_mix_pct", index_col="year")

fig, ax = plt.subplots(figsize=(13, 5.5))
cols = ["Coal", "Gas", "Hydro", "Nuclear", "Wind", "Solar", "Bio / other"]
colors = [COLOR_COAL, COLOR_GAS, COLOR_HYDRO, COLOR_NUCLEAR,
          COLOR_WIND, COLOR_SOLAR, COLOR_BIO]
ax.stackplot(mix.index, *[mix[c] for c in cols],
             labels=cols, colors=colors, alpha=0.92,
             edgecolor="white", linewidth=0.8)
ax.set_title("China's Electricity Generation Mix — % by Source, 2010–2024",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of total electricity generation")
ax.set_ylim(0, 100)
ax.legend(loc="upper right", fontsize=9, framealpha=0.95, ncol=2)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
ax.annotate(
    "Coal share declining (78% → 58%) but coal generation still grew\n"
    "in absolute TWh; renewables fill the marginal demand.\n"
    "Wind + solar reached ~18% of generation in 2024,\n"
    "nuclear ~5% and rising as new reactors come online.\n\n"
    "Source: Ember Global Electricity Review.\n"
    "See raw-data/07b_*.csv for URLs.",
    xy=(0.02, 0.62), xycoords="axes fraction",
    fontsize=9, color="white", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#2c3e50",
              edgecolor="white", linewidth=0.8, alpha=0.85))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/07b_china_generation_mix.png", dpi=150); plt.close()
print("  saved 07b_china_generation_mix.png")


# ---------------------------------------------------------------------------
# 7c. Solar PV capacity additions by country, 2015–2024 (GW per year)
# ---------------------------------------------------------------------------
print("Annual solar PV capacity additions...")
solar = load("07c_solar_pv_additions_gw", index_col="year")
solar["Global"] = solar.sum(axis=1)
solar["China_share_pct"] = (solar["China"] / solar["Global"] * 100).round(1)

fig, ax = plt.subplots(figsize=(13, 5.5))
cols = ["China", "EU27", "United States", "India", "Rest of World"]
colors = [COLOR_CN, COLOR_EU, COLOR_US, COLOR_IN, COLOR_OTHER]
bottom = pd.Series(0, index=solar.index)
for col, color in zip(cols, colors):
    ax.bar(solar.index, solar[col], bottom=bottom, label=col,
           color=color, edgecolor="white", linewidth=0.6, width=0.7)
    bottom = bottom + solar[col]
for x, total in zip(solar.index, solar["Global"]):
    ax.text(x, total + 12, f"{total} GW", ha="center", va="bottom",
            fontsize=9, color="#222", fontweight="bold")
for x in [2023, 2024]:
    ax.text(x, solar.loc[x, "China"] / 2,
            f"{solar.loc[x, 'China_share_pct']:.0f}%\nChina",
            ha="center", va="center", fontsize=10, color="white",
            fontweight="bold")
ax.set_title("Annual Solar PV Capacity Additions — by Country, GW per Year",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("GW of solar PV added")
ax.set_ylim(0, 650)
ax.legend(loc="upper left", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.annotate(
    "China alone added more solar capacity in 2023 and 2024 than the rest of\n"
    "the world combined. Global additions tripled from ~127 GW (2020) to ~556 GW (2024).\n\n"
    "Source: IRENA Renewable Capacity Statistics; IEA Renewables 2024.\n"
    "See raw-data/07c_*.csv for URLs.",
    xy=(0.02, 0.77), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/07c_solar_pv_additions.png", dpi=150); plt.close()
print("  saved 07c_solar_pv_additions.png")


# ---------------------------------------------------------------------------
# 7d. Industrial electricity prices — country snapshot ~2023
# ---------------------------------------------------------------------------
print("Industrial electricity prices snapshot...")
prices = load("07d_industrial_electricity_prices_usd_mwh").sort_values(
    "usd_per_mwh", ascending=True)

color_map = {"China": COLOR_CN, "United States": COLOR_US,
             "Germany": COLOR_EU, "United Kingdom": COLOR_EU,
             "Italy": COLOR_EU, "France": COLOR_EU,
             "Japan": COLOR_JP, "Korea": "#e67e22"}
bar_colors = [color_map.get(c, COLOR_OTHER) for c in prices["country"]]

fig, ax = plt.subplots(figsize=(13, 5.5))
y_pos = range(len(prices))
ax.barh(y_pos, prices["usd_per_mwh"], color=bar_colors, edgecolor="white")
ax.set_yticks(y_pos); ax.set_yticklabels(prices["country"])
for i, v in enumerate(prices["usd_per_mwh"]):
    ax.text(v + 4, i, f"\\${v}", va="center", fontsize=11,
            color="#222", fontweight="bold")
ax.set_xlim(0, 260)
ax.set_xlabel("Industrial electricity price (USD per MWh, 2023)")
ax.set_title("Industrial Electricity Prices — Country Snapshot, 2023",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
ax.annotate(
    "Chinese industrial electricity (\\$80/MWh) is roughly:\n"
    "  one-third of German industrial price (\\$220/MWh)\n"
    "  half of UK / Italian industrial price\n"
    "  ~85% of US industrial price (US is cheap by global standards)\n\n"
    "Compounding effect on energy-intensive industries\n"
    "(aluminium, chemicals, refining, data centres, AI compute).\n\n"
    "Source: OECD/IEA Energy Prices and Taxes 2024.\n"
    "See raw-data/07d_*.csv for URLs.",
    xy=(0.98, 0.05), xycoords="axes fraction",
    fontsize=9, color="#222", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#fdf2ee",
              edgecolor=COLOR_CN, linewidth=1.0))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/07d_industrial_electricity_prices.png", dpi=150); plt.close()
print("  saved 07d_industrial_electricity_prices.png")


# ---------------------------------------------------------------------------
# 7e. Global data-centre electricity demand — 2020–2030 projection
# ---------------------------------------------------------------------------
print("Data centre electricity demand projection...")
dc = load("07e_datacenter_electricity_demand_twh", index_col="year")
dc["Global"] = dc.sum(axis=1)

fig, ax = plt.subplots(figsize=(13, 5.5))
cols = ["United States", "China", "EU27", "Rest of World"]
colors = [COLOR_US, COLOR_CN, COLOR_EU, COLOR_OTHER]
ax.stackplot(dc.index, *[dc[c] for c in cols],
             labels=cols, colors=colors, alpha=0.88,
             edgecolor="white", linewidth=0.8)
ax.set_title("Global Data-Centre Electricity Demand — Historical and Projection, TWh",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Data-centre electricity demand (TWh)")
ax.set_ylim(0, 1200)
ax.legend(loc="upper left", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
for x in [2020, 2024, 2026, 2030]:
    total = dc.loc[x, "Global"]
    ax.text(x, total + 30, f"{total} TWh", ha="center", va="bottom",
            fontsize=10, color="#222", fontweight="bold")
ax.axvline(2024.5, color="#222", linestyle="--", linewidth=1, alpha=0.5)
ax.text(2024.5, 1100, "← actuals | projections →", ha="center", fontsize=8.5,
        color="#444", style="italic")
ax.annotate(
    "Global data-centre electricity demand on track to roughly double 2024→2030.\n"
    "US and China each project to ~400 TWh by 2030.\n"
    "The constraint that bites: where can this generation actually be built?\n\n"
    "Source: IEA Electricity 2024; IEA Energy & AI 2025 (scenario-based).\n"
    "See raw-data/07e_*.csv for URLs.",
    xy=(0.98, 0.05), xycoords="axes fraction",
    fontsize=9, color="#222", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/07e_datacenter_demand.png", dpi=150); plt.close()
print("  saved 07e_datacenter_demand.png")


# ---------------------------------------------------------------------------
# 7f. Nuclear reactors — operating and under construction by country
# ---------------------------------------------------------------------------
print("Nuclear reactors — operating and under construction...")
nuke = load("07f_nuclear_reactors_by_country")
nuke["total"] = nuke["operating"] + nuke["under_construction"]
nuke = nuke.sort_values("total", ascending=True)

fig, ax = plt.subplots(figsize=(13, 6.0))
y_pos = range(len(nuke))
op_colors = [COLOR_CN if c == "China" else COLOR_OTHER for c in nuke["country"]]
uc_colors = [COLOR_CN if c == "China" else "#888" for c in nuke["country"]]
ax.barh(y_pos, nuke["operating"], color=op_colors, alpha=0.7,
        label="Operating", edgecolor="white")
ax.barh(y_pos, nuke["under_construction"], left=nuke["operating"],
        color=uc_colors, alpha=1.0, label="Under construction",
        edgecolor="white", hatch="//")
ax.set_yticks(y_pos); ax.set_yticklabels(nuke["country"])
for i, (op, uc) in enumerate(zip(nuke["operating"], nuke["under_construction"])):
    ax.text(op + uc + 2, i, f"{op}+{uc}", va="center", fontsize=10,
            color="#222", fontweight="bold")
ax.set_xlim(0, 110)
ax.set_xlabel("Reactors — operating (solid) and under construction (hatched)")
ax.set_title("Nuclear Reactors — Operating and Under Construction by Country (end-2024)",
             fontsize=13, fontweight="bold")
ax.legend(loc="lower right", fontsize=10, framealpha=0.95)
ax.grid(axis="x", alpha=0.3)
ax.annotate(
    "China has 55 reactors operating plus 26 under construction — by far the\n"
    "world's largest nuclear build pipeline. Most other major economies have\n"
    "1-4 reactors under construction; many have none.\n"
    "Doubles existing capacity by ~2035 on current schedule.\n\n"
    "Source: IAEA PRIS — Power Reactor Information System (end-2024 snapshot).\n"
    "See raw-data/07f_*.csv for URLs.",
    xy=(0.98, 0.10), xycoords="axes fraction",
    fontsize=9, color="#222", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#fdf2ee",
              edgecolor=COLOR_CN, linewidth=1.0))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/07f_nuclear_reactors.png", dpi=150); plt.close()
print("  saved 07f_nuclear_reactors.png")


print("\nDone — energy charts saved to", OUTPUT)
