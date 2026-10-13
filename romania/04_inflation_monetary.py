"""
Inflation & Monetary Policy: HICP history, BNR policy rate, RON/EUR exchange rate,
euro adoption (Maastricht) convergence criteria.
Sources: Eurostat (prc_hicp_ainr, prc_hicp_minr — ECOICOP 2 HICP tables that
replaced prc_hicp_aind/manr in 2026; ert_bil_eur_a/_m; irt_lt_mcby_m;
gov_10dd_edpt1), BIS central bank policy rates (WS_CBPOL, source: BNR),
ECB Convergence Report 2026 (reference values only).
"""

import io
import os

import pandas as pd
import requests
import matplotlib.pyplot as plt

from common import (OUTPUT, PEERS, PEER_LABELS, COLORS, save_csv, eurostat_wide, eurostat_df,
                    plot_peers, es_url, year_span, TODAY)

LAST_YEAR = 2025
FIRST_YEAR = 1995

# ---------------------------------------------------------------------------
# 1. HICP annual inflation (annual average rate of change)
# ---------------------------------------------------------------------------
print("Fetching HICP inflation (prc_hicp_ainr)...")
cpi = eurostat_wide("prc_hicp_ainr", {"unit": "RCH_A_AVG", "coicop18": "TOTAL"},
                    PEERS + ["EA20"], FIRST_YEAR, LAST_YEAR).rename(columns={"EA20": "EA"})
save_csv(cpi, "04a_hicp_inflation_pct",
         "Eurostat prc_hicp_ainr — HICP all items (TOTAL), annual average rate of change (RCH_A_AVG), %",
         es_url("prc_hicp_ainr"),
         ["EA = euro area 20 (EA20) fixed composition"])

# monthly HICP for Romania (annual rate and 12-month average rate)
hicp_m = pd.DataFrame({
    u: eurostat_wide("prc_hicp_minr", {"unit": u, "coicop18": "TOTAL"}, ["RO"], monthly=True)["RO"]
    for u in ["RCH_A", "RCH_MV12MAVR"]
}).dropna(how="all")
hicp_m.index.name = "month"
save_csv(hicp_m, "04a2_romania_hicp_monthly_pct",
         "Eurostat prc_hicp_minr — Romania HICP all items: annual rate of change (RCH_A) and 12-month average rate (RCH_MV12MAVR), %",
         es_url("prc_hicp_minr"))
latest_m = hicp_m["RCH_MV12MAVR"].dropna().index[-1]
latest_mv12 = hicp_m.loc[latest_m, "RCH_MV12MAVR"]
latest_label = pd.Period(latest_m, "M").strftime("%b %Y")

LBL = {**PEER_LABELS, "EA": "Euro Area (EA20)"}
COL = {**COLORS, "EA": "#7f8c8d"}
fig, axes = plt.subplots(2, 1, figsize=(13, 9))
ax = axes[0]
plot_peers(ax, cpi, labels=LBL, colors=COL, markersize=0)
ax.axhline(2, color="grey", linestyle=":", linewidth=1, alpha=0.7, label="2% reference")
ax.set_title(f"HICP Inflation (%), {year_span(cpi)} — Full History", fontsize=13, fontweight="bold")
ax.set_ylabel("Annual %"); ax.legend(ncol=4, fontsize=8); ax.grid(axis="y", alpha=0.3)
ax.set_ylim(-5, None)

ax2 = axes[1]
recent = cpi[cpi.index >= 2015]
plot_peers(ax2, recent, labels=LBL, colors=COL)
ax2.plot([LAST_YEAR + 1], [latest_mv12], marker="o", markersize=8, markerfacecolor="white",
         markeredgecolor=COLORS["RO"], markeredgewidth=2, linestyle="none",
         label=f"Romania, 12-month avg to {latest_label}")
ax2.annotate(f"{latest_mv12:.1f}", (LAST_YEAR + 1, latest_mv12), xytext=(8, -3),
             textcoords="offset points", color=COLORS["RO"], fontsize=9, fontweight="bold")
ax2.axhline(2, color="grey", linestyle=":", linewidth=1, alpha=0.7, label="2% target")
ax2.set_xlim(2014.5, LAST_YEAR + 1.5)
ax2.set_title(f"HICP Inflation (%), 2015–{recent.index.max()} — Recent Surge",
              fontsize=13, fontweight="bold")
ax2.set_xlabel("Year"); ax2.set_ylabel("Annual %")
ax2.legend(ncol=4, fontsize=8); ax2.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/04a_inflation.png", dpi=150); plt.close()
print("  saved 04a_inflation.png")

