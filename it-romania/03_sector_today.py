"""
Sector today — size and shape of Romanian IT.

Brings together the indicators that establish current scale:
  (a) ICT specialists as % of total employment (Eurostat isoc_sks_itspt)
  (b) IT services exports, EUR bn (Eurostat bop_its6_det, SI category)
  (c) Trade balance in IT services (credits vs debits)
  (d) IT services exports as % of total services exports
  (e) Enterprise count in J62 / J63 from Structural Business Statistics
      — note methodology break between legacy (2005-2020) and new (2021+)
      SBS regulations.

Sources: Eurostat isoc_sks_itspt, bop_its6_det, sbs_na_1a_se_r2 (legacy),
sbs_ovw_act (new SBS Regulation 2019/2152).
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
# 1. ICT specialists as % of total employment — Romania vs peers
# ---------------------------------------------------------------------------
print("Fetching ICT specialists share...")
df = fetch_eurostat("isoc_sks_itspt", {
    "unit": "PC_EMP",
    "geo":  PEERS + ["EU27_2020"],
})
spec = to_year_indexed(df).dropna(how="all")
save_csv(spec, "03a_ict_specialists_pct_emp")

spec_plot = spec[spec.index >= 2005]
fig, ax = plt.subplots(figsize=(13, 5))
for geo in PEERS + ["EU27_2020"]:
    if geo not in spec_plot.columns:
        continue
    lw = 2.5 if geo == "RO" else 1.4
    ax.plot(spec_plot.index, spec_plot[geo], label=PEER_LABELS[geo],
            color=COLORS[geo], linewidth=lw, marker="o", markersize=3)
ax.set_title("ICT Specialists as % of Total Employment",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of total employment")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/03a_ict_specialists_share.png", dpi=150); plt.close()
print("  saved 03a_ict_specialists_share.png")


# ---------------------------------------------------------------------------
# 2. IT services exports — Romania, EUR bn
# ---------------------------------------------------------------------------
print("Fetching IT services exports (BoP SI)...")
df_x = fetch_eurostat("bop_its6_det", {
    "bop_item": "SI",
    "stk_flow": "CRE",
    "currency": "MIO_EUR",
    "partner":  "WRL_REST",
    "geo":      PEERS,
})
exports = to_year_indexed(df_x).dropna(how="all") / 1000.0   # to EUR bn
exports.index.name = "year"
save_csv(exports, "03b_telecom_computer_info_exports_eur_bn")

ro = exports["RO"].dropna()
fig, ax = plt.subplots(figsize=(13, 5))
ax.fill_between(ro.index, 0, ro.values, color=COLORS["RO"], alpha=0.15)
ax.plot(ro.index, ro.values, color=COLORS["RO"], linewidth=2.5, marker="o", markersize=4)
for x, y in zip(ro.index[::2], ro.values[::2]):
    ax.text(x, y + 0.3, f"€{y:.1f}bn", ha="center", fontsize=8, color="#444")
ax.set_title("Romania — Telecommunications, Computer & Information Services Exports",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("EUR billion")
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/03b_it_services_exports_romania.png", dpi=150); plt.close()
print("  saved 03b_it_services_exports_romania.png")


# ---------------------------------------------------------------------------
# 3. Trade balance in IT services (credits − debits)
# ---------------------------------------------------------------------------
print("Fetching IT services trade balance...")
df_cr = fetch_eurostat("bop_its6_det", {
    "bop_item": "SI", "stk_flow": "CRE", "currency": "MIO_EUR",
    "partner":  "WRL_REST", "geo": ["RO"],
})
df_db = fetch_eurostat("bop_its6_det", {
    "bop_item": "SI", "stk_flow": "DEB", "currency": "MIO_EUR",
    "partner":  "WRL_REST", "geo": ["RO"],
})
cr = to_year_indexed(df_cr)["RO"].dropna() / 1000.0
db = to_year_indexed(df_db)["RO"].dropna() / 1000.0
bal = pd.DataFrame({"exports": cr, "imports": db})
bal["balance"] = bal["exports"] - bal["imports"]
bal.index.name = "year"
save_csv(bal, "03c_it_services_trade_balance_eur_bn")

fig, ax = plt.subplots(figsize=(13, 5))
ax.bar(bal.index - 0.2, bal["exports"], width=0.4,
       label="Exports", color="#27ae60", alpha=0.8)
ax.bar(bal.index + 0.2, bal["imports"], width=0.4,
       label="Imports", color="#c0392b", alpha=0.8)
ax.plot(bal.index, bal["balance"], color="black",
        linewidth=2, marker="o", markersize=4, label="Net balance")
ax.axhline(0, color="black", linewidth=0.6)
ax.set_title("Romania — Trade Balance in Telecom / Computer / Information Services",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("EUR billion")
ax.legend(fontsize=9); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/03c_it_services_trade_balance.png", dpi=150); plt.close()
print("  saved 03c_it_services_trade_balance.png")


# ---------------------------------------------------------------------------
# 4. IT services exports as % of total services exports
# ---------------------------------------------------------------------------
print("Computing IT share of services exports...")
df_total_serv = fetch_eurostat("bop_its6_det", {
    "bop_item": "S",                # Total services
    "stk_flow": "CRE",
    "currency": "MIO_EUR",
    "partner":  "WRL_REST",
    "geo":      PEERS,
})
total_serv = to_year_indexed(df_total_serv).dropna(how="all") / 1000.0
it_share = (exports / total_serv) * 100
it_share = it_share.dropna(how="all")
it_share.index.name = "year"
save_csv(it_share, "03d_it_share_of_services_exports_pct")

fig, ax = plt.subplots(figsize=(13, 5))
for geo in PEERS:
    if geo not in it_share.columns:
        continue
    lw = 2.5 if geo == "RO" else 1.4
    ax.plot(it_share.index, it_share[geo], label=PEER_LABELS[geo],
            color=COLORS[geo], linewidth=lw, marker="o", markersize=3)
ax.set_title("IT Services as % of Total Services Exports — Romania vs CEE Peers",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of total services exports")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/03d_it_share_services_exports.png", dpi=150); plt.close()
print("  saved 03d_it_share_services_exports.png")


# ---------------------------------------------------------------------------
# 5. Enterprise counts in J62 / J63 — legacy + new SBS spliced
# ---------------------------------------------------------------------------
print("Fetching enterprise counts (SBS)...")

# Legacy SBS 2005-2020 (indic V11110 = number of enterprises)
df_l62 = fetch_eurostat("sbs_na_1a_se_r2",
                       {"geo": ["RO"], "nace_r2": "J62", "indic_sb": "V11110"})
df_l63 = fetch_eurostat("sbs_na_1a_se_r2",
                       {"geo": ["RO"], "nace_r2": "J63", "indic_sb": "V11110"})
legacy_62 = to_year_indexed(df_l62)["RO"].dropna()
legacy_63 = to_year_indexed(df_l63)["RO"].dropna()

# New SBS 2021+ (ENT_NR)
df_n62 = fetch_eurostat("sbs_ovw_act",
                        {"geo": ["RO"], "nace_r2": "J62", "indic_sbs": "ENT_NR"})
df_n63 = fetch_eurostat("sbs_ovw_act",
                        {"geo": ["RO"], "nace_r2": "J63", "indic_sbs": "ENT_NR"})
new_62 = to_year_indexed(df_n62)["RO"].dropna()
new_63 = to_year_indexed(df_n63)["RO"].dropna()

firms = pd.DataFrame({
    "J62_legacy": legacy_62,
    "J62_new":    new_62,
    "J63_legacy": legacy_63,
    "J63_new":    new_63,
})
firms.index.name = "year"
save_csv(firms, "03e_enterprises_j62_j63")

fig, ax = plt.subplots(figsize=(13, 5))
ax.plot(legacy_62.index, legacy_62.values,
        color="#2980b9", linewidth=2.2, marker="o", markersize=3,
        label="J62 — Computer programming & consulting (legacy SBS)")
ax.plot(new_62.index, new_62.values,
        color="#2980b9", linewidth=2.2, marker="s", markersize=4,
        linestyle=":", label="J62 — new SBS (2021+)")
ax.plot(legacy_63.index, legacy_63.values,
        color="#e67e22", linewidth=2.2, marker="o", markersize=3,
        label="J63 — Information services (legacy SBS)")
ax.plot(new_63.index, new_63.values,
        color="#e67e22", linewidth=2.2, marker="s", markersize=4,
        linestyle=":", label="J63 — new SBS (2021+)")
ax.axvspan(2020.5, 2021.5, alpha=0.10, color="#7f8c8d")
ax.text(2021, ax.get_ylim()[1] * 0.05, "SBS methodology\nchange (Reg. 2019/2152)",
        ha="center", fontsize=8, color="#555")
ax.set_title("Romania — Active Enterprises in J62 / J63 (SBS)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Number of enterprises")
ax.legend(fontsize=8, loc="upper left"); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/03e_enterprises.png", dpi=150); plt.close()
print("  saved 03e_enterprises.png")


print("\nDone — sector-today charts saved to", OUTPUT)
