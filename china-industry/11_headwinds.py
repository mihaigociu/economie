"""
11 — What Could Derail It

The honest forward-looking section. Two-sided — risks to China *and*
risks to "we can wait it out" Western complacency.

The data:
- Working-age population peaked ~2015 and has fallen by ~12 million by
  2024; UN projects a further ~220 million decline by 2050
- Total fertility rate has collapsed to ~1.0 — half of replacement
- Property-sector floor area started fell 50%+ from 2019 peak;
  real-estate investment has been declining year-on-year since 2022
- ICOR (investment per unit of growth) has roughly doubled since the
  early 2000s — diminishing returns from infrastructure-led growth
- US chip / AI export controls have expanded substantially each cycle
  (2019, 2020, 2022, 2023, 2024)
- The counter-view: China's goods trade surplus hit ~\\$992B in 2024 —
  a fresh record. Decoupling rhetoric and demand weakness have not
  reduced the export engine.

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
COLOR_OTHER  = "#bdc3c7"


def load(name, **kwargs):
    return pd.read_csv(f"{RAW_DATA}/{name}.csv", comment="#", **kwargs)


# ---------------------------------------------------------------------------
# 11a. Working-age population trajectories (1990-2050)
# ---------------------------------------------------------------------------
print("Working-age population trajectories...")
pop = load("11a_china_working_age_population", index_col="year")

fig, ax = plt.subplots(figsize=(13, 5.5))
for col, color, lw in [("china", COLOR_CN, 2.8),
                       ("india", COLOR_IN, 2.0),
                       ("united_states", COLOR_US, 1.6),
                       ("european_union", COLOR_EU, 1.6)]:
    lbl = {"china": "China", "india": "India",
           "united_states": "United States",
           "european_union": "European Union"}[col]
    ax.plot(pop.index, pop[col], label=lbl, color=color,
            linewidth=lw, marker="o", markersize=5)
ax.fill_between(pop.index, pop["china"], alpha=0.07, color=COLOR_CN)
# Mark China's peak around 2015
peak_year = pop["china"].idxmax()
peak_val = pop["china"].max()
ax.plot(peak_year, peak_val, marker="*", markersize=18,
        color="black", zorder=5)
ax.text(peak_year + 0.5, peak_val + 18, f"China peak\n{peak_year}: {peak_val} M",
        fontsize=9.5, color="#222", fontweight="bold")
# Endpoint labels
for col, color in [("china", COLOR_CN), ("india", COLOR_IN),
                   ("united_states", COLOR_US),
                   ("european_union", COLOR_EU)]:
    y = pop[col].iloc[-1]
    ax.text(2050.5, y, f"{y:.0f} M", va="center", fontsize=10,
            color=color, fontweight="bold")
ax.axvline(2025, color="#222", linestyle="--", linewidth=1, alpha=0.5)
ax.text(2025.5, 1080, "← history | UN projection →", fontsize=8.5,
        color="#444", style="italic")
ax.set_title("Working-Age Population (15-64) — Historical and UN Projection, Million",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Working-age population (millions)")
ax.set_ylim(0, 1200)
ax.legend(loc="upper left", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
ax.annotate(
    "China's working-age cohort peaked around 2015 and is projected to fall\n"
    "by ~270 million between 2015 and 2050 — roughly the size of the US\n"
    "working-age population. India overtakes China on this measure around 2024.\n\n"
    "Source: UN World Population Prospects 2024 (medium variant).\n"
    "See raw-data/11a_*.csv for URLs.",
    xy=(0.98, 0.05), xycoords="axes fraction",
    fontsize=9, color="#222", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/11a_working_age_population.png", dpi=150); plt.close()
print("  saved 11a_working_age_population.png")


# ---------------------------------------------------------------------------
# 11b. China real-estate slump — floor area started + investment YoY
# ---------------------------------------------------------------------------
print("Real-estate sector indicators...")
re = load("11b_china_real_estate_indicators", index_col="year")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.0))

# Floor area
ax1.bar(re.index, re["floor_started_mn_m2"],
        color=COLOR_CN, edgecolor="white", alpha=0.85, width=0.65)
peak_yr = re["floor_started_mn_m2"].idxmax()
peak_val = re["floor_started_mn_m2"].max()
last_val = re["floor_started_mn_m2"].iloc[-1]
ax1.annotate(
    f"Peak {peak_yr}: {peak_val:,.0f}M m²\n"
    f"2024: {last_val:,.0f}M m² (-{100*(1-last_val/peak_val):.0f}%)",
    xy=(peak_yr, peak_val), xytext=(2017, 2700),
    fontsize=10, color="#222", fontweight="bold",
    arrowprops=dict(arrowstyle="->", color="#444"))
ax1.set_xlabel("Year")
ax1.set_ylabel("Million m² of residential floor area started")
ax1.set_title("New-build floor area started (residential)",
              fontsize=12, fontweight="bold")
ax1.grid(axis="y", alpha=0.3)

# YoY investment
colors_inv = [COLOR_CN if v < 0 else COLOR_OTHER for v in re["property_investment_yoy_pct"]]
ax2.bar(re.index, re["property_investment_yoy_pct"],
        color=colors_inv, edgecolor="white", width=0.65)
for x, v in zip(re.index, re["property_investment_yoy_pct"]):
    ax2.text(x, v + (0.5 if v >= 0 else -0.5),
             f"{v:.1f}%", ha="center",
             va="bottom" if v >= 0 else "top",
             fontsize=9, color="#222", fontweight="bold")
ax2.axhline(0, color="#222", linewidth=0.8)
ax2.set_xlabel("Year")
ax2.set_ylabel("Real-estate investment, YoY %")
ax2.set_title("Real-estate investment growth — sharp contraction since 2022",
              fontsize=12, fontweight="bold")
ax2.grid(axis="y", alpha=0.3)

plt.suptitle("China Real-Estate Sector — Volume Collapse and Investment Contraction",
             fontsize=13, fontweight="bold", y=1.02)
fig.text(0.5, -0.02,
         "Source: National Bureau of Statistics (NBS); IMF China Article IV reports. "
         "See raw-data/11b_*.csv for URLs.",
         ha="center", fontsize=9, color="#555")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/11b_real_estate.png", dpi=150, bbox_inches="tight")
plt.close()
print("  saved 11b_real_estate.png")


# ---------------------------------------------------------------------------
# 11c. ICOR — diminishing returns on capital
# ---------------------------------------------------------------------------
print("ICOR — diminishing returns...")
icor = load("11c_china_icor_capital_efficiency").set_index("period")

fig, ax1 = plt.subplots(figsize=(13, 5.5))

x = range(len(icor))
ax1.bar(x, icor["china_icor"], color=COLOR_CN, alpha=0.85,
        edgecolor="white", width=0.55, label="ICOR (left axis)")
for xi, v in zip(x, icor["china_icor"]):
    ax1.text(xi, v + 0.15, f"{v:.1f}", ha="center", fontsize=11,
             color="#222", fontweight="bold")
ax1.set_xticks(x)
ax1.set_xticklabels(icor.index)
ax1.set_xlabel("Period (5-year average)")
ax1.set_ylabel("ICOR — Incremental Capital-Output Ratio")
ax1.set_ylim(0, 10)
ax1.grid(axis="y", alpha=0.3)

ax2 = ax1.twinx()
ax2.plot(x, icor["china_gdp_growth_pct"], color="#222",
         linewidth=2.5, marker="s", markersize=8,
         label="Real GDP growth, % (right axis)")
for xi, v in zip(x, icor["china_gdp_growth_pct"]):
    ax2.text(xi + 0.18, v, f"{v:.1f}%", va="center", fontsize=10,
             color="#222", fontweight="bold")
ax2.set_ylabel("Real GDP growth (% per year)", color="#222")
ax2.set_ylim(0, 14)
ax2.tick_params(axis="y", labelcolor="#222")

ax1.set_title("China ICOR Rising as GDP Growth Slows — More Capital Needed per Unit of Output",
              fontsize=13, fontweight="bold")
# Combined legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=10)
ax1.annotate(
    "ICOR roughly doubled — from ~3.6 (early-2000s WTO boom) to ~8.0 (2021-24).\n"
    "Meaning: today it takes twice as much investment to generate one unit of\n"
    "extra GDP. Classic diminishing-returns picture — also seen in late-stage\n"
    "Japan (1985-95) and Korea (1995-2005).\n\n"
    "Source: derived from World Bank data; IMF China Article IV 2024.\n"
    "See raw-data/11c_*.csv for URLs.",
    xy=(0.02, 0.95), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/11c_icor.png", dpi=150); plt.close()
print("  saved 11c_icor.png")


# ---------------------------------------------------------------------------
# 11d. US chip export controls — expanding scope, 2019-2024
# ---------------------------------------------------------------------------
print("US chip export controls timeline...")
ctrl = load("11d_us_chip_export_controls_timeline")
ctrl["fyear"] = ctrl["year"] + ctrl["month"] / 12

fig, ax = plt.subplots(figsize=(14, 5.5))
y_pos = list(range(len(ctrl)))
ax.scatter(ctrl["fyear"], y_pos, color=COLOR_US, s=180, zorder=3,
           edgecolor="white", linewidth=1.5)
for i, row in ctrl.iterrows():
    ax.text(row["fyear"] + 0.12, i,
            f"{row['event']}\n  {row['scope_summary']}",
            va="center", fontsize=9.5, color="#222")
    ax.text(row["fyear"] - 0.18, i,
            f"{int(row['year'])}-{int(row['month']):02d}",
            va="center", ha="right", fontsize=9, color=COLOR_US,
            fontweight="bold")
ax.set_xlim(2018.5, 2026)
ax.set_ylim(-0.7, len(ctrl) - 0.3)
ax.set_yticks([])
ax.set_xlabel("Year")
ax.set_title("US Semiconductor / AI-Compute Export Controls Targeting China — Expanding Scope",
             fontsize=13, fontweight="bold")
for spine in ("top", "right", "left"):
    ax.spines[spine].set_visible(False)
ax.grid(axis="x", alpha=0.3)
ax.invert_yaxis()
ax.annotate(
    "Each cycle has broadened the perimeter:\n"
    "Huawei → SMIC → all advanced-AI chips → AI-lab specific →\n"
    "HBM + 24 toolmakers + 140 firms. 'Small yard, high fence'\n"
    "has become a noticeably larger yard.",
    xy=(2019.0, 4.7), xycoords="data",
    fontsize=9.5, color="#222", va="bottom", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/11d_us_chip_controls.png", dpi=150); plt.close()
print("  saved 11d_us_chip_controls.png")


# ---------------------------------------------------------------------------
# 11e. China's goods trade surplus — the counter-view
# ---------------------------------------------------------------------------
print("China's trade surplus trajectory...")
ts = load("11e_china_trade_surplus_usd_bn", index_col="year")

fig, ax = plt.subplots(figsize=(13, 5.2))
ax.fill_between(ts.index, 0, ts["trade_surplus_usd_bn"],
                color=COLOR_CN, alpha=0.12)
ax.plot(ts.index, ts["trade_surplus_usd_bn"], color=COLOR_CN,
        linewidth=2.8, marker="o", markersize=7)
for x, y in zip(ts.index, ts["trade_surplus_usd_bn"]):
    ax.text(x, y + 30, f"\\${y:,.0f}B", ha="center", va="bottom",
            fontsize=10, color="#222", fontweight="bold")
ax.set_title("China's Goods Trade Surplus — Annual, USD Billion",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("USD billion (current)")
ax.set_ylim(0, 1150)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
ax.annotate(
    "The counter-view: tariffs, decoupling rhetoric, and domestic-demand\n"
    "weakness have not slowed the export engine. China's 2024 goods trade\n"
    "surplus hit ~\\$992B, an all-time record. The same demographic argument\n"
    "made for Japan (1990) and Germany (2005) didn't stop either from\n"
    "continuing to export frontier engineering products.\n\n"
    "Source: China General Administration of Customs; IMF DOT.\n"
    "See raw-data/11e_*.csv for URLs.",
    xy=(0.02, 0.95), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/11e_china_trade_surplus.png", dpi=150); plt.close()
print("  saved 11e_china_trade_surplus.png")


# ---------------------------------------------------------------------------
# 11f. Fertility rate collapse
# ---------------------------------------------------------------------------
print("Fertility rate collapse...")
tfr = load("11f_china_fertility_rate", index_col="year")

fig, ax = plt.subplots(figsize=(13, 5.2))
for col, color, lw in [("china", COLOR_CN, 2.8),
                       ("south_korea", COLOR_KR, 1.6),
                       ("japan", COLOR_JP, 1.6),
                       ("united_states", COLOR_US, 1.6),
                       ("india", COLOR_IN, 1.6)]:
    lbl = {"china": "China", "south_korea": "South Korea",
           "japan": "Japan", "united_states": "United States",
           "india": "India"}[col]
    ax.plot(tfr.index, tfr[col], label=lbl, color=color,
            linewidth=lw, marker="o", markersize=6)
    y = tfr[col].iloc[-1]
    ax.text(2023.3, y, f"{y:.2f}", va="center", fontsize=10,
            color=color, fontweight="bold")
ax.axhline(2.1, color="#222", linestyle="--", linewidth=1, alpha=0.7)
ax.text(1990.3, 2.18, "Replacement rate (~2.1)",
        fontsize=9, color="#222", style="italic")
ax.set_title("Total Fertility Rate — Births per Woman, 1990–2023",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Births per woman")
ax.set_ylim(0, 4.5)
ax.legend(loc="upper right", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
ax.annotate(
    "China's TFR has collapsed to ~1.0 — half of replacement.\n"
    "Below Japan, similar to Korea's ultra-low. The 2015 end of the\n"
    "one-child policy and 2021 three-child policy did not reverse the trend.\n"
    "Compounds the working-age decline in 11a.\n\n"
    "Source: World Bank SP.DYN.TFRT.IN; UN WPP 2024.\n"
    "See raw-data/11f_*.csv for URLs.",
    xy=(0.02, 0.55), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/11f_fertility_rate.png", dpi=150); plt.close()
print("  saved 11f_fertility_rate.png")


print("\nDone — headwinds charts saved to", OUTPUT)
