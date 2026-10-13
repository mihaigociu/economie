"""
09 — Supply-Chain Leverage

The second pillar of the thesis: even where China isn't yet innovating
at the frontier, it controls upstream chokepoints that give it leverage
over those who do.

The data (October 2026 edition):
- Rare earths: China ~69% of mining (USGS 2025), ~85% of magnet-REE
  refining (IEA GCMO 2026) — the first decline in refining concentration
- Lithium: mining diversified (Australia 32%, China 21%, Chile 19%,
  Zimbabwe 10%); refining ~74% China
- Cobalt: DRC ~74% and Indonesia ~14% of mining; refining ~76% China
- Solar PV: China 86-96.5% of each manufacturing stage (2024 production)
- Shipbuilding: China ~54% of global deliveries by gross tonnage (2025)
- Critical minerals (refining): gallium 99%, graphite 94%, germanium 94% ...
- Export-control episodes 2010-2026 — leverage deployed (2023-25), then
  partly suspended under the November 2025 US-China truce
- (Pharma API dependency is discussed in the report text only; the
  illustrative API chart was dropped in the October 2026 edition.)

This script only READS data. Every chart's numbers live in a CSV under
raw-data/ with a `# source:` header. See raw-data/SOURCES.md.
"""

import warnings
warnings.filterwarnings("ignore")

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D

OUTPUT   = "charts"
RAW_DATA = "raw-data"
os.makedirs(OUTPUT, exist_ok=True)

COLOR_CN     = "#c0392b"
COLOR_US     = "#2980b9"
COLOR_EU     = "#7f8c8d"
COLOR_JP     = "#8e44ad"
COLOR_KR     = "#e67e22"
COLOR_IN     = "#d4ac0d"
COLOR_AU     = "#16a085"
COLOR_OTHER  = "#bdc3c7"

# Reference year and source line for each snapshot chart. Update these
# together with the CSVs (the CSVs themselves have no year column).
SNAPSHOT = {
    "09a": ("2025", "USGS Mineral Commodity Summaries 2026 (mining, all REEs); "
                    "IEA Global Critical Minerals Outlook 2026 (refining, magnet REEs)"),
    "09b": ("2025", "USGS Mineral Commodity Summaries 2026 (mining); "
                    "IEA Global Critical Minerals Outlook 2026 (refining)"),
    "09c": ("2024", "IEA PVPS Task 1 industry snapshot (Nov 2025), production shares"),
    "09g": ("2025", "IEA Global Critical Minerals Outlook 2026; USGS MCS 2026 (magnesium)"),
}

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def load(name, **kwargs):
    return pd.read_csv(f"{RAW_DATA}/{name}.csv", comment="#", **kwargs)


def pct(v):
    """Format a share for a bar label (integers without decimals)."""
    return f"{v:.0f}%" if float(v).is_integer() else f"{v:.1f}%"


# ---------------------------------------------------------------------------
# 9a. Rare earths — mining vs refining shares
# ---------------------------------------------------------------------------
print("Rare earths — mining and refining shares...")
re_ = load("09a_rare_earth_mining_refining_pct").set_index("country")
re_ = re_.sort_values("mining", ascending=True)
yr, src = SNAPSHOT["09a"]

color_map = {"China": COLOR_CN, "United States": COLOR_US,
             "Australia": COLOR_AU, "Myanmar": "#8e44ad",
             "Vietnam": "#16a085", "Estonia": "#7f8c8d",
             "Malaysia": "#e67e22"}
bar_colors = [color_map.get(c, COLOR_OTHER) for c in re_.index]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
y_pos = range(len(re_))
for ax, col, xmax, xlabel, title in [
        (ax1, "mining", re_["mining"].max() * 1.18,
         "% of global mine production (all rare earths, REO)",
         "Rare-earth mining — geographically diversifying"),
        (ax2, "refining", 100,
         "% of global refining / separation (magnet rare earths)",
         "Rare-earth refining — the real chokepoint")]:
    ax.barh(y_pos, re_[col].fillna(0), color=bar_colors, edgecolor="white")
    ax.set_yticks(y_pos); ax.set_yticklabels(re_.index)
    for i, v in enumerate(re_[col]):
        if pd.isna(v):
            ax.text(1, i, "not broken out (in Other)", va="center",
                    fontsize=8.5, color="#888", style="italic")
        elif v >= 0.5:
            ax.text(v + xmax * 0.012, i, pct(v), va="center", fontsize=10,
                    color="#222", fontweight="bold")
    ax.set_xlim(0, xmax)
    ax.set_xlabel(xlabel)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)

