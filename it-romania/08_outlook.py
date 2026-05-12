"""
Module 8 — Outlook: what could derail or accelerate the next decade.

Five forward-looking lenses, all anchored to public Eurostat data plus one
illustrative scenarios chart (clearly labelled as such).

  08a  Working-age population (15-64) projection — Eurostat proj_23np, baseline
       Romania's labour base shrinks faster than CEE peers; the pool from which
       future ICT specialists are recruited is contracting.

  08b  Young-adult (20-29) population projection — same dataset, narrower age
       band, the cohort feeding fresh CS graduates into the sector.

  08c  Job vacancy rate in NACE J (information & communication) — quarterly
       Eurostat jvs_q_nace2. Romania's JVR fell from 1.1% in 2023-Q1 to 0.7%
       by 2025 — visible demand cooling after the IT tax-exemption phase-out.

  08d  Compensation per employee in J62_J63 — RO vs CEE peers vs Western Europe
       Nominal labour cost convergence: RO is no longer the cheapest CEE option.

  08e  ICT specialists share gap — how much room Romania still has to grow into
       its peer-group average (and to leader benchmarks like Finland, Sweden).

  08f  Illustrative 2030 scenarios for ICT GVA: continuation / stagnation /
       acceleration. Past data is real; futures are thumbnail trajectories,
       not forecasts, and are labelled as such on the chart.

Sources:
  proj_23np         population projection (baseline)
  jvs_q_nace2       quarterly job vacancy rate by NACE
  nama_10_a64       gross value added by activity (B1G, CP_MEUR)
  nama_10_a64_e     employment by activity (D1, SAL_DC, THS_PER)
  isoc_sks_itspt    ICT specialists share of total employment
"""

import warnings
warnings.filterwarnings("ignore")

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import eurostat

OUTPUT   = "charts"
RAW_DATA = "raw-data"
os.makedirs(OUTPUT, exist_ok=True)
os.makedirs(RAW_DATA, exist_ok=True)

PEERS = ["RO", "PL", "CZ", "HU", "BG"]
PEER_LABELS = {"RO": "Romania", "PL": "Poland", "CZ": "Czechia",
               "HU": "Hungary", "BG": "Bulgaria", "EU27_2020": "EU27",
               "DE": "Germany", "FR": "France", "FI": "Finland", "SE": "Sweden"}
COLORS = {"RO": "#c0392b", "PL": "#2980b9", "CZ": "#27ae60",
          "HU": "#8e44ad", "BG": "#e67e22", "EU27_2020": "#7f8c8d",
          "DE": "#34495e", "FR": "#16a085", "FI": "#d35400", "SE": "#9b59b6"}


def save_csv(df, name):
    df.to_csv(f"{RAW_DATA}/{name}.csv")
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


def plot_peer_lines(data, title, ylabel, filename, geos=None,
                    ylim=None, vlines=None, annotations=None):
    geos = geos or (PEERS + ["EU27_2020"])
    fig, ax = plt.subplots(figsize=(13, 5))
    for geo in geos:
        if geo not in data.columns:
            continue
        s = data[geo].dropna()
        if s.empty:
            continue
        lw = 2.6 if geo == "RO" else 1.4
        ax.plot(s.index, s.values, label=PEER_LABELS.get(geo, geo),
                color=COLORS.get(geo, "#444"), linewidth=lw,
                marker="o", markersize=3)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel(ylabel)
    if ylim:
        ax.set_ylim(*ylim)
    if vlines:
        for x, lab in vlines:
            ax.axvline(x, color="#555", linestyle="--", linewidth=0.8)
            ax.text(x, ax.get_ylim()[1] * 0.95, lab,
                    rotation=90, va="top", ha="right", fontsize=8, color="#555")
    if annotations:
        for x, y, t in annotations:
            ax.annotate(t, xy=(x, y), fontsize=8, color="#333",
                        xytext=(5, 5), textcoords="offset points")
    ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/{filename}", dpi=150); plt.close()
    print(f"  saved {filename}")


# ---------------------------------------------------------------------------
# 08a — Working-age population projection (15-64), baseline scenario
# ---------------------------------------------------------------------------
print("Fetching population projection (15-64)...")
df = fetch_eurostat("proj_23np", {
    "projection": "BSL", "sex": "T", "age": "Y15-64", "unit": "PER",
    "geo": PEERS + ["EU27_2020"],
})
wap = to_year_indexed(df).dropna(how="all")
wap_pct = wap.div(wap.iloc[0]) * 100   # index, 2022=100
save_csv(wap, "08a_working_age_pop_projection_persons")
save_csv(wap_pct, "08a_working_age_pop_projection_index2022")
plot_peer_lines(wap_pct,
                "Working-Age Population (15–64) — Baseline Projection, 2022 = 100",
                "Index (2022 = 100)",
                "08a_working_age_population.png")


