"""
Regional Disparities: NUTS2 GDP per capita, Bucharest vs rest, population change.
Sources: Eurostat regional accounts (nama_10r_2gdp, nama_10r_3popgdp) and
regional demography (demo_r_d2jan). No embedded values: every figure is fetched.

"Romania excluding Bucuresti-Ilfov" is DERIVED here:
    (GDP_PPS[RO] - GDP_PPS[RO32]) / (pop[RO] - pop[RO32]),  relative to EU27 GDP_PPS / pop,
i.e. the population-weighted average of the other seven regions.
"""

import pandas as pd
import matplotlib.pyplot as plt

from common import OUTPUT, save_csv, eurostat_wide, eurostat_df, geo_col, es_url

LAST_YEAR = 2025
FIRST_YEAR = 2000

RO_NUTS2 = {
    "RO11": "Nord-Vest", "RO12": "Centru", "RO21": "Nord-Est", "RO22": "Sud-Est",
    "RO31": "Sud-Muntenia", "RO32": "Bucuresti-Ilfov", "RO41": "Sud-Vest Oltenia", "RO42": "Vest",
}

# ---------------------------------------------------------------------------
# 1. NUTS2 GDP per capita PPS (% of EU27) — latest year
# ---------------------------------------------------------------------------
print("Fetching NUTS2 GDP per capita (nama_10r_2gdp, PPS_HAB_EU27_2020)...")
idx = eurostat_wide("nama_10r_2gdp", {"unit": "PPS_HAB_EU27_2020"},
                    ["RO"] + list(RO_NUTS2), FIRST_YEAR, LAST_YEAR)
latest = int(idx[list(RO_NUTS2)].dropna(how="any").index.max())
nuts2 = idx.loc[latest, list(RO_NUTS2)].rename(index=RO_NUTS2)
nuts2.index.name = "region"; nuts2.name = "gdp_per_capita_pps_pct_eu27"
save_csv(nuts2.to_frame(), "07a_nuts2_gdp_pct_eu27",
         f"Eurostat nama_10r_2gdp — GDP per inhabitant in PPS, % of EU27_2020 average (PPS_HAB_EU27_2020), {latest}",
         es_url("nama_10r_2gdp"),
         [f"national value for {latest}: {idx.loc[latest, 'RO']:.0f}"])

nuts2_sorted = nuts2.sort_values()
bar_colors = ["#c0392b" if v < 50 else "#e67e22" if v < 75 else "#27ae60" for v in nuts2_sorted]
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(nuts2_sorted.index, nuts2_sorted.values, color=bar_colors)
ax.axvline(100, color="grey", linestyle="--", linewidth=1.2, label="EU27 average = 100")
ax.axvline(75, color="#e67e22", linestyle=":", linewidth=1, alpha=0.8, label="75% cohesion threshold")
ax.axvline(idx.loc[latest, "RO"], color="#2980b9", linestyle="-.", linewidth=1,
           label=f"Romania = {idx.loc[latest, 'RO']:.0f}")
for bar, val in zip(bars, nuts2_sorted.values):
    ax.text(val + 1.5, bar.get_y() + bar.get_height() / 2, f"{val:.0f}", va="center", fontsize=9)
ax.set_xlim(0, nuts2_sorted.max() * 1.1)
ax.set_title(f"Romania NUTS2 Regions: GDP per Capita (PPS), EU27 = 100, {latest}",
             fontsize=12, fontweight="bold")
ax.set_xlabel("% of EU27 average"); ax.legend(fontsize=8, loc="lower right")
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/07a_nuts2_gdp.png", dpi=150); plt.close()
print("  saved 07a_nuts2_gdp.png")

# ---------------------------------------------------------------------------
# 2. Bucharest vs rest of Romania — time series (derived)
# ---------------------------------------------------------------------------
print("Building Bucharest divergence series (derived)...")
gdp = eurostat_wide("nama_10r_2gdp", {"unit": "MIO_PPS_EU27_2020"},
                    ["RO", "RO32", "EU27_2020"], FIRST_YEAR, LAST_YEAR)
