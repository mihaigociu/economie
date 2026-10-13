"""
10 — How the Model Actually Works: Industrial-Policy Mechanics

Demystifying the "how did they do it" — not as a recipe to copy, but as
a system to understand. The combination of state direction (5-year plans,
sectoral catalogues, subsidies, public procurement, standards) with
fierce private competition (hundreds of firms per sector, brutal price
wars, exit of the weak) is qualitatively distinct from both Soviet
planning and Western market economies.

The data:
- China's industrial-policy spending was at least ~1.7% of GDP in 2019 —
  roughly 2.5-5x the share spent by comparator economies (CSIS "Red
  Ink", DiPippo, Mazzocco & Kennedy 2022). A broader IMF measure puts it
  at ~4.4% of GDP in 2023.
- China's credit-to-GDP ratio is ~300% (BIS, end-2025) — the financing
  engine for industrial directives
- China held 87 ISO technical-committee / subcommittee secretariats at
  end-2024, up from 49 in 2010 — the largest gain of any member
- The "Big Fund" semiconductor vehicle: three central tranches (2014,
  2019, 2024), ~\\$100B combined
- Western response — CHIPS, IRA, EU Net-Zero Industry Act, EU CRMA, EU
  Chips Act — ~\\$670B of headline authority (2022-23), since partly
  reversed (OBBBA 2025) or re-instrumented (Intel equity stake)

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


def note_box(ax, text, xy, va, ha, face="white", edge="#888", lw=0.8):
    ax.annotate(text, xy=xy, xycoords="axes fraction", fontsize=9,
                color="#222", va=va, ha=ha,
                bbox=dict(boxstyle="round,pad=0.4", facecolor=face,
                          edgecolor=edge, linewidth=lw))


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
ax.set_xlim(0, subs["share_pct_gdp"].max() * 1.25)
ax.set_xlabel("Industrial-policy spending, % of GDP (2019)")
ax.set_title("Industrial-Policy Spending — Estimated Share of GDP, China vs Comparators (2019)",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
cn = subs.loc[subs["country"] == "China", "share_pct_gdp"].iloc[0]
others = subs[subs["country"] != "China"]["share_pct_gdp"]
lo, hi = cn / others.max(), cn / others.min()
note_box(ax,
         f"China's industrial-policy spending — direct subsidies, tax breaks,\n"
         f"below-market credit and government investment funds — was at least\n"
         f"{cn:.1f}% of GDP in 2019, {lo:.1f}–{hi:.1f}x the share spent by the\n"
         "comparator economies. A broader IMF estimate (different method,\n"
         "not comparable) puts China at ~4.4% of GDP in 2023.\n\n"
         "Source: CSIS 'Red Ink' (DiPippo, Mazzocco & Kennedy, 2022);\n"
         "IMF WP/25/155. See raw-data/10a_*.csv for URLs.",
         xy=(0.98, 0.05), va="bottom", ha="right",
         face="#fdf2ee", edge=COLOR_CN, lw=1.0)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/10a_industrial_subsidies.png", dpi=150); plt.close()
print("  saved 10a_industrial_subsidies.png")


# ---------------------------------------------------------------------------
# 10b. Credit-to-GDP — the financing engine
# ---------------------------------------------------------------------------
print("China credit-to-GDP trajectory...")
credit = load("10b_china_credit_to_gdp", index_col="year")
last_year = int(credit.index[-1])

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
# end-of-line labels; nudge apart if they would collide
ends = sorted([(credit[c].iloc[-1], c, col) for c, col in
               [("china_total", COLOR_CN), ("china_corporate", COLOR_CN),
                ("united_states", COLOR_US), ("euro_area", COLOR_EU)]])
placed = []
for y, c, col in ends:
    ty = y
    if placed and ty - placed[-1] < 9:
        ty = placed[-1] + 9
    placed.append(ty)
    ax.text(last_year + 0.4, ty, f"{y:.0f}%", va="center", fontsize=10,
            color=col, fontweight="bold")
ax.set_xlim(credit.index[0] - 0.5, last_year + 2)
ax.set_title(f"Credit to the Non-Financial Sector — % of GDP, China vs Comparators "
             f"({int(credit.index[0])}–{last_year}, year-end)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
ax.set_ylim(0, max(340, credit.max().max() * 1.1))
ax.legend(loc="upper left", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
r = credit.iloc[-1]
fig.text(0.01, -0.01,
         f"China's total credit-to-GDP rose to {r.china_total:.0f}% at end-{last_year}, above the US "
         f"({r.united_states:.0f}%) and euro area ({r.euro_area:.0f}%) — and is still rising while both have "
         "fallen since 2020.\n"
         f"Composition is the policy lever: non-financial corporates are {r.china_corporate / r.china_total:.0%} "
         "of China's total, and the state-bank channel steers that credit toward plan sectors.\n"
         "Source: BIS total credit statistics (WS_TC; market value, break-adjusted; Q4 values). "
         "China corporate series starts 2006. See raw-data/10b_*.csv for URLs.",
         ha="left", va="top", fontsize=9, color="#222")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/10b_credit_to_gdp.png", dpi=150, bbox_inches="tight"); plt.close()
print("  saved 10b_credit_to_gdp.png")


# ---------------------------------------------------------------------------
# 10c. China's rise in international standards-setting (ISO)
# ---------------------------------------------------------------------------
print("China's role in international standards-setting...")
iso = load("10c_iso_iec_secretariats_by_country")
iso_sorted = iso.sort_values("iso_2024", ascending=True).reset_index(drop=True)

fig, ax = plt.subplots(figsize=(13, 6.5))
y_pos = range(len(iso_sorted))
bar_colors = [COLOR_CN if c == "China" else COLOR_OTHER
              for c in iso_sorted["country"]]
ax.barh(y_pos, iso_sorted["iso_2010"], color=COLOR_OTHER, alpha=0.45,
        edgecolor="white", label="ISO secretariats — 2010")
ax.barh(y_pos, iso_sorted["iso_2024"], color=bar_colors, alpha=0.9,
        edgecolor="white", label="ISO secretariats — end-2024", height=0.55)
ax.set_yticks(y_pos); ax.set_yticklabels(iso_sorted["country"])
for i, (a, b) in enumerate(zip(iso_sorted["iso_2010"], iso_sorted["iso_2024"])):
    delta = b - a
    sign = "+" if delta >= 0 else ""
    ax.text(max(a, b) + 2, i, f"{b}  ({sign}{delta} vs 2010)", va="center", fontsize=10,
            color="#222", fontweight="bold")
ax.set_xlim(0, iso[["iso_2010", "iso_2024"]].max().max() * 1.35)
ax.set_xlabel("ISO technical-committee and subcommittee secretariats held")
ax.set_title("ISO Technical-Committee Secretariats by Country — 2010 vs end-2024",
             fontsize=13, fontweight="bold")
ax.legend(loc="lower right", fontsize=10, framealpha=0.95)
ax.grid(axis="x", alpha=0.3)
iso["delta"] = iso["iso_2024"] - iso["iso_2010"]
c = iso[iso["country"] == "China"].iloc[0]
ranked = iso.sort_values("iso_2024", ascending=False)["country"].tolist()
rank = ranked.index("China") + 1
largest = iso.loc[iso["delta"].idxmax(), "country"]
gain_txt = "the largest absolute gain" if largest == "China" else f"(largest gain: {largest})"
note_box(ax,
         f"China rose from {c.iso_2010} ISO secretariats in 2010 to {c.iso_2024} at end-2024 —\n"
         f"{gain_txt} — and now ranks #{rank}, behind only {', '.join(ranked[:rank-1])}.\n"
         "Holding a secretariat means running the standards process for that\n"
         f"domain. At IEC China holds {c.iec_2024}, versus Germany's "
         f"{iso.loc[iso.country == 'Germany', 'iec_2024'].iloc[0]} (2010 and IEC columns unverified).\n\n"
         "Source: ISO in figures 2024 (Jan 2025); IEC annual reports.\n"
         "See raw-data/10c_*.csv for URLs.",
         xy=(0.99, 0.18), va="bottom", ha="right",
         face="#fdf2ee", edge=COLOR_CN, lw=1.0)
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
ax.set_xlim(0, bf["announced_usd_bn"].max() * 2.3)
ax.set_xlabel("Announced fund size (USD billion)")
ax.set_title("China's National Integrated Circuit Industry Investment Fund ('Big Fund') — Tranches",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
ax.invert_yaxis()
total = bf["announced_usd_bn"].sum()
note_box(ax,
         f"Combined central Big Fund authority, {len(bf)} tranches: ~\\${total}B, plus\n"
         "provincial / local chip funds that take the announced total well\n"
         "above \\$200B. Phase III is shifting toward packaging, equipment\n"
         "and AI chips. Since Dec 2025 a separate national VC guidance fund\n"
         "(RMB 1tn target, RMB 100bn state seed) backs early-stage hard tech.\n\n"
         "Outcomes: SMIC's N+3 (Kirin 9030, 2025) is a scaled 7nm-class node,\n"
         "still short of TSMC 5nm; YMTC ships 294-layer NAND. Not leading-edge,\n"
         "but the gap closed faster than 2018 expectations.\n\n"
         "Source: Reuters / Yicai / Caixin; TechInsights; TrendForce.\n"
         "See raw-data/10d_*.csv for URLs.",
         xy=(0.99, 0.5), va="center", ha="right")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/10d_big_fund.png", dpi=150); plt.close()
print("  saved 10d_big_fund.png")


# ---------------------------------------------------------------------------
# 10e. Western industrial-policy response — IRA / CHIPS / EU NZIA / CRMA / EU Chips
# ---------------------------------------------------------------------------
print("Western industrial-policy response...")
wp = load("10e_western_industrial_policy_response_usd_bn")
# Exclude the duplicate IRA-revised entry for the bar (we'll annotate it)
is_rev = wp["policy"].str.contains("revised", case=False)
wp_main = wp[~is_rev].copy()
ira_revised = wp[is_rev]["headline_usd_bn"].iloc[0] if is_rev.any() else None
wp_main = wp_main.sort_values("headline_usd_bn", ascending=True)

color_map = {"United States": COLOR_US, "European Union": COLOR_EU,
             "Japan": COLOR_JP, "South Korea": COLOR_KR}
bar_colors = [color_map.get(c, COLOR_OTHER) for c in wp_main["country_region"]]

fig, ax = plt.subplots(figsize=(13, 5.8))
y_pos = range(len(wp_main))
ax.barh(y_pos, wp_main["headline_usd_bn"], color=bar_colors, edgecolor="white")
labels = [f"{p} ({c}, {y})" for p, c, y in
          zip(wp_main["policy"], wp_main["country_region"], wp_main["year"])]
ax.set_yticks(y_pos); ax.set_yticklabels(labels)
for i, v in enumerate(wp_main["headline_usd_bn"]):
    ax.text(v + 8, i, f"\\${v}B", va="center", fontsize=11,
            color="#222", fontweight="bold")
ax.set_xlim(0, wp["headline_usd_bn"].max() * 1.1)
ax.set_xlabel("Announced funding authority (USD billion)")
yrs = f"{wp_main['year'].min()}-{wp_main['year'].max()}"
ax.set_title(f"Western Industrial-Policy Response — Headline Announced Funding ({yrs})",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
total = wp_main["headline_usd_bn"].sum()
rev_line = (f"CBO's 2023 re-score put the IRA energy / EV credits at ~\\${ira_revised}B.\n"
            if ira_revised is not None else "")
note_box(ax,
         f"Combined headline authority of these {len(wp_main)} instruments: ~\\${total}B.\n"
         + rev_line +
         "Since then: the One Big Beautiful Bill Act (Jul 2025) repealed or\n"
         "phased out much of the IRA (~\\$500B over 10y); \\$8.9B of CHIPS /\n"
         "Secure Enclave awards became a 9.9% US stake in Intel (Aug 2025);\n"
         "EU Chips Act 2.0 (proposed Jun 2026) has no new headline sum.\n"
         "Bars show original 2022-23 announcements, not current authority.\n\n"
         "Source: CRS; CBO; EU Commission; Tax Foundation; Intel 8-K.\n"
         "See raw-data/10e_*.csv for URLs.",
         xy=(0.98, 0.04), va="bottom", ha="right")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/10e_western_policy_response.png", dpi=150); plt.close()
print("  saved 10e_western_policy_response.png")


print("\nDone — policy-mechanics charts saved to", OUTPUT)
