"""
Sectoral Analysis: industry, IT/high-tech, energy, agriculture.
Sources: World Bank, Eurostat
"""

import warnings
warnings.filterwarnings("ignore")

import time
import pandas as pd
import matplotlib.pyplot as plt
import wbgapi as wb
import eurostat

OUTPUT   = "charts"
RAW_DATA = "raw-data"
import os; os.makedirs(OUTPUT, exist_ok=True); os.makedirs(RAW_DATA, exist_ok=True)

def save_csv(df, name):
    path = f"{RAW_DATA}/{name}.csv"
    df.to_csv(path)
    print(f"  saved {path}")

def wb_series(indicator, economies, year_range=(2000, 2025), retries=3):
    for attempt in range(retries):
        try:
            df = wb.data.DataFrame(indicator, economy=economies, time=range(*year_range))
            df = df.T
            df.index = df.index.str.replace("YR", "").astype(int)
            return df
        except Exception as e:
            if attempt < retries - 1:
                print(f"  WB retry {attempt+1} ({e})")
                time.sleep(5)
            else:
                raise

PEERS = ["RO", "PL", "CZ", "HU", "BG"]
PEER_LABELS = {"RO": "Romania", "PL": "Poland", "CZ": "Czechia",
               "HU": "Hungary", "BG": "Bulgaria"}
COLORS = {"RO": "#c0392b", "PL": "#2980b9", "CZ": "#27ae60",
          "HU": "#8e44ad", "BG": "#e67e22"}
WB_CODES = ["ROU", "POL", "CZE", "HUN", "BGR"]
COL_MAP  = dict(zip(WB_CODES, PEERS))