plt.suptitle(f"Rare Earths — Mining (left) vs Refining (right), Share by Country, {yr}",
             fontsize=13, fontweight="bold", y=1.02)
fig.text(0.5, -0.02, f"Source: {src}. See raw-data/09a_*.csv for URLs.",
         ha="center", fontsize=9, color="#555")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/09a_rare_earths_mining_refining.png", dpi=150,
            bbox_inches="tight")
plt.close()
print("  saved 09a_rare_earths_mining_refining.png")


# ---------------------------------------------------------------------------
# 9b. Lithium & Cobalt — mining vs refining
# ---------------------------------------------------------------------------
print("Lithium & cobalt — mining vs refining...")
lc = load("09b_lithium_cobalt_mining_vs_refining_pct")
yr, src = SNAPSHOT["09b"]
lc_colors = {"China": COLOR_CN, "Australia": COLOR_AU, "DR Congo": "#16a085",
             "Chile": "#e67e22", "Indonesia": "#8e44ad", "Zimbabwe": "#d4ac0d",
             "Argentina": "#5dade2", "Japan": COLOR_JP}

fig, axes = plt.subplots(2, 2, figsize=(14, 8))
for row_idx, mineral in enumerate(["Lithium", "Cobalt"]):
    for col_idx, stage in enumerate(["Mining", "Refining"]):
        ax = axes[row_idx, col_idx]
        df = (lc[(lc["mineral"] == mineral) & (lc["stage"] == stage)]
              .sort_values("share", ascending=True))
        y_pos = range(len(df))
        ax.barh(y_pos, df["share"],
                color=[lc_colors.get(c, COLOR_OTHER) for c in df["country"]],
                edgecolor="white")
        ax.set_yticks(y_pos); ax.set_yticklabels(df["country"])
        for i, v in enumerate(df["share"]):
            ax.text(v + 1, i, pct(v), va="center", fontsize=10,
                    color="#222", fontweight="bold")
        ax.set_xlim(0, max(85, lc["share"].max() * 1.12))
        ax.set_xlabel(f"% of global {stage.lower()}")
        ax.set_title(f"{mineral} — {stage}", fontsize=12, fontweight="bold")
        ax.grid(axis="x", alpha=0.3)

plt.suptitle(f"Lithium and Cobalt — Mining (diversified) vs Refining (China-led), {yr}",
             fontsize=13, fontweight="bold", y=1.00)
fig.text(0.5, -0.01, f"Source: {src}. See raw-data/09b_*.csv for URLs.",
         ha="center", fontsize=9, color="#555")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/09b_lithium_cobalt_chain.png", dpi=150,
            bbox_inches="tight")
plt.close()
print("  saved 09b_lithium_cobalt_chain.png")


# ---------------------------------------------------------------------------
# 9c. Solar PV value chain — China share at each stage
# ---------------------------------------------------------------------------
print("Solar PV value chain by stage...")
solar = load("09c_solar_pv_value_chain_pct")
yr, src = SNAPSHOT["09c"]

fig, ax = plt.subplots(figsize=(13, 5.0))
y_pos = range(len(solar))
ax.barh(y_pos, solar["china_share"], color=COLOR_CN, alpha=0.85,
        edgecolor="white", label="China")
ax.barh(y_pos, solar["rest_of_world"], left=solar["china_share"],
        color=COLOR_OTHER, edgecolor="white", label="Rest of world")
ax.set_yticks(y_pos); ax.set_yticklabels(solar["stage"])
for i, v in enumerate(solar["china_share"]):
    ax.text(v / 2, i, f"{pct(v)}\nChina", ha="center", va="center",
            fontsize=12, color="white", fontweight="bold")
ax.set_xlim(0, 100)
ax.set_xlabel("% of global production at each stage")
ax.set_title(f"Solar PV Manufacturing — China's Share at Each Value-Chain Stage ({yr})",
             fontsize=13, fontweight="bold")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2,
          fontsize=10, framealpha=0.95)