# ---------------------------------------------------------------------------
# 2. BNR policy rate (BIS, monthly end-of-period) vs HICP
# ---------------------------------------------------------------------------
print("Fetching BNR policy rate (BIS WS_CBPOL)...")
BIS_URL = "https://stats.bis.org/api/v1/data/WS_CBPOL/M.RO/all?format=csv"
r = requests.get(BIS_URL, timeout=60)
r.raise_for_status()
bis = pd.read_csv(io.StringIO(r.text))
rate_m = (bis.set_index("TIME_PERIOD")["OBS_VALUE"].astype(float).dropna().sort_index())
rate_m.index.name = "month"
if rate_m.empty:
    raise RuntimeError("BIS policy-rate fetch returned no data")
save_csv(rate_m.rename("policy_rate_pct").to_frame(), "04b_bnr_policy_rate_monthly_pct",
         "BIS central bank policy rates (WS_CBPOL), Romania, monthly, end of period (compiled from National Bank of Romania)",
         BIS_URL)
years = rate_m.index.str[:4].astype(int)
rate_y = rate_m.groupby(years).last()
rate_y.index.name = "year"
rate_y_full = rate_y[rate_y.index <= LAST_YEAR]
save_csv(rate_y_full.rename("policy_rate_pct").to_frame(), "04b_bnr_policy_rate_pct",
         "BIS central bank policy rates (WS_CBPOL), Romania — end-December value of the monthly series",
         BIS_URL,
         [f"latest monthly observation: {rate_m.index[-1]} = {rate_m.iloc[-1]:.2f}%",
          "BIS series starts 2003-01; earlier hand-typed values (2000-2002) were dropped as unverifiable"])

hicp_a = hicp_m["RCH_A"].dropna()
hicp_a = hicp_a[hicp_a.index >= rate_m.index[0]]
xr = pd.PeriodIndex(rate_m.index, freq="M").to_timestamp()
xh = pd.PeriodIndex(hicp_a.index, freq="M").to_timestamp()

fig, ax = plt.subplots(figsize=(13, 5))
ax.step(xr, rate_m.values, where="post", color="#c0392b", linewidth=2.5, label="BNR policy rate")
ax.plot(xh, hicp_a.values, color="#e67e22", linewidth=1.6, linestyle="--",
        label="HICP inflation, % y/y")
ax.axhline(0, color="black", linewidth=0.6)
ax.annotate(f"{rate_m.iloc[-1]:.2f}% ({pd.Period(rate_m.index[-1], 'M').strftime('%b %Y')})",
            (xr[-1], rate_m.iloc[-1]), xytext=(-20, 75), textcoords="offset points",
            ha="right", color="#c0392b", fontsize=9, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1))
