"""
08 — Where China Is *Not* Yet Leading: The Honest Counter-Evidence

The credibility chapter. Where the imitation-and-dependency story is still
true. Without this chapter the brief reads as a China-puff piece;
including it makes the "selective leadership" claim precisely *selective*.

The data:
- Advanced semiconductors: China ~1% of <=7nm capacity (TrendForce 2025
  forecast), ~9% at <=16/14nm (2024). EUV lithography is single-source
  (ASML) and not exportable to China. Mature nodes (>=28nm): China ~33%
  (2024), forecast ~45% by 2027.
- Commercial aerospace: Airbus + Boeing delivered ~1,390 jets in 2025;
  COMAC ~15 C919s plus ~25 C909 (ex-ARJ21) regional jets.
- Originator biopharma: 0 of the top-30 drugs by global revenue
  originated from Chinese firms.
- Industrial software / cloud: Synopsys + Cadence + Siemens EDA hold
  ~73% of EDA; AWS + Azure + GCP hold ~63% of global cloud.
- Defense: US has 11 nuclear-powered aircraft carriers; China has 3
  (Fujian commissioned Nov 2025), none nuclear-powered. China's WS-15
  fighter engine was declared production-ready in 2023 — the US F-119
  has been in service since 2005.

This script only READS data. Every chart's numbers live in a CSV under
raw-data/ with a `# source:` / `# url:` / `# retrieved:` header. See
raw-data/SOURCES.md for the project-wide source index.
"""

import warnings
warnings.filterwarnings("ignore")

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

OUTPUT   = "charts"
RAW_DATA = "raw-data"
os.makedirs(OUTPUT, exist_ok=True)

COLOR_CN     = "#c0392b"
COLOR_US     = "#2980b9"
COLOR_EU     = "#7f8c8d"
COLOR_JP     = "#8e44ad"
COLOR_KR     = "#e67e22"
COLOR_TW     = "#16a085"
COLOR_OTHER  = "#bdc3c7"

AIRCRAFT_FILE = "08b_commercial_aircraft_deliveries_2025"


def load(name, **kwargs):
    return pd.read_csv(f"{RAW_DATA}/{name}.csv", comment="#", **kwargs)


def note_box(ax, text, xy, va, ha, face="white", edge="#888", lw=0.8):
    ax.annotate(text, xy=xy, xycoords="axes fraction", fontsize=9,
                color="#222", va=va, ha=ha,
                bbox=dict(boxstyle="round,pad=0.4", facecolor=face,
                          edgecolor=edge, linewidth=lw))


# ---------------------------------------------------------------------------
# 8a. Semiconductor fab capacity — China share at advanced vs mature nodes
# ---------------------------------------------------------------------------
print("Semiconductor fab capacity share by node...")
fab = load("08a_fab_capacity_share_by_node_pct", index_col="node_segment")
mature = load("08a_china_mature_node_share_pct")

cols = ["China (mainland)", "Taiwan", "South Korea",
        "United States", "Japan", "Europe + Other"]
colors = [COLOR_CN, COLOR_TW, COLOR_KR, COLOR_US, COLOR_JP, COLOR_EU]
plot_df = fab[cols].fillna(0)
plot_df["Not allocated by source"] = (100 - plot_df.sum(axis=1)).clip(lower=0)

fig, (ax, ax2) = plt.subplots(1, 2, figsize=(15, 5.8),
                              gridspec_kw={"width_ratios": [2.3, 1]})
plot_df.plot.barh(stacked=True, ax=ax, color=colors + ["#ecf0f1"],
                  width=0.55, edgecolor="white", linewidth=0.6)
ax.invert_yaxis()
ax.set_yticks(range(len(plot_df)))
ax.set_yticklabels([s.replace(" — ", "\n") for s in plot_df.index], fontsize=10)
for i, segment in enumerate(plot_df.index):
    left = 0
    for c in plot_df.columns:
        v = plot_df.loc[segment, c]
        if v >= 6 and c != "China (mainland)":
            ax.text(left + v / 2, i, f"{v:.0f}%", ha="center", va="center",
                    fontsize=10, color="white" if c != "Not allocated by source" else "#555",
                    fontweight="bold")
        left += v
    cn = plot_df.loc[segment, "China (mainland)"]
    ax.annotate(f"China {cn:.0f}%", xy=(cn, i - 0.28), xytext=(cn + 3, i - 0.42),
                fontsize=10, color=COLOR_CN, fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=COLOR_CN, lw=0.8))