ax.grid(axis="x", alpha=0.3)
lo = solar.loc[solar["china_share"].idxmin()]
hi = solar.loc[solar["china_share"].idxmax()]
fig.text(0.5, -0.06,
         f"Polysilicon -> wafer -> cell -> module. China's share ranges from "
         f"{pct(lo['china_share'])} ({lo['stage'].lower()}) to "
         f"{pct(hi['china_share'])} ({hi['stage'].lower()}). "
         "Module share fell to ~80% in 2025 (IEA PVPS, Apr 2026; India 5%, "
         "Vietnam and US 3% each).\n"
         f"Source: {src}. See raw-data/09c_*.csv for URLs.",
         ha="center", fontsize=9, color="#555")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/09c_solar_pv_chain.png", dpi=150,
            bbox_inches="tight")
plt.close()
print("  saved 09c_solar_pv_chain.png")


# ---------------------------------------------------------------------------
# 9d. Shipbuilding — China's share of global deliveries
# ---------------------------------------------------------------------------
print("Shipbuilding share over time...")
ship = load("09d_shipbuilding_share_pct", index_col="year")
s0, s1 = ship.index.min(), ship.index.max()

fig, ax = plt.subplots(figsize=(13, 5.5))
cols = ["China", "South Korea", "Japan", "Other"]
colors = [COLOR_CN, COLOR_KR, COLOR_JP, COLOR_OTHER]
ax.stackplot(ship.index, *[ship[c] for c in cols],
             labels=cols, colors=colors, alpha=0.88,
             edgecolor="white", linewidth=0.8)
for yr_lab, x in [(s0, s0 + 1.8), (2010, 2010), (s1, s1 - 1.8)]:
    if yr_lab not in ship.index:
        continue
    cn = ship.loc[yr_lab, "China"]
    ax.text(x, max(cn / 2, 4.5), f"{pct(cn)}\nChina ({yr_lab})",
            ha="center", va="center", fontsize=10.5, color="white",
            fontweight="bold")
ax.set_title(f"Global Shipbuilding — Share of Deliveries by Country, {s0}–{s1}",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year")
ax.set_ylabel("% of global deliveries (gross tonnage)")
ax.set_ylim(0, 100); ax.set_xlim(s0, s1)
ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=10,
          framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
peak_yr = ship["China"].idxmax()
ax.annotate(
    f"China's share rose from ~{ship.loc[s0, 'China']:.0f}% in {s0} to "
    f"{ship.loc[s1, 'China']:.1f}% in {s1}\n"
    f"(peak {ship.loc[peak_yr, 'China']:.1f}% in {peak_yr}) — overtaking "
    "South Korea around 2009.\n"
    "Order share is higher still: ~72% of new orders (CGT) in H1 2026.\n\n"
    "Source: UNCTADstat ships built by country (Clarksons data), GT, 2014+;\n"
    "2000–2010 from earlier compilation. See raw-data/09d_*.csv.",
    xy=(0.02, 0.97), xycoords="axes fraction",
    fontsize=9, color="white", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#2c3e50",
              edgecolor="white", linewidth=0.8, alpha=0.85))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/09d_shipbuilding_share.png", dpi=150); plt.close()
print("  saved 09d_shipbuilding_share.png")


# ---------------------------------------------------------------------------
# 9f. Chinese export-control timeline
# ---------------------------------------------------------------------------
print("Chinese export-control timeline...")
controls = load("09f_china_export_controls_timeline").sort_values(
    ["year", "month"]).reset_index(drop=True)
# Mid-month position so Dec events stay inside their own year
controls["fyear"] = controls["year"] + (controls["month"] - 0.5) / 12
# Events whose measures were suspended under the Nov 2025 truce
# (to 10 / 27 Nov 2026 per MOFCOM Ann. 70 / 72) — see 09f CSV notes.
SUSPENDED = {(2024, 12), (2025, 10)}
controls["suspended"] = [(y, m) in SUSPENDED
                         for y, m in zip(controls["year"], controls["month"])]
t0 = int(controls["year"].min()) - 1
t1 = int(controls["year"].max()) + 1
SPLIT = 2020  # events after this year get their label on the left

n = len(controls)
fig, ax = plt.subplots(figsize=(14, 0.45 * n + 2.2))
for i, row in controls.iterrows():
    face = "white" if row["suspended"] else COLOR_CN
    ax.scatter(row["fyear"], i, s=150, zorder=3, facecolor=face,
               edgecolor=COLOR_CN, linewidth=2)
    date = f"{MONTHS[int(row['month']) - 1]} {int(row['year'])}"
    event = str(row["event"])
    if event.startswith(str(int(row["year"])) + " "):
        event = event.split(" ", 1)[1]
    if row["fyear"] < SPLIT:
        ax.text(row["fyear"] + 0.25, i, f"{date}  {event}",
                va="center", ha="left", fontsize=9.5, color="#222")
    else:
        ax.text(row["fyear"] - 0.25, i, f"{event}  {date}",
                va="center", ha="right", fontsize=9.5, color="#222")
