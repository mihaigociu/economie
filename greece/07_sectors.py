"""
Sectoral structure: services dominance, tourism intensity, construction cycle,
energy transition, manufacturing decline.
Sources: Eurostat (nama_10_a10, tour_occ_nin2, sts_copr_a, nrg_ind_ren, demo_pjan)

Greek distinctives: tourism + shipping services drive growth, manufacturing is
among the smallest in the EU, construction had an extreme boom-bust cycle.
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
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

def plot_peer_lines(ax, df, highlight="GR", include_eu=True):
    order = ["GR","PT","IT","ES","CY"] + (["EU"] if include_eu else [])
    for iso in order:
        if iso in df.columns:
            lw = 2.5 if iso == highlight else 1.4
            ls = "--" if iso == "EU" else "-"
            ax.plot(df.index, df[iso], label=PEER_LABELS[iso],
                    color=COLORS[iso], linewidth=lw, marker="o", markersize=3,
                    linestyle=ls)

def fetch_eurostat(dataset, filters, geos, geo_col_search="geo"):
    """Filter an Eurostat dataset by dict of {dim: value} and return pivot
    table indexed by year, columns by geo (renamed via EU_TO_LBL)."""
    df = eurostat.get_data_df(dataset)
    geo_col = [c for c in df.columns if geo_col_search in c.lower()][0]
    mask = pd.Series(True, index=df.index)
    for dim, val in filters.items():
        mask &= (df[dim] == val)
    mask &= df[geo_col].isin(geos)
    sub = df[mask].copy()
    year_cols = sorted([c for c in sub.columns if str(c).isdigit()])
    out = sub.set_index(geo_col)[year_cols].T
    out.index = out.index.astype(int)
    out = out.rename(columns=EU_TO_LBL)
    return out

# ---------------------------------------------------------------------------
# 1. Sectoral GVA composition — Greek services dominance
# ---------------------------------------------------------------------------
# Stackplot of Greek GVA by NACE A*10 sector, % of total value added.
# Shows manufacturing decline, construction collapse, and the rise of
# services (trade-tourism, finance, public administration).
print("Fetching Greek sectoral GVA composition...")
df_gva = eurostat.get_data_df("nama_10_a10")
# Pick: B-E (industry), C (manufacturing only), F (construction), G-I (trade+transport+accommodation),
# J (info/comms), K (finance), L (real estate), M-N (prof+admin), O-Q (public),
# R-U (other). A is agriculture.
geo_col = [c for c in df_gva.columns if "geo" in c.lower()][0]
year_cols = sorted([c for c in df_gva.columns if str(c).isdigit() and 2000 <= int(c) <= 2024])

# We use SCA (seasonally + calendar adjusted? No — use CP_MEUR for level then % of total).
# Use unit=PC_TOT_VA, na_item=B1G (gross value added) to get sector share of total VA.
sector_map = {
    "A":     "Agriculture",
    "B-E":   "Industry (incl. mfg)",
    "F":     "Construction",
    "G-I":   "Trade, transport, tourism",
    "J":     "Information & comms",
    "K":     "Financial",
    "L":     "Real estate",
    "M_N":   "Professional & admin",
    "O-Q":   "Public, education, health",
    "R-U":   "Other services",
}
sector_colors = {
    "Agriculture": "#27ae60",
    "Industry (incl. mfg)": "#e67e22",
    "Construction": "#c0392b",
    "Trade, transport, tourism": "#2980b9",
    "Information & comms": "#16a085",
    "Financial": "#8e44ad",
    "Real estate": "#d35400",
    "Professional & admin": "#34495e",
    "Public, education, health": "#7f8c8d",
    "Other services": "#bdc3c7",
}

# Filter for Greece, value added at current prices (compute shares ourselves)
greek_b1g = df_gva[(df_gva[geo_col] == "EL") &
                   (df_gva["unit"] == "CP_MEUR") &
                   (df_gva["na_item"] == "B1G")]
# Pull total VA per year for normalization
total_row = greek_b1g[greek_b1g["nace_r2"] == "TOTAL"]
total = total_row[year_cols].iloc[0].astype(float)
total.index = total.index.astype(int)

gva_shares = {}
for nace, label in sector_map.items():
    sub = greek_b1g[greek_b1g["nace_r2"] == nace]
    if not sub.empty:
        s = sub[year_cols].iloc[0].astype(float)
        s.index = s.index.astype(int)
        gva_shares[label] = (s / total) * 100

gva_df = pd.DataFrame(gva_shares)
gva_df.index.name = "year"
save_csv(gva_df, "07a_greek_gva_composition_pct")

# Plot ordered for visual stack: agriculture & industry at bottom, services on top
stack_order = ["Agriculture","Industry (incl. mfg)","Construction",
               "Trade, transport, tourism","Information & comms","Financial",
               "Real estate","Professional & admin","Public, education, health","Other services"]
stack_cols = [c for c in stack_order if c in gva_df.columns]

fig, ax = plt.subplots(figsize=(13, 6))
ax.stackplot(gva_df.index, [gva_df[c].fillna(0) for c in stack_cols],
             labels=stack_cols,
             colors=[sector_colors[c] for c in stack_cols], alpha=0.9)
add_programme_shading(ax, label_y_frac=0.96)
ax.set_title("Greece: Sectoral Composition of Gross Value Added (% of total)",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of total GVA")
ax.set_ylim(0, 100)
ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8, frameon=False)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/07a_gva_composition.png", dpi=150, bbox_inches="tight"); plt.close()
print("  saved 07a_gva_composition.png")

# ---------------------------------------------------------------------------
# 2. Tourism intensity — nights spent at accommodation per capita
# ---------------------------------------------------------------------------
print("Fetching tourism nights spent...")
# tour_occ_ninat: nights spent at tourist accommodation establishments by country of residence
# variables: c_resid (TOTAL), nace_r2 (I551-I553 = all accommodation, often I551_I553), unit (NR), geo, time
df_tour = eurostat.get_data_df("tour_occ_ninat")
geo_col_t = [c for c in df_tour.columns if "geo" in c.lower()][0]
year_cols_t = sorted([c for c in df_tour.columns if str(c).isdigit() and 2005 <= int(c) <= 2024])

# Try I551-I553 (all accommodation establishments), c_resid TOTAL
mask_t = ((df_tour["c_resid"] == "TOTAL") &
          (df_tour["nace_r2"] == "I551-I553") &
          (df_tour["unit"] == "NR") &
          (df_tour[geo_col_t].isin(["EL","PT","IT","ES","CY"])))
sub_t = df_tour[mask_t]
tour_pivot = sub_t.set_index(geo_col_t)[year_cols_t].T
tour_pivot.index = tour_pivot.index.astype(int)
tour_pivot = tour_pivot.rename(columns=EU_TO_LBL).astype(float)

# Population for per-capita normalization
print("Fetching population for per-capita normalization...")
df_pop = eurostat.get_data_df("demo_pjan")
geo_col_p = [c for c in df_pop.columns if "geo" in c.lower()][0]
year_cols_p = sorted([c for c in df_pop.columns if str(c).isdigit() and 2005 <= int(c) <= 2024])
mask_p = ((df_pop["sex"] == "T") & (df_pop["age"] == "TOTAL") &
          (df_pop[geo_col_p].isin(["EL","PT","IT","ES","CY"])))
sub_p = df_pop[mask_p]
pop_pivot = sub_p.set_index(geo_col_p)[year_cols_p].T
pop_pivot.index = pop_pivot.index.astype(int)
pop_pivot = pop_pivot.rename(columns=EU_TO_LBL).astype(float)

# Align years
common_years = sorted(set(tour_pivot.index) & set(pop_pivot.index))
nights_per_cap = (tour_pivot.loc[common_years] / pop_pivot.loc[common_years]).dropna(how="all")
nights_per_cap.index.name = "year"
save_csv(nights_per_cap, "07b_tourism_nights_per_capita")

fig, ax = plt.subplots(figsize=(13, 5))
plot_peer_lines(ax, nights_per_cap, include_eu=False)
add_programme_shading(ax, label_y_frac=0.05)
# Annotate Greece's peak
if "GR" in nights_per_cap.columns:
    el = nights_per_cap["GR"].dropna()
    peak = el.idxmax()
    last = el.index.max()
    ax.annotate(f"Peak: {el[peak]:.1f} nights\n({int(peak)})",
                xy=(peak, el[peak]),
                xytext=(peak - 4, el[peak] - 2),
                fontsize=9, color=COLORS["GR"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["GR"], lw=0.8))
ax.set_title("Tourism Intensity: Nights Spent at Accommodation per Capita",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Nights per resident")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/07b_tourism_intensity.png", dpi=150); plt.close()
print("  saved 07b_tourism_intensity.png")

# ---------------------------------------------------------------------------
# 3. Construction production cycle — boom-bust
# ---------------------------------------------------------------------------
print("Fetching construction production index...")
# sts_copr_a: construction production index, annual
df_cons = eurostat.get_data_df("sts_copr_a")
geo_col_c = [c for c in df_cons.columns if "geo" in c.lower()][0]
year_cols_c = sorted([c for c in df_cons.columns if str(c).isdigit() and 2000 <= int(c) <= 2024])

# variables typically: indic_bt (PROD), nace_r2 (F = construction), unit (I15 = 2015=100),
# s_adj (SCA or CA)
# Try the unadjusted annual index with 2015=100 base
mask_c = ((df_cons["indic_bt"] == "PRD") &
          (df_cons["nace_r2"] == "F") &
          (df_cons["unit"] == "I15") &
          (df_cons["s_adj"] == "CA") &
          (df_cons[geo_col_c].isin(["EL","PT","IT","ES","CY","EU27_2020"])))
sub_c = df_cons[mask_c]
cons_pivot = sub_c.set_index(geo_col_c)[year_cols_c].T
cons_pivot.index = cons_pivot.index.astype(int)
cons_pivot = cons_pivot.rename(columns=EU_TO_LBL).astype(float)
cons_pivot.index.name = "year"
save_csv(cons_pivot, "07c_construction_production_idx_2015_100")

fig, ax = plt.subplots(figsize=(13, 5))
plot_peer_lines(ax, cons_pivot)
ax.axhline(100, color="black", linewidth=0.6, linestyle="--", alpha=0.5)
add_programme_shading(ax, label_y_frac=0.92)
if "GR" in cons_pivot.columns:
    el = cons_pivot["GR"].dropna()
    peak = el.idxmax()
    trough = el.idxmin()
    last = el.index.max()
    drop = (el[trough] - el[peak]) / el[peak] * 100
    ax.annotate(f"Peak: {el[peak]:.0f} ({int(peak)})",
                xy=(peak, el[peak]), xytext=(peak - 3, el[peak] + 30),
                fontsize=9, color=COLORS["GR"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["GR"], lw=0.8))
    ax.annotate(f"Trough: {el[trough]:.0f} ({int(trough)})\n{drop:.0f}% from peak",
                xy=(trough, el[trough]), xytext=(trough - 2, el[trough] + 60),
                fontsize=9, color=COLORS["GR"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["GR"], lw=0.8))
ax.set_title("Construction Production Index (2015 = 100)",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Index, 2015 = 100")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/07c_construction_cycle.png", dpi=150); plt.close()
print("  saved 07c_construction_cycle.png")

# ---------------------------------------------------------------------------
# 4. Renewable energy share — energy transition
# ---------------------------------------------------------------------------
print("Fetching renewable energy share...")
# nrg_ind_ren: share of renewables in gross final energy consumption
ren = fetch_eurostat("nrg_ind_ren",
                     {"nrg_bal": "REN"},
                     ["EL","PT","IT","ES","CY","EU27_2020"])
ren.index.name = "year"
save_csv(ren, "07d_renewables_share_pct")

fig, ax = plt.subplots(figsize=(13, 5))
plot_peer_lines(ax, ren)
add_programme_shading(ax, label_y_frac=0.05)
# Annotate Greece
if "GR" in ren.columns:
    el = ren["GR"].dropna()
    last = el.index.max()
    first = el.index.min()
    ax.annotate(f"{int(last)}: {el[last]:.0f}%\n(from {el[first]:.0f}% in {int(first)})",
                xy=(last, el[last]), xytext=(last - 4, el[last] + 5),
                fontsize=9, color=COLORS["GR"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["GR"], lw=0.8))
ax.set_title("Renewable Energy Share in Gross Final Energy Consumption (%)",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("%")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/07d_renewables.png", dpi=150); plt.close()
print("  saved 07d_renewables.png")

# ---------------------------------------------------------------------------
# 5. Manufacturing share — long-run decline
# ---------------------------------------------------------------------------
print("Computing manufacturing GVA share across peers...")
# Compute share = sector C / TOTAL at current prices (no native % unit in nama_10_a10).
peers_geo = ["EL","PT","IT","ES","CY","EU27_2020"]
b1g = df_gva[(df_gva["unit"] == "CP_MEUR") & (df_gva["na_item"] == "B1G") &
             (df_gva[geo_col].isin(peers_geo))]
mfg_data = {}
for g in peers_geo:
    sub = b1g[b1g[geo_col] == g]
    tot = sub[sub["nace_r2"] == "TOTAL"]
    mc  = sub[sub["nace_r2"] == "C"]
    if tot.empty or mc.empty:
        continue
    t = tot[year_cols].iloc[0].astype(float); t.index = t.index.astype(int)
    m = mc[year_cols].iloc[0].astype(float);  m.index = m.index.astype(int)
    mfg_data[EU_TO_LBL[g]] = (m / t) * 100
mfg = pd.DataFrame(mfg_data)
mfg.index.name = "year"
save_csv(mfg, "07e_manufacturing_share_pct")

fig, ax = plt.subplots(figsize=(13, 5))
plot_peer_lines(ax, mfg)
add_programme_shading(ax, label_y_frac=0.92)
if "GR" in mfg.columns:
    el = mfg["GR"].dropna()
    first = el.index.min()
    last = el.index.max()
    ax.annotate(f"{int(first)}: {el[first]:.1f}%",
                xy=(first, el[first]), xytext=(first + 0.5, el[first] + 1.5),
                fontsize=9, color=COLORS["GR"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["GR"], lw=0.8))
    ax.annotate(f"{int(last)}: {el[last]:.1f}%",
                xy=(last, el[last]), xytext=(last - 4, el[last] - 2),
                fontsize=9, color=COLORS["GR"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["GR"], lw=0.8))
ax.set_title("Manufacturing (NACE C) Share of Gross Value Added (%)",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of total GVA")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/07e_manufacturing.png", dpi=150); plt.close()
print("  saved 07e_manufacturing.png")

print("\nDone — sector charts saved to", OUTPUT)
