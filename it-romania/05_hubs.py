"""
The Hubs — Bucharest-Ilfov, Cluj-Napoca (Nord-Vest), Timișoara (Vest),
and Iași (Nord-Est).

Equal-weight, symmetric treatment: every chart shows the same four NUTS2
regions side by side, never picking one out.

The regional NACE-J series (covering all of "information and communication"
— ICT is the dominant component for these regions) is the closest Eurostat
proxy we get for regional ICT-sector activity. We use:
  (a) NUTS2 ICT-broad employment (lfst_r_lfe2en2, NACE J, sample LFS — noisy)
  (b) NUTS2 NACE-J compensation of employees (nama_10r_2coe — administrative,
      much cleaner; only available from 2008)
  (c) NUTS2 population trend (demo_r_pjangrp3)
  (d) Hub share of national NACE-J compensation — the cleanest concentration
      metric we have.

NUTS2 codes:
  RO32 = București-Ilfov
  RO11 = Nord-Vest (Cluj-Napoca)
  RO42 = Vest (Timișoara)
  RO21 = Nord-Est (Iași)

Note: Eurostat regional house-price indices are not available at NUTS2 for
Romania (only national). Regional housing data is published by INS Tempo
and would need a separate INS-API fetch — out of scope here.
"""

import warnings
warnings.filterwarnings("ignore")

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import eurostat

OUTPUT   = "charts"
RAW_DATA = "raw-data"
os.makedirs(OUTPUT, exist_ok=True)
os.makedirs(RAW_DATA, exist_ok=True)

HUBS = {
    "RO32": "București-Ilfov",
    "RO11": "Nord-Vest (Cluj)",
    "RO42": "Vest (Timișoara)",
    "RO21": "Nord-Est (Iași)",
}
HUB_COLORS = {
    "RO32": "#c0392b",
    "RO11": "#2980b9",
    "RO42": "#27ae60",
    "RO21": "#8e44ad",
}
HUB_ORDER = ["RO32", "RO11", "RO42", "RO21"]
ALL_NUTS2_RO = ["RO11", "RO12", "RO21", "RO22", "RO31", "RO32", "RO41", "RO42"]


def save_csv(df, name):
    """Save df to raw-data/{name}.csv, preserving any '#'-prefixed source
    header lines that were already at the top of the file."""
    path = f"{RAW_DATA}/{name}.csv"
    header_lines = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("#"):
                    header_lines.append(line)
                else:
                    break
    df.to_csv(path)
    if header_lines:
        with open(path, "r", encoding="utf-8") as fh:
            body = fh.read()
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("".join(header_lines) + body)
    print(f"  saved raw-data/{name}.csv")


def fetch_eurostat(code, filters):
    df = eurostat.get_data_df(code, flags=False).rename(columns={"geo\\TIME_PERIOD": "geo"})
    for col, vals in filters.items():
        if isinstance(vals, str):
            vals = [vals]
        df = df[df[col].isin(vals)]
    return df


def to_year_indexed(df, by="geo"):
    yrs = [c for c in df.columns if str(c).isdigit()]
    out = df.set_index(by)[yrs].astype(float)
    out.columns = out.columns.astype(int)
    out = out.T.sort_index()
    out.index.name = "year"
    return out


# ---------------------------------------------------------------------------
# 1. ICT-broad employment by NUTS2 hub (LFS, NACE J)
# ---------------------------------------------------------------------------
print("Fetching NUTS2 ICT employment (LFS, NACE J)...")
df_lfs = fetch_eurostat("lfst_r_lfe2en2", {
    "nace_r2": "J", "sex": "T", "age": "Y_GE15", "unit": "THS_PER",
    "geo": ALL_NUTS2_RO,
})
emp_lfs = to_year_indexed(df_lfs).dropna(how="all")
save_csv(emp_lfs, "05a_ict_employment_nuts2_lfs_ths")

emp_hubs = emp_lfs[HUB_ORDER]
fig, ax = plt.subplots(figsize=(13, 5))
for hub in HUB_ORDER:
    s = emp_hubs[hub].dropna()
    ax.plot(s.index, s.values, color=HUB_COLORS[hub],
            linewidth=2.2, marker="o", markersize=4, label=HUBS[hub])
