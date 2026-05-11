"""
Regional dimension: NUTS2 GDP per capita, Attica's dominance, peer-country
regional comparisons, unemployment dispersion, and regional depopulation.
Sources: Eurostat (nama_10r_2gdp, demo_r_pjangrp, lfst_r_lfu3rt)

Greece has 13 NUTS2 regions. The story: Attica (Athens metro) accounts for
~50% of GDP, the wealthy Aegean tourism islands punch above their weight,
and the continental periphery (Epirus, Thrace) lags both nationally and
versus the EU.
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import eurostat

OUTPUT   = "charts"
RAW_DATA = "raw-data"
import os; os.makedirs(OUTPUT, exist_ok=True); os.makedirs(RAW_DATA, exist_ok=True)

def save_csv(df, name):
    path = f"{RAW_DATA}/{name}.csv"
    df.to_csv(path)
    print(f"  saved {path}")

# Greek NUTS2 codes & English short names
GR_NUTS2 = {
    "EL30": "Attiki (Athens)",
    "EL41": "North Aegean",
    "EL42": "South Aegean",
    "EL43": "Crete",
    "EL51": "East Macedonia & Thrace",
    "EL52": "Central Macedonia",
    "EL53": "West Macedonia",
    "EL54": "Epirus",
    "EL61": "Thessaly",
    "EL62": "Ionian Islands",
    "EL63": "West Greece",
    "EL64": "Central Greece",
    "EL65": "Peloponnese",
}

# ---------------------------------------------------------------------------
# 1. NUTS2 GDP per capita (PPS) as % of EU27 — latest year, all 13 regions
# ---------------------------------------------------------------------------
print("Fetching NUTS2 GDP per capita (PPS, % of EU27)...")
df_gdp = eurostat.get_data_df("nama_10r_2gdp")
geo_col = [c for c in df_gdp.columns if "geo" in c.lower()][0]

# Unit PPS_EU27_2020_HAB is PPS per inhabitant in % of EU27 average is PPS_EU27_HAB.
# Available unit codes: 'EUR_HAB', 'EUR_HAB_EU27_2020', 'MIO_EUR', 'MIO_PPS_EU27_2020',
# 'PPS_EU27_2020_HAB', 'PPS_HAB_EU27_2020' — pick PPS_HAB_EU27_2020 (% of EU avg).
mask_g = (df_gdp["unit"] == "PPS_HAB_EU27_2020") & (df_gdp[geo_col].isin(GR_NUTS2.keys()))
sub_g = df_gdp[mask_g]
year_cols_g = sorted([c for c in sub_g.columns if str(c).isdigit() and 2000 <= int(c) <= 2024])
gdp_pivot = sub_g.set_index(geo_col)[year_cols_g].T.astype(float)
gdp_pivot.index = gdp_pivot.index.astype(int)

# Use most recent year with data for >=10 regions
latest = None
for y in reversed(gdp_pivot.index):
    if gdp_pivot.loc[y].notna().sum() >= 10:
        latest = y; break

# Save full panel
gdp_panel = gdp_pivot.rename(columns=GR_NUTS2)
gdp_panel.index.name = "year"
save_csv(gdp_panel, "08a_nuts2_gdp_per_capita_pps_eu27")

vals = gdp_pivot.loc[latest].dropna().sort_values()
labels = [GR_NUTS2[code] for code in vals.index]
fig, ax = plt.subplots(figsize=(11, 6))
bar_colors = ["#c0392b" if code == "EL30" else "#2980b9" for code in vals.index]
bars = ax.barh(labels, vals.values, color=bar_colors, alpha=0.85)
ax.axvline(100, color="black", linestyle="--", linewidth=1, alpha=0.6)
ax.text(101, len(vals) - 0.5, "EU27 = 100", fontsize=9, color="black", va="bottom")
for i, v in enumerate(vals.values):
    ax.text(v + 1.5, i, f"{v:.0f}", va="center", fontsize=9)
ax.set_title(f"Greek NUTS2 Regions: GDP per Capita (PPS, % of EU27) — {latest}",
             fontsize=13, fontweight="bold")
ax.set_xlabel("% of EU27 average")
ax.grid(axis="x", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/08a_nuts2_gdp.png", dpi=150); plt.close()
print(f"  saved 08a_nuts2_gdp.png (latest year: {latest})")

# ---------------------------------------------------------------------------
# 2. Attica divergence: Attiki vs rest of Greece over time
# ---------------------------------------------------------------------------
print("Building Attica divergence chart...")
# Need GDP MIO_EUR & population to compute Greece-ex-Attica per capita.
# Pull MIO_EUR for EL30 and EL (national).
mask_e = (df_gdp["unit"] == "MIO_EUR") & (df_gdp[geo_col].isin(["EL", "EL30"]))
sub_e = df_gdp[mask_e]
gdp_eur = sub_e.set_index(geo_col)[year_cols_g].T.astype(float)
gdp_eur.index = gdp_eur.index.astype(int)
# Greece ex-Attica
gdp_eur["EL_NOATT"] = gdp_eur["EL"] - gdp_eur["EL30"]

# Population by NUTS-level (demo_r_pjanaggr3): aggregates back to 1990
print("  fetching regional population...")
df_pop = eurostat.get_data_df("demo_r_pjanaggr3")
geo_col_p = [c for c in df_pop.columns if "geo" in c.lower()][0]
mask_pop = ((df_pop["sex"] == "T") & (df_pop["age"] == "TOTAL") &
            (df_pop["unit"] == "NR") & (df_pop[geo_col_p].isin(["EL","EL30"] + list(GR_NUTS2.keys()))))
sub_pop = df_pop[mask_pop]
year_cols_pop = sorted([c for c in sub_pop.columns if str(c).isdigit() and 2000 <= int(c) <= 2024])
pop = sub_pop.set_index(geo_col_p)[year_cols_pop].T.astype(float)
pop.index = pop.index.astype(int)

common = sorted(set(gdp_eur.index) & set(pop.index))
# Attica per capita (€) and rest-of-Greece per capita (€).
# gdp_eur is in MIO_EUR; multiply by 1e6 to get € per person.
att_pc  = (gdp_eur.loc[common, "EL30"]    * 1e6) / pop.loc[common, "EL30"]
rest_pc = (gdp_eur.loc[common, "EL_NOATT"] * 1e6) / (pop.loc[common, "EL"] - pop.loc[common, "EL30"])
div = pd.DataFrame({"Attica": att_pc, "Rest of Greece": rest_pc,
                    "Ratio (Attica/Rest)": att_pc / rest_pc})
div.index.name = "year"
save_csv(div, "08b_attica_vs_rest_per_capita_eur")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
ax = axes[0]
ax.plot(div.index, div["Attica"], color="#c0392b", linewidth=2.5,
        marker="o", markersize=4, label="Attica (Athens)")
ax.plot(div.index, div["Rest of Greece"], color="#2980b9", linewidth=2.5,
        marker="o", markersize=4, label="Rest of Greece")
ax.fill_between(div.index, div["Attica"], div["Rest of Greece"],
                alpha=0.12, color="grey", label="Gap")
ax.set_title("Per-capita GDP: Attica vs Rest of Greece", fontsize=12, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("€ per capita (current prices)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"€{x/1000:.0f}k"))
ax.legend(fontsize=9); ax.grid(axis="y", alpha=0.3)

ax2 = axes[1]
ax2.plot(div.index, div["Ratio (Attica/Rest)"], color="#8e44ad",
         linewidth=2.5, marker="o", markersize=4)
ax2.axhline(1.0, color="black", linestyle="--", linewidth=0.8, alpha=0.5)
ax2.set_title("Ratio: Attica / Rest of Greece", fontsize=12, fontweight="bold")
ax2.set_xlabel("Year"); ax2.set_ylabel("Ratio")
ax2.grid(axis="y", alpha=0.3)

fig.suptitle("Attica dominates: ~50% of Greek GDP from ~35% of the population",
             fontsize=13, fontweight="bold")
plt.tight_layout(); plt.savefig(f"{OUTPUT}/08b_attica_divergence.png", dpi=150); plt.close()
print("  saved 08b_attica_divergence.png")

# ---------------------------------------------------------------------------
# 3. Cross-country NUTS2 comparison — capitals vs poorest regions of peers
# ---------------------------------------------------------------------------
print("Building cross-country NUTS2 comparison...")
# Use latest year, PPS_HAB_EU27_2020
# Hand-picked: capital region + poorest NUTS2 in each peer country
SELECTED = {
    # Greece
    "EL30": "Attica (GR, capital)",
    "EL42": "South Aegean (GR, islands)",
    "EL51": "E. Macedonia & Thrace (GR)",
    # Portugal
    "PT1A": "Lisboa (PT, capital)",
    "PT11": "Norte (PT)",
    # Spain
    "ES30": "Madrid (ES, capital)",
    "ES61": "Andalucía (ES)",
    # Italy
    "ITI4": "Lazio (IT, capital)",
    "ITF3": "Campania (IT)",
    "ITF6": "Calabria (IT)",
    # Cyprus
    "CY00": "Cyprus (single NUTS2)",
}
mask_cc = (df_gdp["unit"] == "PPS_HAB_EU27_2020") & (df_gdp[geo_col].isin(SELECTED.keys()))
sub_cc = df_gdp[mask_cc]
cc = sub_cc.set_index(geo_col)[year_cols_g].T.astype(float)
cc.index = cc.index.astype(int)
# Latest with >= 8 regions
latest_cc = None
for y in reversed(cc.index):
    if cc.loc[y].notna().sum() >= 8:
        latest_cc = y; break

cc_vals = cc.loc[latest_cc].dropna().sort_values()
cc_labels = [SELECTED[c] for c in cc_vals.index]
fig, ax = plt.subplots(figsize=(11, 6))
# Colour Greek regions red, others grey
cc_colors = ["#c0392b" if c.startswith("EL") else "#7f8c8d" for c in cc_vals.index]
ax.barh(cc_labels, cc_vals.values, color=cc_colors, alpha=0.85)
ax.axvline(100, color="black", linestyle="--", linewidth=1, alpha=0.6)
ax.text(101, len(cc_vals) - 0.5, "EU27 = 100", fontsize=9, va="bottom")
for i, v in enumerate(cc_vals.values):
    ax.text(v + 1.5, i, f"{v:.0f}", va="center", fontsize=9)
ax.set_title(f"Selected NUTS2 Regions: GDP per Capita (PPS, % of EU27) — {latest_cc}\n"
             "Capital regions vs poorest regions across peers",
             fontsize=12, fontweight="bold")
ax.set_xlabel("% of EU27 average")
ax.grid(axis="x", alpha=0.3)

# Save CSV
cc_full = cc.rename(columns=SELECTED)
cc_full.index.name = "year"
save_csv(cc_full, "08c_nuts2_peer_comparison_pps_eu27")

plt.tight_layout(); plt.savefig(f"{OUTPUT}/08c_nuts2_peer_comparison.png", dpi=150); plt.close()
print(f"  saved 08c_nuts2_peer_comparison.png (latest: {latest_cc})")

# ---------------------------------------------------------------------------
# 4. NUTS2 unemployment dispersion — latest year
# ---------------------------------------------------------------------------
print("Fetching regional unemployment rates...")
# lfst_r_lfu3rt — Unemployment rate by NUTS2, age, sex
df_unr = eurostat.get_data_df("lfst_r_lfu3rt")
geo_col_u = [c for c in df_unr.columns if "geo" in c.lower()][0]
mask_u = ((df_unr["age"] == "Y15-74") & (df_unr["sex"] == "T") &
          (df_unr["isced11"] == "TOTAL") &
          (df_unr["unit"] == "PC") &
          (df_unr[geo_col_u].isin(GR_NUTS2.keys())))
sub_u = df_unr[mask_u]
year_cols_u = sorted([c for c in sub_u.columns if str(c).isdigit() and 2000 <= int(c) <= 2024])
unr = sub_u.set_index(geo_col_u)[year_cols_u].T.astype(float)
unr.index = unr.index.astype(int)
unr_panel = unr.rename(columns=GR_NUTS2)
unr_panel.index.name = "year"
save_csv(unr_panel, "08d_nuts2_unemployment_rate")

# Latest valid year
latest_u = None
for y in reversed(unr.index):
    if unr.loc[y].notna().sum() >= 10:
        latest_u = y; break

u_vals = unr.loc[latest_u].dropna().sort_values()
u_labels = [GR_NUTS2[c] for c in u_vals.index]
fig, ax = plt.subplots(figsize=(11, 6))
ucolors = ["#c0392b" if c == "EL30" else "#2980b9" for c in u_vals.index]
ax.barh(u_labels, u_vals.values, color=ucolors, alpha=0.85)
for i, v in enumerate(u_vals.values):
    ax.text(v + 0.2, i, f"{v:.1f}%", va="center", fontsize=9)
nat_avg = u_vals.mean()
ax.axvline(nat_avg, color="black", linestyle="--", linewidth=1,
           label=f"Unweighted mean: {nat_avg:.1f}%")
ax.set_title(f"Unemployment Rate by NUTS2 Region — {latest_u}",
             fontsize=13, fontweight="bold")
ax.set_xlabel("%"); ax.legend(fontsize=9); ax.grid(axis="x", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/08d_nuts2_unemployment.png", dpi=150); plt.close()
print(f"  saved 08d_nuts2_unemployment.png (latest: {latest_u})")

# ---------------------------------------------------------------------------
# 5. Regional population change 2007-latest
# ---------------------------------------------------------------------------
print("Building regional population change chart...")
common_pop_years = sorted(set(pop.index))
y0 = 2007 if 2007 in common_pop_years else common_pop_years[0]
y1 = max(common_pop_years)
greek_regs = [c for c in pop.columns if c in GR_NUTS2]
pop_change = pd.DataFrame({
    "pop_y0": pop.loc[y0, greek_regs],
    "pop_y1": pop.loc[y1, greek_regs],
})
pop_change["change_thousands"] = (pop_change["pop_y1"] - pop_change["pop_y0"]) / 1000
pop_change["change_pct"] = (pop_change["pop_y1"] / pop_change["pop_y0"] - 1) * 100
pop_change.index = [GR_NUTS2[c] for c in pop_change.index]
pop_change = pop_change.sort_values("change_pct")
pop_change.index.name = "region"
save_csv(pop_change, f"08e_regional_population_change_{y0}_{y1}")

fig, ax = plt.subplots(figsize=(11, 6))
colors_p = ["#c0392b" if v < 0 else "#27ae60" for v in pop_change["change_pct"]]
ax.barh(pop_change.index, pop_change["change_pct"], color=colors_p, alpha=0.85)
for i, (pct, thou) in enumerate(zip(pop_change["change_pct"], pop_change["change_thousands"])):
    label = f"{pct:+.1f}% ({thou:+.0f}k)"
    ax.text(pct + (0.15 if pct >= 0 else -0.15), i, label,
            va="center", ha="left" if pct >= 0 else "right", fontsize=9)
ax.axvline(0, color="black", linewidth=0.8)
ax.set_title(f"Population Change by Greek NUTS2 Region, {y0}–{y1}",
             fontsize=13, fontweight="bold")
ax.set_xlabel("% change"); ax.grid(axis="x", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/08e_regional_population.png", dpi=150); plt.close()
print(f"  saved 08e_regional_population.png ({y0}-{y1})")

print("\nDone — regional charts saved to", OUTPUT)
