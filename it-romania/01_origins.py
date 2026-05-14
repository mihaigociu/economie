"""
Origins of Romanian IT (1989-2007): the engineering inheritance, the first
outsourcing wave, the policy choices that mattered.

This module is largely qualitative. We produce:
  (a) An annotated event timeline 1989-2010 — the narrative anchor for the 1990s
  (b) ICT field-of-education graduates (Eurostat educ_uoe_grad02) — the
      pipeline of new engineers feeding the sector. Eurostat coverage starts
      ~2013, so this informs the take-off period rather than the 1990s.
  (c) Tertiary STEM graduates per 1000 working-age population (Eurostat
      educ_uoe_grad04) where available — for international comparison.

Sources: Eurostat (educ_uoe_grad02). Timeline events sourced from publicly-
available records (Monitorul Oficial for legislation, company-history pages,
press releases). Dates marked with ~ are approximate.
"""

import warnings
warnings.filterwarnings("ignore")

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import eurostat

OUTPUT   = "charts"
RAW_DATA = "raw-data"
os.makedirs(OUTPUT, exist_ok=True)
os.makedirs(RAW_DATA, exist_ok=True)

PEERS = ["RO", "PL", "CZ", "HU", "BG", "EU27_2020"]
PEER_LABELS = {"RO": "Romania", "PL": "Poland", "CZ": "Czechia",
               "HU": "Hungary", "BG": "Bulgaria", "EU27_2020": "EU27"}
COLORS = {"RO": "#c0392b", "PL": "#2980b9", "CZ": "#27ae60",
          "HU": "#8e44ad", "BG": "#e67e22", "EU27_2020": "#7f8c8d"}


def save_csv(df, name):
    """Save df to raw-data/{name}.csv, preserving any '#'-prefixed source
    header lines that were already at the top of the file (so the public
    Eurostat-source attribution survives subsequent re-runs)."""
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
    print(f"  saved {path}")


def eurostat_filtered(code, filters):
    """Fetch a Eurostat dataset filtered by dimension values; return long DF."""
    df = eurostat.get_data_df(code, flags=False)
    df = df.rename(columns={"geo\\TIME_PERIOD": "geo"})
    for col, vals in filters.items():
        if isinstance(vals, str):
            vals = [vals]
        df = df[df[col].isin(vals)]
    return df


# ---------------------------------------------------------------------------
# 1. Annotated event timeline 1989-2010
# ---------------------------------------------------------------------------
print("Building origins timeline...")

# (year, short_label, description, category, vertical_slot)
# vertical_slot stacks events that fall close in time so labels don't overlap.
events = [
    (1989, "Romanian Revolution",                          "context", 3),
    (1990, "ICI Bucharest —\nacademic Internet",           "infra",  -1),
    (1992, "First domestic software\nfirms (Softwin etc.)", "biz",    1),
    (1993, ".ro top-level domain\nregistered",             "infra",  -2),
    (1995, "First commercial ISPs",                        "infra",  -1),
    (1998, "First wave of foreign\noutsourcing contracts", "biz",     1),
    (2001, "IT employee income-tax\nexemption introduced", "policy",  2),
    (2003, "Bitdefender brand\nlaunched",                  "biz",     1),
    (2004, "Microsoft R&D centre\nin Bucharest",           "biz",    -1),
    (2005, "UiPath founded\n(as DeskOver)",                "biz",     2),
    (2007, "EU accession\n(1 Jan)",                        "context", 3),
    (2008, "Global financial crisis —\nsector keeps growing", "context", -2),
    (2010, "Cluj / Iași / Timișoara\nrecognisable as hubs", "hub",    1),
]

cat_color = {"context": "#7f8c8d", "policy": "#c0392b", "biz": "#2980b9",
             "infra": "#27ae60", "hub": "#8e44ad"}