ax.set_title("ICT-Broad Employment by Hub (NACE J, NUTS2, LFS — note small-sample volatility)",
             fontsize=12.5, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Thousands of persons employed")
ax.legend(fontsize=9); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/05a_hubs_ict_employment.png", dpi=150); plt.close()
print("  saved 05a_hubs_ict_employment.png")


# ---------------------------------------------------------------------------
# 2. Compensation of employees in NACE J by NUTS2 hub — EUR million
# ---------------------------------------------------------------------------
print("Fetching NUTS2 compensation in NACE J...")
df_coe = fetch_eurostat("nama_10r_2coe", {
    "nace_r2": "J", "currency": "MIO_EUR",
    "geo": ALL_NUTS2_RO,
})
coe = to_year_indexed(df_coe).dropna(how="all")
save_csv(coe, "05b_naceJ_compensation_nuts2_meur")

coe_hubs = coe[HUB_ORDER]
fig, ax = plt.subplots(figsize=(13, 5))
for hub in HUB_ORDER:
    s = coe_hubs[hub].dropna()
    ax.plot(s.index, s.values, color=HUB_COLORS[hub],
            linewidth=2.2, marker="o", markersize=4, label=HUBS[hub])
ax.set_title("Information & Communication (NACE J) — Compensation of Employees by Hub",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("EUR million")
ax.legend(fontsize=9); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/05b_hubs_compensation.png", dpi=150); plt.close()
print("  saved 05b_hubs_compensation.png")


# ---------------------------------------------------------------------------
# 3. Hub share of national NACE-J compensation — concentration metric
# ---------------------------------------------------------------------------
print("Computing hub share of national NACE J compensation...")
# RO national = sum of all NUTS2 regions
national_coe = coe[ALL_NUTS2_RO].sum(axis=1)
share = coe[HUB_ORDER].div(national_coe, axis=0) * 100
share.index.name = "year"
save_csv(share, "05c_hubs_share_of_naceJ_pct")

share_long = share.dropna(how="all")
fig, ax = plt.subplots(figsize=(13, 5))
ax.stackplot(share_long.index,
             [share_long[h] for h in HUB_ORDER],
             labels=[HUBS[h] for h in HUB_ORDER],
             colors=[HUB_COLORS[h] for h in HUB_ORDER],
             alpha=0.85)
rest = 100 - share_long.sum(axis=1)
ax.fill_between(share_long.index, share_long.sum(axis=1),
                share_long.sum(axis=1) + rest,
                color="#bdc3c7", alpha=0.55, label="Rest of Romania")
ax.set_title("Hub Share of National NACE-J Compensation (Information & Communication)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of national NACE-J compensation")
ax.set_ylim(0, 100)
ax.legend(fontsize=9, loc="lower right"); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/05c_hubs_concentration.png", dpi=150); plt.close()
print("  saved 05c_hubs_concentration.png")


# ---------------------------------------------------------------------------
# 4. Indexed compensation growth per hub (2008=100) — relative dynamism
# ---------------------------------------------------------------------------
print("Computing indexed compensation growth per hub...")
base = 2008
coe_idx = coe[HUB_ORDER].copy()
coe_idx = coe_idx.div(coe_idx.loc[base]) * 100
coe_idx = coe_idx[coe_idx.index >= base].dropna(how="all")
save_csv(coe_idx, "05d_hubs_compensation_index_2008_100")

fig, ax = plt.subplots(figsize=(13, 5))
for hub in HUB_ORDER:
    s = coe_idx[hub].dropna()
    ax.plot(s.index, s.values, color=HUB_COLORS[hub],
            linewidth=2.2, marker="o", markersize=4, label=HUBS[hub])
ax.axhline(100, color="black", linestyle="--", linewidth=0.6)
ax.set_title("NACE-J Compensation Growth by Hub (2008 = 100)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Index (2008 = 100)")
ax.legend(fontsize=9); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/05d_hubs_indexed_growth.png", dpi=150); plt.close()
print("  saved 05d_hubs_indexed_growth.png")


# ---------------------------------------------------------------------------
# 5. Population trajectory by hub — IT-hub regions buck the national trend
# ---------------------------------------------------------------------------
print("Fetching NUTS2 population trends...")
df_pop = fetch_eurostat("demo_r_pjangrp3", {
    "sex": "T", "age": "TOTAL", "unit": "NR",
    "geo": ALL_NUTS2_RO + ["RO"],
})
pop = to_year_indexed(df_pop).dropna(how="all")
save_csv(pop, "05e_population_nuts2")

base_pop = 2014
pop_index = pop.div(pop.loc[base_pop]) * 100
pop_index = pop_index[pop_index.index >= base_pop].dropna(how="all")

fig, ax = plt.subplots(figsize=(13, 5))
for hub in HUB_ORDER:
    if hub not in pop_index.columns:
        continue
    s = pop_index[hub].dropna()
    ax.plot(s.index, s.values, color=HUB_COLORS[hub],
            linewidth=2.2, marker="o", markersize=4, label=HUBS[hub])
if "RO" in pop_index.columns:
    s = pop_index["RO"].dropna()
    ax.plot(s.index, s.values, color="black", linewidth=1.6,
            linestyle="--", marker="o", markersize=3, label="Romania (national)")
ax.axhline(100, color="#7f8c8d", linewidth=0.6)
ax.set_title(f"Hub Population vs National ({base_pop} = 100)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel(f"Index ({base_pop} = 100)")
ax.legend(fontsize=9, loc="best"); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/05e_hubs_population.png", dpi=150); plt.close()
print("  saved 05e_hubs_population.png")


# ---------------------------------------------------------------------------
# 6. National house price index — for context (no regional breakdown on EU)
# ---------------------------------------------------------------------------
print("Fetching national house price index...")
df_hpi = fetch_eurostat("prc_hpi_a", {
    "purchase": "TOTAL", "unit": "I15_A_AVG",
    "geo": ["RO", "EU27_2020"],
})
hpi = to_year_indexed(df_hpi).dropna(how="all")
save_csv(hpi, "05f_house_price_index_2015_100")

fig, ax = plt.subplots(figsize=(13, 5))
for geo, lbl, c in [("RO", "Romania", "#c0392b"),
                     ("EU27_2020", "EU27", "#7f8c8d")]:
    if geo in hpi.columns:
        s = hpi[geo].dropna()
        ax.plot(s.index, s.values, color=c, linewidth=2.2,
                marker="o", markersize=4, label=lbl)
ax.axhline(100, color="black", linestyle="--", linewidth=0.6, alpha=0.5)
ax.set_title("House Price Index — Romania vs EU27 (2015 = 100)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Index (2015 = 100)")
ax.legend(fontsize=10); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/05f_house_price_index.png", dpi=150); plt.close()
print("  saved 05f_house_price_index.png")


print("\nDone — hub charts saved to", OUTPUT)
