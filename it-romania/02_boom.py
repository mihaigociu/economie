"""
The outsourcing boom (2000-2010) and its continuation.

Eurostat national-accounts series for NACE J62_J63 (computer programming,
consultancy, information service activities) — gross value added in current
prices and persons employed — go back to 1995 for Romania and are the
cleanest measure of sector size over time. We use them throughout.

Sources: Eurostat nama_10_a64 (value added), nama_10_a64_e (employment).
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

PEERS = ["RO", "PL", "CZ", "HU", "BG"]
PEER_LABELS = {"RO": "Romania", "PL": "Poland", "CZ": "Czechia",
               "HU": "Hungary", "BG": "Bulgaria", "EU27_2020": "EU27"}
COLORS = {"RO": "#c0392b", "PL": "#2980b9", "CZ": "#27ae60",
          "HU": "#8e44ad", "BG": "#e67e22", "EU27_2020": "#7f8c8d"}


def save_csv(df, name):
    path = f"{RAW_DATA}/{name}.csv"
    df.to_csv(path)
    print(f"  saved {path}")


def fetch_eurostat(code, filters):
    df = eurostat.get_data_df(code, flags=False).rename(columns={"geo\\TIME_PERIOD": "geo"})
    for col, vals in filters.items():
        if isinstance(vals, str):
            vals = [vals]
        df = df[df[col].isin(vals)]
    return df


def to_year_indexed(df, geo_col="geo"):
    yrs = [c for c in df.columns if str(c).isdigit()]
    out = df.set_index(geo_col)[yrs].astype(float)
    out.columns = out.columns.astype(int)
    out = out.T.sort_index()
    out.index.name = "year"
    return out


# ---------------------------------------------------------------------------
# 1. Sector value added — Romania alone, 1995-present
# ---------------------------------------------------------------------------
print("Fetching ICT services value added (Romania)...")
df = fetch_eurostat("nama_10_a64", {
    "nace_r2": "J62_J63",
    "na_item": "B1G",          # Gross value added
    "unit":    "CP_MEUR",      # Current prices, million EUR
    "geo":     PEERS + ["EU27_2020"],
})
gva = to_year_indexed(df).dropna(how="all")
save_csv(gva, "02a_ict_gva_meur")

ro = gva["RO"].dropna()
fig, ax = plt.subplots(figsize=(13, 5))
ax.fill_between(ro.index, 0, ro.values, color=COLORS["RO"], alpha=0.15)
ax.plot(ro.index, ro.values, color=COLORS["RO"], linewidth=2.5, marker="o", markersize=3)
ax.axvline(2007, color="#7f8c8d", linestyle="--", linewidth=1, alpha=0.6)
ax.text(2007.1, ro.max()*0.92, "EU accession", fontsize=9, color="#7f8c8d")
ax.axvline(2001, color="#27ae60", linestyle="--", linewidth=1, alpha=0.6)
ax.text(2001.1, ro.max()*0.78, "IT income-tax\nexemption", fontsize=9, color="#27ae60")
ax.set_title("Romania — Gross Value Added in Computer Programming & Information Services (NACE J62_J63)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("EUR million (current prices)")
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/02a_ict_gva_romania.png", dpi=150); plt.close()
print("  saved 02a_ict_gva_romania.png")


# ---------------------------------------------------------------------------
# 2. ICT services GVA as % of total GVA — sector "weight" in the economy
# ---------------------------------------------------------------------------
print("Computing ICT share of total GVA...")
df_total = fetch_eurostat("nama_10_a64", {
    "nace_r2": "TOTAL",
    "na_item": "B1G",
    "unit":    "CP_MEUR",
    "geo":     PEERS + ["EU27_2020"],
})
total_gva = to_year_indexed(df_total)
share = (gva / total_gva) * 100
share.index.name = "year"
save_csv(share, "02b_ict_gva_share_pct")

share_plot = share[share.index >= 2000].dropna(how="all")
fig, ax = plt.subplots(figsize=(13, 5))
for geo in PEERS + ["EU27_2020"]:
    if geo not in share_plot.columns:
        continue
    lw = 2.5 if geo == "RO" else 1.4
    ax.plot(share_plot.index, share_plot[geo], label=PEER_LABELS[geo],
            color=COLORS[geo], linewidth=lw, marker="o", markersize=3)
ax.set_title("ICT Services (J62_J63) as % of Total GVA — Romania vs CEE peers and EU27",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of total GVA")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/02b_ict_gva_share.png", dpi=150); plt.close()
print("  saved 02b_ict_gva_share.png")


# ---------------------------------------------------------------------------
# 3. Employment in J62_J63 — national accounts (cleaner than LFS)
# ---------------------------------------------------------------------------
print("Fetching ICT employment (national accounts)...")
df_emp = fetch_eurostat("nama_10_a64_e", {
    "nace_r2": "J62_J63",
    "na_item": "EMP_DC",       # Total employment, domestic concept
    "unit":    "THS_PER",
    "geo":     PEERS + ["EU27_2020"],
})
emp = to_year_indexed(df_emp).dropna(how="all")
save_csv(emp, "02c_ict_employment_ths")

ro_emp = emp["RO"].dropna()
fig, ax = plt.subplots(figsize=(13, 5))
ax.fill_between(ro_emp.index, 0, ro_emp.values, color=COLORS["RO"], alpha=0.15)
ax.plot(ro_emp.index, ro_emp.values, color=COLORS["RO"], linewidth=2.5, marker="o", markersize=3)
ax.axvline(2007, color="#7f8c8d", linestyle="--", linewidth=1, alpha=0.6)
ax.text(2007.1, ro_emp.max()*0.92, "EU accession", fontsize=9, color="#7f8c8d")
ax.set_title("Romania — Employment in Computer Programming & Information Services (NACE J62_J63)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Thousands of persons")
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/02c_ict_employment_romania.png", dpi=150); plt.close()
print("  saved 02c_ict_employment_romania.png")


# ---------------------------------------------------------------------------
# 4. Indexed growth — Romania vs peers (2000=100) on employment
# ---------------------------------------------------------------------------
print("Computing indexed employment growth...")
base_year = 2000
emp_index = emp.div(emp.loc[base_year]) * 100
emp_index = emp_index[emp_index.index >= base_year].dropna(how="all")
save_csv(emp_index, "02d_ict_employment_index_2000_100")

fig, ax = plt.subplots(figsize=(13, 5))
for geo in PEERS + ["EU27_2020"]:
    if geo not in emp_index.columns:
        continue
    lw = 2.5 if geo == "RO" else 1.4
    ax.plot(emp_index.index, emp_index[geo], label=PEER_LABELS[geo],
            color=COLORS[geo], linewidth=lw, marker="o", markersize=3)
ax.axhline(100, color="black", linestyle="--", linewidth=0.8)
ax.set_title("ICT Sector Employment — Indexed Growth (2000=100)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Index (2000=100)")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/02d_employment_index_growth.png", dpi=150); plt.close()
print("  saved 02d_employment_index_growth.png")


# ---------------------------------------------------------------------------
# 5. Productivity — GVA per worker, EUR thousand (current prices)
# ---------------------------------------------------------------------------
print("Computing GVA per worker...")
common_yrs = sorted(set(gva.index) & set(emp.index))
# gva is in MEUR, emp is in thousand persons -> raw quotient is thousand EUR / person
prod = gva.loc[common_yrs] / emp.loc[common_yrs]
prod = prod.dropna(how="all")
prod.index.name = "year"
save_csv(prod, "02e_ict_productivity_keur_per_worker")

prod_plot = prod[prod.index >= 2000]
fig, ax = plt.subplots(figsize=(13, 5))
for geo in PEERS + ["EU27_2020"]:
    if geo not in prod_plot.columns:
        continue
    lw = 2.5 if geo == "RO" else 1.4
    ax.plot(prod_plot.index, prod_plot[geo], label=PEER_LABELS[geo],
            color=COLORS[geo], linewidth=lw, marker="o", markersize=3)
ax.set_title("ICT Services — Gross Value Added per Worker (current prices)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Thousand EUR per worker")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/02e_ict_productivity.png", dpi=150); plt.close()
print("  saved 02e_ict_productivity.png")


print("\nDone — boom-era charts saved to", OUTPUT)