ax.set_title("Advanced-node capacity share by fab location",
             fontsize=12, fontweight="bold")
ax.set_xlabel("% of global capacity at that node segment")
ax.set_ylabel("")
ax.set_xlim(0, 100)
ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.12), fontsize=9)
ax.grid(axis="x", alpha=0.3)

# Right panel: China share of mature-node capacity (only China is citable)
x = range(len(mature))
bars = ax2.bar(x, mature["china_share_pct"], color=COLOR_CN, width=0.55,
               edgecolor="white")
for b, status in zip(bars, mature["status"]):
    if status == "forecast":
        b.set_alpha(0.55); b.set_hatch("//")
for i, (v, st) in enumerate(zip(mature["china_share_pct"], mature["status"])):
    ax2.text(i, v + 1.2, f"{v:.0f}%", ha="center", fontsize=12,
             fontweight="bold", color=COLOR_CN)
ax2.set_xticks(list(x))
ax2.set_xticklabels([f"{y}\n({s})" for y, s in zip(mature["year"], mature["status"])])
ax2.set_ylim(0, 60)
ax2.set_ylabel("China share of global capacity, %")
ax2.set_title("China — mature nodes (28nm and above)",
              fontsize=12, fontweight="bold")
ax2.grid(axis="y", alpha=0.3)

fig.suptitle("Semiconductor Fab Capacity — China Marginal at the Leading Edge, "
             "Large and Rising at Mature Nodes", fontsize=13, fontweight="bold")
fig.text(0.5, -0.04,
         "Row definitions differ: <=7nm is TrendForce's 2022 forecast for 2025; <=16/14nm is its 2024 "
         "foundry-capacity estimate (4% not allocated by TrendForce). No free source gives a full country split "
         "at mature nodes, so only China is shown.\nSource: TrendForce (Aug 2022; May 2024). "
         "See raw-data/08a_*.csv for URLs.",
         ha="center", fontsize=8.5, color="#444")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/08a_fab_capacity_by_node.png", dpi=150, bbox_inches="tight")
plt.close()
print("  saved 08a_fab_capacity_by_node.png")


# ---------------------------------------------------------------------------
# 8b. Commercial aircraft deliveries by manufacturer (latest snapshot year)
# ---------------------------------------------------------------------------
print("Commercial aircraft deliveries by manufacturer...")
aircraft = load(AIRCRAFT_FILE)
dcol = [c for c in aircraft.columns if c.startswith("deliveries_")][0]
year = dcol.split("_")[1]
aircraft = aircraft.sort_values(dcol, ascending=True).reset_index(drop=True)

color_map = {"European Union": COLOR_EU, "United States": COLOR_US,
             "Brazil": COLOR_OTHER, "Canada": COLOR_OTHER,
             "France/Italy": COLOR_OTHER, "China": COLOR_CN}
bar_colors = [color_map.get(c, COLOR_OTHER) for c in aircraft["country"]]

fig, ax = plt.subplots(figsize=(13, 5.5))
y_pos = range(len(aircraft))
ax.barh(y_pos, aircraft[dcol], color=bar_colors, edgecolor="white")
ax.set_yticks(y_pos)
labels = [f"{m} ({c})" for m, c in zip(aircraft["manufacturer"], aircraft["country"])]
ax.set_yticklabels(labels)
vmax = aircraft[dcol].max()
for i, v in enumerate(aircraft[dcol]):
    ax.text(v + vmax * 0.01, i, f"{v}", va="center", fontsize=11,
            color="#222", fontweight="bold")
ax.set_xlim(0, vmax * 1.12)
ax.set_xlabel(f"Aircraft deliveries, {year} (units)")
ax.set_title(f"Commercial Aircraft Deliveries — by Manufacturer, {year}",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)


def deliveries(name_part):
    m = aircraft[aircraft["manufacturer"].str.contains(name_part, regex=False)]
    return int(m[dcol].sum())


