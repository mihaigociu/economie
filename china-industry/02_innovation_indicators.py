"""
02 — From Imitator to Co-Innovator: National Indicators

National-level innovation indicators that test whether the "selective
frontier leadership" thesis is visible *before* we drill into individual
sectors. R&D intensity, R&D absolute, patent volumes, high-tech exports,
researcher density.

Comparison set: China vs US, EU27, Japan, Korea.

This script only READS the World Bank CSVs in raw-data/ — it does not
fetch live. To refresh the data, run `python3 00_fetch_world_bank.py`
first. Each CSV in raw-data/ carries a `# source:` header documenting
provenance.

Follow-up (per plan.md):
- WIPO PCT applications by applicant origin — stricter patent-quality cut
- USPTO PatentsView — US grants to Chinese-resident inventors
- OECD MSTI for BERD share of GERD
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

LABELS = {"CN": "China", "US": "United States", "EU": "EU27",
          "JP": "Japan", "KR": "Korea"}
COLORS = {"CN": "#c0392b", "US": "#2980b9", "EU": "#7f8c8d",
          "JP": "#8e44ad", "KR": "#e67e22"}


def load(name, **kwargs):
    return pd.read_csv(f"{RAW_DATA}/{name}.csv", comment="#",
                       index_col="year", **kwargs)


def line_plot(df, title, ylabel, savename, highlight="CN",
              fill_highlight=False, annotation=None):
    fig, ax = plt.subplots(figsize=(13, 5.2))
    for iso in df.columns:
        if iso not in LABELS:
            continue
        lw = 2.6 if iso == highlight else 1.4
        ax.plot(df.index, df[iso], label=LABELS[iso], color=COLORS[iso],
                linewidth=lw, marker="o", markersize=3)
    if fill_highlight and highlight in df.columns:
        ax.fill_between(df.index, df[highlight].fillna(0),
                        alpha=0.08, color=COLORS[highlight])
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel(ylabel)
    ax.legend(ncol=5, fontsize=9); ax.grid(axis="y", alpha=0.3)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
    if annotation:
        ax.annotate(annotation, xy=(0.99, 0.05), xycoords="axes fraction",
                    fontsize=8, color="#555", va="bottom", ha="right",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                              edgecolor="#bbb", linewidth=0.6))
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/{savename}.png", dpi=150); plt.close()
    print(f"  saved {savename}.png")


# ---------------------------------------------------------------------------
# 2a. GERD as % of GDP — R&D intensity over time
# ---------------------------------------------------------------------------
print("GERD as % of GDP...")
gerd_share = load("02a_gerd_pct_gdp")
line_plot(
    gerd_share,
    title="Gross Domestic Expenditure on R&D (% of GDP)",
    ylabel="% of GDP",
    savename="02a_gerd_pct_gdp",
    annotation="Source: World Bank GB.XPD.RSDV.GD.ZS (UNESCO via WB).\n"
               "China overtook the EU27 average around 2013 and continues to close on US/Korea.",
)


# ---------------------------------------------------------------------------
# 2b. GERD absolute, USD PPP — derived as GERD%GDP × GDP_PPP
# ---------------------------------------------------------------------------
print("R&D spending absolute (derived from 02a + 02b GDP)...")
gdp_ppp = load("02b_gdp_ppp_current_intl_usd")
common_yrs = sorted(set(gerd_share.index) & set(gdp_ppp.index))
gerd_abs_bn = ((gerd_share.loc[common_yrs] / 100) *
               gdp_ppp.loc[common_yrs]) / 1e9
line_plot(
    gerd_abs_bn,
    title="R&D Spending — Absolute, USD PPP (billion, current intl $)",
    ylabel="USD billion (PPP, current intl $)",
    savename="02b_gerd_absolute_ppp",
    fill_highlight=True,
    annotation="Derived in-script as (GERD%GDP / 100) × GDP_PPP.\n"
               "Inputs: 02a_gerd_pct_gdp.csv, 02b_gdp_ppp_current_intl_usd.csv.\n"
               "China overtook EU27 in absolute R&D around 2014; now within ~15% of US.",
)


# ---------------------------------------------------------------------------
# 2c. Patent applications by residents (thousands per year)
# ---------------------------------------------------------------------------
print("Patent applications by residents...")
pat_k = load("02c_patent_applications_residents_thousands")
line_plot(
    pat_k,
    title="Patent Applications by Residents (thousands per year)",
    ylabel="Thousands of applications",
    savename="02c_patent_applications_residents",
    fill_highlight=True,
    annotation="Source: World Bank IP.PAT.RESD (WIPO via WB).\n"
               "Resident counts include domestic utility models; PCT international\n"
               "filings (follow-up) are the stricter quality measure.",
)


# ---------------------------------------------------------------------------
# 2d. High-tech exports — absolute, USD billion
# ---------------------------------------------------------------------------
print("High-tech exports (USD billion)...")
htex_bn = load("02d_high_tech_exports_usd_bn")
line_plot(
    htex_bn,
    title="High-Technology Exports — Current USD (billion)",
    ylabel="USD billion (current)",
    savename="02d_high_tech_exports_abs",
    fill_highlight=True,
    annotation="Source: World Bank TX.VAL.TECH.CD (goods only).\n"
               "US figure understates because much US high-tech 'value' travels\n"
               "via software/services, not in this goods-only indicator.",
)


# ---------------------------------------------------------------------------
# 2e. High-tech exports as % of manufactured exports
# ---------------------------------------------------------------------------
print("High-tech share of manufactured exports...")
htshare = load("02e_high_tech_pct_manuf_exports")
line_plot(
    htshare,
    title="High-Technology Exports — % of Manufactured Exports",
    ylabel="% of manufactured exports",
    savename="02e_high_tech_pct_manuf",
    annotation="Source: World Bank TX.VAL.TECH.MF.ZS (Comtrade-derived).\n"
               "Headline share has been falling for China, US, and Japan since\n"
               "~2007 as software/services and battery-EV exports shift composition.\n"
               "Absolute high-tech exports continued to grow (see 02d).",
)


# ---------------------------------------------------------------------------
# 2f. Researchers in R&D per million people
# ---------------------------------------------------------------------------
print("Researchers per million people...")
res = load("02f_researchers_per_million")
line_plot(
    res,
    title="Researchers in R&D — per Million People",
    ylabel="Researchers per million population",
    savename="02f_researchers_per_million",
    annotation="Source: World Bank SP.POP.SCIE.RD.P6 (UNESCO via WB, FTE basis).\n"
               "China's per-capita researcher density still trails developed\n"
               "comparators, but the absolute stock is far larger.",
)


print("\nDone — innovation-indicator charts saved to", OUTPUT)
