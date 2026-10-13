"""
11 — What Could Derail It

The honest forward-looking section. Two-sided — risks to China *and*
risks to "we can wait it out" Western complacency.

The data:
- Working-age population (15-64) peaked ~2015 at ~1,018 M; UN WPP 2024
  (medium variant) projects ~750 M by 2050 — ~268 M below the 2015 peak,
  of which ~225 M falls between 2025 and 2050. India overtakes China on
  this measure between 2025 and 2030.
- Total fertility rate has collapsed to ~1.0 — half of replacement
- Floor area newly started (all buildings) is down ~74% from the 2019
  peak; real-estate investment has fallen year-on-year since 2022, and
  the 2025 fall (-17.2%) was the steepest yet
- ICOR (investment per unit of growth) has roughly doubled since the
  2000s — diminishing returns from infrastructure-led growth
- US chip / AI export controls broadened every cycle from 2019 to
  Sept 2025; since late 2025 the direction has been mixed (suspensions,
  case-by-case H200 licensing)
- The counter-view: China's goods trade surplus hit ~\\$1.19 trillion in
  2025 — a fresh record and the first above \\$1 trillion.

All annotation numbers are computed from the CSVs, so the charts stay
correct when rows are added.

This script only READS data. Every chart's numbers live in a CSV under
raw-data/ with a `# source:` header. See raw-data/SOURCES.md.
"""

import warnings
warnings.filterwarnings("ignore")

import os
import textwrap
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D

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

PROJ_START = 2025   # first projection year shown (UN WPP 2024 medium variant)

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
# Mark China's peak
peak_year = pop["china"].idxmax()
peak_val = pop["china"].max()
ax.plot(peak_year, peak_val, marker="*", markersize=18,
        color="black", zorder=5)
ax.text(peak_year + 0.5, peak_val + 18, f"China peak\n{peak_year}: {peak_val} M",
        fontsize=9.5, color="#222", fontweight="bold")
# Endpoint labels
last_year = pop.index[-1]
for col, color in [("china", COLOR_CN), ("india", COLOR_IN),
                   ("united_states", COLOR_US),
                   ("european_union", COLOR_EU)]:
    y = pop[col].iloc[-1]
    ax.text(last_year + 0.5, y, f"{y:.0f} M", va="center", fontsize=10,
            color=color, fontweight="bold")
ax.axvline(PROJ_START, color="#222", linestyle="--", linewidth=1, alpha=0.5)
ax.text(PROJ_START + 0.5, 1130, "← history | UN projection →", fontsize=8.5,
        color="#444", style="italic")

# Data-driven numbers for the annotation
china_end = pop["china"].iloc[-1]
fall_from_peak = peak_val - china_end
fall_from_proj = pop.loc[PROJ_START, "china"] - china_end
india_ahead = pop.index[pop["india"] > pop["china"]]
cross_hi = india_ahead.min()
cross_lo = pop.index[pop.index < cross_hi].max()
us_end = pop["united_states"].iloc[-1]

