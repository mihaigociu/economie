"""
Banking sector: NPL crisis, deposit flight & capital controls, credit deleveraging,
bank capital adequacy.
Sources: World Bank (NPL, credit, capital), ECB SDW (deposits)

The Greek banking story is distinctive: an NPL ratio that peaked near 50%,
multiple recapitalisations, capital controls 2015-2019, and a deposit base
that fell by ~40% from peak before recovering.
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import requests
import wbgapi as wb

OUTPUT   = "charts"
RAW_DATA = "raw-data"
import os; os.makedirs(OUTPUT, exist_ok=True); os.makedirs(RAW_DATA, exist_ok=True)

def save_csv(df, name):
    path = f"{RAW_DATA}/{name}.csv"
    df.to_csv(path)
    print(f"  saved {path}")

def wb_series(indicator, economies, year_range=(2005, 2025)):
    df = wb.data.DataFrame(indicator, economy=economies, time=range(*year_range))
    df = df.T
    df.index = df.index.str.replace("YR", "").astype(int)
    return df

PEERS_WB = ["GRC", "PRT", "ITA", "ESP", "CYP"]
WB_TO_LBL = {"GRC":"GR","PRT":"PT","ITA":"IT","ESP":"ES","CYP":"CY"}
PEER_LABELS = {"GR":"Greece","PT":"Portugal","IT":"Italy","ES":"Spain","CY":"Cyprus"}
COLORS = {"GR":"#c0392b","PT":"#e67e22","IT":"#27ae60","ES":"#2980b9","CY":"#8e44ad"}
PROG_START, PROG_END = 2010, 2018

def add_programme_shading(ax, label_y_frac=0.92):
    ax.axvspan(PROG_START, PROG_END, alpha=0.06, color="grey")
    ylim = ax.get_ylim()
    y = ylim[0] + (ylim[1] - ylim[0]) * label_y_frac
    ax.text((PROG_START + PROG_END) / 2, y, "Adjustment programmes\n2010-2018",
            ha="center", fontsize=8, color="#555")

def plot_peer_lines(ax, df, highlight="GR"):
    for iso in ["GR","PT","IT","ES","CY"]:
        if iso in df.columns:
            lw = 2.5 if iso == highlight else 1.4
            ax.plot(df.index, df[iso], label=PEER_LABELS[iso],
                    color=COLORS[iso], linewidth=lw, marker="o", markersize=3)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%d"))

# ---------------------------------------------------------------------------
# 1. NPL ratio — the defining banking metric
# ---------------------------------------------------------------------------
print("Fetching NPL ratios...")
npl = wb_series("FB.AST.NPER.ZS", PEERS_WB).rename(columns=WB_TO_LBL)
npl.index.name = "year"
save_csv(npl, "05a_npl_ratio_pct")

fig, ax = plt.subplots(figsize=(13, 5))
plot_peer_lines(ax, npl)
add_programme_shading(ax, label_y_frac=0.92)
# Annotate Greek peak
if "GR" in npl.columns:
    el = npl["GR"].dropna()
    peak = el.idxmax()
    last = el.index.max()
    ax.annotate(f"Peak: {el[peak]:.0f}% ({int(peak)})",
                xy=(peak, el[peak]),
                xytext=(peak - 4, el[peak] - 5),
                fontsize=9, ha="left", color=COLORS["GR"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["GR"], lw=0.8))
    ax.annotate(f"{int(last)}: {el[last]:.1f}%",
                xy=(last, el[last]),
                xytext=(last - 3, el[last] + 8),
                fontsize=9, ha="left", color=COLORS["GR"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["GR"], lw=0.8))
ax.set_title("Non-Performing Loan Ratio (% of gross loans)",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("%")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/05a_npl_ratio.png", dpi=150); plt.close()
print("  saved 05a_npl_ratio.png")

# ---------------------------------------------------------------------------
# 2. Greek private-sector deposits (monthly) — capital controls story
# ---------------------------------------------------------------------------
# ECB SDW series: MFI balance sheet, deposits of NFCs + households at Greek MFIs.
# Series key: BSI.M.GR.N.A.L20.A.1.U2.2300.Z01.E (monthly, € million)
print("Fetching Greek bank deposits from ECB SDW...")
url = "https://data-api.ecb.europa.eu/service/data/BSI/M.GR.N.A.L20.A.1.U2.2300.Z01.E"
r = requests.get(url, headers={"Accept":"application/json"},
                 params={"startPeriod":"2005-01","endPeriod":"2024-12"}, timeout=60)
r.raise_for_status()
js = r.json()
series = list(js["dataSets"][0]["series"].values())[0]["observations"]
time_dim = js["structure"]["dimensions"]["observation"][0]["values"]
times = [t["id"] for t in time_dim]
records = []
for k, v in series.items():
    records.append((times[int(k)], v[0]))
dep = pd.DataFrame(records, columns=["period", "deposits_mn_eur"])
dep["date"] = pd.to_datetime(dep["period"])
dep = dep.set_index("date").sort_index()
dep["deposits_bn_eur"] = dep["deposits_mn_eur"] / 1000.0
save_csv(dep[["deposits_bn_eur"]], "05b_greek_bank_deposits_bn_eur")

fig, ax = plt.subplots(figsize=(13, 5))
ax.fill_between(dep.index, dep["deposits_bn_eur"], alpha=0.2, color=COLORS["GR"])
ax.plot(dep.index, dep["deposits_bn_eur"], color=COLORS["GR"], linewidth=2.2)

# Key events
events = [
    ("2010-05", "First MoU\nMay 2010"),
    ("2012-03", "PSI\nMar 2012"),
    ("2015-06", "Capital controls\nimposed Jun 2015"),
    ("2019-09", "Capital controls\nfully lifted Sep 2019"),
]
for date_str, label in events:
    x = pd.to_datetime(date_str)
    if dep.index.min() <= x <= dep.index.max():
        ax.axvline(x, color="black", linestyle=":", linewidth=0.7, alpha=0.6)
        ax.text(x, dep["deposits_bn_eur"].max() * 1.02, label,
                rotation=0, fontsize=7, ha="center", va="bottom", color="#333")

peak_date = dep["deposits_bn_eur"].idxmax()
trough_date = dep.loc[peak_date:"2018-01"]["deposits_bn_eur"].idxmin()
ax.annotate(f"Peak: €{dep['deposits_bn_eur'].loc[peak_date]:.0f}bn\n({peak_date.strftime('%b %Y')})",
            xy=(peak_date, dep['deposits_bn_eur'].loc[peak_date]),
            xytext=(peak_date - pd.Timedelta(days=900), dep['deposits_bn_eur'].loc[peak_date] - 15),
            fontsize=8, color=COLORS["GR"], fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=COLORS["GR"], lw=0.8))
drop_pct = (dep['deposits_bn_eur'].loc[peak_date] - dep['deposits_bn_eur'].loc[trough_date]) / dep['deposits_bn_eur'].loc[peak_date] * 100
ax.annotate(f"Trough: €{dep['deposits_bn_eur'].loc[trough_date]:.0f}bn\n({trough_date.strftime('%b %Y')})  −{drop_pct:.0f}%",
            xy=(trough_date, dep['deposits_bn_eur'].loc[trough_date]),
            xytext=(trough_date + pd.Timedelta(days=180), dep['deposits_bn_eur'].loc[trough_date] - 25),
            fontsize=8, color=COLORS["GR"], fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=COLORS["GR"], lw=0.8))

ax.set_title("Greek Bank Deposits — Households & Non-Financial Corps (€ billions, monthly)",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Date"); ax.set_ylabel("€ billions")
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"€{x:.0f}bn"))
ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/05b_bank_deposits.png", dpi=150); plt.close()
print("  saved 05b_bank_deposits.png")

# ---------------------------------------------------------------------------
# 3. Credit to private sector (% GDP) — the deleveraging cycle
# ---------------------------------------------------------------------------
print("Fetching domestic credit to private sector...")
credit = wb_series("FD.AST.PRVT.GD.ZS", PEERS_WB, (2000, 2025)).rename(columns=WB_TO_LBL)
credit.index.name = "year"
save_csv(credit, "05c_credit_to_private_pct_gdp")

fig, ax = plt.subplots(figsize=(13, 5))
plot_peer_lines(ax, credit)
add_programme_shading(ax, label_y_frac=0.92)
if "GR" in credit.columns:
    el = credit["GR"].dropna()
    peak = el.idxmax()
    last = el.index.max()
    drop = el[peak] - el[last]
    ax.annotate(f"Peak: {el[peak]:.0f}% ({int(peak)})",
                xy=(peak, el[peak]), xytext=(peak - 4, el[peak] + 10),
                fontsize=9, ha="left", color=COLORS["GR"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["GR"], lw=0.8))
    ax.annotate(f"{int(last)}: {el[last]:.0f}%\n(deleveraging: −{drop:.0f}pp)",
                xy=(last, el[last]), xytext=(last - 4, el[last] - 25),
                fontsize=9, ha="left", color=COLORS["GR"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["GR"], lw=0.8))
ax.set_title("Domestic Credit to Private Sector by Banks (% of GDP)",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/05c_credit.png", dpi=150); plt.close()
print("  saved 05c_credit.png")

# ---------------------------------------------------------------------------
# 4. Bank capital to assets ratio — solvency story
# ---------------------------------------------------------------------------
print("Fetching bank capital ratio...")
cap = wb_series("FB.BNK.CAPA.ZS", PEERS_WB).rename(columns=WB_TO_LBL)
cap.index.name = "year"
save_csv(cap, "05d_bank_capital_to_assets_pct")

fig, ax = plt.subplots(figsize=(13, 5))
plot_peer_lines(ax, cap)
add_programme_shading(ax, label_y_frac=0.05)
ax.set_title("Bank Capital to Total Assets Ratio (%)",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("%")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/05d_bank_capital.png", dpi=150); plt.close()
print("  saved 05d_bank_capital.png")

print("\nDone — banking sector charts and CSVs saved.")
