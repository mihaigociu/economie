"""
GDP Overview: growth rates, convergence to EU average, sector composition.
Sources: Eurostat (nama_10_gdp, nama_10_pc), World Bank (sector shares, USD per capita)
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from common import (OUTPUT, PEERS, PEER_LABELS, COLORS, save_csv, wb_series,
                    eurostat_wide, plot_peers, es_url, wb_url, year_span)

LAST_YEAR = 2025
FIRST_YEAR = 2000
EU_GEOS = PEERS + ["EU27_2020"]

# ---------------------------------------------------------------------------
# 1. Real GDP growth rate (annual %) — Eurostat national accounts
# ---------------------------------------------------------------------------
print("Fetching GDP growth rates (Eurostat nama_10_gdp)...")
growth = eurostat_wide("nama_10_gdp", {"unit": "CLV_PCH_PRE", "na_item": "B1GQ"},
                       EU_GEOS, FIRST_YEAR, LAST_YEAR)
save_csv(growth, "01a_gdp_growth_pct",
         "Eurostat nama_10_gdp — GDP, chain-linked volumes, % change on previous year (CLV_PCH_PRE, B1GQ)",
         es_url("nama_10_gdp"))

fig, ax = plt.subplots(figsize=(12, 5))
plot_peers(ax, growth)
ax.axhline(0, color="black", linewidth=0.8)
ax.fill_between(growth.index, growth["RO"], alpha=0.08, color=COLORS["RO"])
ax.set_title(f"Real GDP Growth Rate (%), {year_span(growth)}", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Annual % change")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/01a_gdp_growth.png", dpi=150); plt.close()
print("  saved 01a_gdp_growth.png")

# ---------------------------------------------------------------------------
# 2. GDP per capita in PPS as % of EU27 — Eurostat volume index
# ---------------------------------------------------------------------------
print("Fetching GDP per capita in PPS, EU27=100 (Eurostat nama_10_pc)...")
conv = eurostat_wide("nama_10_pc", {"unit": "PC_EU27_2020_HAB_MPPS_CP", "na_item": "B1GQ"},
                     PEERS, FIRST_YEAR, LAST_YEAR)
save_csv(conv, "01b_gdp_ppp_pct_eu27",
         "Eurostat nama_10_pc — GDP per capita in PPS, index EU27_2020=100 (PC_EU27_2020_HAB_MPPS_CP)",
         es_url("nama_10_pc"))

fig, ax = plt.subplots(figsize=(12, 5))
ax.axhline(100, color=COLORS["EU"], linestyle="--", linewidth=1.5, label="EU27 = 100")
plot_peers(ax, conv)
ro_last = conv["RO"].dropna()
ax.annotate(f"{ro_last.iloc[-1]:.0f}", (ro_last.index[-1], ro_last.iloc[-1]),
            xytext=(6, -4), textcoords="offset points", color=COLORS["RO"], fontweight="bold")
ax.set_title(f"GDP per Capita (PPS) as % of EU27 Average, {year_span(conv)}",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of EU27")
ax.legend(ncol=3, fontsize=9, loc="lower right"); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/01b_gdp_convergence.png", dpi=150); plt.close()
print("  saved 01b_gdp_convergence.png")

# World Bank PPP (current international $) kept as a cross-check series
gdp_ppp = wb_series("NY.GDP.PCAP.PP.CD", ["ROU", "POL", "CZE", "HUN", "BGR", "EUU"],
                    FIRST_YEAR, LAST_YEAR,
                    {"ROU": "RO", "POL": "PL", "CZE": "CZ", "HUN": "HU", "BGR": "BG", "EUU": "EU"})
save_csv(gdp_ppp, "01b_gdp_per_capita_ppp_usd",
         "World Bank WDI NY.GDP.PCAP.PP.CD — GDP per capita, PPP (current international $)",
         wb_url("NY.GDP.PCAP.PP.CD"),
         ["cross-check only; the report's convergence figures use Eurostat PPS (01b_gdp_ppp_pct_eu27)"])

# ---------------------------------------------------------------------------
# 3. GDP composition by sector (Romania) — value added, % of GDP
# ---------------------------------------------------------------------------
print("Fetching sector composition...")
indicators = {"Agriculture": "NV.AGR.TOTL.ZS", "Industry": "NV.IND.TOTL.ZS",
              "Services": "NV.SRV.TOTL.ZS"}
sectors = {}
for name, code in indicators.items():
    sectors[name] = wb_series(code, ["ROU", "EUU"], FIRST_YEAR, LAST_YEAR,
                              {"ROU": "RO", "EUU": "EU"})
ro_sec = pd.DataFrame({k: v["RO"] for k, v in sectors.items()}).dropna()
ro_sec["EU_Agriculture"] = sectors["Agriculture"]["EU"]
ro_sec.index.name = "year"
save_csv(ro_sec, "01c_gdp_sectors_romania_pct",
         "World Bank WDI NV.AGR.TOTL.ZS / NV.IND.TOTL.ZS (incl. construction) / NV.SRV.TOTL.ZS — value added, % of GDP",
         wb_url("NV.SRV.TOTL.ZS"),
         ["shares do not sum to 100: the remainder is net taxes on products",
          "EU_Agriculture = EU27 aggregate (EUU) for comparison"])

fig, ax = plt.subplots(figsize=(12, 5))
ax.stackplot(ro_sec.index, ro_sec["Agriculture"], ro_sec["Industry"], ro_sec["Services"],
             labels=["Agriculture", "Industry (incl. construction)", "Services"],
             colors=["#27ae60", "#2980b9", "#e67e22"], alpha=0.85)
ax.set_title(f"Romania: Gross Value Added by Sector (% of GDP), {year_span(ro_sec)}",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
ax.set_ylim(0, 105); ax.legend(loc="upper left", fontsize=9, ncol=3); ax.grid(axis="y", alpha=0.3)
ax.margins(x=0)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/01c_gdp_sectors.png", dpi=150); plt.close()
print("  saved 01c_gdp_sectors.png")

# ---------------------------------------------------------------------------
# 4. GDP per capita in USD — absolute level comparison
# ---------------------------------------------------------------------------
print("Fetching GDP per capita nominal...")
gdp_cap = wb_series("NY.GDP.PCAP.CD", ["ROU", "POL", "CZE", "HUN", "BGR", "EUU"],
                    FIRST_YEAR, LAST_YEAR,
                    {"ROU": "RO", "POL": "PL", "CZE": "CZ", "HUN": "HU", "BGR": "BG", "EUU": "EU"})
save_csv(gdp_cap, "01d_gdp_per_capita_nominal_usd",
         "World Bank WDI NY.GDP.PCAP.CD — GDP per capita (current US$)", wb_url("NY.GDP.PCAP.CD"))

fig, ax = plt.subplots(figsize=(12, 5))
plot_peers(ax, gdp_cap / 1000)
ax.set_title(f"GDP per Capita, Nominal (USD thousands), {year_span(gdp_cap)}",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("USD thousands")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}k"))
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/01d_gdp_per_capita.png", dpi=150); plt.close()
print("  saved 01d_gdp_per_capita.png")

print("\nDone — charts and CSVs saved.")