fig, ax = plt.subplots(figsize=(16, 7))
ax.axhline(0, color="#bdc3c7", linewidth=2, zorder=0)
for year, desc, cat, slot in events:
    y = slot * 0.9
    color = cat_color[cat]
    ax.scatter(year, 0, s=120, color=color, zorder=3,
               edgecolor="black", linewidth=0.5)
    ax.vlines(year, 0, y, color=color, linewidth=1.0, alpha=0.5, zorder=2)
    va = "bottom" if y > 0 else "top"
    pad = 0.18 if y > 0 else -0.18
    ax.text(year, y + pad, f"{year}\n{desc}",
            ha="center", va=va, fontsize=8.5, color="#222",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=color, linewidth=0.8))

ax.set_xlim(1988, 2011)
ax.set_ylim(-3.5, 4.0)
ax.set_yticks([])
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)
ax.set_title("Romanian IT — From Inheritance to Sector (1989–2010)",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year")
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))

legend_handles = [mpatches.Patch(color=c, label=l.capitalize())
                  for l, c in cat_color.items()]
ax.legend(handles=legend_handles, loc="lower right", fontsize=9, frameon=False)

plt.tight_layout()
plt.savefig(f"{OUTPUT}/01a_origins_timeline.png", dpi=150)
plt.close()
print("  saved 01a_origins_timeline.png")