# ---------------------------------------------------------------------------
# 08b — Young-adult population (20-29) — cohort feeding fresh CS graduates
# ---------------------------------------------------------------------------
# proj_23np exposes single-year ages; sum Y20..Y29 ourselves.
print("Fetching young-adult population projection (20-29)...")
df = fetch_eurostat("proj_23np", {
    "projection": "BSL", "sex": "T",
    "age": [f"Y{a}" for a in range(20, 30)],
    "unit": "PER", "geo": PEERS + ["EU27_2020"],
})
yrs = [c for c in df.columns if str(c).isdigit()]
ya = df.groupby("geo")[yrs].sum().astype(float)
ya.columns = ya.columns.astype(int)
ya = ya.T.sort_index()
ya.index.name = "year"
ya_pct = ya.div(ya.iloc[0]) * 100
save_csv(ya, "08b_young_adult_pop_projection_persons")
save_csv(ya_pct, "08b_young_adult_pop_projection_index2022")
plot_peer_lines(ya_pct,
                "Young-Adult Population (20–29) — Baseline Projection, 2022 = 100",
                "Index (2022 = 100)",
                "08b_young_adult_population.png")


# ---------------------------------------------------------------------------
# 08c — Job vacancy rate in NACE J (information & communication)
# ---------------------------------------------------------------------------
print("Fetching job vacancy rate in NACE J...")
df = fetch_eurostat("jvs_q_nace2", {
    "indic_em": "JVR", "sizeclas": "TOTAL", "s_adj": "NSA", "nace_r2": "J",
    "geo": PEERS + ["EU27_2020"],
})
qcols = [c for c in df.columns if "-Q" in str(c)]
jvr = df.set_index("geo")[qcols].astype(float)
# Convert quarter strings to fractional years
def q_to_year(q):
    y, qn = q.split("-Q")
    return int(y) + (int(qn) - 1) / 4.0
jvr.columns = [q_to_year(c) for c in jvr.columns]
jvr = jvr.T.sort_index().dropna(how="all")
save_csv(jvr, "08c_job_vacancy_rate_nace_j_quarterly")

fig, ax = plt.subplots(figsize=(13, 5))
for geo in PEERS + ["EU27_2020"]:
    if geo not in jvr.columns:
        continue
    s = jvr[geo].dropna()
    if s.empty:
        continue
    lw = 2.6 if geo == "RO" else 1.4
    ax.plot(s.index, s.values, label=PEER_LABELS[geo],
            color=COLORS[geo], linewidth=lw, marker="o", markersize=3)
ax.axvline(2023, color="#555", linestyle="--", linewidth=0.8)
ax.text(2023.05, ax.get_ylim()[1] * 0.95 if ax.get_ylim()[1] else 5,
        "IT income-tax\nexemption capped\n(Nov 2022)",
        fontsize=8, color="#555", va="top")
ax.set_title("Job Vacancy Rate — Information & Communication (NACE J), quarterly",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Vacancies as % of (occupied + vacant) posts")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/08c_job_vacancy_rate.png", dpi=150); plt.close()
print("  saved 08c_job_vacancy_rate.png")


# ---------------------------------------------------------------------------
# 08d — Compensation per employee in J62_J63: cost convergence
# ---------------------------------------------------------------------------
print("Fetching ICT compensation per employee (RO vs CEE vs Western EU)...")
geos_all = PEERS + ["EU27_2020", "DE", "FR"]
df_d1 = fetch_eurostat("nama_10_a64", {
    "unit": "CP_MEUR", "na_item": "D1", "nace_r2": "J62_J63",
    "geo": geos_all,
})
df_emp = fetch_eurostat("nama_10_a64_e", {
    "unit": "THS_PER", "na_item": "SAL_DC", "nace_r2": "J62_J63",
    "geo": geos_all,
})
d1  = to_year_indexed(df_d1)
emp = to_year_indexed(df_emp)
# Compensation per employee, EUR thousand per year
cpe = (d1 * 1000) / emp.replace(0, np.nan) / 1000  # MEUR*1000/1000(thousand pers) = thousand EUR
cpe = cpe.dropna(how="all")
save_csv(cpe, "08d_compensation_per_employee_ict_keur")
plot_peer_lines(cpe,
                "Annual Compensation per Employee — Computer Programming & IT Services (NACE J62–63)",
                "EUR thousand per employee per year (nominal)",
                "08d_compensation_per_employee.png",
                geos=geos_all)


# ---------------------------------------------------------------------------
# 08e — ICT specialists share gap: room to grow
# ---------------------------------------------------------------------------
print("Fetching ICT specialists share of employment...")
df = fetch_eurostat("isoc_sks_itspt", {
    "unit": "PC_EMP",
    "geo": PEERS + ["EU27_2020", "FI", "SE"],
})
ict_share = to_year_indexed(df).dropna(how="all")
save_csv(ict_share, "08e_ict_specialists_share_emp")

fig, ax = plt.subplots(figsize=(13, 5))
for geo in PEERS + ["EU27_2020", "FI", "SE"]:
    if geo not in ict_share.columns:
        continue
    s = ict_share[geo].dropna()
    if s.empty:
        continue
    lw = 2.6 if geo == "RO" else 1.4
    ls = "--" if geo in ("FI", "SE") else "-"
    ax.plot(s.index, s.values, label=PEER_LABELS[geo],
            color=COLORS[geo], linewidth=lw, marker="o", markersize=3,
            linestyle=ls)

