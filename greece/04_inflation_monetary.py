"""
Inflation & Monetary: HICP inflation, REER competitiveness, unit labour costs
(internal devaluation), 10-year sovereign yields, Greek-Bund spread.
Sources: Eurostat (prc_hicp_aind, ert_eff_ic_a, nama_10_lp_ulc, irt_lt_mcby_a)

Note: Greece is in the euro since 2001 — there is no national policy rate or
exchange rate. The relevant story is internal adjustment vs ECB-area peers.
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import matplotlib.pyplot as plt
import eurostat

OUTPUT   = "charts"
RAW_DATA = "raw-data"
import os; os.makedirs(OUTPUT, exist_ok=True); os.makedirs(RAW_DATA, exist_ok=True)

def save_csv(df, name):
    path = f"{RAW_DATA}/{name}.csv"
    df.to_csv(path)
    print(f"  saved {path}")

PEERS = ["EL", "PT", "IT", "ES", "CY"]
PEER_LABELS = {"EL": "Greece", "PT": "Portugal", "IT": "Italy",
               "ES": "Spain", "CY": "Cyprus"}
COLORS = {"EL": "#c0392b", "PT": "#e67e22", "IT": "#27ae60",
          "ES": "#2980b9", "CY": "#8e44ad"}
PROG_START, PROG_END = 2010, 2018

def add_programme_shading(ax, label_y_frac=0.92):
    ax.axvspan(PROG_START, PROG_END, alpha=0.06, color="grey")
    ylim = ax.get_ylim()
    y = ylim[0] + (ylim[1] - ylim[0]) * label_y_frac
    ax.text((PROG_START + PROG_END) / 2, y, "Adjustment programmes\n2010-2018",
            ha="center", fontsize=8, color="#555")

def fetch_eurostat(dataset, filters, geos, geo_col_search="geo"):
    df = eurostat.get_data_df(dataset)
    geo_col = [c for c in df.columns if geo_col_search in c.lower()][0]
    mask = df[geo_col].isin(geos)
    for col, val in filters.items():
        mask = mask & (df[col] == val)
    sub = df[mask].set_index(geo_col)
    year_cols = sorted([c for c in sub.columns if str(c).isdigit() and 2000 <= int(c) <= 2024])
    out = sub[year_cols].T.astype(float)
    out.index = out.index.astype(int)
    out.index.name = "year"
    return out

# ---------------------------------------------------------------------------
# 1. HICP inflation rate — Greece vs euro area & southern peers (with deflation episode)
# ---------------------------------------------------------------------------
print("Fetching HICP inflation...")
hicp = fetch_eurostat("prc_hicp_aind",
                     {"unit": "RCH_A_AVG", "coicop": "CP00"},
                     PEERS + ["EA20"])
hicp = hicp.rename(columns={"EA20": "EA"})
save_csv(hicp, "04a_hicp_inflation_pct")

fig, axes = plt.subplots(2, 1, figsize=(13, 9))

# top: full history (2000-2024)
ax = axes[0]
for iso in PEERS:
    if iso in hicp.columns:
        lw = 2.5 if iso == "EL" else 1.2
        ax.plot(hicp.index, hicp[iso], label=PEER_LABELS[iso],
                color=COLORS[iso], linewidth=lw)
if "EA" in hicp.columns:
    ax.plot(hicp.index, hicp["EA"], label="Euro Area", color="#7f8c8d",
            linewidth=1.4, linestyle="--")
ax.axhline(2, color="grey", linestyle=":", linewidth=1, alpha=0.7, label="2% ECB target")
ax.axhline(0, color="black", linewidth=0.6)
# Highlight the deflation episode 2013-2015
ax.axvspan(2013, 2016, alpha=0.10, color="#3498db", label="Greek deflation episode")
ax.set_title("HICP Inflation (annual %), 2000–2024", fontsize=13, fontweight="bold")
ax.set_ylabel("Annual %"); ax.legend(ncol=3, fontsize=8, loc="upper right")
ax.grid(axis="y", alpha=0.3)

# bottom: 2010-2024 zoom (deflation + recent surge)
ax2 = axes[1]
recent = hicp[hicp.index >= 2010]
for iso in PEERS:
    if iso in recent.columns:
        lw = 2.5 if iso == "EL" else 1.2
        ax2.plot(recent.index, recent[iso], label=PEER_LABELS[iso],
                 color=COLORS[iso], linewidth=lw, marker="o", markersize=3)
if "EA" in recent.columns:
    ax2.plot(recent.index, recent["EA"], label="Euro Area",
             color="#7f8c8d", linewidth=1.4, linestyle="--", marker="o", markersize=3)
ax2.axhline(2, color="grey", linestyle=":", linewidth=1, alpha=0.7, label="2% target")
ax2.axhline(0, color="black", linewidth=0.6)
ax2.axvspan(2013, 2016, alpha=0.10, color="#3498db")
ax2.set_title("Inflation since 2010 — Deflation Episode and 2021–23 Surge",
              fontsize=13, fontweight="bold")
ax2.set_xlabel("Year"); ax2.set_ylabel("Annual %")
ax2.legend(ncol=3, fontsize=8, loc="upper left"); ax2.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig(f"{OUTPUT}/04a_inflation.png", dpi=150); plt.close()
print("  saved 04a_inflation.png")

# ---------------------------------------------------------------------------
# 2. Real Effective Exchange Rate (REER, CPI-deflated, vs 42 partners) — competitiveness
# ---------------------------------------------------------------------------
print("Fetching REER (CPI-deflated, vs 42 partners)...")
reer = fetch_eurostat("ert_eff_ic_a",
                     {"exch_rt": "REER_IC42_CPI", "unit": "I15"},
                     PEERS)
save_csv(reer, "04b_reer_ic42_cpi_2015_100")

fig, ax = plt.subplots(figsize=(13, 5))
for iso in PEERS:
    if iso in reer.columns:
        lw = 2.5 if iso == "EL" else 1.4
        ax.plot(reer.index, reer[iso], label=PEER_LABELS[iso],
                color=COLORS[iso], linewidth=lw, marker="o", markersize=3)
ax.axhline(100, color="black", linestyle="--", linewidth=0.8, label="2015 = 100")
add_programme_shading(ax, label_y_frac=0.95)
# Annotate Greek peak (loss of competitiveness) and post-programme trough
if "EL" in reer.columns:
    el = reer["EL"].dropna()
    peak = el.loc[:2012].idxmax()
    trough = el.loc[2012:].idxmin()
    ax.annotate(f"Peak overvaluation\n{int(peak)}: {el[peak]:.0f}",
                xy=(peak, el[peak]),
                xytext=(peak - 3, el[peak] + 3),
                fontsize=8, ha="left", color=COLORS["EL"],
                arrowprops=dict(arrowstyle="->", color=COLORS["EL"], lw=0.8))
    ax.annotate(f"Post-devaluation\n{int(trough)}: {el[trough]:.0f}",
                xy=(trough, el[trough]),
                xytext=(trough + 1, el[trough] - 3),
                fontsize=8, ha="left", color=COLORS["EL"],
                arrowprops=dict(arrowstyle="->", color=COLORS["EL"], lw=0.8))
ax.set_title("Real Effective Exchange Rate (CPI-deflated, vs 42 partners, 2015 = 100)\n"
             "Higher = less competitive",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Index, 2015 = 100")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/04b_reer.png", dpi=150); plt.close()
print("  saved 04b_reer.png")

# ---------------------------------------------------------------------------
# 3. Nominal Unit Labour Cost — internal devaluation vs euro area
# ---------------------------------------------------------------------------
print("Fetching Nominal Unit Labour Costs...")
ulc = fetch_eurostat("nama_10_lp_ulc",
                    {"na_item": "NULC_PER", "unit": "I15"},
                    PEERS + ["EA20"])
ulc = ulc.rename(columns={"EA20": "EA"})
save_csv(ulc, "04c_nominal_ulc_2015_100")

fig, ax = plt.subplots(figsize=(13, 5))
for iso in PEERS:
    if iso in ulc.columns:
        lw = 2.5 if iso == "EL" else 1.4
        ax.plot(ulc.index, ulc[iso], label=PEER_LABELS[iso],
                color=COLORS[iso], linewidth=lw, marker="o", markersize=3)
if "EA" in ulc.columns:
    ax.plot(ulc.index, ulc["EA"], label="Euro Area",
            color="#7f8c8d", linewidth=1.4, linestyle="--", marker="o", markersize=3)
ax.axhline(100, color="black", linestyle="--", linewidth=0.8)
add_programme_shading(ax, label_y_frac=0.05)
# Annotate Greek peak and trough during internal devaluation
if "EL" in ulc.columns:
    el = ulc["EL"].dropna()
    peak = el.loc[:2012].idxmax()
    trough = el.loc[2012:2020].idxmin()
    drop = (el[peak] - el[trough]) / el[peak] * 100
    ax.annotate(f"Internal devaluation:\nULC −{drop:.0f}% ({int(peak)}→{int(trough)})",
                xy=(trough, el[trough]),
                xytext=(trough + 1, el[trough] - 12),
                fontsize=9, ha="left", color=COLORS["EL"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["EL"], lw=0.8))
ax.set_title("Nominal Unit Labour Cost (Index, 2015 = 100)\n"
             "Greece is the only peer where ULC barely grew over 2010-2024",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Index, 2015 = 100")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/04c_ulc.png", dpi=150); plt.close()
print("  saved 04c_ulc.png")

# ---------------------------------------------------------------------------
# 4. 10-year sovereign bond yield — the crisis spike and recovery
# ---------------------------------------------------------------------------
print("Fetching 10-year sovereign yields...")
yields = fetch_eurostat("irt_lt_mcby_a",
                      {"int_rt": "MCBY"},
                      PEERS + ["DE"])
save_csv(yields, "04d_long_term_yields_pct")

fig, ax = plt.subplots(figsize=(13, 5))
for iso in PEERS:
    if iso in yields.columns:
        lw = 2.5 if iso == "EL" else 1.4
        ax.plot(yields.index, yields[iso], label=PEER_LABELS[iso],
                color=COLORS[iso], linewidth=lw, marker="o", markersize=3)
if "DE" in yields.columns:
    ax.plot(yields.index, yields["DE"], label="Germany (Bund)",
            color="#2c3e50", linewidth=1.4, linestyle="--", marker="o", markersize=3)
add_programme_shading(ax, label_y_frac=0.92)
# Annotate Greek peak
if "EL" in yields.columns:
    el = yields["EL"].dropna()
    peak = el.idxmax()
    ax.annotate(f"Crisis peak\n{int(peak)}: {el[peak]:.1f}%",
                xy=(peak, el[peak]),
                xytext=(peak + 1.5, el[peak] - 4),
                fontsize=9, ha="left", color=COLORS["EL"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["EL"], lw=0.8))
    # Annotate the investment-grade restoration era
    if 2023 in el.index:
        ax.annotate(f"Investment grade\nrestored {int(el.index.max())}: {el.loc[el.index.max()]:.1f}%",
                    xy=(el.index.max(), el.loc[el.index.max()]),
                    xytext=(el.index.max() - 4, el.loc[el.index.max()] + 4),
                    fontsize=8, ha="center", color=COLORS["EL"],
                    arrowprops=dict(arrowstyle="->", color=COLORS["EL"], lw=0.8))
ax.set_title("10-Year Sovereign Bond Yields (annual average, %)",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Yield, %")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/04d_sovereign_yields.png", dpi=150); plt.close()
print("  saved 04d_sovereign_yields.png")

# ---------------------------------------------------------------------------
# 5. Greek-Bund spread — convergence to peer-level risk
# ---------------------------------------------------------------------------
print("Computing Greek-Bund spread...")
if "EL" in yields.columns and "DE" in yields.columns:
    spread = (yields[PEERS].subtract(yields["DE"], axis=0)).dropna(how="all")
    spread.index.name = "year"
    save_csv(spread, "04e_sovereign_spread_vs_bund_pp")

    fig, ax = plt.subplots(figsize=(13, 5))
    for iso in PEERS:
        if iso in spread.columns:
            lw = 2.5 if iso == "EL" else 1.4
            ax.plot(spread.index, spread[iso], label=PEER_LABELS[iso],
                    color=COLORS[iso], linewidth=lw, marker="o", markersize=3)
    ax.axhline(0, color="black", linewidth=0.8)
    add_programme_shading(ax, label_y_frac=0.92)
    if "EL" in spread.columns:
        el = spread["EL"].dropna()
        peak = el.idxmax()
        last = el.index.max()
        ax.annotate(f"Peak spread\n{int(peak)}: +{el[peak]:.0f}pp",
                    xy=(peak, el[peak]),
                    xytext=(peak + 1.5, el[peak] - 3),
                    fontsize=9, ha="left", color=COLORS["EL"], fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=COLORS["EL"], lw=0.8))
        ax.annotate(f"{int(last)}: +{el[last]:.1f}pp",
                    xy=(last, el[last]),
                    xytext=(last - 4, el[last] + 1.5),
                    fontsize=8, ha="left", color=COLORS["EL"],
                    arrowprops=dict(arrowstyle="->", color=COLORS["EL"], lw=0.8))
    ax.set_title("Sovereign Bond Spread vs Germany (10y, percentage points)",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel("Spread, pp")
    ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/04e_spread.png", dpi=150); plt.close()
    print("  saved 04e_spread.png")

print("\nDone — inflation & monetary charts saved to", OUTPUT)
