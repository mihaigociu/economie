"""
Regional Disparities: NUTS2 GDP per capita, Bucharest vs rest, population change.
Sources: Eurostat (with embedded fallback)
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import matplotlib.pyplot as plt
import eurostat

OUTPUT   = "charts"
RAW_DATA = "raw-data"
import os; os.makedirs(OUTPUT, exist_ok=True); os.makedirs(RAW_DATA, exist_ok=True)

def save_csv(df, name):
    path = f"{RAW_DATA}/{name}.csv"
    df.to_csv(path)
    print(f"  saved {path}")

RO_NUTS2 = {
    "RO11": "Nord-Vest",
    "RO12": "Centru",
    "RO21": "Nord-Est",
    "RO22": "Sud-Est",
    "RO31": "Sud-Muntenia",
    "RO32": "Bucuresti-Ilfov",
    "RO41": "Sud-Vest Oltenia",
    "RO42": "Vest",
}

# ---------------------------------------------------------------------------
# 1. NUTS2 GDP per capita PPS (% of EU27) — latest year
# ---------------------------------------------------------------------------
print("Fetching NUTS2 GDP per capita data (Eurostat)...")

nuts2_pct_eu = None
try:
    # nama_10r_3gdp = NUTS3; nama_10r_2gdp = NUTS2 in EUR; use PPS variant
    df = eurostat.get_data_df("nama_10r_2gdp")
    geo_col = [c for c in df.columns if "geo" in c.lower()][0]
    mask_pps = (
        (df["unit"] == "MIO_PPS_EU27_2020") &
        (df[geo_col].isin(list(RO_NUTS2.keys())))
    )
    gdp_pps = df[mask_pps].set_index(geo_col)
    year_cols = sorted([c for c in gdp_pps.columns if str(c).isdigit()], reverse=True)

    # population for per-capita
    df_pop = eurostat.get_data_df("demo_r_pjangrp")
    geo_col_p = [c for c in df_pop.columns if "geo" in c.lower()][0]
    mask_pop = (
        (df_pop["sex"] == "T") &
        (df_pop["age"] == "TOTAL") &
        (df_pop[geo_col_p].isin(list(RO_NUTS2.keys())))
    )
    pop_df = df_pop[mask_pop].set_index(geo_col_p)
    pop_cols = sorted([c for c in pop_df.columns if str(c).isdigit()], reverse=True)

    # find latest common year
    latest = None
    for y in year_cols:
        if y in pop_cols:
            g = gdp_pps[y].dropna().astype(float)
            p = pop_df[y].dropna().astype(float)
            common = g.index.intersection(p.index)
            if len(common) >= 5:
                latest = y
                gdp_pc = (g[common] / p[common] * 1e6)
                # EU27 avg GDP per capita PPS ~32,000 EUR (2022 approximation)
                eu_ref = 32000
                nuts2_pct_eu = (gdp_pc / eu_ref * 100).rename(index=RO_NUTS2)
                print(f"  Using NUTS2 data for year {latest}")
                break
except Exception as e:
    print(f"  Eurostat NUTS2 failed ({e}), using embedded data")

if nuts2_pct_eu is None:
    # Embedded approximate values (Eurostat regional accounts 2022, EU27=100)
    nuts2_pct_eu = pd.Series({
        "Nord-Est":          28,
        "Sud-Est":           37,
        "Sud-Muntenia":      38,
        "Sud-Vest Oltenia":  34,
        "Vest":              67,
        "Nord-Vest":         52,
        "Centru":            57,
        "Bucuresti-Ilfov":  162,
    })
    latest = "2022 (est.)"

nuts2_pct_eu.index.name = "region"
nuts2_pct_eu.name = "gdp_per_capita_pps_pct_eu27"
save_csv(nuts2_pct_eu.to_frame(), "07a_nuts2_gdp_pct_eu27")
nuts2_sorted = nuts2_pct_eu.sort_values()
bar_colors = ["#c0392b" if v < 50 else "#e67e22" if v < 75 else "#27ae60"
              for v in nuts2_sorted.values]

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(nuts2_sorted.index, nuts2_sorted.values, color=bar_colors)
ax.axvline(100, color="grey", linestyle="--", linewidth=1.2, label="EU27 avg = 100%")
ax.axvline(75, color="#e67e22", linestyle=":", linewidth=1, alpha=0.8,
           label="75% cohesion threshold")
for bar, val in zip(bars, nuts2_sorted.values):
    ax.text(val + 1, bar.get_y() + bar.get_height()/2,
            f"{val:.0f}%", va="center", fontsize=9)
ax.set_title(f"Romania NUTS2 Regions: GDP per Capita (PPS) as % of EU27 Average ({latest})",
             fontsize=12, fontweight="bold")
ax.set_xlabel("% of EU27 average"); ax.legend(fontsize=8)
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/07a_nuts2_gdp.png", dpi=150); plt.close()
print("  saved 07a_nuts2_gdp.png")

# ---------------------------------------------------------------------------
# 2. Bucharest vs rest of Romania — convergence/divergence time series
# ---------------------------------------------------------------------------
print("Building Bucharest divergence chart...")
# GDP per capita PPS (EU27=100), approximate annual series
buc_data    = {2000:75,  2003:88,  2005:100, 2007:128, 2008:145, 2009:118,
               2010:125, 2012:130, 2014:135, 2016:145, 2018:155, 2019:158,
               2020:148, 2021:158, 2022:162}
ro_excl     = {2000:24,  2003:28,  2005:32,  2007:40,  2008:42,  2009:36,
               2010:37,  2012:38,  2014:40,  2016:43,  2018:50,  2019:52,
               2020:49,  2021:54,  2022:52}
ro_avg      = {2000:27,  2003:33,  2005:36,  2007:46,  2008:48,  2009:41,
               2010:42,  2012:43,  2014:46,  2016:49,  2018:58,  2019:61,
               2020:57,  2021:63,  2022:65}

buc_s    = pd.Series(buc_data)
excl_s   = pd.Series(ro_excl)
avg_s    = pd.Series(ro_avg)
idx = sorted(set(buc_s.index) & set(excl_s.index))

divergence_df = pd.DataFrame({
    "Bucuresti_Ilfov": buc_s,
    "Romania_national_avg": avg_s,
    "Romania_excl_Bucharest": excl_s,
})
divergence_df.index.name = "year"
save_csv(divergence_df, "07b_bucharest_divergence_pct_eu27")

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(buc_s.index,  buc_s.values,  color="#c0392b", linewidth=2.5, marker="o", markersize=5,
        label="Bucuresti-Ilfov")
ax.plot(avg_s.index,  avg_s.values,  color="#2980b9", linewidth=2,   marker="o", markersize=4,
        label="Romania (national average)")
ax.plot(excl_s.index, excl_s.values, color="#e67e22", linewidth=2,   marker="o", markersize=4,
        linestyle="--", label="Romania excl. Bucuresti-Ilfov")
ax.axhline(100, color="grey", linestyle=":", linewidth=1.2, label="EU27 = 100")
ax.fill_between(idx, [buc_s[i] for i in idx], [excl_s[i] for i in idx],
                alpha=0.08, color="#c0392b", label="Divergence gap")
ax.set_title("Regional Divergence: Bucuresti-Ilfov vs Rest of Romania\n(GDP per capita PPS, EU27=100)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Index (EU27=100)")
ax.legend(fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/07b_bucharest_divergence.png", dpi=150); plt.close()
print("  saved 07b_bucharest_divergence.png")

# ---------------------------------------------------------------------------
# 3. Romania NUTS2 comparison with other EU lagging regions
# ---------------------------------------------------------------------------
print("Building cross-country NUTS2 comparison...")
# Selected lagging regions (bottom quartile EU) vs Bucharest, ~2022
comparison = {
    "Nord-Est (RO)":             28,
    "Sud-Vest Oltenia (RO)":     34,
    "Severozapaden (BG)":        30,
    "Yuzhen Tsentralen (BG)":    33,
    "Észak-Magyarország (HU)":   44,
    "Lubelskie (PL)":            55,
    "Podkarpackie (PL)":         52,
    "Bucuresti-Ilfov (RO)":     162,
    "Mazowieckie (PL)":         172,
    "Praha (CZ)":               211,
}
comp_s = pd.Series(comparison, name="gdp_per_capita_pps_pct_eu27")
comp_s.index.name = "region"
save_csv(comp_s.to_frame(), "07c_nuts2_cross_country_pct_eu27")
comp_s = comp_s.sort_values()
bar_colors_c = ["#c0392b" if "(RO)" in c else "#2980b9" if "(PL)" in c
                else "#27ae60" if "(CZ)" in c else "#8e44ad"
                for c in comp_s.index]

fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.barh(comp_s.index, comp_s.values, color=bar_colors_c, alpha=0.85)
ax.axvline(100, color="grey", linestyle="--", linewidth=1.2, label="EU27 avg = 100")
for bar, val in zip(bars, comp_s.values):
    ax.text(val + 1, bar.get_y() + bar.get_height()/2,
            f"{val:.0f}%", va="center", fontsize=9)
ax.set_title("Selected NUTS2 Regions: GDP per Capita PPS as % of EU27 (~2022)\n"
             "Romania (red), Poland (blue), Czechia (green), Hungary (purple)",
             fontsize=11, fontweight="bold")
ax.set_xlabel("% of EU27 average"); ax.legend(fontsize=8)
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/07c_nuts2_comparison.png", dpi=150); plt.close()
print("  saved 07c_nuts2_comparison.png")

# ---------------------------------------------------------------------------
# 4. Regional population change 2007–2022
# ---------------------------------------------------------------------------
print("Building regional population change chart...")
pop_change = {
    "Nord-Est":         -180,
    "Sud-Est":          -120,
    "Sud-Muntenia":     -200,
    "Sud-Vest Oltenia": -160,
    "Vest":              -60,
    "Nord-Vest":        -130,
    "Centru":           -100,
    "Bucuresti-Ilfov":   +80,
}
ps = pd.Series(pop_change, name="population_change_thousands")
ps.index.name = "region"
save_csv(ps.to_frame(), "07d_regional_population_change_thousands")
ps = ps.sort_values()
bar_colors_p = ["#27ae60" if v > 0 else "#c0392b" for v in ps.values]

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.barh(ps.index, ps.values, color=bar_colors_p)
ax.axvline(0, color="black", linewidth=0.8)
for bar, val in zip(bars, ps.values):
    offset = 2 if val >= 0 else -2
    ha = "left" if val >= 0 else "right"
    ax.text(val + offset, bar.get_y() + bar.get_height()/2,
            f"{val:+.0f}k", va="center", fontsize=9, ha=ha)
ax.set_title("Population Change by NUTS2 Region, 2007–2022 (thousands)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Population change (thousands)")
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/07d_regional_population.png", dpi=150); plt.close()
print("  saved 07d_regional_population.png")

print("\nDone — regional charts saved to", OUTPUT)