ab = deliveries("Airbus") + deliveries("Boeing")
c919 = deliveries("C919")
c909 = deliveries("C909")
note_box(ax,
         f"Airbus + Boeing delivered {ab:,} jets in {year}; COMAC delivered\n"
         f"~{c919} C919s (initial target 75) plus ~{c909} C909 (ex-ARJ21)\n"
         "regional jets. The C919 flies on CFM LEAP-1C engines (GE/Safran)\n"
         "with Western avionics; US export licences for those engines were\n"
         "suspended May–Jul 2025. The indigenous CJ-1000A is not yet certified.\n"
         "COMAC figures are trade-press tallies (sources range 13–16 C919s).\n"
         "Bombardier = business jets.\n\n"
         "Source: Airbus, Boeing, Embraer, Bombardier, ATR releases; trade press.\n"
         "See raw-data/08b_*.csv for URLs.",
         xy=(0.98, 0.04), va="bottom", ha="right")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/08b_commercial_aircraft_deliveries.png", dpi=150); plt.close()
print("  saved 08b_commercial_aircraft_deliveries.png")


# ---------------------------------------------------------------------------
# 8c. Top-30 drugs by global revenue, 2023 — originator country breakdown
# ---------------------------------------------------------------------------
print("Top-30 drugs by global revenue — originator country...")
drugs = load("08c_top30_drugs_by_originator_country").sort_values(
    "originators", ascending=True)

color_map = {"United States": COLOR_US, "European Union": COLOR_EU,
             "United Kingdom": "#9b59b6", "Switzerland": "#34495e",
             "Japan": COLOR_JP, "China": COLOR_CN}
bar_colors = [color_map.get(c, COLOR_OTHER) for c in drugs["country"]]

fig, ax = plt.subplots(figsize=(11, 5))
y_pos = range(len(drugs))
ax.barh(y_pos, drugs["originators"], color=bar_colors, edgecolor="white")
ax.set_yticks(y_pos); ax.set_yticklabels(drugs["country"])
for i, v in enumerate(drugs["originators"]):
    ax.text(v + 0.2, i, f"{v}", va="center", fontsize=12,
            color="#222", fontweight="bold")
ax.set_xlim(0, drugs["originators"].max() * 1.2)
ax.set_xlabel("Number of top-30 drugs by 2023 global revenue")
ax.set_title("Top-30 Blockbuster Drugs by 2023 Global Revenue — Originator Country",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
note_box(ax,
         "Zero of the world's top-30 blockbuster drugs in 2023 (Humira,\n"
         "Keytruda, Eliquis, Ozempic, Mounjaro, Stelara, etc.) originated\n"
         "from a Chinese firm. China's pipeline is now licensed out at record\n"
         "scale (~\\$136B of deals in 2025), but those molecules have not\n"
         "yet reached blockbuster revenue.\n\n"
         "Source: Evaluate Pharma 2024 top-30 list; FDA Orange Book; EMA;\n"
         "Caixin (2025 licensing deals). "
         "See raw-data/08c_*.csv for URLs.",
         xy=(0.98, 0.05), va="bottom", ha="right",
         face="#fdf2ee", edge=COLOR_CN, lw=1.0)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/08c_top30_drugs.png", dpi=150); plt.close()
print("  saved 08c_top30_drugs.png")


# ---------------------------------------------------------------------------
# 8d. Industrial software & cloud — market share snapshots
# ---------------------------------------------------------------------------
print("Industrial software & cloud market share...")
eda = load("08d_eda_market_share_pct")
cloud = load("08d_cloud_market_share_pct")

color_map = {"United States": COLOR_US, "European Union": COLOR_EU,
             "China": COLOR_CN, "Mixed": COLOR_OTHER}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.8))

# EDA
eda_sorted = eda.sort_values("share", ascending=True)
y_pos = range(len(eda_sorted))
ax1.barh(y_pos, eda_sorted["share"],
         color=[color_map.get(c, COLOR_OTHER) for c in eda_sorted["country"]],
         edgecolor="white")
ax1.set_yticks(y_pos); ax1.set_yticklabels(eda_sorted["vendor"])
for i, v in enumerate(eda_sorted["share"]):
    ax1.text(v + 0.5, i, f"{v}%", va="center", fontsize=10,
             color="#222", fontweight="bold")
