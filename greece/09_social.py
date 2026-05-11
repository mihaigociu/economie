"""
Social outcomes: poverty (AROPE), inequality (Gini), youth NEET rate,
tertiary attainment, life expectancy. Peer comparisons throughout.
Sources: Eurostat (ilc_peps01[n], ilc_di12c, lfsi_neet_a, edat_lfse_03, demo_mlexpec)

The Greek crisis produced a sharp rise in poverty and material deprivation,
the worst NEET rate in the EU at peak (~30%), and a brain drain that
coexisted with continued education expansion.
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

PEERS_EU = ["EL", "PT", "IT", "ES", "CY", "EU27_2020"]
EU_TO_LBL = {"EL":"GR","PT":"PT","IT":"IT","ES":"ES","CY":"CY","EU27_2020":"EU"}
PEER_LABELS = {"GR":"Greece","PT":"Portugal","IT":"Italy","ES":"Spain","CY":"Cyprus","EU":"EU-27"}
COLORS = {"GR":"#c0392b","PT":"#e67e22","IT":"#27ae60","ES":"#2980b9","CY":"#8e44ad","EU":"#7f8c8d"}
PROG_START, PROG_END = 2010, 2018

def add_programme_shading(ax, label_y_frac=0.92):
    ax.axvspan(PROG_START, PROG_END, alpha=0.06, color="grey")
    ylim = ax.get_ylim()
    y = ylim[0] + (ylim[1] - ylim[0]) * label_y_frac
    ax.text((PROG_START + PROG_END) / 2, y, "Adjustment programmes\n2010-2018",
            ha="center", fontsize=8, color="#555")

def plot_peer_lines(ax, df, highlight="GR"):
    for iso in ["GR","PT","IT","ES","CY","EU"]:
        if iso in df.columns:
            lw = 2.5 if iso == highlight else 1.4
            ls = "--" if iso == "EU" else "-"
            ax.plot(df.index, df[iso], label=PEER_LABELS[iso],
                    color=COLORS[iso], linewidth=lw, marker="o", markersize=3,
                    linestyle=ls)

def fetch_eurostat(dataset, filters, geos):
    df = eurostat.get_data_df(dataset)
    geo_col = [c for c in df.columns if "geo" in c.lower()][0]
    mask = pd.Series(True, index=df.index)
    for dim, val in filters.items():
        mask &= (df[dim] == val)
    mask &= df[geo_col].isin(geos)
    sub = df[mask].copy()
    year_cols = sorted([c for c in sub.columns if str(c).isdigit()])
    out = sub.set_index(geo_col)[year_cols].T.astype(float)
    out.index = out.index.astype(int)
    return out.rename(columns=EU_TO_LBL)

# ---------------------------------------------------------------------------
# 1. AROPE — at-risk-of-poverty or social exclusion
# ---------------------------------------------------------------------------
# Splice the old methodology (2003-2020) with the new (2015+).
# We use the old series through 2020 and the new series from 2021 onward, both PC.
print("Fetching AROPE (old methodology 2003-2020)...")
arope_old = fetch_eurostat("ilc_peps01",
                           {"unit":"PC","age":"TOTAL","sex":"T"}, PEERS_EU)
print("Fetching AROPE (new methodology 2015+)...")
arope_new = fetch_eurostat("ilc_peps01n",
                           {"unit":"PC","age":"TOTAL","sex":"T"}, PEERS_EU)

# Splice
old_until = 2020
new_from  = 2021
arope = pd.concat([arope_old.loc[arope_old.index <= old_until],
                   arope_new.loc[arope_new.index >= new_from]])
arope.index.name = "year"
save_csv(arope, "09a_arope_pct")

fig, ax = plt.subplots(figsize=(13, 5))
plot_peer_lines(ax, arope)
add_programme_shading(ax, label_y_frac=0.05)
ax.axvline(2020.5, color="black", linestyle=":", linewidth=0.7, alpha=0.5)
ax.text(2020.5, ax.get_ylim()[1] * 0.97, "Methodology change",
        rotation=90, va="top", ha="right", fontsize=7, color="#555")
if "GR" in arope.columns:
    el = arope["GR"].dropna()
    peak = el.idxmax()
    last = el.index.max()
    ax.annotate(f"Peak: {el[peak]:.0f}% ({int(peak)})",
                xy=(peak, el[peak]), xytext=(peak - 4, el[peak] + 3),
                fontsize=9, color=COLORS["GR"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["GR"], lw=0.8))
    ax.annotate(f"{int(last)}: {el[last]:.1f}%",
                xy=(last, el[last]), xytext=(last - 4, el[last] - 5),
                fontsize=9, color=COLORS["GR"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["GR"], lw=0.8))
ax.set_title("At-Risk-of-Poverty or Social Exclusion (AROPE, % of population)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of population")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/09a_arope.png", dpi=150); plt.close()
print("  saved 09a_arope.png")

# ---------------------------------------------------------------------------
# 2. Gini coefficient — inequality
# ---------------------------------------------------------------------------
print("Fetching Gini coefficient...")
gini = fetch_eurostat("ilc_di12c", {"indic_il":"GINI_HND"}, PEERS_EU)
gini.index.name = "year"
save_csv(gini, "09b_gini")

fig, ax = plt.subplots(figsize=(13, 5))
plot_peer_lines(ax, gini)
add_programme_shading(ax, label_y_frac=0.05)
ax.set_title("Gini Coefficient of Equivalised Disposable Income\n"
             "(0 = perfect equality, 100 = maximum inequality)",
             fontsize=12, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Gini")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/09b_gini.png", dpi=150); plt.close()
print("  saved 09b_gini.png")

# ---------------------------------------------------------------------------
# 3. NEET rate — young people 15-29 not in employment, education or training
# ---------------------------------------------------------------------------
print("Fetching NEET rates...")
neet = fetch_eurostat("lfsi_neet_a",
                      {"age":"Y15-29","sex":"T","unit":"PC_POP"}, PEERS_EU)
neet.index.name = "year"
save_csv(neet, "09c_neet_15_29_pct")

fig, ax = plt.subplots(figsize=(13, 5))
plot_peer_lines(ax, neet)
add_programme_shading(ax, label_y_frac=0.92)
if "GR" in neet.columns:
    el = neet["GR"].dropna()
    peak = el.idxmax()
    last = el.index.max()
    ax.annotate(f"Peak: {el[peak]:.1f}% ({int(peak)})",
                xy=(peak, el[peak]), xytext=(peak - 5, el[peak] + 2),
                fontsize=9, color=COLORS["GR"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["GR"], lw=0.8))
    ax.annotate(f"{int(last)}: {el[last]:.1f}%",
                xy=(last, el[last]), xytext=(last - 4, el[last] - 5),
                fontsize=9, color=COLORS["GR"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["GR"], lw=0.8))
ax.set_title("NEET Rate: Young People 15–29 Not in Employment, Education or Training (%)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of 15-29 population")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/09c_neet.png", dpi=150); plt.close()
print("  saved 09c_neet.png")

# ---------------------------------------------------------------------------
# 4. Tertiary attainment 25-34
# ---------------------------------------------------------------------------
print("Fetching tertiary attainment 25-34...")
tert = fetch_eurostat("edat_lfse_03",
                      {"sex":"T","age":"Y25-34","unit":"PC","isced11":"ED5-8"},
                      PEERS_EU)
tert.index.name = "year"
save_csv(tert, "09d_tertiary_attainment_25_34_pct")

fig, ax = plt.subplots(figsize=(13, 5))
plot_peer_lines(ax, tert)
add_programme_shading(ax, label_y_frac=0.92)
if "GR" in tert.columns:
    el = tert["GR"].dropna()
    first = el.index.min(); last = el.index.max()
    ax.annotate(f"{int(first)}: {el[first]:.0f}%",
                xy=(first, el[first]), xytext=(first + 0.5, el[first] - 7),
                fontsize=9, color=COLORS["GR"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["GR"], lw=0.8))
    ax.annotate(f"{int(last)}: {el[last]:.0f}%",
                xy=(last, el[last]), xytext=(last - 5, el[last] - 7),
                fontsize=9, color=COLORS["GR"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["GR"], lw=0.8))
ax.set_title("Tertiary Educational Attainment, Age 25–34 (%)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of 25-34 population with tertiary education")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/09d_tertiary.png", dpi=150); plt.close()
print("  saved 09d_tertiary.png")

# ---------------------------------------------------------------------------
# 5. Life expectancy at birth
# ---------------------------------------------------------------------------
print("Fetching life expectancy at birth...")
le = fetch_eurostat("demo_mlexpec",
                    {"unit":"YR","sex":"T","age":"Y_LT1"}, PEERS_EU)
# Trim to 2000+
le = le.loc[le.index >= 2000]
le.index.name = "year"
save_csv(le, "09e_life_expectancy_years")

fig, ax = plt.subplots(figsize=(13, 5))
plot_peer_lines(ax, le)
add_programme_shading(ax, label_y_frac=0.05)
# Mark COVID dip
ax.axvline(2020, color="black", linestyle=":", linewidth=0.7, alpha=0.5)
ax.text(2020, ax.get_ylim()[1] * 0.99, "COVID-19",
        rotation=90, va="top", ha="right", fontsize=7, color="#555")
ax.set_title("Life Expectancy at Birth (years, both sexes)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Years")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/09e_life_expectancy.png", dpi=150); plt.close()
print("  saved 09e_life_expectancy.png")

print("\nDone — social charts saved to", OUTPUT)
