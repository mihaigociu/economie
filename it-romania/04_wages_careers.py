"""
Wages, careers, and the generation that Romanian IT built.

Most important chart is the wage premium: average compensation per employee
in J62_J63 vs the whole-economy average. Eurostat national accounts have
both numerator (D1 compensation of employees) and denominator (SAL_DC
employees) by NACE for Romania from 1995, so we can build a continuous
30-year series — rare for sector-specific wages.

Also covered:
  (a) Wage premium ratio across CEE peers (where the IT wage opens up the
      widest vs the local economy — Romania consistently tops this).
  (b) Women in ICT specialist roles share.
  (c) ICT specialist growth rate vs ICT graduate output — the supply-demand
      pressure that has driven wages up.

Sources: Eurostat nama_10_a64 (D1), nama_10_a64_e (SAL_DC), isoc_sks_itsps,
isoc_sks_itspt, educ_uoe_grad02.
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
# 1. Annual compensation per employee — J62_J63 vs whole economy, Romania
# ---------------------------------------------------------------------------
print("Fetching compensation of employees (RO J62_J63 vs TOTAL)...")
df_comp = fetch_eurostat("nama_10_a64", {
    "nace_r2": ["J62_J63", "TOTAL"],
    "na_item": "D1",
    "unit":    "CP_MEUR",
    "geo":     PEERS + ["EU27_2020"],
})
df_emp = fetch_eurostat("nama_10_a64_e", {
    "nace_r2": ["J62_J63", "TOTAL"],
    "na_item": "SAL_DC",
    "unit":    "THS_PER",
    "geo":     PEERS + ["EU27_2020"],
})

# Build dataframes: year x geo, separately for J62_J63 and TOTAL
def by_nace(df, value):
    sub = df[df["nace_r2"] == value]
    return to_year_indexed(sub)

comp_ict   = by_nace(df_comp, "J62_J63")
comp_total = by_nace(df_comp, "TOTAL")
emp_ict    = by_nace(df_emp,  "J62_J63")
emp_total  = by_nace(df_emp,  "TOTAL")

# Avg comp per employee (EUR per year). MEUR / thousand persons -> thousand EUR.
wage_ict   = (comp_ict   / emp_ict)   * 1000.0      # EUR per year
wage_total = (comp_total / emp_total) * 1000.0
wage_ict.index.name   = "year"
wage_total.index.name = "year"

ro_wages = pd.DataFrame({
    "ict_eur":   wage_ict["RO"],
    "total_eur": wage_total["RO"],
}).dropna()
ro_wages["premium_x"] = ro_wages["ict_eur"] / ro_wages["total_eur"]
save_csv(ro_wages, "04a_ro_compensation_per_employee")

fig, ax = plt.subplots(figsize=(13, 5))
ax.plot(ro_wages.index, ro_wages["ict_eur"] / 1000.0,
        color="#c0392b", linewidth=2.5, marker="o", markersize=4,
        label="IT services (J62_J63)")
ax.plot(ro_wages.index, ro_wages["total_eur"] / 1000.0,
        color="#7f8c8d", linewidth=2.0, marker="o", markersize=3,
        label="Whole-economy average")
ax.set_title("Romania — Average Annual Compensation per Employee",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Thousand EUR per employee per year")
ax.legend(fontsize=10); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/04a_ro_wage_levels.png", dpi=150); plt.close()
print("  saved 04a_ro_wage_levels.png")


# ---------------------------------------------------------------------------
# 2. Wage premium ratio (IT / whole economy) — RO over time
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(13, 5))
ax.fill_between(ro_wages.index, 1.0, ro_wages["premium_x"],
                color="#c0392b", alpha=0.15)
ax.plot(ro_wages.index, ro_wages["premium_x"],
        color="#c0392b", linewidth=2.5, marker="o", markersize=4)
ax.axhline(1.0, color="#7f8c8d", linestyle="--", linewidth=1, alpha=0.6)
ax.axvline(2001, color="#27ae60", linestyle=":", linewidth=1, alpha=0.7)
ax.text(2001.2, ro_wages["premium_x"].max() * 0.95,
        "IT income-tax\nexemption", fontsize=8.5, color="#27ae60")
ax.axvline(2007, color="#7f8c8d", linestyle=":", linewidth=1, alpha=0.7)
ax.text(2007.2, ro_wages["premium_x"].max() * 0.85,
        "EU accession", fontsize=8.5, color="#7f8c8d")
ax.set_title("Romania — IT Wage Premium (J62_J63 compensation / whole-economy avg)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Multiple of national average")
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1fx"))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/04b_ro_wage_premium.png", dpi=150); plt.close()
print("  saved 04b_ro_wage_premium.png")


# ---------------------------------------------------------------------------
# 3. Wage premium across CEE peers — comparable measure
# ---------------------------------------------------------------------------
print("Computing wage premium for CEE peers...")
premium = wage_ict / wage_total
premium = premium[premium.index >= 2000].dropna(how="all")
premium.index.name = "year"
save_csv(premium, "04c_wage_premium_ratio_cee")

fig, ax = plt.subplots(figsize=(13, 5))
for geo in PEERS + ["EU27_2020"]:
    if geo not in premium.columns:
        continue
    lw = 2.5 if geo == "RO" else 1.4
    ax.plot(premium.index, premium[geo], label=PEER_LABELS[geo],
            color=COLORS[geo], linewidth=lw, marker="o", markersize=3)
ax.axhline(1.0, color="black", linestyle="--", linewidth=0.6)
ax.set_title("IT Wage Premium — IT Sector vs Whole-Economy Average (CEE comparison)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Multiple of national average")
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1fx"))
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/04c_wage_premium_cee.png", dpi=150); plt.close()
print("  saved 04c_wage_premium_cee.png")


# ---------------------------------------------------------------------------
# 4. Women in ICT specialist roles — RO vs peers
# ---------------------------------------------------------------------------
print("Fetching women's share among ICT specialists...")
df_w = fetch_eurostat("isoc_sks_itsps", {
    "unit": "PC", "sex": "F",
    "geo":  PEERS + ["EU27_2020"],
})
women = to_year_indexed(df_w).dropna(how="all")
save_csv(women, "04d_women_ict_specialists_pct")

women_plot = women[women.index >= 2005]
fig, ax = plt.subplots(figsize=(13, 5))
for geo in PEERS + ["EU27_2020"]:
    if geo not in women_plot.columns:
        continue
    lw = 2.5 if geo == "RO" else 1.4
    ax.plot(women_plot.index, women_plot[geo], label=PEER_LABELS[geo],
            color=COLORS[geo], linewidth=lw, marker="o", markersize=3)
ax.set_title("Women as % of ICT Specialists",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of ICT specialists")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/04d_women_in_ict.png", dpi=150); plt.close()
print("  saved 04d_women_in_ict.png")


# ---------------------------------------------------------------------------
# 5. Supply vs demand: ICT specialists (RO) vs annual ICT graduates
# ---------------------------------------------------------------------------
print("Building supply-demand chart (RO)...")
df_sp = fetch_eurostat("isoc_sks_itspt", {
    "unit": "THS_PER", "geo": ["RO"],
})
spec_ths = to_year_indexed(df_sp)["RO"].dropna()

df_gr = fetch_eurostat("educ_uoe_grad02", {
    "iscedf13": "F06", "isced11": "ED5-8",
    "sex": "T", "unit": "NR", "geo": ["RO"],
})
grads = to_year_indexed(df_gr)["RO"].dropna() / 1000.0   # to thousands

# Start at 2015: RO ICT-grads 2013-2014 contain only bachelor-level (ED6);
# master-level (ED7) is reported as zero, a Eurostat coverage gap. The
# 5x jump between 2014 and 2015 is an artefact of that gap, not real
# supply growth, so drop those points (same treatment as 01b chart).
grads = grads[grads.index >= 2015]
spec_ths = spec_ths[spec_ths.index >= 2015]

fig, ax = plt.subplots(figsize=(13, 5))
ax2 = ax.twinx()
l1, = ax.plot(spec_ths.index, spec_ths.values,
              color="#c0392b", linewidth=2.5, marker="o", markersize=4,
              label="ICT specialists in employment (thousands, left)")
l2 = ax2.bar(grads.index, grads.values, alpha=0.45, color="#2980b9", width=0.7,
             label="ICT tertiary graduates per year (thousands, right)")
ax.set_title("Romania — ICT Specialists in Employment vs Annual ICT Graduates",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year")
ax.set_ylabel("ICT specialists (thousands)", color="#c0392b")
ax2.set_ylabel("ICT graduates per year (thousands)", color="#2980b9")
ax.tick_params(axis="y", colors="#c0392b")
ax2.tick_params(axis="y", colors="#2980b9")
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
fig.legend(handles=[l1, l2], loc="upper left", bbox_to_anchor=(0.08, 0.95),
           fontsize=9, frameon=True)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/04e_supply_demand_ro.png", dpi=150); plt.close()
print("  saved 04e_supply_demand_ro.png")


print("\nDone — wages & careers charts saved to", OUTPUT)