ax.set_title("Working-Age Population (15-64) — Historical and UN Projection, Million",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Working-age population (millions)")
ax.set_xlim(pop.index[0] - 1, last_year + 4)
ax.set_ylim(0, 1200)
ax.legend(loc="upper left", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
ax.annotate(
    f"China's working-age cohort peaked in {peak_year} ({peak_val:,.0f} M). The UN\n"
    f"projects {china_end:,.0f} M by {last_year}: ~{fall_from_peak:,.0f} M below the peak,\n"
    f"of which ~{fall_from_proj:,.0f} M falls in {PROJ_START}-{last_year} — about the size of\n"
    f"today's US working-age population. India overtakes China on this\n"
    f"measure between {cross_lo} and {cross_hi}.\n\n"
    "Source: UN World Population Prospects 2024 (medium variant).\n"
    "See raw-data/11a_*.csv for URLs.",
    xy=(0.96, 0.30), xycoords="axes fraction",
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

# Floor area (NBS headline series: all building types, not residential only)
ax1.bar(re.index, re["floor_started_mn_m2"],
        color=COLOR_CN, edgecolor="white", alpha=0.85, width=0.65)
peak_yr = re["floor_started_mn_m2"].idxmax()
peak_val = re["floor_started_mn_m2"].max()
last_yr = re.index[-1]
last_val = re["floor_started_mn_m2"].iloc[-1]
ax1.set_ylim(0, peak_val * 1.32)
ax1.annotate(
    f"Peak {peak_yr}: {peak_val:,.0f}M m²\n"
    f"{last_yr}: {last_val:,.0f}M m² (-{100*(1-last_val/peak_val):.0f}%)",
    xy=(peak_yr, peak_val), xytext=(re.index[0] + 0.5, peak_val * 1.12),
    fontsize=10, color="#222", fontweight="bold",
    arrowprops=dict(arrowstyle="->", color="#444"))
ax1.set_xlabel("Year")
ax1.set_ylabel("Million m² newly started (all buildings)")
ax1.set_title("Floor space newly started (all building types)",
              fontsize=12, fontweight="bold")
ax1.xaxis.set_major_locator(mticker.MultipleLocator(1))
ax1.tick_params(axis="x", labelsize=9)
ax1.grid(axis="y", alpha=0.3)

# YoY investment
inv = re["property_investment_yoy_pct"]
colors_inv = [COLOR_CN if v < 0 else COLOR_OTHER for v in inv]
ax2.bar(re.index, inv, color=colors_inv, edgecolor="white", width=0.65)
for x, v in zip(re.index, inv):
    ax2.text(x, v + (0.5 if v >= 0 else -0.5),
             f"{v:.1f}%", ha="center",
             va="bottom" if v >= 0 else "top",
             fontsize=9, color="#222", fontweight="bold")
ax2.axhline(0, color="#222", linewidth=0.8)
ax2.set_ylim(min(inv.min() * 1.25, -2), max(inv.max() * 1.25, 2))
first_neg = inv.index[inv < 0].min()
ax2.set_xlabel("Year")
ax2.set_ylabel("Real-estate investment, YoY %")
ax2.set_title(f"Real-estate investment growth — contracting every year since {first_neg}",
              fontsize=12, fontweight="bold")
ax2.xaxis.set_major_locator(mticker.MultipleLocator(1))
ax2.tick_params(axis="x", labelsize=9)
ax2.grid(axis="y", alpha=0.3)

plt.suptitle("China Real-Estate Sector — Volume Collapse and Investment Contraction",
             fontsize=13, fontweight="bold", y=1.02)
fig.text(0.5, -0.02,
         "Source: National Bureau of Statistics (NBS); IMF China Article IV reports. "
         "YoY rates are NBS comparable-basis figures. See raw-data/11b_*.csv for URLs.",
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
ax1.set_xlabel("Period (multi-year average)")
ax1.set_ylabel("ICOR — Incremental Capital-Output Ratio")
ax1.set_ylim(0, max(12, icor["china_icor"].max() * 1.6))
ax1.grid(axis="y", alpha=0.3)

ax2 = ax1.twinx()
ax2.plot(x, icor["china_gdp_growth_pct"], color="#222",
         linewidth=2.5, marker="s", markersize=8,
         label="Real GDP growth, % (right axis)")
for xi, v in zip(x, icor["china_gdp_growth_pct"]):
    ax2.text(xi, v + 0.7, f"{v:.1f}%", ha="center", va="bottom",
             fontsize=10, color="#222", fontweight="bold")
ax2.set_ylabel("Real GDP growth (% per year)", color="#222")
ax2.set_ylim(0, max(20, icor["china_gdp_growth_pct"].max() * 1.75))
ax2.tick_params(axis="y", labelcolor="#222")

ax1.set_title("China ICOR Rising as GDP Growth Slows — More Capital Needed per Unit of Output",
              fontsize=13, fontweight="bold")
# Combined legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=10)

first_p, last_p = icor.index[0], icor.index[-1]
first_v, last_v = icor["china_icor"].iloc[0], icor["china_icor"].iloc[-1]
ax1.annotate(
    f"ICOR roughly doubled — from {first_v:.1f} ({first_p}) to {last_v:.1f} ({last_p}).\n"
    f"Meaning: each unit of extra GDP now needs ~{last_v/first_v:.1f}x as much\n"
    "investment. Classic diminishing-returns picture — also seen in late-stage\n"
    "Japan (1985-95) and Korea (1995-2005).\n\n"
    "Source: derived from World Bank WDI (gross capital formation % GDP /\n"
    "real GDP growth, period averages). See raw-data/11c_*.csv for URLs.",
    xy=(0.02, 0.95), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/11c_icor.png", dpi=150); plt.close()
print("  saved 11c_icor.png")


# ---------------------------------------------------------------------------
# 11d. US chip export controls — expanding, then mixed, scope
# ---------------------------------------------------------------------------
print("US chip export controls timeline...")
ctrl = load("11d_us_chip_export_controls_timeline")
ctrl["fyear"] = ctrl["year"] + (ctrl["month"] - 0.5) / 12
# Easing events are identified from the event wording in the CSV
EASING = r"rescind|suspend|granted|case-by-case"
ctrl["easing"] = ctrl["event"].str.contains(EASING, case=False, regex=True)

x_lo = ctrl["year"].min() - 0.5
x_hi = ctrl["year"].max() + 1.0
mid = (x_lo + x_hi) / 2

n = len(ctrl)
fig, ax = plt.subplots(figsize=(14, 1.5 + 0.62 * n))
y_pos = list(range(n))
ax.scatter(ctrl["fyear"], y_pos,
           color=[COLOR_KR if e else COLOR_US for e in ctrl["easing"]],
           s=180, zorder=3, edgecolor="white", linewidth=1.5)
for i, row in ctrl.iterrows():
    summary = textwrap.fill(row["scope_summary"], 72,
                            subsequent_indent="  ")
    label = f"{row['event']}\n  {summary}"
    date = f"{int(row['year'])}-{int(row['month']):02d}"
    color = COLOR_KR if row["easing"] else COLOR_US
    if row["fyear"] < mid:        # text to the right of the point
        ax.text(row["fyear"] + 0.12, i, label, va="center", ha="left",
                fontsize=9, color="#222")
        ax.text(row["fyear"] - 0.15, i, date, va="center", ha="right",
                fontsize=9, color=color, fontweight="bold")
    else:                          # late events: text to the left
        ax.text(row["fyear"] - 0.12, i, label, va="center", ha="right",
                fontsize=9, color="#222")
        ax.text(row["fyear"] + 0.15, i, date, va="center", ha="left",
                fontsize=9, color=color, fontweight="bold")
ax.set_xlim(x_lo, x_hi)
ax.set_ylim(-0.7, n - 0.3)
ax.set_yticks([])
ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
ax.set_xlabel("Year")
ax.set_title(f"US Semiconductor / AI-Compute Export Controls Targeting China, "
             f"{ctrl['year'].min()}–{ctrl['year'].max()}",
             fontsize=13, fontweight="bold")
for spine in ("top", "right", "left"):
    ax.spines[spine].set_visible(False)
ax.grid(axis="x", alpha=0.3)
ax.invert_yaxis()
ax.legend(handles=[
    Line2D([0], [0], marker="o", color="w", markerfacecolor=COLOR_US,
           markersize=11, label="Tightening"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor=COLOR_KR,
           markersize=11, label="Easing / suspension")],
    loc="lower left", fontsize=9.5, framealpha=0.95)
last_tight = ctrl.loc[~ctrl["easing"]].iloc[-1]
fig.text(0.5, 0.005,
         f"Each cycle to {int(last_tight['year'])}-{int(last_tight['month']):02d} broadened the perimeter "
         "(Huawei → SMIC → advanced-AI chips → named AI labs → HBM + equipment → affiliates).\n"
         "Since mid-2025 the direction has been mixed: AI Diffusion Rule rescinded, H20 licensed, "
         "affiliates rule suspended, H200 moved to case-by-case.\n"
         "Source: BIS / Federal Register; NVIDIA SEC filings; press for the Aug 2025 revenue-share deal. "
         "See raw-data/11d_*.csv.",
         ha="center", va="bottom", fontsize=9, color="#333")
plt.tight_layout(rect=(0, 0.07, 1, 1))
plt.savefig(f"{OUTPUT}/11d_us_chip_controls.png", dpi=150); plt.close()
print("  saved 11d_us_chip_controls.png")


# ---------------------------------------------------------------------------
# 11e. China's goods trade surplus — the counter-view
# ---------------------------------------------------------------------------
print("China's trade surplus trajectory...")
ts = load("11e_china_trade_surplus_usd_bn", index_col="year")
s = ts["trade_surplus_usd_bn"]

fig, ax = plt.subplots(figsize=(13, 5.2))
ax.fill_between(ts.index, 0, s, color=COLOR_CN, alpha=0.12)
ax.plot(ts.index, s, color=COLOR_CN, linewidth=2.8, marker="o", markersize=7)
y_top = s.max() * 1.2
pad = y_top * 0.025
prev = None
for x, y in zip(ts.index, s):
    lbl = f"\\${y/1000:.2f}tn" if y >= 1000 else f"\\${y:,.0f}B"
    # Dips (value below the previous point) are labelled underneath to
    # avoid colliding with the neighbouring labels in dense years.
    below = prev is not None and y < prev
    ax.text(x + (0 if below else -0.15), y - pad if below else y + pad, lbl,
            ha="center" if below else "right" if x != ts.index[0] else "center",
            va="top" if below else "bottom",
            fontsize=9, color="#222", fontweight="bold")
    prev = y
ax.set_title(f"China's Goods Trade Surplus — Annual, USD Billion, "
             f"{ts.index[0]}–{ts.index[-1]}",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("USD billion (current)")
ax.set_ylim(0, y_top)
ax.set_xlim(ts.index[0] - 1, ts.index[-1] + 1)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(5))

last_y, last_v = ts.index[-1], s.iloc[-1]
prev_v = s.iloc[-2]
ax.annotate(
    "The counter-view: tariffs, decoupling rhetoric, and domestic-demand\n"
    f"weakness have not slowed the export engine. China's {last_y} goods trade\n"
    f"surplus hit ~\\${last_v:,.0f}B (up from \\${prev_v:,.0f}B), an all-time record —\n"
    "despite US tariffs that peaked at 145% in April 2025.\n\n"
    "Source: China General Administration of Customs; NBS; IMF DOT.\n"
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
t_first, t_last = tfr.index[0], tfr.index[-1]

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
    ax.text(t_last + 0.4, y, f"{y:.2f}", va="center", fontsize=10,
            color=color, fontweight="bold")
ax.axhline(2.1, color="#222", linestyle="--", linewidth=1, alpha=0.7)
ax.text(t_first + 0.3, 2.18, "Replacement rate (~2.1)",
        fontsize=9, color="#222", style="italic")
ax.set_title(f"Total Fertility Rate — Births per Woman, {t_first}–{t_last}",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Births per woman")
ax.set_xlim(t_first - 1, t_last + 2.5)
ax.set_ylim(0, 4.5)
ax.legend(loc="upper right", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
cn_last = tfr["china"].iloc[-1]
ax.annotate(
    f"China's TFR has collapsed to {cn_last:.2f} ({t_last}) — half of replacement.\n"
    "Below Japan, above only Korea's ultra-low. The 2015 end of the\n"
    "one-child policy and 2021 three-child policy did not reverse the trend;\n"
    "births fell again to a record-low 7.92 M in 2025 (NBS).\n"
    "Compounds the working-age decline in 11a.\n\n"
    "Source: World Bank SP.DYN.TFRT.IN; UN WPP 2024; NBS.\n"
    "See raw-data/11f_*.csv for URLs.",
    xy=(0.42, 0.97), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/11f_fertility_rate.png", dpi=150); plt.close()
print("  saved 11f_fertility_rate.png")


print("\nDone — headwinds charts saved to", OUTPUT)