pop_ra = eurostat_wide("nama_10r_3popgdp", {"unit": "THS"},
                       ["RO", "RO32", "EU27_2020"], FIRST_YEAR, LAST_YEAR)
jan = eurostat_wide("demo_r_d2jan", {"sex": "T", "age": "TOTAL", "unit": "NR"},
                    ["RO", "RO32"], FIRST_YEAR, LAST_YEAR + 1) / 1000
jan_avg = (jan + jan.shift(-1)) / 2          # mean of 1 Jan t and 1 Jan t+1
pop = pop_ra.copy()
filled = pop["RO32"].isna() & jan_avg["RO32"].notna()
pop.loc[filled, "RO32"] = jan_avg.loc[filled, "RO32"]
pop = pop.reindex(gdp.index)

eu_pc = gdp["EU27_2020"] / pop["EU27_2020"]
div = pd.DataFrame({
    "Bucuresti_Ilfov": gdp["RO32"] / pop["RO32"] / eu_pc * 100,
    "Romania_national_avg": gdp["RO"] / pop["RO"] / eu_pc * 100,
    "Romania_excl_Bucharest_derived": (gdp["RO"] - gdp["RO32"]) / (pop["RO"] - pop["RO32"]) / eu_pc * 100,
})
div["RO32_population_estimated"] = filled.reindex(div.index).fillna(False)
div = div.dropna(subset=["Bucuresti_Ilfov", "Romania_national_avg"])
div.index.name = "year"
# consistency check against Eurostat's published (rounded) index
check = (div[["Bucuresti_Ilfov", "Romania_national_avg"]]
         - idx[["RO32", "RO"]].rename(columns={"RO32": "Bucuresti_Ilfov", "RO": "Romania_national_avg"})).abs()
max_dev = check.max().max()
print(f"  max deviation from published index: {max_dev:.2f} pts")
if max_dev > 1.5:
    raise RuntimeError(f"derived regional index deviates from Eurostat's by {max_dev:.2f} pts")
save_csv(div.round(1), "07b_bucharest_divergence_pct_eu27",
         "Derived from Eurostat nama_10r_2gdp (GDP, MIO_PPS_EU27_2020) and nama_10r_3popgdp (average population, THS); "
         "GDP per inhabitant in PPS as % of EU27",
         es_url("nama_10r_2gdp"),
         ["Romania_excl_Bucharest_derived = (GDP RO - GDP RO32) / (pop RO - pop RO32), relative to EU27 — derived, not published by Eurostat",
          "where nama_10r_3popgdp lacks RO32 population (2002-2011) the mean of 1-Jan populations from demo_r_d2jan is used (flag column)",
          f"check: derived RO32/RO values are within {max_dev:.2f} pts of Eurostat's published rounded index"])

fig, ax = plt.subplots(figsize=(12, 5.5))
est = div["RO32_population_estimated"]
for col, color, ls, label in [
    ("Bucuresti_Ilfov", "#c0392b", "-", "Bucuresti-Ilfov"),
    ("Romania_national_avg", "#2980b9", "-", "Romania (national)"),
    ("Romania_excl_Bucharest_derived", "#e67e22", "--", "Romania excl. Bucuresti-Ilfov (derived)"),
]:
    s = div[col]
    ax.plot(s.index, s.values, color=color, linewidth=2.3, linestyle=ls, label=label)
    solid = ~est if col != "Romania_national_avg" else s.notna()
    ax.plot(s.index[solid], s[solid], "o", color=color, markersize=4)
    if col != "Romania_national_avg":
        ax.plot(s.index[est], s[est], "o", markerfacecolor="white", markeredgecolor=color, markersize=5)
    ax.annotate(f"{s.iloc[-1]:.0f}", (s.index[-1], s.iloc[-1]), xytext=(6, -3),
                textcoords="offset points", color=color, fontweight="bold", fontsize=9)
ax.plot([], [], "o", markerfacecolor="white", markeredgecolor="grey",
        label="hollow = regional population estimated from 1-Jan data")