# Annotate the "headroom" for RO to reach EU leaders
latest_yr = ict_share.dropna(how="all").index.max()
ro_latest = ict_share.loc[latest_yr, "RO"] if "RO" in ict_share.columns else None
fi_latest = ict_share.loc[latest_yr, "FI"] if "FI" in ict_share.columns else None
if ro_latest is not None and fi_latest is not None:
    ax.annotate("",
                xy=(latest_yr, fi_latest), xytext=(latest_yr, ro_latest),
                arrowprops=dict(arrowstyle="<->", color="#555"))
    ax.text(latest_yr + 0.3, (ro_latest + fi_latest) / 2,
            f"Headroom\n{fi_latest - ro_latest:.1f} pp",
            fontsize=8, color="#333", va="center")

ax.set_title("ICT Specialists as % of Total Employment — RO, peers, EU leaders (dashed)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of total employment")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/08e_ict_specialists_headroom.png", dpi=150); plt.close()
print("  saved 08e_ict_specialists_headroom.png")


# ---------------------------------------------------------------------------
# 08f — Illustrative 2030 scenarios for Romanian ICT GVA
# ---------------------------------------------------------------------------
print("Building illustrative 2030 scenarios...")
df_gva = fetch_eurostat("nama_10_a64", {
    "unit": "CP_MEUR", "na_item": "B1G", "nace_r2": "J62_J63", "geo": "RO",
})
ro_gva = to_year_indexed(df_gva)["RO"].dropna() / 1000.0  # to € bn
ro_gva.name = "RO ICT GVA (€bn)"
save_csv(ro_gva.to_frame(), "08f_ro_ict_gva_history_eurbn")

last_year = int(ro_gva.index.max())
last_val  = float(ro_gva.iloc[-1])
# Reference: recent 10y nominal CAGR (printed in console for transparency)
yrs10 = ro_gva.index >= (last_year - 10)
cagr10 = (ro_gva[yrs10].iloc[-1] / ro_gva[yrs10].iloc[0]) ** (1 / (yrs10.sum() - 1)) - 1
print(f"  recent 10y nominal CAGR: {cagr10*100:.1f}%")

# Calibrated thumbnails (NOT extrapolations of recent CAGR — base effects make
# 17% nominal unsustainable from an already-large base). Calibration:
#   stagnation:  1% nominal (real growth ~ -2% offset by inflation, sector contracts)
#   continuation: 9% nominal (~5-7% real + ~2-4% inflation; moderation but expansion)
#   acceleration: 14% nominal (recent pace sustained via AI productivity dividend
#                              + nearshoring + higher-value mix)
RATE_STAG, RATE_CONT, RATE_ACCEL = 0.01, 0.09, 0.14

scen_years = list(range(last_year, 2031))
def project(rate):
    out = []
    v = last_val
    for _ in scen_years:
        out.append(v)
        v *= (1 + rate)
    return out[:len(scen_years)]

cont  = project(RATE_CONT)
stag  = project(RATE_STAG)
accel = project(RATE_ACCEL)

fig, ax = plt.subplots(figsize=(13, 6))
ax.plot(ro_gva.index, ro_gva.values, color="#c0392b", linewidth=2.6,
        marker="o", markersize=3, label="Actual (Eurostat)")
ax.plot(scen_years, cont,  color="#2980b9", linewidth=2.0, linestyle="--",
        marker="^", markersize=4,
        label=f"Continuation ({RATE_CONT*100:.0f}% nominal p.a.)")
ax.plot(scen_years, stag,  color="#7f8c8d", linewidth=2.0, linestyle="--",
        marker="s", markersize=4,
        label=f"Stagnation ({RATE_STAG*100:.0f}% nominal p.a.)")
ax.plot(scen_years, accel, color="#27ae60", linewidth=2.0, linestyle="--",
        marker="v", markersize=4,
        label=f"Acceleration ({RATE_ACCEL*100:.0f}% nominal p.a.)")
ax.set_title(
    "Romanian ICT (J62-63) GVA — actual + illustrative 2030 scenarios\n"
    "Scenarios are calibrated thumbnails for narrative purposes, not forecasts. "
    "Recent 10y CAGR (~17%) excluded as continuation due to base effects.",
    fontsize=11, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Gross value added (EUR bn, nominal)")
ax.axvline(last_year, color="#555", linestyle=":", linewidth=0.8)
ax.text(last_year + 0.15, ax.get_ylim()[1] * 0.05, f"last actual: {last_year}",
        fontsize=8, color="#555")
ax.legend(loc="upper left", fontsize=9); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/08f_scenarios_2030.png", dpi=150); plt.close()
print("  saved 08f_scenarios_2030.png")

# Save scenario table
scen_df = pd.DataFrame({
    "year": scen_years,
    "continuation_eurbn": cont,
    "stagnation_eurbn": stag,
    "acceleration_eurbn": accel,
}).set_index("year")
save_csv(scen_df, "08f_scenarios_2030_eurbn")


print("\nDone — outlook charts saved to", OUTPUT)
