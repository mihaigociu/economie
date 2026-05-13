"""
01 — Forty Years in Numbers (1978–present)

Macro backdrop for the brief: how big China's economy and manufacturing
base have become, how trade-integrated it is, where FDI flowed, and the
five policy-phase markers (Reform & Opening 1978, WTO 2001, 4-trillion-RMB
stimulus 2008-09, Made in China 2025, Dual Circulation 2020) that
structure the rest of the narrative.

Comparison set: China vs US, EU27, Japan, Korea.

This script only READS the World Bank CSVs in raw-data/ — it does not
fetch live. To refresh the data, run `python3 00_fetch_world_bank.py`
first. Each CSV in raw-data/ carries a `# source:` / `# indicator:`
/ `# url:` / `# retrieved:` header documenting provenance.
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

POLICY_MARKERS = [
    (1978, "Reform &\nOpening"),
    (2001, "WTO\naccession"),
    (2008, "RMB-4tn\nstimulus"),
    (2015, "Made in\nChina 2025"),
    (2020, "Dual\nCirculation"),
]


def load(name, **kwargs):
    return pd.read_csv(f"{RAW_DATA}/{name}.csv", comment="#",
                       index_col="year", **kwargs)


def line_plot(df, title, ylabel, savename, highlight="CN",
              fill_highlight=False, vlines=None,
              ymax_for_labels=None):
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
    if vlines:
        ymax = ymax_for_labels if ymax_for_labels is not None else df.max().max()
        for x, label in vlines:
            ax.axvline(x, color="#555", linestyle=":", linewidth=1, alpha=0.6)
            ax.text(x + 0.25, ymax * 0.96, label, fontsize=8, color="#444",
                    va="top")
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel(ylabel)
    ax.legend(ncol=5, fontsize=9); ax.grid(axis="y", alpha=0.3)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/{savename}.png", dpi=150); plt.close()
    print(f"  saved {savename}.png")


# ---------------------------------------------------------------------------
# 1a. Real GDP (constant 2015 USD) — absolute scale
# ---------------------------------------------------------------------------
print("Real GDP (constant 2015 USD)...")
gdp_tn = load("01a_real_gdp_const2015_usd_tn")
line_plot(
    gdp_tn,
    title="Real GDP — Constant 2015 USD (trillion)",
    ylabel="USD trillion (constant 2015)",
    savename="01a_real_gdp",
    fill_highlight=True,
    vlines=POLICY_MARKERS,
)


# ---------------------------------------------------------------------------
# 1b. GDP per capita (PPP) — absolute and as % of US (convergence)
# ---------------------------------------------------------------------------
print("GDP per capita PPP — convergence...")
pcap = load("01b_gdp_per_capita_ppp_usd")
conv = pcap.div(pcap["US"], axis=0) * 100  # derived: % of US

fig, ax = plt.subplots(figsize=(13, 5.2))
ax.axhline(100, color=COLORS["US"], linestyle="--", linewidth=1.4,
           label="US = 100", alpha=0.8)
for iso in ["CN", "EU", "JP", "KR"]:
    if iso not in conv.columns: continue
    lw = 2.6 if iso == "CN" else 1.4
    ax.plot(conv.index, conv[iso], label=LABELS[iso], color=COLORS[iso],
            linewidth=lw, marker="o", markersize=3)
ax.set_title("GDP per Capita (PPP) as % of United States",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of US level (PPP, current intl $)")
ax.legend(ncol=5, fontsize=9); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/01b_gdp_per_capita_ppp.png", dpi=150); plt.close()
print("  saved 01b_gdp_per_capita_ppp.png")


# ---------------------------------------------------------------------------
# 1c. Manufacturing value added — current USD, absolute (5 economies only)
# ---------------------------------------------------------------------------
print("Manufacturing value added (current USD)...")
mva_all = load("01c_manufacturing_va_current_usd_tn")
mva_5 = mva_all.drop(columns=["WORLD"], errors="ignore")
line_plot(
    mva_5,
    title="Manufacturing Value Added — Current USD (trillion)",
    ylabel="USD trillion (current prices)",
    savename="01c_manufacturing_va",
    fill_highlight=True,
)


# ---------------------------------------------------------------------------
# 1d. China's share of WORLD manufacturing value added — derived
# ---------------------------------------------------------------------------
print("Manufacturing share of world (derived)...")
share = pd.DataFrame(index=mva_all.index)
for iso in ["CN", "US", "EU", "JP", "KR"]:
    if iso in mva_all.columns:
        share[iso] = mva_all[iso] / mva_all["WORLD"] * 100
share = share.dropna(how="all")

fig, ax = plt.subplots(figsize=(13, 5.2))
for iso in ["CN", "US", "EU", "JP", "KR"]:
    if iso not in share.columns: continue
    lw = 2.6 if iso == "CN" else 1.4
    ax.plot(share.index, share[iso], label=LABELS[iso], color=COLORS[iso],
            linewidth=lw, marker="o", markersize=3)
ax.fill_between(share.index, share["CN"].fillna(0), alpha=0.08,
                color=COLORS["CN"])
ax.set_title("Share of Global Manufacturing Value Added",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of world manufacturing VA (current USD)")
ax.legend(ncol=5, fontsize=9); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
ax.annotate(
    "Derived from raw-data/01c_manufacturing_va_current_usd_tn.csv\n"
    "(WORLD column / country columns). Source: World Bank NV.IND.MANF.CD.\n"
    "EU27 dip post-2020 reflects UK exit from the aggregate, not relative decline.\n"
    "China NV.IND.MANF.CD series begins 2004 in WB data.",
    xy=(0.99, 0.45), xycoords="axes fraction",
    fontsize=8, color="#555", va="top", ha="right",
    bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
              edgecolor="#bbb", linewidth=0.6))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/01d_manufacturing_share_of_world.png", dpi=150)
plt.close()
print("  saved 01d_manufacturing_share_of_world.png")


# ---------------------------------------------------------------------------
# 1e. Trade-to-GDP ratio
# ---------------------------------------------------------------------------
print("Trade-to-GDP ratio...")
trade = load("01e_trade_gdp_share_pct")
line_plot(
    trade,
    title="Trade (Exports + Imports) as % of GDP",
    ylabel="% of GDP",
    savename="01e_trade_gdp_share",
    vlines=[(2001, "WTO accession")],
)


# ---------------------------------------------------------------------------
# 1f. FDI inflows
# ---------------------------------------------------------------------------
print("FDI inflows...")
fdi_bn = load("01f_fdi_inflows_current_usd_bn")
line_plot(
    fdi_bn,
    title="Inward FDI — Foreign Direct Investment, Net Inflows (BoP, current USD)",
    ylabel="USD billion (current)",
    savename="01f_fdi_inflows",
    fill_highlight=True,
)


# ---------------------------------------------------------------------------
# 1g. Three-phase timeline with five policy markers
# ---------------------------------------------------------------------------
print("Three-phase policy-timeline chart...")
PHASES = [
    ("Absorb & scale",         1978, 2005, "#bdc3c7"),
    ("Catch up & substitute",  2005, 2015, "#95a5a6"),
    ("Lead selectively",       2015, 2025, "#c0392b"),
]
fig, ax = plt.subplots(figsize=(13, 3.2))
for label, start, end, color in PHASES:
    ax.barh(0, end - start, left=start, height=0.6, color=color, alpha=0.55,
            edgecolor="#444", linewidth=0.7)
    ax.text((start + end) / 2, 0, label, ha="center", va="center",
            fontsize=11, fontweight="bold", color="#222")
for year, lbl in POLICY_MARKERS:
    ax.axvline(year, color="#222", linewidth=1.2)
    ax.text(year, 0.55, str(year), ha="center", va="bottom",
            fontsize=9, fontweight="bold", color="#222")
    ax.text(year, -0.55, lbl, ha="center", va="top", fontsize=8.5,
            color="#333")
ax.set_xlim(1976, 2027)
ax.set_ylim(-1.2, 1.2)
ax.set_yticks([])
ax.set_xlabel("Year")
ax.set_title("China's Industrial Trajectory — Three Phases and Five Policy Markers",
             fontsize=13, fontweight="bold")
for spine in ("top", "right", "left"):
    ax.spines[spine].set_visible(False)
ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/01g_policy_timeline.png", dpi=150); plt.close()
print("  saved 01g_policy_timeline.png")


print("\nDone — macro-overview charts saved to", OUTPUT)