ax.axhline(100, color="grey", linestyle=":", linewidth=1.2, label="EU27 = 100")
ax.fill_between(div.index, div["Bucuresti_Ilfov"], div["Romania_excl_Bucharest_derived"],
                alpha=0.07, color="#c0392b")
ax.set_xlim(div.index.min() - 0.5, div.index.max() + 1.2)
ax.set_title(f"Regional Divergence: Bucuresti-Ilfov vs Rest of Romania, {div.index.min()}–{div.index.max()}\n"
             "(GDP per capita in PPS, EU27 = 100)", fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Index (EU27 = 100)")
ax.legend(fontsize=8, loc="upper left"); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/07b_bucharest_divergence.png", dpi=150); plt.close()
print("  saved 07b_bucharest_divergence.png")

# ---------------------------------------------------------------------------
# 3. Romania NUTS2 comparison with other EU regions (latest year)
# ---------------------------------------------------------------------------
print("Building cross-region comparison...")
COMPARE = {
    "RO21": "Nord-Est (RO)", "RO31": "Sud-Muntenia (RO)", "RO32": "Bucuresti-Ilfov (RO)",
    "BG31": "Severozapaden (BG)", "BG42": "Yuzhen tsentralen (BG)", "BG41": "Yugozapaden, incl. Sofia (BG)",
    "HU31": "Észak-Magyarország (HU)", "HU11": "Budapest (HU)",
    "PL81": "Lubelskie (PL)", "PL82": "Podkarpackie (PL)", "PL91": "Warszawski stołeczny (PL)",
    "CZ01": "Praha (CZ)", "SK01": "Bratislavský kraj (SK)",
    "DE30": "Berlin (DE)", "AT13": "Wien (AT)", "SE11": "Stockholm (SE)",
}
comp_all = eurostat_wide("nama_10r_2gdp", {"unit": "PPS_HAB_EU27_2020"}, list(COMPARE),
                         FIRST_YEAR, LAST_YEAR)
comp_year = int(comp_all.dropna(how="any").index.max())
comp_s = comp_all.loc[comp_year].rename(index=COMPARE)
comp_s.index.name = "region"; comp_s.name = "gdp_per_capita_pps_pct_eu27"
save_csv(comp_s.to_frame(), "07c_nuts2_cross_country_pct_eu27",
         f"Eurostat nama_10r_2gdp — GDP per inhabitant in PPS, % of EU27_2020 average, selected NUTS2 regions, {comp_year}",
         es_url("nama_10r_2gdp"))
comp_s = comp_s.sort_values()
cmap = {"(RO)": "#c0392b", "(PL)": "#2980b9", "(CZ)": "#27ae60", "(HU)": "#8e44ad",
        "(BG)": "#e67e22", "(SK)": "#16a085"}
bar_colors_c = [next((v for k, v in cmap.items() if k in c), "#95a5a6") for c in comp_s.index]
fig, ax = plt.subplots(figsize=(11, 7))
bars = ax.barh(comp_s.index, comp_s.values, color=bar_colors_c, alpha=0.9)
ax.axvline(100, color="grey", linestyle="--", linewidth=1.2, label="EU27 average = 100")
for bar, val in zip(bars, comp_s.values):
    ax.text(val + 1.5, bar.get_y() + bar.get_height() / 2, f"{val:.0f}", va="center", fontsize=9)
ax.set_xlim(0, comp_s.max() * 1.1)
ax.set_title(f"Selected NUTS2 Regions: GDP per Capita (PPS), EU27 = 100, {comp_year}\n"
             "RO red · BG orange · HU purple · PL blue · CZ green · SK teal · Western capitals grey",
             fontsize=11, fontweight="bold")
ax.set_xlabel("% of EU27 average"); ax.legend(fontsize=8, loc="lower right")
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/07c_nuts2_comparison.png", dpi=150); plt.close()
print("  saved 07c_nuts2_comparison.png")

# richest/poorest NUTS2 ratio within each CEE country (data only; used in text)
ratio_rows = {}
raw = eurostat_df("nama_10r_2gdp")
g = geo_col(raw)
for cc in ["RO", "PL", "HU", "BG", "CZ", "SK"]:
    sub = raw[(raw["unit"] == "PPS_HAB_EU27_2020") & raw[g].str.match(rf"^{cc}\d\w$")]
    v = sub.set_index(g)[str(comp_year)].astype(float).dropna()
    ratio_rows[cc] = {"year": comp_year, "richest": v.idxmax(), "richest_value": v.max(),
                      "poorest": v.idxmin(), "poorest_value": v.min(), "ratio": round(v.max() / v.min(), 2),
                      "n_regions": len(v)}
ratios = pd.DataFrame(ratio_rows).T
ratios.index.name = "country"
save_csv(ratios, "07e_nuts2_richest_poorest_ratio",
         "Derived from Eurostat nama_10r_2gdp (PPS_HAB_EU27_2020): ratio of highest to lowest NUTS2 GDP per inhabitant in PPS, by country",
         es_url("nama_10r_2gdp"))

# ---------------------------------------------------------------------------
# 4. Regional population change between census-anchored estimates
# ---------------------------------------------------------------------------
print("Building regional population change (demo_r_d2jan)...")
POP_START = 2012   # first 1-Jan estimate anchored on the 2011 census
popj = eurostat_wide("demo_r_d2jan", {"sex": "T", "age": "TOTAL", "unit": "NR"},
                     ["RO"] + list(RO_NUTS2), FIRST_YEAR, LAST_YEAR + 1)
pop_end = int(popj[list(RO_NUTS2)].dropna(how="any").index.max())
change = ((popj.loc[pop_end] - popj.loc[POP_START]) / 1000)
pct = (popj.loc[pop_end] / popj.loc[POP_START] - 1) * 100
pc = pd.DataFrame({"population_change_thousands": change.round(1), "change_pct": pct.round(1),
                   f"pop_1jan_{POP_START}": popj.loc[POP_START], f"pop_1jan_{pop_end}": popj.loc[pop_end]})
pc = pc.rename(index={**RO_NUTS2, "RO": "Romania (total)"})
pc.index.name = "region"
save_csv(pc, "07d_regional_population_change_thousands",
         f"Eurostat demo_r_d2jan — population on 1 January by NUTS2 region; change 1 Jan {POP_START} to 1 Jan {pop_end}",
         es_url("demo_r_d2jan"),
         [f"{POP_START} is the first estimate anchored on the 2011 census; from 2022 estimates are anchored on the 2021 census "
          "(break in series in 2022). Pre-2012 regional estimates are not census-consistent and are not used."])

ps = pc.drop(index="Romania (total)")["population_change_thousands"].sort_values()
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.barh(ps.index, ps.values, color=["#27ae60" if v > 0 else "#c0392b" for v in ps.values])
ax.axvline(0, color="black", linewidth=0.8)
for bar, val, p in zip(bars, ps.values, pc.loc[ps.index, "change_pct"]):
    ha = "left" if val >= 0 else "right"
    ax.text(val + (4 if val >= 0 else -4), bar.get_y() + bar.get_height() / 2,
            f"{val:+.0f}k ({p:+.1f}%)", va="center", fontsize=9, ha=ha)
ax.set_xlim(ps.min() * 1.35, max(ps.max(), 0) + 110)
ax.set_title(f"Population Change by NUTS2 Region, 1 Jan {POP_START} – 1 Jan {pop_end} (thousands)\n"
             f"Romania total: {pc.loc['Romania (total)', 'population_change_thousands']:+,.0f}k "
             f"({pc.loc['Romania (total)', 'change_pct']:+.1f}%)", fontsize=12, fontweight="bold")
ax.set_xlabel("Population change (thousands)")
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/07d_regional_population.png", dpi=150); plt.close()
print("  saved 07d_regional_population.png")

print("\nDone — regional charts saved to", OUTPUT)
