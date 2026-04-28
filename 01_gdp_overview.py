"""
GDP Overview: growth rates, convergence to EU average, sector composition.
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

ECONOMIES = ["ROU", "POL", "CZE", "HUN", "BGR", "EUU"]
COL_MAP   = dict(zip(ECONOMIES, ["RO", "PL", "CZ", "HU", "BG", "EU"]))
PEER_LABELS = {"RO": "Romania", "PL": "Poland", "CZ": "Czechia",
               "HU": "Hungary", "BG": "Bulgaria", "EU": "EU27"}
COLORS = {"RO": "#c0392b", "PL": "#2980b9", "CZ": "#27ae60",
          "HU": "#8e44ad", "BG": "#e67e22", "EU": "#7f8c8d"}

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
    lw = 2.5 if iso == "RO" else 1.4
    ax.plot(growth.index, growth[iso], label=label, color=COLORS[iso],
            linewidth=lw, marker="o", markersize=3)
ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax.fill_between(growth.index, growth["RO"], alpha=0.08, color=COLORS["RO"])
ax.set_title("Real GDP Growth Rate (%)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Annual % change")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/01a_gdp_growth.png", dpi=150); plt.close()
print("  saved 01a_gdp_growth.png")

# ---------------------------------------------------------------------------
# 2. GDP per capita (PPP, % of EU27 average) — convergence
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
for iso in ["RO", "PL", "CZ", "HU", "BG"]:
    if iso not in conv.columns: continue
    lw = 2.5 if iso == "RO" else 1.4
    ax.plot(conv.index, conv[iso], label=PEER_LABELS[iso], color=COLORS[iso],
            linewidth=lw, marker="o", markersize=3)
ax.set_title("GDP per Capita (PPP) as % of EU27 Average", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of EU27")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/01b_gdp_convergence.png", dpi=150); plt.close()
print("  saved 01b_gdp_convergence.png")

# ---------------------------------------------------------------------------
# 3. GDP composition by sector (Romania)
# ---------------------------------------------------------------------------
print("Fetching sector composition...")
indicators = {
    "Agriculture": "NV.AGR.TOTL.ZS",
    "Industry":    "NV.IND.TOTL.ZS",
    "Services":    "NV.SRV.TOTL.ZS",
}
sector_data = {}
for name, code in indicators.items():
    s = wb_series(code, ["ROU"], (2000, 2024))
    s.columns = ["ROU"]
    sector_data[name] = s["ROU"]

sectors = pd.DataFrame(sector_data).dropna()
sectors.index.name = "year"
save_csv(sectors, "01c_gdp_sectors_romania_pct")

fig, ax = plt.subplots(figsize=(12, 5))
ax.stackplot(sectors.index,
             sectors["Agriculture"], sectors["Industry"], sectors["Services"],
             labels=["Agriculture", "Industry", "Services"],
             colors=["#27ae60", "#2980b9", "#e67e22"], alpha=0.85)
ax.set_title("Romania: GDP Composition by Sector (% of GDP)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
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
    lw = 2.5 if iso == "RO" else 1.4
    ax.plot(gdp_cap.index, gdp_cap[iso] / 1000, label=label, color=COLORS[iso],
            linewidth=lw, marker="o", markersize=3)
ax.set_title("GDP per Capita, Nominal (USD thousands)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("USD thousands")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}k"))
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/01d_gdp_per_capita.png", dpi=150); plt.close()
print("  saved 01d_gdp_per_capita.png")

print("\nDone — charts and CSVs saved.")
