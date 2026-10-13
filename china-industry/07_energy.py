"""
07 — Energy: The AI-Era Strategic Asset

China's electricity build-out as a strategic asset, particularly in the
era where AI is becoming energy-bound rather than purely chip-bound.

The data:
- China generates more electricity than the US + EU27 combined; gap widening
- China installs more solar PV each year than the rest of the world combined
- China has the world's largest pipeline of nuclear reactors under
  construction (37 of ~78 worldwide, IAEA PRIS Oct 2026)
- Data-centre demand roughly doubles 2025->2030 (IEA); the US and China
  account for most of the increase
- (Industrial electricity prices are discussed in the report text only:
  IEA Electricity 2026 ratios; the 2023 price-snapshot chart was dropped
  in the October 2026 edition because no citable 2025 country table exists.)

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


def retrieved(name):
    """Return the '# retrieved:' date from a CSV header (for chart labels)."""
    with open(f"{RAW_DATA}/{name}.csv") as fh:
        for line in fh:
            if line.startswith("# retrieved:"):
                return line.split(":", 1)[1].strip()
    return "n/a"


# ---------------------------------------------------------------------------
# 7a. Total electricity generation by country (TWh)
# ---------------------------------------------------------------------------
print("Total electricity generation by country...")
gen = load("07a_electricity_generation_twh", index_col="year")
first_yr, last_yr = gen.index.min(), gen.index.max()
us_eu = gen["United States"] + gen["EU27"]

fig, ax = plt.subplots(figsize=(13, 5.5))
for col, color, lw in [("China", COLOR_CN, 2.8),
                       ("United States", COLOR_US, 2.0),
                       ("EU27", COLOR_EU, 1.8),
                       ("India", COLOR_IN, 1.5),
                       ("Japan", COLOR_JP, 1.5)]:
    ax.plot(gen.index, gen[col], label=col, color=color,
            linewidth=lw, marker="o", markersize=5)
ax.fill_between(gen.index, gen["China"], alpha=0.08, color=COLOR_CN)
ax.plot(gen.index, us_eu, color="#222", linewidth=1.5, linestyle="--",
        label="US + EU27 combined", alpha=0.6)
for col, color in [("China", COLOR_CN), ("United States", COLOR_US),
                   ("EU27", COLOR_EU), ("India", COLOR_IN),
                   ("Japan", COLOR_JP)]:
    y = gen[col].iloc[-1]
    ax.text(last_yr + 0.6, y, f"{y:,.0f}", va="center", fontsize=9.5,
            color=color, fontweight="bold")
ax.set_title(f"Electricity Generation by Country — TWh per Year, "
             f"{first_yr}–{last_yr}", fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Generation (TWh per year)")
ax.set_xlim(first_yr - 1, last_yr + 3)
ax.set_ylim(0, gen.max().max() * 1.12)
ax.legend(loc="upper left", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
cn_last, cn_prev = gen["China"].iloc[-1], gen["China"].iloc[-2]
ax.annotate(
    f"China's {last_yr} generation (~{cn_last:,.0f} TWh) is "
    f"{cn_last / us_eu.iloc[-1]:.1f}x the US + EU27 combined "
    f"(~{us_eu.iloc[-1]:,.0f} TWh).\n"
    f"China added ~{cn_last - cn_prev:,.0f} TWh in {last_yr} alone — "
    f"roughly Germany's entire 2025 generation (~500 TWh, Ember).\n\n"
    "Source: Ember Yearly Electricity Data / Global Electricity Review 2026\n"
    "(2000 onwards; 1990–95 from earlier compilation). See raw-data/07a_*.csv.",
    xy=(0.20, 0.97), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/07a_electricity_generation.png", dpi=150); plt.close()
print("  saved 07a_electricity_generation.png")


# ---------------------------------------------------------------------------
# 7b. China's electricity generation mix by source
# ---------------------------------------------------------------------------
print("China generation mix by source...")
mix = load("07b_china_generation_mix_pct", index_col="year")
m0, m1 = mix.index.min(), mix.index.max()
# Absolute coal TWh = share x total generation (07a) where both years exist
coal_twh = (mix["Coal"] / 100 * gen["China"]).dropna()

fig, ax = plt.subplots(figsize=(13, 5.5))
cols = ["Coal", "Gas", "Hydro", "Nuclear", "Wind", "Solar", "Bio / other"]
colors = [COLOR_COAL, COLOR_GAS, COLOR_HYDRO, COLOR_NUCLEAR,
          COLOR_WIND, COLOR_SOLAR, COLOR_BIO]
ax.stackplot(mix.index, *[mix[c] for c in cols],
             labels=cols, colors=colors, alpha=0.92,
             edgecolor="white", linewidth=0.8)
ax.set_title(f"China's Electricity Generation Mix — % by Source, {m0}–{m1}",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of total electricity generation")
ax.set_ylim(0, 100); ax.set_xlim(m0, m1)
ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=9,
          framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
ws = mix["Wind"] + mix["Solar"]
coal_note = ""
if len(coal_twh) >= 2 and coal_twh.index[-1] == m1:
    c_prev, c_last = coal_twh.iloc[-2], coal_twh.iloc[-1]
    trend = "fell" if c_last < c_prev else "rose"
    coal_note = (f"Coal generation {trend} in absolute terms in {m1} "
                 f"(~{c_prev:,.0f} -> ~{c_last:,.0f} TWh).\n")
ax.annotate(
    f"Coal share {mix['Coal'].iloc[0]:.0f}% ({m0}) -> {mix['Coal'].iloc[-1]:.0f}% ({m1}).\n"
    + coal_note +
    f"Wind + solar reached {ws.iloc[-1]:.0f}% of generation in {m1} "
    f"(solar alone {mix['Solar'].iloc[-1]:.0f}%);\n"
    f"nuclear {mix['Nuclear'].iloc[-1]:.1f}%.\n\n"
    "Source: Ember Global Electricity Review 2026.\n"
    "See raw-data/07b_*.csv for URLs.",
    xy=(0.02, 0.62), xycoords="axes fraction",
    fontsize=9, color="white", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#2c3e50",
              edgecolor="white", linewidth=0.8, alpha=0.85))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/07b_china_generation_mix.png", dpi=150); plt.close()
print("  saved 07b_china_generation_mix.png")


# ---------------------------------------------------------------------------
# 7c. Solar PV capacity additions by country (GW per year, IRENA basis)
# ---------------------------------------------------------------------------
print("Annual solar PV capacity additions...")
solar = load("07c_solar_pv_additions_gw", index_col="year")
solar["Global"] = solar.sum(axis=1)
solar["China_share_pct"] = (solar["China"] / solar["Global"] * 100).round(1)
s_last = solar.index.max()

fig, ax = plt.subplots(figsize=(13, 5.5))
cols = ["China", "EU27", "United States", "India", "Rest of World"]
colors = [COLOR_CN, COLOR_EU, COLOR_US, COLOR_IN, COLOR_OTHER]
bottom = pd.Series(0, index=solar.index)
for col, color in zip(cols, colors):
    ax.bar(solar.index, solar[col], bottom=bottom, label=col,
           color=color, edgecolor="white", linewidth=0.6, width=0.7)
    bottom = bottom + solar[col]
ymax = solar["Global"].max() * 1.22
for x, total in zip(solar.index, solar["Global"]):
    ax.text(x, total + ymax * 0.015, f"{total:.0f} GW", ha="center",
            va="bottom", fontsize=9, color="#222", fontweight="bold")
for x in solar.index[-3:]:
    ax.text(x, solar.loc[x, "China"] / 2,
            f"{solar.loc[x, 'China_share_pct']:.0f}%\nChina",
            ha="center", va="center", fontsize=10, color="white",
            fontweight="bold")
ax.set_title(f"Annual Solar PV Capacity Additions — by Country, GW per Year "
             f"({solar.index.min()}–{s_last})", fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("GW of solar PV added (IRENA, mostly AC)")
ax.set_ylim(0, ymax)
ax.set_xticks(solar.index)
ax.legend(loc="upper left", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
g0yr = 2020 if 2020 in solar.index else solar.index.min()
ax.annotate(
    f"China added {solar.loc[s_last, 'China']:.0f} GW in {s_last} — "
    f"{solar.loc[s_last, 'China_share_pct']:.0f}% of the world total, more than\n"
    f"every other country combined. Global additions rose from "
    f"~{solar.loc[g0yr, 'Global']:.0f} GW ({g0yr})\n"
    f"to ~{solar.loc[s_last, 'Global']:.0f} GW ({s_last}).\n\n"
    "Source: IRENA Renewable Capacity Statistics 2026 (net change in\n"
    "cumulative capacity, via Ember); China NEA. See raw-data/07c_*.csv.",
    xy=(0.17, 0.97), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/07c_solar_pv_additions.png", dpi=150); plt.close()
print("  saved 07c_solar_pv_additions.png")


# ---------------------------------------------------------------------------
# 7e. Data-centre electricity demand — IEA estimates and 2030 Base Case
# ---------------------------------------------------------------------------
print("Data centre electricity demand (IEA)...")
dc = load("07e_datacenter_electricity_demand_twh", index_col="year")
regions = ["United States", "China", "Europe", "Rest of World"]
reg_colors = [COLOR_US, COLOR_CN, COLOR_EU, COLOR_OTHER]
proj_yr = dc.index[dc["basis"] == "projection"].max()
base_yr = dc.dropna(subset=regions).index.min()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5),
                               gridspec_kw={"width_ratios": [1, 1.6]})
# Left: global totals
xs = [str(y) + (" (proj.)" if b == "projection" else "")
      for y, b in zip(dc.index, dc["basis"])]
bars = ax1.bar(xs, dc["Global"], color=["#555" if b == "estimate" else "#bbb"
                                        for b in dc["basis"]],
               edgecolor="#333", width=0.6,
               hatch=None)
for b, basis in zip(bars, dc["basis"]):
    if basis == "projection":
        b.set_hatch("//")
for x, v in zip(xs, dc["Global"]):
    ax1.text(x, v + 15, f"{v:.0f} TWh", ha="center", va="bottom",
             fontsize=10.5, fontweight="bold", color="#222")
ax1.set_ylim(0, dc["Global"].max() * 1.18)
ax1.set_ylabel("Data-centre electricity consumption (TWh)")
ax1.set_title("Global — IEA estimates and Base Case", fontsize=12,
              fontweight="bold")
ax1.grid(axis="y", alpha=0.3)

# Right: regional comparison base year vs projection year
import numpy as np
xpos = np.arange(len(regions)); w = 0.38
v0 = dc.loc[base_yr, regions].astype(float)
v1 = dc.loc[proj_yr, regions].astype(float)
ax2.bar(xpos - w / 2, v0, w, color=reg_colors, alpha=0.55,
        edgecolor="#333", label=f"{base_yr} (estimate)")
ax2.bar(xpos + w / 2, v1, w, color=reg_colors, alpha=1.0,
        edgecolor="#333", hatch="//", label=f"{proj_yr} (IEA Base Case)")
for i in range(len(regions)):
    ax2.text(xpos[i] - w / 2, v0.iloc[i] + 6, f"~{v0.iloc[i]:.0f}",
             ha="center", fontsize=9.5, color="#222")
    ax2.text(xpos[i] + w / 2, v1.iloc[i] + 6, f"~{v1.iloc[i]:.0f}",
             ha="center", fontsize=9.5, color="#222", fontweight="bold")
ax2.set_xticks(xpos); ax2.set_xticklabels(regions)
ax2.set_ylim(0, v1.max() * 1.25)
ax2.set_ylabel("TWh (derived from IEA shares and increments)")
ax2.set_title(f"By region, {base_yr} vs {proj_yr} — derived", fontsize=12,
              fontweight="bold")
ax2.legend(loc="upper right", fontsize=9.5, framealpha=0.95)
ax2.grid(axis="y", alpha=0.3)

plt.suptitle("Data-Centre Electricity Demand — Roughly Doubling by 2030 (IEA)",
             fontsize=13, fontweight="bold", y=1.0)
fig.text(0.5, -0.04,
         f"Regional TWh are derived: {base_yr} = IEA shares (US 45%, China 25%, "
         f"Europe 15%) x {dc.loc[base_yr, 'Global']:.0f} TWh; {proj_yr} = "
         f"{base_yr} + IEA increments (US +240, China +175, Europe +45 TWh). "
         "Rest of World = residual.\n"
         "Sources: IEA Energy and AI (2025); IEA Key Questions on Energy and AI "
         "(2026: 2025 = 485 TWh, 2030 ~950 TWh). See raw-data/07e_*.csv.",
         ha="center", fontsize=8.5, color="#555")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/07e_datacenter_demand.png", dpi=150,
            bbox_inches="tight")
plt.close()
print("  saved 07e_datacenter_demand.png")


# ---------------------------------------------------------------------------
# 7f. Nuclear reactors — operating and under construction by country
# ---------------------------------------------------------------------------
print("Nuclear reactors — operating and under construction...")
nuke = load("07f_nuclear_reactors_by_country")
nuke["total"] = nuke["operating"] + nuke["under_construction"]
nuke = nuke.sort_values("total", ascending=True).reset_index(drop=True)
snap = retrieved("07f_nuclear_reactors_by_country")

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
for i, (c, op, uc) in enumerate(zip(nuke["country"], nuke["operating"],
                                    nuke["under_construction"])):
    label = f"{op}+{uc}"
    if c == "Japan":
        label += "   (+19 idle units PRIS now classes 'suspended', not shown)"
    ax.text(op + uc + 1.5, i, label, va="center", fontsize=10 if c != "Japan" else 9,
            color="#222", fontweight="bold" if c != "Japan" else "normal")
ax.set_xlim(0, nuke["total"].max() * 1.3)
ax.set_xlabel("Reactors — operating (solid) and under construction (hatched)")
ax.set_title(f"Nuclear Reactors — Operating and Under Construction by Country "
             f"(IAEA PRIS, {snap})", fontsize=13, fontweight="bold")
ax.legend(loc="lower right", fontsize=10, framealpha=0.95)
ax.grid(axis="x", alpha=0.3)
cn = nuke[nuke["country"] == "China"].iloc[0]
others_uc = nuke[nuke["country"] != "China"]["under_construction"]
ax.annotate(
    f"China: {cn['operating']} operating + {cn['under_construction']} under "
    f"construction —\nthe world's largest build pipeline (~half of all reactors "
    f"under\nconstruction worldwide). Other economies shown: "
    f"{others_uc.min()}–{others_uc.max()} each.\n\n"
    "'Operating' = PRIS status Operational.\n"
    "Source: IAEA PRIS. See raw-data/07f_*.csv for URLs.",
    xy=(0.98, 0.16), xycoords="axes fraction",
    fontsize=9, color="#222", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#fdf2ee",
              edgecolor=COLOR_CN, linewidth=1.0))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/07f_nuclear_reactors.png", dpi=150); plt.close()
print("  saved 07f_nuclear_reactors.png")


print("\nDone — energy charts saved to", OUTPUT)
