"""
00 — Fetch World Bank indicators used by chapters 01 and 02.

Run this script when you need to refresh the World Bank-sourced CSVs in
raw-data/. The chart scripts (01_macro_overview.py, 02_innovation_indicators.py)
read these CSVs directly — they do not fetch live themselves.

Each CSV written here has a `# source:`, `# indicator:`, `# url:`,
`# retrieved:` header documenting where the data came from. Charts that
derive series from these inputs (e.g. China's share of world manufacturing,
GDP per capita as % of US) compute those derivations in the chart script.

Requires `wbgapi`. Run:  python3 00_fetch_world_bank.py
"""

import warnings
warnings.filterwarnings("ignore")

import os
from datetime import date
import wbgapi as wb

RAW_DATA = "raw-data"
TODAY = date.today().isoformat()
os.makedirs(RAW_DATA, exist_ok=True)

ECONOMIES = ["CHN", "USA", "EUU", "JPN", "KOR"]
COL_MAP   = dict(zip(ECONOMIES, ["CN", "US", "EU", "JP", "KR"]))


def fetch(indicator, years, economies=None):
    economies = economies or ECONOMIES
    df = wb.data.DataFrame(indicator, economy=economies, time=range(*years))
    df = df.T
    df.index = df.index.str.replace("YR", "").astype(int)
    df.index.name = "year"
    return df


def write_csv(df, name, indicator, description, notes=()):
    path = f"{RAW_DATA}/{name}.csv"
    header = [
        f"# source: World Bank Open Data — {description}",
        f"# indicator: {indicator}",
        f"# url: https://data.worldbank.org/indicator/{indicator}",
        f"# retrieved: {TODAY} (fetched via wbgapi)",
    ]
    for n in notes:
        header.append(f"# notes: {n}")
    with open(path, "w") as f:
        for line in header:
            f.write(line + "\n")
        df.to_csv(f)
    print(f"  wrote {path}")


# ---------- Chapter 01 ----------

print("Fetching NY.GDP.MKTP.KD — Real GDP (constant 2015 USD) ...")
df = fetch("NY.GDP.MKTP.KD", (1978, 2025)).rename(columns=COL_MAP) / 1e12
write_csv(df, "01a_real_gdp_const2015_usd_tn", "NY.GDP.MKTP.KD",
          "GDP (constant 2015 USD), trillions",
          notes=("Values divided by 1e12 (trillion USD, constant 2015 prices).",))

print("Fetching NY.GDP.PCAP.PP.CD — GDP per capita PPP ...")
df = fetch("NY.GDP.PCAP.PP.CD", (1990, 2025)).rename(columns=COL_MAP)
write_csv(df, "01b_gdp_per_capita_ppp_usd", "NY.GDP.PCAP.PP.CD",
          "GDP per capita, PPP (current international USD)",
          notes=("Chart 01b 'GDP per capita as % of US' is derived in script as "
                 "(country / US) * 100.",))

print("Fetching NV.IND.MANF.CD — Manufacturing VA (current USD), incl. WORLD ...")
df = fetch("NV.IND.MANF.CD", (1978, 2025),
           economies=ECONOMIES + ["WLD"])
df = df.rename(columns={**COL_MAP, "WLD": "WORLD"}) / 1e12
write_csv(df, "01c_manufacturing_va_current_usd_tn", "NV.IND.MANF.CD",
          "Manufacturing, value added (current USD), trillions",
          notes=("Includes WORLD column. Chart 01d 'share of global manufacturing VA' "
                 "is derived in script as country / WORLD * 100.",
                 "China NV.IND.MANF.CD series begins 2004 in WB data.",
                 "EU27 series uses WB 'EUU' aggregate; apparent dip post-2020 "
                 "reflects UK exit from the aggregate, not relative decline."))

print("Fetching NE.TRD.GNFS.ZS — Trade as % of GDP ...")
df = fetch("NE.TRD.GNFS.ZS", (1978, 2025)).rename(columns=COL_MAP)
write_csv(df, "01e_trade_gdp_share_pct", "NE.TRD.GNFS.ZS",
          "Trade (% of GDP) — sum of exports and imports of goods+services")

print("Fetching BX.KLT.DINV.CD.WD — FDI net inflows ...")
df = fetch("BX.KLT.DINV.CD.WD", (1982, 2025)).rename(columns=COL_MAP) / 1e9
write_csv(df, "01f_fdi_inflows_current_usd_bn", "BX.KLT.DINV.CD.WD",
          "Foreign direct investment, net inflows (BoP, current USD), billions",
          notes=("Values divided by 1e9 (billion USD).",))


# ---------- Chapter 02 ----------

print("Fetching GB.XPD.RSDV.GD.ZS — GERD % of GDP ...")
df = fetch("GB.XPD.RSDV.GD.ZS", (1996, 2025)).rename(columns=COL_MAP)
write_csv(df, "02a_gerd_pct_gdp", "GB.XPD.RSDV.GD.ZS",
          "GERD — Gross domestic expenditure on R&D (% of GDP)",
          notes=("Source-of-source: UNESCO Institute of Statistics, via World Bank.",))

print("Fetching NY.GDP.MKTP.PP.CD — GDP PPP (current intl $) ...")
df = fetch("NY.GDP.MKTP.PP.CD", (1996, 2025)).rename(columns=COL_MAP)
write_csv(df, "02b_gdp_ppp_current_intl_usd", "NY.GDP.MKTP.PP.CD",
          "GDP, PPP (current international USD)",
          notes=("Chart 02b 'R&D spending absolute' is derived in script as "
                 "(GERD%GDP / 100) * GDP_PPP.",))

print("Fetching IP.PAT.RESD — Patent applications by residents ...")
df = fetch("IP.PAT.RESD", (1996, 2025)).rename(columns=COL_MAP) / 1000
write_csv(df, "02c_patent_applications_residents_thousands", "IP.PAT.RESD",
          "Patent applications by residents (thousands)",
          notes=("Values divided by 1000 (thousands of applications).",
                 "Resident counts include domestic utility models. PCT international "
                 "filings (not in this CSV) are the stricter quality measure.",
                 "WB does not publish IP.PAT.RESD for the EUU aggregate; EU column may be NaN."))

print("Fetching TX.VAL.TECH.CD — High-technology exports ...")
df = fetch("TX.VAL.TECH.CD", (2000, 2025)).rename(columns=COL_MAP) / 1e9
write_csv(df, "02d_high_tech_exports_usd_bn", "TX.VAL.TECH.CD",
          "High-technology exports, current USD (billions)",
          notes=("Values divided by 1e9 (USD billion).",
                 "Goods only — services excluded. US figure understates because "
                 "US high-tech 'value' increasingly travels in software/services."))

print("Fetching TX.VAL.TECH.MF.ZS — High-tech % of manufactured exports ...")
df = fetch("TX.VAL.TECH.MF.ZS", (2000, 2025)).rename(columns=COL_MAP)
write_csv(df, "02e_high_tech_pct_manuf_exports", "TX.VAL.TECH.MF.ZS",
          "High-technology exports (% of manufactured exports)")

print("Fetching SP.POP.SCIE.RD.P6 — Researchers per million people ...")
df = fetch("SP.POP.SCIE.RD.P6", (1996, 2025)).rename(columns=COL_MAP)
write_csv(df, "02f_researchers_per_million", "SP.POP.SCIE.RD.P6",
          "Researchers in R&D, per million people (FTE)",
          notes=("Source-of-source: UNESCO Institute of Statistics, via World Bank.",))


print("\nDone — World Bank CSVs refreshed with source headers.")
