"""
Social Indicators: poverty, inequality, education, healthcare.
Sources: Eurostat, World Bank
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

EU_SET = PEERS + ["EU27_2020"]
EU_LABELS = {**PEER_LABELS, "EU27_2020": "EU27"}
EU_COLORS = {**COLORS, "EU27_2020": "#7f8c8d"}

# ---------------------------------------------------------------------------
# 1. At-Risk-of-Poverty or Social Exclusion (AROPE) rate
# ---------------------------------------------------------------------------
print("Fetching poverty / AROPE data...")
try:
    df_arope = eurostat.get_data_df("ilc_peps01n")
    mask = (
        (df_arope["unit"] == "PC") &
        (df_arope["age"] == "TOTAL") &
        (df_arope["sex"] == "T") &
        (df_arope["geo\\TIME_PERIOD"].isin(EU_SET))
    )
    arope = df_arope[mask].set_index("geo\\TIME_PERIOD")
    year_cols = sorted([c for c in arope.columns if str(c).isdigit() and int(c) >= 2005])
    arope = arope[year_cols].T.astype(float)
    arope.index = arope.index.astype(int)
    arope.index.name = "year"
    save_csv(arope, "08a_arope_poverty_pct")

    fig, ax = plt.subplots(figsize=(13, 5))
    for iso in EU_SET:
        if iso not in arope.columns:
            continue
        lw = 2.8 if iso == "RO" else 1.5 if iso == "EU27_2020" else 1.2
        ls = "--" if iso == "EU27_2020" else "-"
        ax.plot(arope.index, arope[iso], label=EU_LABELS.get(iso, iso),
                color=EU_COLORS.get(iso, "#333"), linewidth=lw, linestyle=ls,
                marker="o", markersize=2)
    ax.set_title("At-Risk-of-Poverty or Social Exclusion Rate (AROPE, %)",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel("% of population")
    ax.legend(ncol=3, fontsize=8); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/08a_poverty.png", dpi=150); plt.close()
    print("  saved 08a_poverty.png")
except Exception as e:
    print(f"  AROPE failed ({e}), World Bank fallback")
    # Multidimensional poverty / $6.85 day
    pov = wb_series("SI.POV.DDAY", WB_CODES).rename(columns=COL_MAP)
    fig, ax = plt.subplots(figsize=(13, 5))
    for iso in PEERS:
        if iso not in pov.columns:
            continue
        lw = 2.5 if iso == "RO" else 1.4
        ax.plot(pov.index, pov[iso], label=PEER_LABELS[iso],
                color=COLORS[iso], linewidth=lw, marker="o", markersize=3)
    ax.set_title("Poverty Headcount (<$6.85/day, PPP)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel("% of population")
    ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/08a_poverty.png", dpi=150); plt.close()
    print("  saved 08a_poverty.png (WB fallback)")

# ---------------------------------------------------------------------------
# 2. Gini coefficient
# ---------------------------------------------------------------------------
print("Fetching Gini data...")
try:
    df_gini = eurostat.get_data_df("ilc_di12")
    geo_col = [c for c in df_gini.columns if "geo" in c.lower()][0]
    # dataset uses 'statinfo' column with values like 'GINI_HND'
    stat_col = "statinfo" if "statinfo" in df_gini.columns else "indic_il"
    gini_code = "GINI_HND" if "statinfo" in df_gini.columns else "GINI"
    mask = (df_gini[stat_col] == gini_code) & (df_gini["age"] == "TOTAL") & (df_gini[geo_col].isin(EU_SET))
    gini = df_gini[mask].set_index(geo_col)
    year_cols = sorted([c for c in gini.columns if str(c).isdigit() and int(c) >= 2005])
    gini = gini[year_cols].T.astype(float)
    gini.index = gini.index.astype(int)
    gini.index.name = "year"
    save_csv(gini, "08b_gini_coefficient")

    fig, ax = plt.subplots(figsize=(12, 5))
    for iso in EU_SET:
        if iso not in gini.columns:
            continue
        lw = 2.5 if iso == "RO" else 1.5 if iso == "EU27_2020" else 1.2
        ls = "--" if iso == "EU27_2020" else "-"
        ax.plot(gini.index, gini[iso], label=EU_LABELS.get(iso, iso),
                color=EU_COLORS.get(iso, "#333"), linewidth=lw, linestyle=ls,
                marker="o", markersize=3)
    ax.set_title("Gini Coefficient (0 = perfect equality, 100 = maximum inequality)",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel("Gini coefficient")
    ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/08b_gini.png", dpi=150); plt.close()
    print("  saved 08b_gini.png")
except Exception as e:
    print(f"  Gini skipped: {e}")

# ---------------------------------------------------------------------------
# 3. Early school leaving rate
# ---------------------------------------------------------------------------
print("Fetching early school leaving data...")
try:
    df_esl = eurostat.get_data_df("edat_lfse_14")
    geo_col = [c for c in df_esl.columns if "geo" in c.lower()][0]
    # wstatus="POP" gives the total-population headline rate (other values split by employment status)
    mask = (df_esl["sex"] == "T") & (df_esl["wstatus"] == "POP") & (df_esl[geo_col].isin(EU_SET))
    esl = df_esl[mask].set_index(geo_col)
    year_cols = sorted([c for c in esl.columns if str(c).isdigit() and int(c) >= 2005])
    esl = esl[year_cols].T.astype(float)
    esl.index = esl.index.astype(int)
    esl.index.name = "year"
    save_csv(esl, "08c_early_school_leaving_pct")

    fig, ax = plt.subplots(figsize=(12, 5))
    for iso in EU_SET:
        if iso not in esl.columns:
            continue
        lw = 2.5 if iso == "RO" else 1.5 if iso == "EU27_2020" else 1.2
        ls = "--" if iso == "EU27_2020" else "-"
        ax.plot(esl.index, esl[iso], label=EU_LABELS.get(iso, iso),
                color=EU_COLORS.get(iso, "#333"), linewidth=lw, linestyle=ls,
                marker="o", markersize=3)
    ax.axhline(9, color="green", linestyle=":", linewidth=1.2, alpha=0.8,
               label="EU 2030 target: 9%")
    ax.set_title("Early School Leaving Rate, Ages 18–24 (%)",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel("%")
    ax.legend(ncol=3, fontsize=8); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/08c_early_school_leaving.png", dpi=150); plt.close()
    print("  saved 08c_early_school_leaving.png")
except Exception as e:
    print(f"  early school leaving skipped: {e}")

# ---------------------------------------------------------------------------
# 4. Health expenditure per capita
# ---------------------------------------------------------------------------
print("Fetching health expenditure data...")
h_codes = WB_CODES + ["DEU"]
h_map   = {**COL_MAP, "DEU": "DE"}
health_exp = wb_series("SH.XPD.CHEX.PC.CD", h_codes, (2000, 2023)).rename(columns=h_map)
health_exp.index.name = "year"
save_csv(health_exp, "08d_health_expenditure_per_capita_usd")
labels_h = {**PEER_LABELS, "DE": "Germany"}
colors_h = {**COLORS, "DE": "#f39c12"}

fig, ax = plt.subplots(figsize=(12, 5))
for iso in health_exp.columns:
    lw = 2.5 if iso == "RO" else 1.2
    ax.plot(health_exp.index, health_exp[iso], label=labels_h.get(iso, iso),
            color=colors_h.get(iso, "#333"), linewidth=lw, marker="o", markersize=2)
ax.set_title("Current Health Expenditure per Capita (USD)",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("USD")
ax.legend(ncol=3, fontsize=8); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/08d_health_expenditure.png", dpi=150); plt.close()
print("  saved 08d_health_expenditure.png")

# ---------------------------------------------------------------------------
# 5. Life expectancy
# ---------------------------------------------------------------------------
print("Fetching life expectancy data...")
le = wb_series("SP.DYN.LE00.IN", h_codes, (2000, 2023)).rename(columns=h_map)
le.index.name = "year"
save_csv(le, "08e_life_expectancy_years")

fig, ax = plt.subplots(figsize=(12, 5))
for iso in le.columns:
    lw = 2.5 if iso == "RO" else 1.2
    ax.plot(le.index, le[iso], label=labels_h.get(iso, iso),
            color=colors_h.get(iso, "#333"), linewidth=lw, marker="o", markersize=2)
ax.set_title("Life Expectancy at Birth (years)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Years")
ax.legend(ncol=3, fontsize=8); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/08e_life_expectancy.png", dpi=150); plt.close()
print("  saved 08e_life_expectancy.png")

# ---------------------------------------------------------------------------
# 6. Infant mortality rate
# ---------------------------------------------------------------------------
print("Fetching infant mortality data...")
im = wb_series("SP.DYN.IMRT.IN", h_codes, (2000, 2023)).rename(columns=h_map)
im.index.name = "year"
save_csv(im, "08f_infant_mortality_per_1000")

fig, ax = plt.subplots(figsize=(12, 5))
for iso in im.columns:
    lw = 2.5 if iso == "RO" else 1.2
    ax.plot(im.index, im[iso], label=labels_h.get(iso, iso),
            color=colors_h.get(iso, "#333"), linewidth=lw, marker="o", markersize=2)
ax.set_title("Infant Mortality Rate (per 1,000 live births)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("per 1,000 live births")
ax.legend(ncol=3, fontsize=8); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/08f_infant_mortality.png", dpi=150); plt.close()
print("  saved 08f_infant_mortality.png")

print("\nDone — social indicator charts saved to", OUTPUT)
