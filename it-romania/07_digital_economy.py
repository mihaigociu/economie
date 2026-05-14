"""
The digital economy paradox.

Romania is a top IT *producer* (Module 3-6) but a digital laggard at home.
This module quantifies the contrast across the four DESI dimensions:
  - Connectivity / internet adoption: RO has converged on EU27
  - Digital skills (population): RO is bottom of EU27
  - Digital integration in business (cloud, etc.): RO bottom half
  - Digital public services (e-gov use): RO at the bottom

Sources: Eurostat
  isoc_ci_ifp_iu     — individuals using internet
  isoc_ci_in_h       — households with internet access
  isoc_sk_dskl_i21   — individuals with basic+ digital skills (2021+)
  isoc_sk_dskl_i     — individuals with basic+ digital skills (pre-2021)
  isoc_cicce_use     — enterprises buying cloud computing services
  isoc_ciegi_ac      — individuals submitting forms online to public auth
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


def plot_lines(data, title, ylabel, filename, ylim=None):
    fig, ax = plt.subplots(figsize=(13, 5))
    for geo in PEERS + ["EU27_2020"]:
        if geo not in data.columns:
            continue
        s = data[geo].dropna()
        if s.empty:
            continue
        lw = 2.5 if geo == "RO" else 1.4
        ax.plot(s.index, s.values, label=PEER_LABELS[geo],
                color=COLORS[geo], linewidth=lw, marker="o", markersize=3)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel(ylabel)
    if ylim:
        ax.set_ylim(*ylim)
    ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/{filename}", dpi=150); plt.close()
    print(f"  saved {filename}")


# ---------------------------------------------------------------------------
# 1. Internet use — individuals (last 3 months)
# ---------------------------------------------------------------------------
print("Fetching individuals using internet...")
df = fetch_eurostat("isoc_ci_ifp_iu", {
    "indic_is": "I_IU3", "ind_type": "IND_TOTAL", "unit": "PC_IND",
    "geo": PEERS + ["EU27_2020"],
})
iuse = to_year_indexed(df).dropna(how="all")
save_csv(iuse, "07a_internet_use_pct_individuals")
plot_lines(iuse,
           "Individuals Using Internet in Last 3 Months",
           "% of population aged 16-74",
           "07a_internet_use.png",
           ylim=(30, 100))


# ---------------------------------------------------------------------------
# 2. Households with internet access
# ---------------------------------------------------------------------------
print("Fetching households with internet access...")
df = fetch_eurostat("isoc_ci_in_h", {
    "unit": "PC_HH", "hhtyp": "TOTAL",
    "geo": PEERS + ["EU27_2020"],
})
hh = to_year_indexed(df).dropna(how="all")
save_csv(hh, "07b_household_internet_access_pct")
plot_lines(hh,
           "Households with Internet Access at Home",
           "% of households",
           "07b_household_internet.png",
           ylim=(40, 100))


# ---------------------------------------------------------------------------
# 3. Basic+ digital skills (population) — splice pre/post-2021 series
# ---------------------------------------------------------------------------
print("Fetching digital skills (basic+)...")
df_new = fetch_eurostat("isoc_sk_dskl_i21", {
    "indic_is": "I_DSK2_BAB", "ind_type": "IND_TOTAL", "unit": "PC_IND",
    "geo": PEERS + ["EU27_2020"],
})
skills_new = to_year_indexed(df_new).dropna(how="all")

df_old = fetch_eurostat("isoc_sk_dskl_i", {
    "indic_is": "I_DSK_BAB", "ind_type": "IND_TOTAL", "unit": "PC_IND",
    "geo": PEERS + ["EU27_2020"],
})
skills_old = to_year_indexed(df_old).dropna(how="all")

save_csv(skills_old, "07c_digital_skills_basic_plus_pre2021")
save_csv(skills_new, "07c_digital_skills_basic_plus_2021plus")

fig, ax = plt.subplots(figsize=(13, 5))
for geo in PEERS + ["EU27_2020"]:
    lw = 2.5 if geo == "RO" else 1.4
    if geo in skills_old.columns:
        s = skills_old[geo].dropna()
        if not s.empty:
            ax.plot(s.index, s.values, color=COLORS[geo],
                    linewidth=lw, marker="o", markersize=3, linestyle="-",
                    label=f"{PEER_LABELS[geo]} (pre-2021 def)")
    if geo in skills_new.columns:
        s = skills_new[geo].dropna()
        if not s.empty:
            ax.plot(s.index, s.values, color=COLORS[geo],
                    linewidth=lw, marker="s", markersize=4, linestyle=":",
                    label=f"{PEER_LABELS[geo]} (2021+ def)")
ax.axvspan(2019.5, 2021.5, color="#bdc3c7", alpha=0.15)
ax.text(2020.5, ax.get_ylim()[1] * 0.06, "Definition\nchange",
        ha="center", fontsize=8, color="#555")
ax.set_title("Individuals with Basic or Above-Basic Digital Skills",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of population aged 16-74")
ax.legend(ncol=3, fontsize=7); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/07c_digital_skills.png", dpi=150); plt.close()
print("  saved 07c_digital_skills.png")


# ---------------------------------------------------------------------------
# 4. Cloud adoption by enterprises (10+ employees)
# ---------------------------------------------------------------------------
print("Fetching enterprise cloud adoption...")
df = fetch_eurostat("isoc_cicce_use", {
    "indic_is": "E_CC", "size_emp": "GE10", "unit": "PC_ENT",
    "geo": PEERS + ["EU27_2020"],
})
# NACE filter is implicit (only one NACE here)
cloud = to_year_indexed(df).dropna(how="all")
save_csv(cloud, "07d_cloud_adoption_enterprises_pct")
plot_lines(cloud,
           "Enterprises (10+ employees) Buying Cloud Computing Services",
           "% of enterprises",
           "07d_cloud_adoption.png")


# ---------------------------------------------------------------------------
# 5. E-government use — individuals submitting forms online
# ---------------------------------------------------------------------------
print("Fetching e-government use...")
df = fetch_eurostat("isoc_ciegi_ac", {
    "indic_is": "I_IGOV12FM", "ind_type": "IND_TOTAL", "unit": "PC_IND",
    "geo": PEERS + ["EU27_2020"],
})
egov = to_year_indexed(df).dropna(how="all")
save_csv(egov, "07e_egov_forms_pct_individuals")
plot_lines(egov,
           "Individuals Submitting Forms Online to Public Authorities (last 12 months)",
           "% of population aged 16-74",
           "07e_egov_use.png")


# ---------------------------------------------------------------------------
# 6. Paradox summary — IT producer rank vs digital skills rank
# ---------------------------------------------------------------------------
print("Building paradox summary chart...")
# Latest year for each indicator, RO and peers
def latest_value(df, geo):
    if geo not in df.columns:
        return None
    s = df[geo].dropna()
    return s.iloc[-1] if not s.empty else None

# We re-use already-fetched ICT-related series via the earlier modules where
# possible. For this summary we recompute from Eurostat to keep this script
# self-contained.

# ICT specialists share of employment (latest)
df_sp = fetch_eurostat("isoc_sks_itspt",
                       {"unit": "PC_EMP", "geo": PEERS + ["EU27_2020"]})
spec_share = to_year_indexed(df_sp).dropna(how="all")

# IT services share of services exports (latest) — recompute briefly
df_si = fetch_eurostat("bop_its6_det", {
    "bop_item": "SI", "stk_flow": "CRE", "currency": "MIO_EUR",
    "partner": "WRL_REST", "geo": PEERS,
})
df_st = fetch_eurostat("bop_its6_det", {
    "bop_item": "S", "stk_flow": "CRE", "currency": "MIO_EUR",
    "partner": "WRL_REST", "geo": PEERS,
})
si = to_year_indexed(df_si); st = to_year_indexed(df_st)
it_share = (si / st * 100).dropna(how="all")

# Latest "production" indicators
production = pd.DataFrame({
    "ICT specialists\n% employment":       {g: latest_value(spec_share,  g) for g in PEERS},
    "IT services\n% services exports":     {g: latest_value(it_share,    g) for g in PEERS},
})

# Latest "consumption / readiness" indicators
consumption = pd.DataFrame({
    "Basic+ digital\nskills % of pop":    {g: latest_value(skills_new,  g) for g in PEERS},
    "Cloud adoption\n% of enterprises":    {g: latest_value(cloud,       g) for g in PEERS},
    "E-gov forms\n% of population":        {g: latest_value(egov,        g) for g in PEERS},
})

fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

prod = production.loc[PEERS]
prod.plot(kind="bar", ax=axes[0],
          color=["#c0392b", "#27ae60"], width=0.7, edgecolor="white")
axes[0].set_title("IT Production indicators (latest year)",
                  fontsize=12, fontweight="bold")
axes[0].set_xlabel(""); axes[0].set_ylabel("%")
axes[0].set_xticklabels([PEER_LABELS[g] for g in PEERS], rotation=0, fontsize=9)
axes[0].legend(fontsize=8); axes[0].grid(axis="y", alpha=0.3)

cons = consumption.loc[PEERS]
cons.plot(kind="bar", ax=axes[1],
          color=["#2980b9", "#8e44ad", "#e67e22"], width=0.7, edgecolor="white")
axes[1].set_title("Digital Adoption indicators (latest year)",
                  fontsize=12, fontweight="bold")
axes[1].set_xlabel(""); axes[1].set_ylabel("%")
axes[1].set_xticklabels([PEER_LABELS[g] for g in PEERS], rotation=0, fontsize=9)
axes[1].legend(fontsize=8); axes[1].grid(axis="y", alpha=0.3)

fig.suptitle("The Romanian Digital Paradox — Top on production, bottom on adoption",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/07f_paradox_summary.png", dpi=150, bbox_inches="tight")
plt.close()
print("  saved 07f_paradox_summary.png")
save_csv(production.loc[PEERS], "07f_production_indicators_latest")
save_csv(consumption.loc[PEERS], "07f_adoption_indicators_latest")


print("\nDone — digital-economy charts saved to", OUTPUT)
