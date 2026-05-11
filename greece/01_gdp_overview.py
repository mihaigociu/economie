"""
GDP Overview: growth rates, convergence reversal vs EU average, sector composition.
Sources: Eurostat, World Bank
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import wbgapi as wb

OUTPUT   = "charts"
RAW_DATA = "raw-data"
import os; os.makedirs(OUTPUT, exist_ok=True); os.makedirs(RAW_DATA, exist_ok=True)

def wb_series(indicator, economies, years):
    df = wb.data.DataFrame(indicator, economy=economies, time=range(*years))
    df = df.T
    df.index = df.index.str.replace("YR", "").astype(int)
    return df

def save_csv(df, name):
    path = f"{RAW_DATA}/{name}.csv"
    df.to_csv(path)
    print(f"  saved {path}")

# Greece + southern-euro peer set (incl. two fellow programme countries: PRT, CYP)
ECONOMIES = ["GRC", "PRT", "ITA", "ESP", "CYP", "EUU"]
COL_MAP   = dict(zip(ECONOMIES, ["GR", "PT", "IT", "ES", "CY", "EU"]))
PEER_LABELS = {"GR": "Greece", "PT": "Portugal", "IT": "Italy",
               "ES": "Spain", "CY": "Cyprus", "EU": "EU27"}
COLORS = {"GR": "#c0392b", "PT": "#e67e22", "IT": "#27ae60",
          "ES": "#2980b9", "CY": "#8e44ad", "EU": "#7f8c8d"}

# ---------------------------------------------------------------------------
# 1. Real GDP growth rate (annual %)
# ---------------------------------------------------------------------------
print("Fetching GDP growth rates...")
growth = wb_series("NY.GDP.MKTP.KD.ZG", ECONOMIES, (2000, 2025)).rename(columns=COL_MAP)
growth.index.name = "year"
save_csv(growth, "01a_gdp_growth_pct")

fig, ax = plt.subplots(figsize=(12, 5))
for iso, label in PEER_LABELS.items():
    if iso not in growth.columns: continue
    lw = 2.5 if iso == "GR" else 1.4
    ax.plot(growth.index, growth[iso], label=label, color=COLORS[iso],
            linewidth=lw, marker="o", markersize=3)
ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax.fill_between(growth.index, growth["GR"], alpha=0.08, color=COLORS["GR"])
# Mark the depression years (Greece in recession 2008-2016, with brief 2014 stabilisation)
ax.axvspan(2008, 2016, alpha=0.06, color="grey", label=None)
ax.text(2012, ax.get_ylim()[1] * 0.85, "Crisis & programmes\n2008-2016",
        ha="center", fontsize=8, color="#555")
ax.set_title("Real GDP Growth Rate (%)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Annual % change")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/01a_gdp_growth.png", dpi=150); plt.close()
print("  saved 01a_gdp_growth.png")

# ---------------------------------------------------------------------------
# 2. GDP per capita (PPP, % of EU27 average) — convergence reversal
# ---------------------------------------------------------------------------
print("Fetching GDP per capita PPP...")
gdp_ppp = wb_series("NY.GDP.PCAP.PP.CD", ECONOMIES, (2000, 2025)).rename(columns=COL_MAP)
gdp_ppp.index.name = "year"
save_csv(gdp_ppp, "01b_gdp_per_capita_ppp_usd")

conv = gdp_ppp.div(gdp_ppp["EU"], axis=0) * 100
conv.index.name = "year"
save_csv(conv, "01b_gdp_ppp_pct_eu27")

fig, ax = plt.subplots(figsize=(12, 5))
ax.axhline(100, color=COLORS["EU"], linestyle="--", linewidth=1.5, label="EU27 = 100")
for iso in ["GR", "PT", "IT", "ES", "CY"]:
    if iso not in conv.columns: continue
    lw = 2.5 if iso == "GR" else 1.4
    ax.plot(conv.index, conv[iso], label=PEER_LABELS[iso], color=COLORS[iso],
            linewidth=lw, marker="o", markersize=3)
# Annotate pre-crisis peak and trough for Greece
gr_series = conv["GR"].dropna()
if not gr_series.empty:
    peak_year = gr_series.loc[:2009].idxmax()
    trough_year = gr_series.loc[2008:2018].idxmin()
    ax.annotate(f"Pre-crisis peak\n{int(peak_year)}: {gr_series[peak_year]:.0f}%",
                xy=(peak_year, gr_series[peak_year]),
                xytext=(peak_year - 2, gr_series[peak_year] + 12),
                fontsize=8, ha="center", color=COLORS["GR"],
                arrowprops=dict(arrowstyle="->", color=COLORS["GR"], lw=0.8))
    ax.annotate(f"Trough\n{int(trough_year)}: {gr_series[trough_year]:.0f}%",
                xy=(trough_year, gr_series[trough_year]),
                xytext=(trough_year + 1, gr_series[trough_year] - 12),
                fontsize=8, ha="center", color=COLORS["GR"],
                arrowprops=dict(arrowstyle="->", color=COLORS["GR"], lw=0.8))
ax.set_title("GDP per Capita (PPP) as % of EU27 Average — Greece's Convergence Reversal",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of EU27")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/01b_gdp_convergence.png", dpi=150); plt.close()
print("  saved 01b_gdp_convergence.png")

# ---------------------------------------------------------------------------
# 3. GDP composition by sector (Greece)
# ---------------------------------------------------------------------------
print("Fetching sector composition...")
indicators = {
    "Agriculture": "NV.AGR.TOTL.ZS",
    "Industry":    "NV.IND.TOTL.ZS",
    "Services":    "NV.SRV.TOTL.ZS",
}
sector_data = {}
for name, code in indicators.items():
    s = wb_series(code, ["GRC"], (2000, 2024))
    s.columns = ["GRC"]
    sector_data[name] = s["GRC"]

sectors = pd.DataFrame(sector_data).dropna()
sectors.index.name = "year"
save_csv(sectors, "01c_gdp_sectors_greece_pct")

fig, ax = plt.subplots(figsize=(12, 5))
ax.stackplot(sectors.index,
             sectors["Agriculture"], sectors["Industry"], sectors["Services"],
             labels=["Agriculture", "Industry", "Services"],
             colors=["#27ae60", "#2980b9", "#e67e22"], alpha=0.85)
ax.set_title("Greece: GDP Composition by Sector (% of GVA)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GVA")
ax.set_ylim(0, 105); ax.legend(loc="upper left", fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/01c_gdp_sectors.png", dpi=150); plt.close()
print("  saved 01c_gdp_sectors.png")

# ---------------------------------------------------------------------------
# 4. GDP per capita in USD — absolute level comparison
# ---------------------------------------------------------------------------
print("Fetching GDP per capita nominal...")
gdp_cap = wb_series("NY.GDP.PCAP.CD", ECONOMIES, (2000, 2025)).rename(columns=COL_MAP)
gdp_cap.index.name = "year"
save_csv(gdp_cap, "01d_gdp_per_capita_nominal_usd")

fig, ax = plt.subplots(figsize=(12, 5))
for iso, label in PEER_LABELS.items():
    if iso not in gdp_cap.columns: continue
    lw = 2.5 if iso == "GR" else 1.4
    ax.plot(gdp_cap.index, gdp_cap[iso] / 1000, label=label, color=COLORS[iso],
            linewidth=lw, marker="o", markersize=3)
ax.set_title("GDP per Capita, Nominal (USD thousands)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("USD thousands")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}k"))
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/01d_gdp_per_capita.png", dpi=150); plt.close()
print("  saved 01d_gdp_per_capita.png")

# ---------------------------------------------------------------------------
# 5. Real GDP level (index, 2007 = 100) — the depression in stark terms
# ---------------------------------------------------------------------------
# Greece-specific addition: the cumulative real GDP loss is the most striking
# single number of the period. Indexing to the 2007 peak shows it directly.
print("Fetching real GDP (constant 2015 USD) for indexed view...")
real_gdp = wb_series("NY.GDP.MKTP.KD", ECONOMIES, (2000, 2025)).rename(columns=COL_MAP)
real_gdp.index.name = "year"

# Index to 2007 = 100 for each country (last pre-crisis year for Greece)
base = real_gdp.loc[2007]
real_idx = real_gdp.div(base, axis=1) * 100
save_csv(real_idx, "01e_real_gdp_index_2007")

fig, ax = plt.subplots(figsize=(12, 5))
ax.axhline(100, color="black", linewidth=0.8, linestyle="--", label="2007 = 100")
for iso, label in PEER_LABELS.items():
    if iso not in real_idx.columns: continue
    lw = 2.5 if iso == "GR" else 1.4
    ax.plot(real_idx.index, real_idx[iso], label=label, color=COLORS[iso],
            linewidth=lw, marker="o", markersize=3)
# Annotate peak-to-trough drop for Greece
gr_idx = real_idx["GR"].dropna()
if not gr_idx.empty:
    trough = gr_idx.loc[2008:2018].idxmin()
    drop = 100 - gr_idx[trough]
    ax.annotate(f"Peak-to-trough\nreal GDP loss: -{drop:.0f}%",
                xy=(trough, gr_idx[trough]),
                xytext=(trough + 1.5, gr_idx[trough] - 8),
                fontsize=9, ha="left", color=COLORS["GR"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["GR"], lw=1.0))
ax.set_title("Real GDP Index (2007 = 100) — the Greek Depression in Context",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Index, 2007 = 100")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/01e_real_gdp_index.png", dpi=150); plt.close()
print("  saved 01e_real_gdp_index.png")

print("\nDone — charts and CSVs saved.")