ax.set_xlim(t0, t1)
ax.set_ylim(n - 0.4, -0.6)
ax.set_yticks([])
ax.set_xlabel("Year")
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
ax.set_title("Chinese Export Controls / Embargoes on Critical Minerals & Materials, "
             f"{int(controls['year'].min())}–{int(controls['year'].max())}",
             fontsize=13, fontweight="bold")
for spine in ("top", "right", "left"):
    ax.spines[spine].set_visible(False)
ax.grid(axis="x", alpha=0.3)
ax.legend(handles=[
    Line2D([], [], marker="o", ls="", markersize=10, markerfacecolor=COLOR_CN,
           markeredgecolor=COLOR_CN, label="In force"),
    Line2D([], [], marker="o", ls="", markersize=10, markerfacecolor="white",
           markeredgecolor=COLOR_CN, markeredgewidth=2,
           label="Suspended under Nov 2025 truce (to Nov 2026)")],
    loc="lower left", fontsize=9.5, framealpha=0.95)
ax.annotate(
    "Leverage deployed, then partly traded: the WTO DS431 ruling (2014) made\n"
    "quotas untenable, so 2023-25 controls use licensing. The October 2025\n"
    "package and the US-specific Ga/Ge/Sb ban were suspended after the\n"
    "Busan Trump-Xi meeting; the April 2025 rare-earth licensing stays.\n\n"
    "Source: MOFCOM announcements; WTO DS431; law-firm and Reuters summaries.\n"
    "See raw-data/09f_*.csv for URLs.",
    xy=(0.99, 0.99), xycoords="axes fraction",
    fontsize=8.5, color="#222", va="top", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#fdf2ee",
              edgecolor=COLOR_CN, linewidth=1.0))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/09f_export_controls_timeline.png", dpi=150); plt.close()
print("  saved 09f_export_controls_timeline.png")


# ---------------------------------------------------------------------------
# 9g. Critical minerals overview — China's refining share by mineral
# ---------------------------------------------------------------------------
print("Critical minerals — China's refining share...")
cm = load("09g_critical_minerals_china_share_pct").sort_values("china_share")
yr, src = SNAPSHOT["09g"]

fig, ax = plt.subplots(figsize=(13, 6.5))
y_pos = range(len(cm))
bar_colors = [COLOR_CN if v >= 50 else COLOR_OTHER for v in cm["china_share"]]
ax.barh(y_pos, cm["china_share"], color=bar_colors, alpha=0.85,
        edgecolor="white")
ax.set_yticks(y_pos); ax.set_yticklabels(cm["mineral"])
for i, v in enumerate(cm["china_share"]):
    ax.text(v + 1, i, pct(v), va="center", fontsize=10,
            color="#222", fontweight="bold")
ax.axvline(50, color="#888", linestyle="--", linewidth=1)
ax.text(50.5, -0.45, "50% line", fontsize=8, color="#666")
ax.set_xlim(0, 105)
ax.set_xlabel("China's share of global refining / processing (%)")
ax.set_title(f"China's Share of Global Critical-Mineral Refining — {yr}",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)


def short(names):
    return ", ".join(n.split(" (")[0].lower() for n in names)


hi_ = cm[cm["china_share"] >= 80]["mineral"][::-1]
mid = cm[(cm["china_share"] >= 50) & (cm["china_share"] < 80)]["mineral"][::-1]
low = cm[cm["china_share"] < 50]
note = ("Refining concentration is the leverage point, not mining.  "
        f">=80%: {short(hi_)}.  50-80%: {short(mid)}.\n"
        "Below 50%: " + "; ".join(f"{r.mineral.split(' (')[0].lower()} "
                                  f"{pct(r.china_share)}"
                                  + (" (Indonesia is the top refiner, ~45%)"
                                     if r.mineral.startswith("Nickel") else "")
                                  for r in low.itertuples())
        + ".  "
        f"Source: {src}. See raw-data/09g_*.csv for URLs.")
fig.text(0.5, -0.04, note, ha="center", fontsize=9, color="#555")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/09g_critical_minerals_overview.png", dpi=150,
            bbox_inches="tight")
plt.close()
print("  saved 09g_critical_minerals_overview.png")


print("\nDone — supply-chain charts saved to", OUTPUT)