ax.set_title(f"Romania: BNR Policy Rate vs HICP Inflation (monthly), {xr[0].year}–{pd.Period(rate_m.index[-1], 'M').strftime('%b %Y')}",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("%")
ax.grid(axis="y", alpha=0.3); ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/04b_policy_rate.png", dpi=150); plt.close()
print("  saved 04b_policy_rate.png")

# ---------------------------------------------------------------------------
# 3. RON/EUR exchange rate (annual average) — Eurostat primary
# ---------------------------------------------------------------------------
print("Fetching RON/EUR exchange rate (ert_bil_eur_a)...")
# Emergency fallback ONLY: annual averages copied from Eurostat ert_bil_eur_a
# (retrieved 2026-10-13). Used only if ALLOW_FALLBACK=1 is set; otherwise a
# failed fetch stops the script.
RON_EUR_FALLBACK = {
    1999: 1.6345, 2000: 1.9922, 2001: 2.6004, 2002: 3.1270, 2003: 3.7551,
    2004: 4.0510, 2005: 3.6209, 2006: 3.5258, 2007: 3.3353, 2008: 3.6826,
    2009: 4.2399, 2010: 4.2122, 2011: 4.2391, 2012: 4.4593, 2013: 4.4190,
    2014: 4.4437, 2015: 4.4454, 2016: 4.4904, 2017: 4.5688, 2018: 4.6540,
    2019: 4.7453, 2020: 4.8383, 2021: 4.9215, 2022: 4.9313, 2023: 4.9467,
    2024: 4.9746, 2025: 5.0424,
}


def ert(code, statinfo):
    df = eurostat_df(code)
    ccol = [c for c in df.columns if c.startswith("currency")][0]
    sub = df[(df[ccol] == "RON") & (df["statinfo"] == statinfo)]
    if len(sub) != 1:
        raise RuntimeError(f"{code}: expected one RON/{statinfo} row, got {len(sub)}")
    s = sub.iloc[0][[c for c in sub.columns if str(c)[:4].isdigit()]].astype(float).dropna()
    return s


fx_note = []
try:
    fx = ert("ert_bil_eur_a", "AVG")
    fx.index = fx.index.astype(int)
    fx = fx[(fx.index >= 1999) & (fx.index <= LAST_YEAR)]
    fx_src = "Eurostat ert_bil_eur_a — euro/RON exchange rate, annual average (RON per 1 EUR; pre-2005 values in new-leu equivalent)"
except Exception as e:
    if os.environ.get("ALLOW_FALLBACK") != "1":
        raise
    print(f"  !!! RON/EUR fetch failed ({e}); USING EMBEDDED FALLBACK (ALLOW_FALLBACK=1)")
    fx = pd.Series(RON_EUR_FALLBACK, dtype=float)
    fx_src = "EMBEDDED FALLBACK copy of Eurostat ert_bil_eur_a (retrieved 2026-10-13)"
    fx_note = ["fallback values used because the live fetch failed"]
fx = fx.rename("RON_per_EUR"); fx.index.name = "year"

fx_m = ert("ert_bil_eur_m", "AVG")
ytd = fx_m[fx_m.index.str.startswith(str(LAST_YEAR + 1))]
if len(ytd):
    fx_note.append(f"{LAST_YEAR + 1} average of monthly averages {ytd.index[0]}..{ytd.index[-1]} "
                   f"(ert_bil_eur_m) = {ytd.mean():.4f}")
save_csv(fx.to_frame(), "04c_ron_eur_exchange_rate", fx_src, es_url("ert_bil_eur_a"), fx_note)
fx_m.index.name = "month"
save_csv(fx_m[fx_m.index >= "2019-01"].rename("RON_per_EUR").to_frame(), "04c2_ron_eur_monthly",
         "Eurostat ert_bil_eur_m — euro/RON exchange rate, monthly average (RON per 1 EUR)",
         es_url("ert_bil_eur_m"))

fig, ax = plt.subplots(figsize=(13, 4.5))
ax.plot(fx.index, fx.values, color="#2980b9", linewidth=2.5, marker="o", markersize=3,
        label="Annual average")
if len(ytd):
    ax.plot([LAST_YEAR + 1], [ytd.mean()], marker="o", markersize=8, markerfacecolor="white",
            markeredgecolor="#2980b9", markeredgewidth=2, linestyle="none",
            label=f"{LAST_YEAR + 1} to date ({pd.Period(ytd.index[-1], 'M').strftime('%b')})")
    ax.annotate(f"{ytd.mean():.2f}", (LAST_YEAR + 1, ytd.mean()), xytext=(0, 8),
                textcoords="offset points", ha="center", fontsize=9, color="#2980b9")
ax.annotate(f"{fx.iloc[-1]:.2f}", (fx.index[-1], fx.iloc[-1]), xytext=(-4, -14),
            textcoords="offset points", ha="center", fontsize=9, color="#2980b9")
ax.set_ylim(fx.min() - 0.2, max(fx.max(), ytd.mean() if len(ytd) else 0) + 0.45)
ax.axvline(2007, color="green", linestyle="--", linewidth=1.2, alpha=0.7)
ax.text(2007.2, fx.min() + 0.2, "EU accession", fontsize=8, color="green")
ax.set_title(f"RON / EUR Exchange Rate (Annual Average), {year_span(fx)}",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("RON per 1 EUR")
ax.grid(axis="y", alpha=0.3); ax.legend(fontsize=9, loc="lower right")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/04c_ron_eur.png", dpi=150); plt.close()
print("  saved 04c_ron_eur.png")

# ---------------------------------------------------------------------------
# 4. Euro adoption convergence criteria
# ---------------------------------------------------------------------------
print("Building euro criteria dashboard...")
# Reference values and period: ECB/EC Convergence Report, June 2026
# (https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.pr260624~ec1dcac037.en.html).
# Inflation reference = avg of 3 best performers (CY 0.9, FR 1.2, DK 1.6) + 1.5pp = 2.7%;
# long-term rate reference = avg of the same three (3.1%) + 2pp = 5.1%.
# No machine-readable source exists for these two numbers, so they are typed here.
CR_YEAR = 2026
CR_REF_MONTH = "2026-05"                    # 12 months to May 2026
CR_LT_WINDOW = ("2025-06", "2026-05")
REF_INFLATION, REF_LT_RATE = 2.7, 5.1

mv12 = hicp_m["RCH_MV12MAVR"]
ro_infl = mv12.loc[CR_REF_MONTH]
lt_m = eurostat_wide("irt_lt_mcby_m", {}, ["RO"], monthly=True)["RO"]
lt_window = lt_m.loc[CR_LT_WINDOW[0]:CR_LT_WINDOW[1]]
if len(lt_window) != 12:
    raise RuntimeError(f"long-term rate window incomplete: {len(lt_window)} months")
ro_lt = lt_window.mean()
edp = eurostat_df("gov_10dd_edpt1")
g = [c for c in edp.columns if "geo" in c.lower()][0]
def edp_last(item):
    s = edp[(edp.na_item == item) & (edp.unit == "PC_GDP") & (edp.sector == "S13") & (edp[g] == "RO")]
    s = s[[c for c in s.columns if str(c).isdigit() and int(c) <= LAST_YEAR]].iloc[0].astype(float).dropna()
    return int(s.index[-1]), s.iloc[-1]
def_year, ro_def = edp_last("B9")
debt_year, ro_debt = edp_last("GD")

criteria_df = pd.DataFrame([
    ["Inflation (HICP, 12-month average)", f"12 months to {CR_REF_MONTH}", ro_infl, REF_INFLATION],
    ["Long-term interest rate (10y, 12-month average)", f"{CR_LT_WINDOW[0]} to {CR_LT_WINDOW[1]}", ro_lt, REF_LT_RATE],
    ["Budget deficit (% GDP)", str(def_year), -ro_def, 3.0],
    ["Public debt (% GDP)", str(debt_year), ro_debt, 60.0],
], columns=["criterion", "period", "Romania_value", "limit"]).set_index("criterion")
criteria_df["Romania_value"] = criteria_df["Romania_value"].round(2)
criteria_df["pass"] = criteria_df["Romania_value"] <= criteria_df["limit"]
latest_lt = lt_m.dropna()
criteria_notes = [
    f"reference values (inflation {REF_INFLATION}%, long-term rate {REF_LT_RATE}%) from the ECB/EC Convergence Report {CR_YEAR}",
    "Romania values computed from Eurostat prc_hicp_minr (RCH_MV12MAVR), irt_lt_mcby_m, gov_10dd_edpt1",
    f"for context: latest HICP 12-month average = {latest_mv12:.1f}% ({latest_m}); latest 12-month avg long-term rate = {latest_lt.iloc[-12:].mean():.2f}% (to {latest_lt.index[-1]})",
]
save_csv(criteria_df, "04d_euro_maastricht_criteria",
         "Romania vs Maastricht convergence criteria — Eurostat data on Convergence Report 2026 periods",
         "https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.pr260624~ec1dcac037.en.html",
         criteria_notes)

chart_labels = [
    f"Inflation\n(ref. {REF_INFLATION}%; 12m to {pd.Period(CR_REF_MONTH, 'M').strftime('%b %Y')})",
    f"LT Interest Rate\n(ref. {REF_LT_RATE}%; 12m to {pd.Period(CR_LT_WINDOW[1], 'M').strftime('%b %Y')})",
    f"Budget Deficit\n(≤ 3% GDP; {def_year})",
    f"Public Debt\n(≤ 60% GDP; {debt_year})",
]
fig, axes = plt.subplots(1, 4, figsize=(14, 5))
for ax, label, (_, row) in zip(axes, chart_labels, criteria_df.iterrows()):
    ro_val, limit, ok = row["Romania_value"], row["limit"], row["pass"]
    color = "#27ae60" if ok else "#c0392b"
    ax.bar(["Romania", "Limit"], [ro_val, limit], color=[color, "#95a5a6"])
    ax.set_title(label, fontsize=9, fontweight="bold")
    top = max(ro_val, limit)
    ax.set_ylim(0, top * 1.25)
    for x, v in zip([0, 1], [ro_val, limit]):
        ax.text(x, v + top * 0.02, f"{v:.1f}", ha="center", fontsize=9, fontweight="bold")
    ax.text(0.5, 0.96, "PASS ✓" if ok else "FAIL ✗", transform=ax.transAxes, ha="center",
            fontsize=12, fontweight="bold", color=color, va="top")
    ax.grid(axis="y", alpha=0.3)
axes[0].set_ylabel("%")
fig.suptitle(f"Romania vs Maastricht Criteria (Convergence Report {CR_YEAR} periods; fiscal data: EDP, {def_year})",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/04d_euro_criteria.png", dpi=150); plt.close()
print("  saved 04d_euro_criteria.png")

print("\nDone — inflation & monetary charts saved to", OUTPUT)