# ---------------------------------------------------------------------------
# 1. Industrial production index
# ---------------------------------------------------------------------------
print("Fetching industrial production data...")
try:
    df_ip = eurostat.get_data_df("sts_inpr_a")
    peers_eu = ["RO", "PL", "CZ", "HU", "BG", "EU27_2020"]
    mask = (
        (df_ip["nace_r2"] == "B-D") &
        (df_ip["s_adj"] == "NSA") &
        (df_ip["unit"] == "I15") &
        (df_ip["geo\\TIME_PERIOD"].isin(peers_eu))
    )
    ip = df_ip[mask].set_index("geo\\TIME_PERIOD")
    year_cols = sorted([c for c in ip.columns if str(c).isdigit() and int(c) >= 2000])
    ip = ip[year_cols].T.astype(float)
    ip.index = ip.index.astype(int)
    ip.index.name = "year"
    save_csv(ip, "06a_industrial_production_index_2015_100")

    labels = {**PEER_LABELS, "EU27_2020": "EU27"}
    colors = {**COLORS, "EU27_2020": "#7f8c8d"}

    fig, ax = plt.subplots(figsize=(13, 5))
    for iso in ip.columns:
        lw = 2.5 if iso == "RO" else 1.2
        ax.plot(ip.index, ip[iso], label=labels.get(iso, iso),
                color=colors.get(iso, "#333"), linewidth=lw, marker="o", markersize=2)
    ax.set_title("Industrial Production Index (2015=100)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel("Index (2015=100)")
    ax.legend(ncol=3, fontsize=8); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/06a_industrial_production.png", dpi=150); plt.close()
    print("  saved 06a_industrial_production.png")
except Exception as e:
    print(f"  industrial production skipped: {e}")

# ---------------------------------------------------------------------------
# 2. High-technology exports (% of manufactured exports)
# ---------------------------------------------------------------------------
print("Fetching high-tech exports data...")
try:
    ht = wb_series("TX.VAL.TECH.MF.ZS", WB_CODES).rename(columns=COL_MAP)
    ht.index.name = "year"
    save_csv(ht, "06b_hightech_exports_pct_manufactured")
    fig, ax = plt.subplots(figsize=(12, 5))
    for iso in PEERS:
        if iso not in ht.columns:
            continue
        lw = 2.5 if iso == "RO" else 1.4
        ax.plot(ht.index, ht[iso], label=PEER_LABELS[iso],
                color=COLORS[iso], linewidth=lw, marker="o", markersize=3)
    ax.set_title("High-Technology Exports (% of Manufactured Exports)",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel("%")
    ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/06b_hightech_exports.png", dpi=150); plt.close()
    print("  saved 06b_hightech_exports.png")
except Exception as e:
    print(f"  high-tech exports skipped: {e}")

# ---------------------------------------------------------------------------
# 3. Energy intensity (GDP per unit energy use)
# ---------------------------------------------------------------------------
print("Fetching energy intensity data...")
try:
    ei_codes = WB_CODES + ["DEU"]
    ei_map   = {**COL_MAP, "DEU": "DE"}
    ei = wb_series("EG.EGY.PRIM.PP.KD", ei_codes, (2000, 2023)).rename(columns=ei_map)
    ei.index.name = "year"
    save_csv(ei, "06c_energy_intensity_gdp_per_kg_oil")
    labels_e = {**PEER_LABELS, "DE": "Germany"}
    colors_e = {**COLORS, "DE": "#f39c12"}

    fig, ax = plt.subplots(figsize=(12, 5))
    for iso in ei.columns:
        lw = 2.5 if iso == "RO" else 1.2
        ax.plot(ei.index, ei[iso], label=labels_e.get(iso, iso),
                color=colors_e.get(iso, "#333"), linewidth=lw, marker="o", markersize=2)
    ax.set_title("GDP per Unit of Energy Use (PPP $/kg oil eq.) — Higher = More Efficient",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel("PPP $ per kg oil eq.")
    ax.legend(ncol=3, fontsize=8); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/06c_energy_intensity.png", dpi=150); plt.close()
    print("  saved 06c_energy_intensity.png")
except Exception as e:
    print(f"  energy intensity skipped: {e}")

# ---------------------------------------------------------------------------
# 4. Electricity generation mix (Romania, embedded series)
# ---------------------------------------------------------------------------
print("Building electricity mix chart...")
elec_mix = {
    "Hydro":        [38, 30, 28, 29, 28, 32, 25, 27, 30, 28, 22, 30, 28, 25],
    "Nuclear":      [18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18],
    "Coal/Lignite": [30, 35, 33, 30, 28, 26, 26, 25, 24, 22, 22, 19, 17, 16],
    "Gas":          [ 9, 12, 14, 15, 16, 14, 16, 15, 13, 14, 15, 13, 14, 14],
    "Wind":         [ 0,  0,  1,  2,  3,  5,  7,  9, 10, 11, 12, 12, 13, 14],
    "Solar":        [ 0,  0,  0,  0,  0,  1,  2,  3,  4,  4,  5,  5,  6,  8],
    "Other":        [ 5,  5,  6,  6,  7,  4,  6,  3,  1,  3,  6,  3,  4,  4],
}
years_e = list(range(2010, 2024))
df_mix = pd.DataFrame(elec_mix, index=years_e)
df_mix.index.name = "year"
save_csv(df_mix, "06d_electricity_mix_romania_pct")

fig, ax = plt.subplots(figsize=(12, 5))
colors_m = ["#3498db", "#9b59b6", "#7f8c8d", "#e67e22", "#27ae60", "#f1c40f", "#95a5a6"]
ax.stackplot(df_mix.index, df_mix.T.values,
             labels=df_mix.columns, colors=colors_m, alpha=0.85)
ax.set_title("Romania: Electricity Generation Mix (%)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of total generation")
ax.set_ylim(0, 105); ax.legend(loc="upper right", fontsize=8, ncol=2)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/06d_electricity_mix.png", dpi=150); plt.close()
print("  saved 06d_electricity_mix.png")

# ---------------------------------------------------------------------------
# 5. Cereal yield (kg/ha) — agriculture productivity
# ---------------------------------------------------------------------------
print("Fetching cereal yield data...")
try:
    cer_codes = WB_CODES + ["DEU"]
    cer_map   = {**COL_MAP, "DEU": "DE"}
    cereal = wb_series("AG.YLD.CREL.KG", cer_codes, (2000, 2023)).rename(columns=cer_map)
    cereal.index.name = "year"
    save_csv(cereal, "06e_cereal_yield_kg_per_ha")
    labels_c = {**PEER_LABELS, "DE": "Germany"}
    colors_c = {**COLORS, "DE": "#f39c12"}

    fig, ax = plt.subplots(figsize=(12, 5))
    for iso in cereal.columns:
        lw = 2.5 if iso == "RO" else 1.2
        ax.plot(cereal.index, cereal[iso], label=labels_c.get(iso, iso),
                color=colors_c.get(iso, "#333"), linewidth=lw, marker="o", markersize=2)
    ax.set_title("Cereal Yield (kg per hectare)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel("kg/ha")
    ax.legend(ncol=3, fontsize=8); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/06e_cereal_yield.png", dpi=150); plt.close()
    print("  saved 06e_cereal_yield.png")
except Exception as e:
    print(f"  cereal yield skipped: {e}")

print("\nDone — sector charts saved to", OUTPUT)