ax1.set_title("Electronic Design Automation (EDA)\nGlobal Market Share, 2024",
              fontsize=12, fontweight="bold")
ax1.set_xlim(0, eda["share"].max() * 1.2)
ax1.grid(axis="x", alpha=0.3)
top3 = eda[eda["vendor"].isin(["Synopsys", "Cadence", "Siemens EDA"])]["share"].sum()
ax1.set_xlabel(f"% of global EDA software market\n"
               f"Synopsys + Cadence + Siemens EDA = {top3:.0f}%. "
               "Synopsys acquired Ansys (Jul 2025).",
               color="#222")

# Cloud
cloud_sorted = cloud.sort_values("share", ascending=True)
y_pos = range(len(cloud_sorted))
ax2.barh(y_pos, cloud_sorted["share"],
         color=[color_map.get(c, COLOR_OTHER) for c in cloud_sorted["country"]],
         edgecolor="white")
ax2.set_yticks(y_pos); ax2.set_yticklabels(cloud_sorted["vendor"])
for i, v in enumerate(cloud_sorted["share"]):
    ax2.text(v + 0.5, i, f"{v}%", va="center", fontsize=10,
             color="#222", fontweight="bold")
big3 = cloud[cloud["vendor"].isin(["AWS", "Microsoft Azure", "Google Cloud"])]["share"].sum()
cn_cloud = cloud[cloud["country"] == "China"]["share"].sum()
ax2.set_xlabel(f"% of global cloud-infrastructure market\n"
               f"AWS + Azure + GCP = {big3:.0f}% (Q2 2026); Chinese clouds ~{cn_cloud:.0f}% "
               "(Q4 2024, latest public)")
ax2.set_title("Cloud-Infrastructure Service Providers\n"
              "Global Market Share — big three Q2 2026, others Q4 2024",
              fontsize=12, fontweight="bold")
ax2.set_xlim(0, cloud["share"].max() * 1.2)
ax2.grid(axis="x", alpha=0.3)

plt.suptitle("Industrial Software & Cloud — Western Vendor Dominance",
             fontsize=14, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/08d_industrial_software_cloud.png", dpi=150,
            bbox_inches="tight")
plt.close()
print("  saved 08d_industrial_software_cloud.png")


# ---------------------------------------------------------------------------
# 8e. Defense — aircraft carriers in commission, by propulsion
# ---------------------------------------------------------------------------
print("Aircraft carriers in commission by country...")
carriers = load("08e_aircraft_carriers_by_country")
if "non_operational" not in carriers.columns:
    carriers["non_operational"] = 0
carriers["total"] = carriers["nuclear"] + carriers["conventional"]
carriers = carriers.sort_values("total", ascending=True).reset_index(drop=True)

fig, ax = plt.subplots(figsize=(13, 5.5))
y_pos = range(len(carriers))
conv_colors = [COLOR_CN if c == "China" else COLOR_OTHER for c in carriers["country"]]
ax.barh(y_pos, carriers["conventional"], color=conv_colors,
        label="Conventional propulsion", edgecolor="white")
ax.barh(y_pos, carriers["nuclear"], left=carriers["conventional"],
        color=COLOR_US, label="Nuclear propulsion",
        edgecolor="white", hatch="//")
# overlay non-operational hulls
nonop = carriers["non_operational"]
if nonop.sum() > 0:
    ax.barh(y_pos, nonop, left=carriers["total"] - nonop, color="white",
            edgecolor="#555", hatch="xx", linewidth=0.8,
            label="In commission but non-operational")
ax.set_yticks(y_pos); ax.set_yticklabels(carriers["country"])
for i, r in carriers.iterrows():
    label = (f"{r.nuclear} nuc + {r.conventional} conv" if r.nuclear > 0
             else f"{r.conventional} conv")
    if r.non_operational > 0:
        label += f"  ({r.non_operational} non-operational)"
    ax.text(r.total + 0.2, i, label, va="center", fontsize=10,
            color="#222", fontweight="bold")