# ---------------------------------------------------------------------------
# 2. ICT field-of-education graduates (Eurostat educ_uoe_grad02)
# ---------------------------------------------------------------------------
print("Fetching ICT graduates by country...")
try:
    df = eurostat_filtered("educ_uoe_grad02", {
        "iscedf13": "F06",            # ICT field
        "isced11":  "ED5-8",          # Tertiary education (all levels combined)
        "sex":      "T",              # Total
        "unit":     "NR",             # Number of graduates
        "geo":      PEERS,
    })
    year_cols = [c for c in df.columns if str(c).isdigit()]
    grads = df.set_index("geo")[year_cols].astype(float)
    grads.columns = grads.columns.astype(int)
    grads = grads.T.sort_index()
    grads.index.name = "year"
    grads = grads.dropna(how="all")
    save_csv(grads, "01b_ict_graduates_tertiary")

    # Drop EU27 from the country-level chart — it dwarfs CEE peers
    country_peers = [g for g in PEERS if g != "EU27_2020"]
    # RO 2013-2014: ED5-8 contains only ED6 (bachelor); ED7 reported as 0,
    # a Eurostat coverage gap — drop those two points so the chart does not
    # imply a 4x supply jump in 2015. Raw values remain in the CSV.
    grads_plot = grads.copy()
    if "RO" in grads_plot.columns:
        for yr in (2013, 2014):
            if yr in grads_plot.index:
                grads_plot.loc[yr, "RO"] = float("nan")

    fig, ax = plt.subplots(figsize=(12, 5))
    for geo in country_peers:
        if geo not in grads_plot.columns:
            continue
        lw = 2.5 if geo == "RO" else 1.4
        ax.plot(grads_plot.index, grads_plot[geo], label=PEER_LABELS[geo],
                color=COLORS[geo], linewidth=lw, marker="o", markersize=3)
    ax.annotate(
        "RO 2013-2014 omitted: Eurostat ED5-8 total for those\n"
        "years contains only bachelor-level (ED6) graduates;\n"
        "master-level (ED7) reported as zero — coverage gap.",
        xy=(0.02, 0.97), xycoords="axes fraction",
        fontsize=8, color="#555", va="top",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                  edgecolor="#bbb", linewidth=0.6))
    ax.set_title("Tertiary Graduates in ICT (ISCED-F 06, all levels) — CEE peers",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel("Number of graduates per year")
    ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/01b_ict_graduates.png", dpi=150); plt.close()
    print("  saved 01b_ict_graduates.png")
except Exception as e:
    print(f"  ICT graduates skipped: {e}")


# ---------------------------------------------------------------------------
# 3. Engineering, manufacturing & construction graduates (F07) — wider STEM base
# ---------------------------------------------------------------------------
print("Fetching engineering graduates by country...")
try:
    df = eurostat_filtered("educ_uoe_grad02", {
        "iscedf13": "F07",            # Engineering, manufacturing, construction
        "isced11":  "ED5-8",
        "sex":      "T",
        "unit":     "NR",
        "geo":      PEERS,
    })
    year_cols = [c for c in df.columns if str(c).isdigit()]
    eng = df.set_index("geo")[year_cols].astype(float)
    eng.columns = eng.columns.astype(int)
    eng = eng.T.sort_index()
    eng.index.name = "year"
    eng = eng.dropna(how="all")
    save_csv(eng, "01c_engineering_graduates_tertiary")

    country_peers = [g for g in PEERS if g != "EU27_2020"]
    fig, ax = plt.subplots(figsize=(12, 5))
    for geo in country_peers:
        if geo not in eng.columns:
            continue
        lw = 2.5 if geo == "RO" else 1.4
        ax.plot(eng.index, eng[geo], label=PEER_LABELS[geo],
                color=COLORS[geo], linewidth=lw, marker="o", markersize=3)
    ax.set_title("Tertiary Graduates in Engineering, Manufacturing & Construction (ISCED-F 07) — CEE peers",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel("Number of graduates per year")
    ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/01c_engineering_graduates.png", dpi=150); plt.close()
    print("  saved 01c_engineering_graduates.png")
except Exception as e:
    print(f"  engineering graduates skipped: {e}")


# ---------------------------------------------------------------------------
# 4. ICT graduates as % of all tertiary graduates — sector "intensity"
# ---------------------------------------------------------------------------
print("Computing ICT share of total tertiary graduates...")
try:
    df_total = eurostat_filtered("educ_uoe_grad02", {
        "iscedf13": "TOTAL",
        "isced11":  "ED5-8",
        "sex":      "T",
        "unit":     "NR",
        "geo":      PEERS,
    })
    year_cols = [c for c in df_total.columns if str(c).isdigit()]
    total = df_total.set_index("geo")[year_cols].astype(float)
    total.columns = total.columns.astype(int)
    total = total.T.sort_index().dropna(how="all")
    total.index.name = "year"

    # reuse `grads` from step 2 if available
    if "grads" in dir():
        common_yrs = sorted(set(total.index) & set(grads.index))
        common_geos = [g for g in PEERS if g in total.columns and g in grads.columns]
        share = (grads.loc[common_yrs, common_geos] /
                 total.loc[common_yrs, common_geos]) * 100
        share.index.name = "year"
        save_csv(share, "01d_ict_share_of_grads_pct")

        # Pre-2015 is dropped because of the RO ED7 coverage gap propagating
        # into the share denominator. HU 2020 is kept: total-graduate count
        # nearly tripled that year (likely pandemic-era backlog clearance
        # in the Hungarian university system), F06 also spiked ~80%; the
        # resulting share dip is what Eurostat publishes.
        share_plot = share[share.index >= 2015]

        fig, ax = plt.subplots(figsize=(12, 5))
        for geo in PEERS:
            if geo not in share_plot.columns:
                continue
            lw = 2.5 if geo == "RO" else 1.4
            ax.plot(share_plot.index, share_plot[geo], label=PEER_LABELS[geo],
                    color=COLORS[geo], linewidth=lw, marker="o", markersize=3)
        ax.set_title("ICT Graduates as % of All Tertiary Graduates (2015+)",
                     fontsize=13, fontweight="bold")
        ax.set_xlabel("Year"); ax.set_ylabel("% of all tertiary graduates")
        ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
        ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        plt.tight_layout()
        plt.savefig(f"{OUTPUT}/01d_ict_share_of_grads.png", dpi=150); plt.close()
        print("  saved 01d_ict_share_of_grads.png")
except Exception as e:
    print(f"  ICT share skipped: {e}")


print("\nDone — origins charts saved to", OUTPUT)
