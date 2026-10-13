"""
Social Indicators: poverty, inequality, education, healthcare.
Sources: Eurostat (EU-SILC ilc_peps01n, ilc_di12; LFS edat_lfse_14), World Bank
(health expenditure, life expectancy, infant mortality)
"""

import matplotlib.pyplot as plt

from common import (OUTPUT, PEERS, PEER_LABELS, COLORS, WB_CODES, WB_MAP, save_csv,
                    wb_series, eurostat_wide, eurostat_df, plot_peers, es_url, wb_url, year_span)

LAST_YEAR = 2025
FIRST_YEAR = 2000

EU_SET = PEERS + ["EU27_2020"]
LBL_DE = {**PEER_LABELS, "DE": "Germany"}
COL_DE = {**COLORS, "DE": "#2c3e50"}


def line_chart(df, title, ylabel, fname, labels=PEER_LABELS, colors=COLORS, hline=None, ms=3):
    fig, ax = plt.subplots(figsize=(12, 5))
    plot_peers(ax, df, labels=labels, colors=colors, markersize=ms)
    if hline:
        ax.axhline(hline[0], color="green", linestyle=":", linewidth=1.2, alpha=0.8, label=hline[1])
    ax.set_title(f"{title}, {year_span(df)}", fontsize=14, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel(ylabel)
    ax.legend(ncol=4, fontsize=8); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/{fname}", dpi=150); plt.close()
    print(f"  saved {fname}")


# ---------------------------------------------------------------------------
# 1. At-Risk-of-Poverty or Social Exclusion (AROPE) rate — EU 2030 definition
# ---------------------------------------------------------------------------
print("Fetching AROPE (ilc_peps01n)...")
arope = eurostat_wide("ilc_peps01n", {"unit": "PC", "age": "TOTAL", "sex": "T"},
                      EU_SET, 2005, LAST_YEAR)
save_csv(arope, "08a_arope_poverty_pct",
         "Eurostat ilc_peps01n — persons at risk of poverty or social exclusion (EU 2030 target definition), % of population",
         es_url("ilc_peps01n"),
         ["EU-SILC survey year; income reference period is the previous calendar year"])
line_chart(arope, "At-Risk-of-Poverty or Social Exclusion Rate (AROPE, %)", "% of population",
           "08a_poverty.png")

# ---------------------------------------------------------------------------
# 2. Gini coefficient
# ---------------------------------------------------------------------------
print("Fetching Gini (ilc_di12)...")
df_gini = eurostat_df("ilc_di12")
filt = {"statinfo": "GINI_HND"} if "statinfo" in df_gini.columns else {"indic_il": "GINI"}
if "age" in df_gini.columns:
    filt["age"] = "TOTAL"
gini = eurostat_wide("ilc_di12", filt, EU_SET, 2005, LAST_YEAR)
save_csv(gini, "08b_gini_coefficient",
         "Eurostat ilc_di12 — Gini coefficient of equivalised disposable income (EU-SILC), 0-100",
         es_url("ilc_di12"),
         ["EU-SILC survey year; income reference period is the previous calendar year"])
line_chart(gini, "Gini Coefficient of Disposable Income (0 = equality, 100 = max inequality)",
           "Gini coefficient", "08b_gini.png")

# ---------------------------------------------------------------------------
# 3. Early leavers from education and training
# ---------------------------------------------------------------------------
print("Fetching early school leaving (edat_lfse_14)...")
esl = eurostat_wide("edat_lfse_14", {"sex": "T", "wstatus": "POP"}, EU_SET, 2005, LAST_YEAR)
save_csv(esl, "08c_early_school_leaving_pct",
         "Eurostat edat_lfse_14 — early leavers from education and training, ages 18-24, % (LFS)",
         es_url("edat_lfse_14"))
line_chart(esl, "Early Leavers from Education & Training, Ages 18–24 (%)", "%",
           "08c_early_school_leaving.png", hline=(9, "EU 2030 target: 9%"))

# ---------------------------------------------------------------------------
# 4-6. Health expenditure, life expectancy, infant mortality (World Bank)
# ---------------------------------------------------------------------------
h_codes = WB_CODES + ["DEU"]
h_map = {**WB_MAP, "DEU": "DE"}
for ind, csv, src, title, ylabel, png in [
    ("SH.XPD.CHEX.PC.CD", "08d_health_expenditure_per_capita_usd",
     "current health expenditure per capita (current US$)",
     "Current Health Expenditure per Capita (USD)", "USD", "08d_health_expenditure.png"),
    ("SP.DYN.LE00.IN", "08e_life_expectancy_years", "life expectancy at birth, total (years)",
     "Life Expectancy at Birth (years)", "Years", "08e_life_expectancy.png"),
    ("SP.DYN.IMRT.IN", "08f_infant_mortality_per_1000",
     "mortality rate, infant (per 1,000 live births)",
     "Infant Mortality Rate (per 1,000 live births)", "per 1,000 live births",
     "08f_infant_mortality.png"),
]:
    print(f"Fetching {ind}...")
    df = wb_series(ind, h_codes, FIRST_YEAR, LAST_YEAR, h_map)
    save_csv(df, csv, f"World Bank WDI {ind} — {src}", wb_url(ind))
    line_chart(df, title, ylabel, png, LBL_DE, COL_DE, ms=2)

# health expenditure as % of GDP (data only; used in text)
hx = wb_series("SH.XPD.CHEX.GD.ZS", h_codes + ["EUU"], FIRST_YEAR, LAST_YEAR, {**h_map, "EUU": "EU"})
save_csv(hx, "08g_health_expenditure_pct_gdp",
         "World Bank WDI SH.XPD.CHEX.GD.ZS — current health expenditure, % of GDP", wb_url("SH.XPD.CHEX.GD.ZS"))

print("\nDone — social indicator charts saved to", OUTPUT)