ax.set_xlim(0, carriers["total"].max() + 3)
ax.set_xlabel("Aircraft carriers in commission, October 2026")
ax.set_title("Aircraft Carriers in Commission by Country — Propulsion Breakdown",
             fontsize=13, fontweight="bold")
ax.legend(loc="center right", fontsize=9, framealpha=0.95)
ax.grid(axis="x", alpha=0.3)
cn = carriers[carriers["country"] == "China"].iloc[0]
us = carriers[carriers["country"] == "United States"].iloc[0]
note_box(ax,
         f"US: {us.nuclear} nuclear-powered CATOBAR carriers. China: {cn.total}, all\n"
         "conventional — Liaoning (2012), Shandong (2019) and the CATOBAR\n"
         "Fujian (EM catapults, commissioned Nov 2025). A larger fourth hull\n"
         "(Type 004, nuclear power suspected) is under construction at Dalian.\n"
         "US carrier aviation dates to 1922; the PLAN's to 2012.\n"
         "Russia's Kuznetsov has not been operational since 2017.\n\n"
         "Source: Xinhua/China Daily; USNI News; CSIS; IISS Military Balance.\n"
         "See raw-data/08e_*.csv for URLs.",
         xy=(0.98, 0.03), va="bottom", ha="right")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/08e_aircraft_carriers.png", dpi=150); plt.close()
print("  saved 08e_aircraft_carriers.png")


# ---------------------------------------------------------------------------
# 8f. 5th-generation fighter engine introduction year — the persistent lag
# ---------------------------------------------------------------------------
print("5th-gen fighter engine timeline...")
engines = load("08f_fifth_gen_engine_ioc_year").sort_values("ioc_year").reset_index(drop=True)
baseline = int(engines["ioc_year"].min())
base_engine = engines.loc[engines["ioc_year"].idxmin(), "engine"].split(" ")[0]

color_map = {"United States": COLOR_US, "Russia": "#a93226",
             "China": COLOR_CN}
bar_colors = [color_map.get(c, COLOR_OTHER) for c in engines["country"]]

fig, ax = plt.subplots(figsize=(13, 4.8))
y_pos = range(len(engines))
start = baseline - 10
ax.barh(y_pos, [y - start for y in engines["ioc_year"]], left=start,
        color=bar_colors, edgecolor="white", height=0.55)
ax.set_yticks(y_pos)
labels = [f"{e}\n({c})" for e, c in zip(engines["engine"], engines["country"])]
ax.set_yticklabels(labels, fontsize=10)
for i, (y, c) in enumerate(zip(engines["ioc_year"], engines["country"])):
    gap = y - baseline
    text = f"IOC {y}" if gap == 0 else f"IOC {y} (+{gap} years vs {base_engine})"
    if c == "China":
        text = f"{y}* (+{gap} years vs {base_engine})"
    ax.text(y + 0.5, i, text, va="center", fontsize=10,
            color="#222", fontweight="bold")
ax.set_xlim(start, max(engines["ioc_year"].max() + 12, 2032))
ax.set_xlabel("Year of Initial Operational Capability (IOC)")
ax.set_title("Indigenous 5th-Generation Fighter Engine — Year of Operational Status",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
ax.axvline(baseline, color=COLOR_US, linestyle="--", linewidth=1.2, alpha=0.7)
ax.text(baseline + 0.3, 0.5, f"{base_engine} baseline ({baseline})",
        fontsize=9, color=COLOR_US, fontweight="bold", va="center")
fig.text(0.01, -0.02,
         "* China has never announced a formal WS-15 IOC: 2023 is when AECC declared the engine ready for "
         "mass production; serial J-20As with twin WS-15s were first seen in Dec 2025.\n"
         "On commercial turbofans the gap is larger: the C919 flies on the CFM LEAP-1C and the indigenous "
         "CJ-1000A is not yet certified.\n"
         "Source: USAF / Pratt & Whitney / AECC statements; Janes. See raw-data/08f_*.csv for URLs.",
         ha="left", va="top", fontsize=9, color="#222")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/08f_fighter_engine_timeline.png", dpi=150, bbox_inches="tight"); plt.close()
print("  saved 08f_fighter_engine_timeline.png")


print("\nDone — counter-evidence charts saved to", OUTPUT)
