"""
08 — Where China Is *Not* Yet Leading: The Honest Counter-Evidence

The credibility chapter. Where the imitation-and-dependency story is still
true. Without this chapter the brief reads as a China-puff piece;
including it makes the "selective leadership" claim precisely *selective*.

The data:
- Advanced semiconductors (≤7nm): SMIC <1% of leading-edge capacity;
  TSMC 90%+. EUV lithography is single-source (ASML), zero China access.
- Commercial aerospace: Airbus + Boeing delivered ~1,260 jets in 2023;
  COMAC delivered ~7 C919s (plus regional ARJ21).
- Originator biopharma: 0 of the top-30 drugs by global revenue
  originated from Chinese firms; ~70% from US originators.
- Industrial software / cloud: Synopsys + Cadence + Siemens EDA hold
  ~73% of EDA; AWS+Azure+GCP hold ~63% of global cloud; Chinese clouds
  marginal abroad.
- Defense: US has 11 nuclear-powered aircraft carriers; China has 3
  carriers, none nuclear-powered. China's 5th-gen-fighter indigenous
  engine (WS-15) reached operational status in 2023 — F-119 has been in
  service since 2005.

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


def load(name, **kwargs):
    return pd.read_csv(f"{RAW_DATA}/{name}.csv", comment="#", **kwargs)


# ---------------------------------------------------------------------------
# 8a. Semiconductor fab capacity — China share at advanced vs mature nodes
# ---------------------------------------------------------------------------
print("Semiconductor fab capacity share by node...")
fab = load("08a_fab_capacity_share_by_node_pct", index_col="node_segment")

fig, ax = plt.subplots(figsize=(13, 5.5))
cols = ["China (mainland)", "Taiwan (TSMC)", "South Korea",
        "United States", "Japan", "Europe + Other"]
colors = [COLOR_CN, COLOR_TW, COLOR_KR, COLOR_US, COLOR_JP, COLOR_OTHER]
fab[cols].plot.barh(stacked=True, ax=ax,
                    color=colors, width=0.55, edgecolor="white", linewidth=0.6)
for i, segment in enumerate(fab.index):
    cn_share = fab.loc[segment, "China (mainland)"]
    ax.text(cn_share / 2, i, f"{cn_share:.0f}%\nChina",
            ha="center", va="center", fontsize=12, color="white",
            fontweight="bold")
ax.set_title("Global Semiconductor Fab Capacity Share — Advanced vs Mature Nodes (2024)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("% of global capacity at that node segment")
ax.set_xlim(0, 100)
ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.10), fontsize=9)
ax.grid(axis="x", alpha=0.3)
ax.annotate(
    "China's share at leading-edge (≤7nm) is <1%; at mature nodes ~32%.\n"
    "EUV lithography (required for ≤7nm at scale) is single-source\n"
    "(ASML, Netherlands) and not exportable to China since 2019.\n\n"
    "Source: TrendForce 2024; SEMI World Fab Forecast.\n"
    "See raw-data/08a_*.csv for URLs.",
    xy=(0.98, 0.95), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/08a_fab_capacity_by_node.png", dpi=150); plt.close()
print("  saved 08a_fab_capacity_by_node.png")


# ---------------------------------------------------------------------------
# 8b. Commercial aircraft deliveries by manufacturer, 2023
# ---------------------------------------------------------------------------
print("Commercial aircraft deliveries by manufacturer...")
aircraft = load("08b_commercial_aircraft_deliveries_2023").sort_values(
    "deliveries_2023", ascending=True)

color_map = {"European Union": COLOR_EU, "United States": COLOR_US,
             "Brazil": COLOR_OTHER, "Canada": COLOR_OTHER,
             "France/Italy": COLOR_OTHER, "China": COLOR_CN}
bar_colors = [color_map[c] for c in aircraft["country"]]

fig, ax = plt.subplots(figsize=(13, 5.5))
y_pos = range(len(aircraft))
ax.barh(y_pos, aircraft["deliveries_2023"], color=bar_colors,
        edgecolor="white")
ax.set_yticks(y_pos)
labels = [f"{m} ({c})" for m, c in zip(aircraft["manufacturer"], aircraft["country"])]
ax.set_yticklabels(labels)
for i, v in enumerate(aircraft["deliveries_2023"]):
    ax.text(v + 8, i, f"{v}", va="center", fontsize=11,
            color="#222", fontweight="bold")
ax.set_xlim(0, 820)
ax.set_xlabel("Commercial aircraft deliveries, 2023 (units)")
ax.set_title("Commercial Aircraft Deliveries — by Manufacturer, 2023",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
ax.annotate(
    "Airbus + Boeing delivered ~1,260 jets in 2023; COMAC delivered 7 C919s\n"
    "(plus ~50 ARJ21 regional jets). And COMAC's C919 uses CFM LEAP engines\n"
    "(GE/Safran), Western avionics (Honeywell, Collins), and ~60% Western\n"
    "content by value — the indigenous CJ-1000A engine remains in testing.\n\n"
    "Source: Airbus, Boeing, COMAC, Embraer, Bombardier, ATR annual reports.\n"
    "See raw-data/08b_*.csv for URLs.",
    xy=(0.98, 0.05), xycoords="axes fraction",
    fontsize=9, color="#222", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
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
bar_colors = [color_map[c] for c in drugs["country"]]

fig, ax = plt.subplots(figsize=(11, 5))
y_pos = range(len(drugs))
ax.barh(y_pos, drugs["originators"], color=bar_colors, edgecolor="white")
ax.set_yticks(y_pos); ax.set_yticklabels(drugs["country"])
for i, v in enumerate(drugs["originators"]):
    ax.text(v + 0.2, i, f"{v}", va="center", fontsize=12,
            color="#222", fontweight="bold")
ax.set_xlim(0, 24)
ax.set_xlabel("Number of top-30 drugs by 2023 global revenue")
ax.set_title("Top-30 Blockbuster Drugs by 2023 Global Revenue — Originator Country",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
ax.annotate(
    "Zero of the world's top-30 blockbuster drugs in 2023 (Humira,\n"
    "Keytruda, Eliquis, Ozempic, Mounjaro, Stelara, etc.) originated\n"
    "from a Chinese firm. China is strong in APIs and generics — see\n"
    "supply-chain chapter §10 — but originator development still\n"
    "concentrates in US, EU, Swiss, UK pharma majors.\n\n"
    "Source: Evaluate Pharma 2024 top-30 list; FDA Orange Book; EMA.\n"
    "See raw-data/08c_*.csv for URLs.",
    xy=(0.98, 0.05), xycoords="axes fraction",
    fontsize=9, color="#222", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#fdf2ee",
              edgecolor=COLOR_CN, linewidth=1.0))
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

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.5))

# EDA
eda_sorted = eda.sort_values("share", ascending=True)
y_pos = range(len(eda_sorted))
ax1.barh(y_pos, eda_sorted["share"],
         color=[color_map[c] for c in eda_sorted["country"]], edgecolor="white")
ax1.set_yticks(y_pos); ax1.set_yticklabels(eda_sorted["vendor"])
for i, v in enumerate(eda_sorted["share"]):
    ax1.text(v + 0.5, i, f"{v}%", va="center", fontsize=10,
             color="#222", fontweight="bold")
ax1.set_xlabel("% of global EDA software market")
ax1.set_title("Electronic Design Automation (EDA)\nGlobal Market Share, 2024",
              fontsize=12, fontweight="bold")
ax1.set_xlim(0, 38)
ax1.grid(axis="x", alpha=0.3)
ax1.text(20, -0.7, "Synopsys + Cadence + Siemens EDA = 73% of global EDA",
         fontsize=9, color=COLOR_CN, style="italic", ha="center")

# Cloud
cloud_sorted = cloud.sort_values("share", ascending=True)
y_pos = range(len(cloud_sorted))
ax2.barh(y_pos, cloud_sorted["share"],
         color=[color_map[c] for c in cloud_sorted["country"]], edgecolor="white")
ax2.set_yticks(y_pos); ax2.set_yticklabels(cloud_sorted["vendor"])
for i, v in enumerate(cloud_sorted["share"]):
    ax2.text(v + 0.5, i, f"{v}%", va="center", fontsize=10,
             color="#222", fontweight="bold")
ax2.set_xlabel("% of global cloud-infrastructure market")
ax2.set_title("Cloud-Infrastructure Service Providers\nGlobal Market Share, Q4 2024",
              fontsize=12, fontweight="bold")
ax2.set_xlim(0, 36)
ax2.grid(axis="x", alpha=0.3)
ax2.text(18, -1.0, "AWS + Azure + GCP = 63% of global cloud; Chinese clouds together ~8%",
         fontsize=9, color=COLOR_CN, style="italic", ha="center")

plt.suptitle("Industrial Software & Cloud — Western Vendor Dominance",
             fontsize=14, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/08d_industrial_software_cloud.png", dpi=150,
            bbox_inches="tight")
plt.close()
print("  saved 08d_industrial_software_cloud.png")


# ---------------------------------------------------------------------------
# 8e. Defense — aircraft carriers, operational status by propulsion
# ---------------------------------------------------------------------------
print("Aircraft carriers operational by country...")
carriers = load("08e_aircraft_carriers_by_country")
carriers["total"] = carriers["nuclear"] + carriers["conventional"]
carriers = carriers.sort_values("total", ascending=True).reset_index(drop=True)

fig, ax = plt.subplots(figsize=(13, 5.5))
y_pos = range(len(carriers))
ax.barh(y_pos, carriers["conventional"], color=COLOR_OTHER,
        label="Conventional propulsion", edgecolor="white")
ax.barh(y_pos, carriers["nuclear"], left=carriers["conventional"],
        color=COLOR_US, label="Nuclear propulsion",
        edgecolor="white", hatch="//")
china_idx = carriers.index[carriers["country"] == "China"][0]
ax.barh(china_idx, carriers.iloc[china_idx]["conventional"],
        color=COLOR_CN, edgecolor="white")
ax.set_yticks(y_pos); ax.set_yticklabels(carriers["country"])
for i, (nuc, conv) in enumerate(zip(carriers["nuclear"], carriers["conventional"])):
    total = nuc + conv
    label = f"{nuc} nuc + {conv} conv" if nuc > 0 else f"{conv} conv"
    ax.text(total + 0.3, i, label, va="center", fontsize=10,
            color="#222", fontweight="bold")
ax.set_xlim(0, 14)
ax.set_xlabel("Aircraft carriers — operational, end-2024")
ax.set_title("Aircraft Carriers Operational by Country — Propulsion Breakdown",
             fontsize=13, fontweight="bold")
ax.legend(loc="lower right", fontsize=10, framealpha=0.95)
ax.grid(axis="x", alpha=0.3)
ax.annotate(
    "US: 11 nuclear-powered CATOBAR carriers; China: 3 carriers, all\n"
    "conventional (2 STOBAR, 1 newly CATOBAR — Type 003 Fujian). China's\n"
    "first nuclear carrier (Type 004) is under construction.\n"
    "Operational carrier-aviation experience: US has 100+ years;\n"
    "PLAN's first carrier (Liaoning) entered service in 2012.\n\n"
    "Source: US ONI testimony; CSIS open analyses; IISS Military Balance 2024.\n"
    "See raw-data/08e_*.csv for URLs.",
    xy=(0.98, 0.05), xycoords="axes fraction",
    fontsize=9, color="#222", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/08e_aircraft_carriers.png", dpi=150); plt.close()
print("  saved 08e_aircraft_carriers.png")


# ---------------------------------------------------------------------------
# 8f. 5th-generation fighter engine introduction year — the persistent lag
# ---------------------------------------------------------------------------
print("5th-gen fighter engine timeline...")
engines = load("08f_fifth_gen_engine_ioc_year").sort_values("ioc_year")

color_map = {"United States": COLOR_US, "Russia": "#a93226",
             "China": COLOR_CN}
bar_colors = [color_map[c] for c in engines["country"]]

fig, ax = plt.subplots(figsize=(13, 4.5))
y_pos = range(len(engines))
ax.barh(y_pos, [y - 1995 for y in engines["ioc_year"]], left=1995,
        color=bar_colors, edgecolor="white", height=0.55)
ax.set_yticks(y_pos)
labels = [f"{e}\n({c})" for e, c in zip(engines["engine"], engines["country"])]
ax.set_yticklabels(labels, fontsize=10)
for i, (y, e) in enumerate(zip(engines["ioc_year"], engines["engine"])):
    gap = y - 2005
    text = f"IOC {y}" if gap == 0 else f"IOC {y} (+{gap} years vs F-119)"
    ax.text(y + 0.5, i, text, va="center", fontsize=10,
            color="#222", fontweight="bold")
ax.set_xlim(1995, 2030)
ax.set_xlabel("Year of Initial Operational Capability (IOC)")
ax.set_title("Indigenous 5th-Generation Fighter Engine — Year of Operational Status",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
ax.axvline(2005, color=COLOR_US, linestyle="--", linewidth=1.2, alpha=0.7)
ax.text(2005.3, len(engines) - 0.4,
        "F-119 baseline (2005)",
        fontsize=9, color=COLOR_US, fontweight="bold")
ax.annotate(
    "China's WS-15 reached operational status in 2023 — 18 years after\n"
    "the US F-119 (the engine for the F-22) entered service in 2005.\n"
    "On commercial high-thrust turbofans the gap is even larger: COMAC's\n"
    "C919 still uses CFM LEAP (GE/Safran) — indigenous CJ-1000A is in testing.\n\n"
    "Source: US Air Force / Pratt & Whitney / AVIC public statements.\n"
    "See raw-data/08f_*.csv for URLs.",
    xy=(0.02, 0.95), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/08f_fighter_engine_timeline.png", dpi=150); plt.close()
print("  saved 08f_fighter_engine_timeline.png")


print("\nDone — counter-evidence charts saved to", OUTPUT)
