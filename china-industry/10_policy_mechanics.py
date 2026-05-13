"""
10 — How the Model Actually Works: Industrial-Policy Mechanics

Demystifying the "how did they do it" — not as a recipe to copy, but as
a system to understand. The combination of state direction (5-year plans,
sectoral catalogues, subsidies, public procurement, standards) with
fierce private competition (hundreds of firms per sector, brutal price
wars, exit of the weak) is qualitatively distinct from both Soviet
planning and Western market economies.

The data:
- China's industrial-policy spending was ~1.7% of GDP in 2019 — roughly
  2-3x the share spent by comparator economies (OECD / DiPippo 2022)
- China's credit-to-GDP ratio sits at ~310% (BIS) — financing engine
  for industrial directives
- China now holds ~76 ISO technical-committee secretariats, up from 49
  in 2010, with similar growth at IEC
- The "Big Fund" semiconductor vehicle has injected ~\\$100B+ across
  three tranches (2014, 2019, 2024)
- Western response — CHIPS, IRA, EU Net-Zero Industry Act, EU CRMA —
  totals well over \\$1T in announced authority since 2022

This script only READS data. Every chart's numbers live in a CSV under
raw-data/ with a `# source:` header. See raw-data/SOURCES.md.
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
COLOR_DE     = "#16a085"
COLOR_OTHER  = "#bdc3c7"


def load(name, **kwargs):
    return pd.read_csv(f"{RAW_DATA}/{name}.csv", comment="#", **kwargs)


# ---------------------------------------------------------------------------
# 10a. Industrial-policy spending — China vs comparators, % of GDP
# ---------------------------------------------------------------------------
print("Industrial-policy spending share of GDP...")
subs = load("10a_industrial_subsidies_pct_gdp").sort_values(
    "share_pct_gdp", ascending=True)

color_map = {"China": COLOR_CN, "United States": COLOR_US,
             "Germany": COLOR_DE, "France": COLOR_EU,
             "Japan": COLOR_JP, "South Korea": COLOR_KR,
             "Brazil": COLOR_OTHER}
bar_colors = [color_map.get(c, COLOR_OTHER) for c in subs["country"]]

fig, ax = plt.subplots(figsize=(13, 5.5))
y_pos = range(len(subs))
ax.barh(y_pos, subs["share_pct_gdp"], color=bar_colors, edgecolor="white")
ax.set_yticks(y_pos); ax.set_yticklabels(subs["country"])
for i, v in enumerate(subs["share_pct_gdp"]):
    ax.text(v + 0.03, i, f"{v:.2f}%", va="center", fontsize=11,
            color="#222", fontweight="bold")
ax.set_xlim(0, 2.1)
ax.set_xlabel("Industrial-policy spending, % of GDP (2019)")
ax.set_title("Industrial-Policy Spending — Estimated Share of GDP, China vs Comparators (2019)",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
ax.annotate(
    "China's industrial-policy spending — direct subsidies + below-market\n"
    "credit + tax expenditures + land grants — was ~1.7% of GDP in 2019,\n"
    "roughly 2-3x the share spent by comparator economies. In absolute USD\n"
    "the multiple is closer to 3-5x.\n\n"
    "Source: OECD Trade Policy Paper 270 (DiPippo et al. 'Red Ink'), 2022.\n"
    "See raw-data/10a_*.csv for URLs.",
    xy=(0.98, 0.05), xycoords="axes fraction",
    fontsize=9, color="#222", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#fdf2ee",
              edgecolor=COLOR_CN, linewidth=1.0))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/10a_industrial_subsidies.png", dpi=150); plt.close()
print("  saved 10a_industrial_subsidies.png")


# ---------------------------------------------------------------------------
# 10b. Credit-to-GDP — the financing engine
# ---------------------------------------------------------------------------
print("China credit-to-GDP trajectory...")
credit = load("10b_china_credit_to_gdp", index_col="year")

fig, ax = plt.subplots(figsize=(13, 5.5))
ax.plot(credit.index, credit["china_total"], color=COLOR_CN, linewidth=2.8,
        marker="o", markersize=6, label="China — total credit / GDP")
ax.plot(credit.index, credit["china_corporate"], color=COLOR_CN, linewidth=1.8,
        linestyle="--", marker="s", markersize=5, alpha=0.7,
        label="China — non-financial corporate / GDP")
ax.plot(credit.index, credit["united_states"], color=COLOR_US, linewidth=1.5,
        marker="^", markersize=4, label="United States — total / GDP")
ax.plot(credit.index, credit["euro_area"], color=COLOR_EU, linewidth=1.5,
        marker="D", markersize=4, label="Euro area — total / GDP")
ax.fill_between(credit.index, credit["china_total"], alpha=0.07, color=COLOR_CN)
for col, color in [("china_total", COLOR_CN), ("china_corporate", COLOR_CN),
                   ("united_states", COLOR_US), ("euro_area", COLOR_EU)]:
    y = credit[col].iloc[-1]
    ax.text(2024.3, y, f"{y:.0f}%", va="center", fontsize=10,
            color=color, fontweight="bold")
ax.set_title("Credit to the Non-Financial Sector — % of GDP, China vs Comparators",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
ax.set_ylim(0, 340)
ax.legend(loc="upper left", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
ax.annotate(
    "China's total credit-to-GDP at ~310% is higher than the US (~225%)\n"
    "and euro area (~210%). The composition is the policy lever: ~50% of\n"
    "China's credit goes to non-financial corporates (vs ~75% household/govt\n"
    "in US), and the state-bank channel allocates it directionally toward\n"
    "sectors named in the 5-year plans.\n\n"
    "Source: BIS — Credit to the non-financial sector (table F1.1).\n"
    "See raw-data/10b_*.csv for URLs.",
    xy=(0.02, 0.95), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/10b_credit_to_gdp.png", dpi=150); plt.close()
print("  saved 10b_credit_to_gdp.png")


# ---------------------------------------------------------------------------
# 10c. China's rise in international standards-setting (ISO/IEC)
# ---------------------------------------------------------------------------
print("China's role in international standards-setting...")
iso = load("10c_iso_iec_secretariats_by_country")
iso_sorted = iso.sort_values("iso_2024", ascending=True)

fig, ax = plt.subplots(figsize=(13, 6.5))
y_pos = range(len(iso_sorted))
bar_colors = [COLOR_CN if c == "China" else COLOR_OTHER
              for c in iso_sorted["country"]]
ax.barh(y_pos, iso_sorted["iso_2010"], color=COLOR_OTHER, alpha=0.45,
        edgecolor="white", label="ISO secretariats — 2010")
ax.barh(y_pos, iso_sorted["iso_2024"], color=bar_colors, alpha=0.9,
        edgecolor="white", label="ISO secretariats — 2024", height=0.55)
ax.set_yticks(y_pos); ax.set_yticklabels(iso_sorted["country"])
for i, (a, b) in enumerate(zip(iso_sorted["iso_2010"], iso_sorted["iso_2024"])):
    delta = b - a
    sign = "+" if delta >= 0 else ""
    ax.text(b + 2, i, f"{b}  ({sign}{delta})", va="center", fontsize=10,
            color="#222", fontweight="bold")
ax.set_xlim(0, 175)
ax.set_xlabel("ISO technical-committee secretariats held")
ax.set_title("ISO Technical-Committee Secretariats by Country — 2010 vs 2024",
             fontsize=13, fontweight="bold")
ax.legend(loc="lower right", fontsize=10, framealpha=0.95)
ax.grid(axis="x", alpha=0.3)
ax.annotate(
    "China rose from 49 ISO secretariats in 2010 to 76 in 2024 — the largest\n"
    "absolute gain. Holding a TC secretariat means leading the standards\n"
    "process for that domain. China is now within range of Germany, the US\n"
    "and France — and well ahead at IEC for newer tech (5G, AI, batteries).\n\n"
    "Source: ISO + IEC annual reports.\n"
    "See raw-data/10c_*.csv for URLs.",
    xy=(0.99, 0.05), xycoords="axes fraction",
    fontsize=9, color="#222", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#fdf2ee",
              edgecolor=COLOR_CN, linewidth=1.0))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/10c_iso_iec_secretariats.png", dpi=150); plt.close()
print("  saved 10c_iso_iec_secretariats.png")


# ---------------------------------------------------------------------------
# 10d. China's Big Fund semiconductor investment tranches
# ---------------------------------------------------------------------------
print("Big Fund semiconductor investment tranches...")
bf = load("10d_china_big_fund_semiconductors")

fig, ax = plt.subplots(figsize=(13, 5.0))
y_pos = range(len(bf))
ax.barh(y_pos, bf["announced_usd_bn"], color=COLOR_CN, alpha=0.85,
        edgecolor="white")
ax.set_yticks(y_pos)
labels = [f"{p}\n({y})" for p, y in zip(bf["phase"], bf["year"])]
ax.set_yticklabels(labels, fontsize=10)
for i, v in enumerate(bf["announced_usd_bn"]):
    ax.text(v + 1.2, i, f"\\${v}B", va="center", fontsize=12,
            color="#222", fontweight="bold")
ax.set_xlim(0, 60)
ax.set_xlabel("Announced fund size (USD billion)")
ax.set_title("China's National Integrated Circuit Industry Investment Fund ('Big Fund') — Tranches",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
ax.invert_yaxis()
total = bf["announced_usd_bn"].sum()
ax.annotate(
    f"Combined Big Fund authority across the three central tranches: ~\\${total}B,\n"
    "plus provincial / local-government chip-industry funds that bring the\n"
    "publicly-announced national total well above \\$200B since 2014.\n\n"
    "Outcomes: SMIC ramped 14nm and announced 7nm-equivalent in 2023;\n"
    "YMTC reached 232-layer NAND; CXMT shipped DDR5. None of these match\n"
    "the global leading-edge — but the gap closed faster than 2018 expectations.\n"
    "(Big Fund I also had a notable corruption probe outcome in 2022-23.)\n\n"
    "Source: SASAC / MIIT announcements; Reuters / Caixin reporting.\n"
    "See raw-data/10d_*.csv for URLs.",
    xy=(0.99, 0.5), xycoords="axes fraction",
    fontsize=9, color="#222", va="center", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/10d_big_fund.png", dpi=150); plt.close()
print("  saved 10d_big_fund.png")


# ---------------------------------------------------------------------------
# 10e. Western industrial-policy response — IRA / CHIPS / EU NZIA / CRMA / EU Chips
# ---------------------------------------------------------------------------
print("Western industrial-policy response...")
wp = load("10e_western_industrial_policy_response_usd_bn")
# Exclude the duplicate IRA-revised entry for the bar (we'll annotate it)
wp_main = wp[wp["policy"] != "IRA (CBO revised)"].copy()
ira_revised = wp[wp["policy"] == "IRA (CBO revised)"]["headline_usd_bn"].iloc[0]
wp_main = wp_main.sort_values("headline_usd_bn", ascending=True)

color_map = {"United States": COLOR_US, "European Union": COLOR_EU}
bar_colors = [color_map[c] for c in wp_main["country_region"]]

fig, ax = plt.subplots(figsize=(13, 5.5))
y_pos = range(len(wp_main))
ax.barh(y_pos, wp_main["headline_usd_bn"], color=bar_colors, edgecolor="white")
labels = [f"{p} ({c})" for p, c in zip(wp_main["policy"], wp_main["country_region"])]
ax.set_yticks(y_pos); ax.set_yticklabels(labels)
for i, v in enumerate(wp_main["headline_usd_bn"]):
    ax.text(v + 8, i, f"\\${v}B", va="center", fontsize=11,
            color="#222", fontweight="bold")
ax.set_xlim(0, 720)
ax.set_xlabel("Announced funding authority (USD billion)")
ax.set_title("Western Industrial-Policy Response — Headline Announced Funding (2022-2023)",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
total = wp_main["headline_usd_bn"].sum()
ax.annotate(
    f"Combined headline authority of these five instruments: ~\\${total}B.\n"
    f"CBO's 2023 revision of the IRA energy / EV tax-credit cost alone\n"
    f"raised the estimate to ~\\${ira_revised}B over 10 years.\n\n"
    "The US bet is heavier on demand-side tax credits (IRA); the EU bet is\n"
    "heavier on regulatory framework + leveraging existing funds (NZIA, CRMA).\n"
    "Both are convergent with elements of China's playbook — production\n"
    "subsidies, domestic-content preferences, strategic-sector targeting.\n\n"
    "Source: CRS reports (IRA, CHIPS); EU Commission communications.\n"
    "See raw-data/10e_*.csv for URLs.",
    xy=(0.98, 0.05), xycoords="axes fraction",
    fontsize=9, color="#222", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/10e_western_policy_response.png", dpi=150); plt.close()
print("  saved 10e_western_policy_response.png")


print("\nDone — policy-mechanics charts saved to", OUTPUT)
