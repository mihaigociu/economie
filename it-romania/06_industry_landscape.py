"""
Industry landscape — what kind of sector is this?

Reads the industry laterally: how mature is it, how much R&D and IP comes
out of it, and how does it compare in this regard to CEE peers.

The Romanian IT story is famously services-heavy. This module quantifies
that — large by employment and exports, but modest by R&D intensity and
patent output, suggesting the value-creation is largely engineering hours
shipped abroad rather than IP retained at home.

Sources: Eurostat rd_e_berdindr2 (business R&D by NACE), pat_ep_ntot
(EPO patent applications, all fields), pat_ep_ntec (high-tech patent
applications by IPC subset).
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
# 1. Business R&D in ICT (NACE J) — Romania trajectory
# ---------------------------------------------------------------------------
print("Fetching business R&D in NACE J (RO)...")
df = fetch_eurostat("rd_e_berdindr2", {
    "nace_r2": ["J", "J62", "TOTAL"],
    "unit":    "MIO_EUR",
    "geo":     ["RO"],
})

def col_for(nace):
    sub = df[df["nace_r2"] == nace]
    if sub.empty:
        return pd.Series(dtype=float)
    yrs = [c for c in df.columns if str(c).isdigit()]
    s = sub[yrs].iloc[0].astype(float)
    s.index = s.index.astype(int)
    return s

berd_j     = col_for("J")
berd_j62   = col_for("J62")
berd_total = col_for("TOTAL")

ro_berd = pd.DataFrame({
    "j_meur":   berd_j,
    "j62_meur": berd_j62,
    "total_meur": berd_total,
}).dropna(how="all")
ro_berd.index.name = "year"
save_csv(ro_berd, "06a_business_rd_ro_meur")

fig, ax = plt.subplots(figsize=(13, 5))
ax.plot(berd_total.index, berd_total.values, color="#7f8c8d",
        linewidth=2, marker="o", markersize=3, label="Total business R&D")
ax.plot(berd_j.index, berd_j.values, color="#c0392b",
        linewidth=2.5, marker="o", markersize=4,
        label="Information & communication (NACE J)")
ax.plot(berd_j62.index, berd_j62.values, color="#27ae60",
        linewidth=2.5, marker="o", markersize=4,
        label="Computer programming & consulting (J62)")
ax.set_title("Romania — Business Expenditure on R&D, by NACE",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("EUR million")
ax.legend(fontsize=9); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/06a_ro_business_rd.png", dpi=150); plt.close()
print("  saved 06a_ro_business_rd.png")


# ---------------------------------------------------------------------------
# 2. ICT (NACE J) share of business R&D — RO vs peers
# ---------------------------------------------------------------------------
print("Fetching ICT share of business R&D for peers...")
df_j = fetch_eurostat("rd_e_berdindr2",
                      {"nace_r2": "J", "unit": "MIO_EUR", "geo": PEERS + ["EU27_2020"]})
df_t = fetch_eurostat("rd_e_berdindr2",
                      {"nace_r2": "TOTAL", "unit": "MIO_EUR", "geo": PEERS + ["EU27_2020"]})

j_by_geo = to_year_indexed(df_j)
t_by_geo = to_year_indexed(df_t)
share = (j_by_geo / t_by_geo) * 100
share = share.dropna(how="all")
share.index.name = "year"
save_csv(share, "06b_ict_share_of_business_rd_pct")

share_plot = share[share.index >= 2005]
fig, ax = plt.subplots(figsize=(13, 5))
for geo in PEERS + ["EU27_2020"]:
    if geo not in share_plot.columns:
        continue
    lw = 2.5 if geo == "RO" else 1.4
    ax.plot(share_plot.index, share_plot[geo], label=PEER_LABELS[geo],
            color=COLORS[geo], linewidth=lw, marker="o", markersize=3)
ax.set_title("Information & Communication (NACE J) as % of Business R&D",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of business R&D")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/06b_ict_share_of_rd.png", dpi=150); plt.close()
print("  saved 06b_ict_share_of_rd.png")


# ---------------------------------------------------------------------------
# 3. Business R&D as % of sector GVA — intensity ratio for J62_J63
# ---------------------------------------------------------------------------
print("Computing R&D intensity in J62_J63...")
gva_j62_j63 = fetch_eurostat("nama_10_a64",
                             {"nace_r2": "J62_J63", "na_item": "B1G",
                              "unit": "CP_MEUR", "geo": PEERS + ["EU27_2020"]})
gva_idx = to_year_indexed(gva_j62_j63)

# Use J62 berd as numerator (closest match) — by_geo for J62
df_j62 = fetch_eurostat("rd_e_berdindr2",
                        {"nace_r2": "J62", "unit": "MIO_EUR", "geo": PEERS + ["EU27_2020"]})
j62_berd = to_year_indexed(df_j62)
intensity = (j62_berd / gva_idx) * 100
intensity = intensity.dropna(how="all")
intensity.index.name = "year"
save_csv(intensity, "06c_rd_intensity_j62_pct_gva")

intensity_plot = intensity[intensity.index >= 2005]
fig, ax = plt.subplots(figsize=(13, 5))
for geo in PEERS + ["EU27_2020"]:
    if geo not in intensity_plot.columns:
        continue
    lw = 2.5 if geo == "RO" else 1.4
    ax.plot(intensity_plot.index, intensity_plot[geo],
            label=PEER_LABELS[geo],
            color=COLORS[geo], linewidth=lw, marker="o", markersize=3)
ax.set_title("R&D Intensity — J62 Business R&D / J62_J63 GVA",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of sector GVA")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/06c_rd_intensity.png", dpi=150); plt.close()
print("  saved 06c_rd_intensity.png")


# ---------------------------------------------------------------------------
# 4. EPO patent applications — RO vs CEE peers (total, all fields)
# ---------------------------------------------------------------------------
print("Fetching EPO patent applications...")
df_p = fetch_eurostat("pat_ep_ntot",
                     {"unit": "NR", "geo": PEERS + ["EU27_2020"]})
patents = to_year_indexed(df_p).dropna(how="all")
save_csv(patents, "06d_epo_patent_applications")

# Exclude EU27 from this chart — it dwarfs CEE peers
fig, ax = plt.subplots(figsize=(13, 5))
patents_plot = patents[patents.index >= 2000]
for geo in PEERS:
    if geo not in patents_plot.columns:
        continue
    lw = 2.5 if geo == "RO" else 1.4
    ax.plot(patents_plot.index, patents_plot[geo],
            label=PEER_LABELS[geo],
            color=COLORS[geo], linewidth=lw, marker="o", markersize=3)
ax.set_title("EPO Patent Applications — CEE peers, all technology fields",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Number of applications per year")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/06d_epo_patents.png", dpi=150); plt.close()
print("  saved 06d_epo_patents.png")


# ---------------------------------------------------------------------------
# 5. EPO patent applications in computing-related IPC fields (CAB + CTE + SMC)
# ---------------------------------------------------------------------------
print("Fetching EPO patents in computing/communication/semiconductors...")
df_t = fetch_eurostat("pat_ep_ntec",
                      {"unit": "NR", "ipc": ["CAB", "CTE", "SMC"],
                       "geo": PEERS})

def sum_ict(geo):
    sub = df_t[df_t["geo"] == geo]
    yrs = [c for c in df_t.columns if str(c).isdigit()]
    if sub.empty:
        return pd.Series(dtype=float)
    s = sub[yrs].sum(min_count=1).astype(float)
    s.index = s.index.astype(int)
    return s

ict_patents = pd.DataFrame({g: sum_ict(g) for g in PEERS}).dropna(how="all")
ict_patents.index.name = "year"
save_csv(ict_patents, "06e_epo_ict_related_patents")

ip_plot = ict_patents[ict_patents.index >= 2000]
fig, ax = plt.subplots(figsize=(13, 5))
for geo in PEERS:
    if geo not in ip_plot.columns:
        continue
    lw = 2.5 if geo == "RO" else 1.4
    ax.plot(ip_plot.index, ip_plot[geo],
            label=PEER_LABELS[geo],
            color=COLORS[geo], linewidth=lw, marker="o", markersize=3)
ax.set_title("EPO Patent Applications in Computing / Communication / Semiconductors",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Applications per year (CAB+CTE+SMC)")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/06e_epo_ict_patents.png", dpi=150); plt.close()
print("  saved 06e_epo_ict_patents.png")


print("\nDone — industry-landscape charts saved to", OUTPUT)
