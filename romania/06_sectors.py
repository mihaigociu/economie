"""
Sectoral Analysis: industry, IT/high-tech, energy, agriculture.
Sources: Eurostat (sts_inpr_a), World Bank (high-tech exports, energy intensity,
cereal yield), Ember (yearly electricity data, bulk CSV)
"""

import io

import pandas as pd
import requests
import matplotlib.pyplot as plt

from common import (OUTPUT, PEERS, PEER_LABELS, COLORS, WB_CODES, WB_MAP, save_csv,
                    wb_series, eurostat_wide, plot_peers, es_url, wb_url, year_span)

LAST_YEAR = 2025
FIRST_YEAR = 2000

LBL_DE = {**PEER_LABELS, "DE": "Germany"}
COL_DE = {**COLORS, "DE": "#2c3e50"}


def line_chart(df, title, ylabel, fname, labels=PEER_LABELS, colors=COLORS, ms=3):
    fig, ax = plt.subplots(figsize=(12, 5))
    plot_peers(ax, df, labels=labels, colors=colors, markersize=ms)
    ax.set_title(f"{title}, {year_span(df)}", fontsize=13, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel(ylabel)
    ax.legend(ncol=3, fontsize=8); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/{fname}", dpi=150); plt.close()
    print(f"  saved {fname}")


# ---------------------------------------------------------------------------
# 1. Industrial production index (B-D), rebased to 2015 = 100
# ---------------------------------------------------------------------------
print("Fetching industrial production data (sts_inpr_a)...")
ip21 = eurostat_wide("sts_inpr_a", {"indic_bt": "PRD", "nace_r2": "B-D", "s_adj": "CA",
                                    "unit": "I21"},
                     PEERS + ["EU27_2020"], FIRST_YEAR, LAST_YEAR)
ip = ip21.div(ip21.loc[2015]) * 100
save_csv(ip.round(2), "06a_industrial_production_index_2015_100",
         "Eurostat sts_inpr_a — volume index of production, industry B-D (mining, manufacturing, energy), "
         "calendar adjusted, published as 2021=100 (I21) and rebased here to 2015=100",
         es_url("sts_inpr_a"),
         ["the old I15 series (2015=100) is no longer updated after 2023; rebasing I21 keeps the 2015 base"])
line_chart(ip, "Industrial Production Index (2015 = 100)", "Index (2015 = 100)",
           "06a_industrial_production.png", ms=2)

# ---------------------------------------------------------------------------
# 2. High-technology exports (% of manufactured exports)
# ---------------------------------------------------------------------------
print("Fetching high-tech exports data...")
ht = wb_series("TX.VAL.TECH.MF.ZS", WB_CODES, FIRST_YEAR, LAST_YEAR, WB_MAP)
save_csv(ht, "06b_hightech_exports_pct_manufactured",
         "World Bank WDI TX.VAL.TECH.MF.ZS — high-technology exports, % of manufactured exports",
         wb_url("TX.VAL.TECH.MF.ZS"))
line_chart(ht, "High-Technology Exports (% of Manufactured Exports)", "%",
           "06b_hightech_exports.png")

# ---------------------------------------------------------------------------
# 3. Energy intensity of primary energy (MJ per $ of PPP GDP) — LOWER = more efficient
#    (the first edition mislabelled this series as "GDP per unit of energy use")
# ---------------------------------------------------------------------------
print("Fetching energy intensity data...")
ei = wb_series("EG.EGY.PRIM.PP.KD", WB_CODES + ["DEU"], FIRST_YEAR, LAST_YEAR,
               {**WB_MAP, "DEU": "DE"})
save_csv(ei, "06c_energy_intensity_mj_per_ppp_usd",
         "World Bank WDI EG.EGY.PRIM.PP.KD — energy intensity level of primary energy, MJ per $ of GDP (constant 2021 PPP $)",
         wb_url("EG.EGY.PRIM.PP.KD"))
line_chart(ei, "Energy Intensity of Primary Energy (MJ per PPP $ of GDP) — Lower = More Efficient",
           "MJ per PPP $ of GDP", "06c_energy_intensity.png", LBL_DE, COL_DE, ms=2)

# ---------------------------------------------------------------------------
# 4. Electricity generation mix (Romania) — Ember yearly data
# ---------------------------------------------------------------------------
print("Fetching Ember yearly electricity data (bulk CSV, ~50 MB)...")
EMBER_URL = ("https://storage.googleapis.com/emb-prod-bkt-publicdata/public-downloads/"
             "yearly_full_release_long_format.csv")
r = requests.get(EMBER_URL, timeout=300)
r.raise_for_status()
ember = pd.read_csv(io.BytesIO(r.content), low_memory=False)
ro = ember[(ember["Area"] == "Romania") & (ember["Category"] == "Electricity generation")
           & (ember["Subcategory"] == "Fuel") & (ember["Unit"] == "%")]
if ro.empty:
    raise RuntimeError("Ember: no Romania generation-share rows")
mix = ro.pivot(index="Year", columns="Variable", values="Value").fillna(0)
mix = mix[(mix.index >= FIRST_YEAR) & (mix.index <= LAST_YEAR)]
groups = {"Hydro": ["Hydro"], "Nuclear": ["Nuclear"], "Coal/Lignite": ["Coal"], "Gas": ["Gas"],
          "Wind": ["Wind"], "Solar": ["Solar"],
          "Other (bioenergy, oil, other)": ["Bioenergy", "Other Fossil", "Other Renewables"]}
df_mix = pd.DataFrame({k: mix[[c for c in v if c in mix.columns]].sum(axis=1)
                       for k, v in groups.items()})
df_mix.index.name = "year"
total_twh = ember[(ember["Area"] == "Romania") & (ember["Variable"] == "Total Generation")
                  & (ember["Unit"] == "TWh")].set_index("Year")["Value"]
df_mix["Total_generation_TWh"] = total_twh.reindex(df_mix.index)
save_csv(df_mix.round(2), "06d_electricity_mix_romania_pct",
         "Ember — Yearly electricity data (full release, long format): Romania, share of generation by fuel (%), and total generation (TWh)",
         EMBER_URL,
         ["'Other' = Bioenergy + Other Fossil + Other Renewables; shares may not sum to exactly 100 due to rounding"])

shares = df_mix.drop(columns="Total_generation_TWh")
fig, ax = plt.subplots(figsize=(12, 5.5))
colors_m = ["#3498db", "#9b59b6", "#7f8c8d", "#e67e22", "#27ae60", "#f1c40f", "#95a5a6"]
ax.stackplot(shares.index, shares.T.values, labels=shares.columns, colors=colors_m, alpha=0.85)
ax.set_title(f"Romania: Electricity Generation Mix (% of total), {year_span(shares)}",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of total generation")
ax.set_ylim(0, 100); ax.margins(x=0)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), fontsize=8, ncol=7, frameon=False)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/06d_electricity_mix.png", dpi=150); plt.close()
print("  saved 06d_electricity_mix.png")

# ---------------------------------------------------------------------------
# 5. Cereal yield (kg/ha) — agriculture productivity
# ---------------------------------------------------------------------------
print("Fetching cereal yield data...")
cereal = wb_series("AG.YLD.CREL.KG", WB_CODES + ["DEU"], FIRST_YEAR, LAST_YEAR,
                   {**WB_MAP, "DEU": "DE"})
save_csv(cereal, "06e_cereal_yield_kg_per_ha",
         "World Bank WDI AG.YLD.CREL.KG — cereal yield, kg per hectare", wb_url("AG.YLD.CREL.KG"))
line_chart(cereal, "Cereal Yield (kg per hectare)", "kg/ha", "06e_cereal_yield.png",
           LBL_DE, COL_DE, ms=2)

print("\nDone — sector charts saved to", OUTPUT)
