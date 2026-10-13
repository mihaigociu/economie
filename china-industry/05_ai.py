"""
05 — Sectoral Deep Dive: Artificial Intelligence

The messiest of the three frontier-sector cases — and the most contested.
The data supports a "China at-or-near frontier in some AI dimensions,
behind in others" picture:

Where China is at or near the frontier:
- Generative-AI patent filings: China dominant by a large margin
- Top-cited AI publications: China overtook US around 2019
- Model quality: on the Arena human-preference leaderboard the top
  Chinese model trailed the top US model by ~2.7% in March 2026, and the
  top open-weight model was Chinese (Zhipu GLM-5) — made in the report
  text, not charted (the open-weight leaderboard chart was dropped in
  the October 2026 edition)

Where China still lags:
- Notable model count: the US still releases more notable models
- Private AI investment: US ~23x China in 2025
- Compute / chip access: bound by US export controls

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
COLOR_UK     = "#8e44ad"
COLOR_KR     = "#e67e22"
COLOR_JP     = "#16a085"
COLOR_OTHER  = "#bdc3c7"


def load(name, **kwargs):
    return pd.read_csv(f"{RAW_DATA}/{name}.csv", comment="#", **kwargs)


def fmt_num(v):
    """Integer if whole, else one decimal."""
    return f"{v:.0f}" if float(v).is_integer() else f"{v:.1f}"


# ---------------------------------------------------------------------------
# 5a. Notable AI models released by lab country
# ---------------------------------------------------------------------------
print("Notable AI models released by country...")
models = load("05a_notable_ai_models_by_country", index_col="year")
y0, y1 = models.index.min(), models.index.max()

fig, ax = plt.subplots(figsize=(13, 5.8))
models.plot.bar(stacked=True, ax=ax,
                color=[COLOR_US, COLOR_CN, COLOR_UK, COLOR_EU, COLOR_OTHER],
                width=0.65, edgecolor="white", linewidth=0.6)
ax.set_title(f"Notable AI Models Released — by Lab Country, {y0}–{y1}",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Number of notable AI models released")
ax.set_xticklabels(models.index, rotation=0)
ax.legend(ncol=5, loc="upper left", fontsize=9, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
totals = models.sum(axis=1)
ax.set_ylim(0, totals.max() * 1.55)
for i, t in enumerate(totals):
    ax.text(i, t + 1.5, f"{t:.0f}", ha="center", va="bottom",
            fontsize=10, color="#222", fontweight="bold")
last = models.loc[y1]
ax.annotate(
    f"{y1}: US {last['United States']:.0f}, China {last['China']:.0f} "
    f"(AI Index 2026 data file).\n"
    "The AI Index 2026 PDF quotes a later Epoch snapshot (22 Apr 2026):\n"
    "US 59, China 35, South Korea 8. Epoch keeps adding historical\n"
    "models, so earlier years are revised upward each edition.\n"
    "\"Notable\" = Epoch AI curation, broader than LLMs.\n"
    "Source: Stanford HAI AI Index 2026; data from Epoch AI.",
    xy=(0.99, 0.97), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/05a_notable_ai_models.png", dpi=150); plt.close()
print("  saved 05a_notable_ai_models.png")


# ---------------------------------------------------------------------------
# 5b. Top-cited AI publications — share of top 1% by country
# ---------------------------------------------------------------------------
print("Top-cited AI publication share by country...")
cites = load("05b_top_cited_ai_publications_share_pct", index_col="year")

fig, ax = plt.subplots(figsize=(13, 5.2))
for col, color, lw in [("China", COLOR_CN, 2.8),
                       ("United States", COLOR_US, 2.2),
                       ("European Union", COLOR_EU, 1.5),
                       ("United Kingdom", COLOR_UK, 1.5),
                       ("Other", COLOR_OTHER, 1.5)]:
    ax.plot(cites.index, cites[col], label=col, color=color,
            linewidth=lw, marker="o", markersize=5)
    y = cites[col].iloc[-1]
    ax.text(cites.index[-1] + 0.15, y, f"{y}%", va="center", fontsize=9,
            color=color, fontweight="bold")
ax.set_title("Top-1% Most-Cited AI Publications — Share by Country/Region",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of top-1% cited AI publications")
ax.set_ylim(0, 50)
ax.set_xlim(cites.index.min() - 0.5, cites.index.max() + 1.0)
ax.legend(loc="upper right", ncol=5, fontsize=9, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
ax.annotate(
    "China overtook the US in top-cited AI publication share around 2019.\n"
    "Caveat: citation-based rankings are partly self-citation patterns;\n"
    "among the 100 most-cited AI papers of 2024 the US still led (46 vs 41).\n\n"
    "Source: NSF S&E Indicators 2024; CSET; Stanford AI Index 2024/2026.\n"
    "See raw-data/05b_*.csv for URLs.",
    xy=(0.02, 0.97), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/05b_top_cited_ai_publications.png", dpi=150); plt.close()
print("  saved 05b_top_cited_ai_publications.png")


# ---------------------------------------------------------------------------
# 5c. Generative-AI patent families, cumulative 2014–2023, by inventor country
# ---------------------------------------------------------------------------
print("Generative-AI patent families by country, cumulative 2014–2023...")
gai_patents = load("05c_gai_patent_filings_by_country")
gai_patents = gai_patents.sort_values("patent_families_2014_2023", ascending=True)

country_colors = {
    "China": COLOR_CN, "United States": COLOR_US,
    "South Korea": COLOR_KR, "Japan": COLOR_JP,
    "India": COLOR_OTHER, "United Kingdom": COLOR_UK,
    "Germany": COLOR_EU,
}
colors = [country_colors.get(c, COLOR_OTHER) for c in gai_patents["country"]]
vals = gai_patents["patent_families_2014_2023"]
cn = int(gai_patents.set_index("country").loc["China", "patent_families_2014_2023"])
us = int(gai_patents.set_index("country").loc["United States", "patent_families_2014_2023"])

fig, ax = plt.subplots(figsize=(13, 5.5))
bars = ax.barh(gai_patents["country"], vals, color=colors)
for bar, val in zip(bars, vals):
    ax.text(val + vals.max() * 0.01, bar.get_y() + bar.get_height() / 2,
            f"{val:,}", va="center", fontsize=10, fontweight="bold")
ax.set_title("Generative-AI Patent Families — Cumulative 2014–2023, by Inventor Country",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Patent families filed 2014–2023 (cumulative)")
ax.set_xlim(0, vals.max() * 1.1)
ax.grid(axis="x", alpha=0.3)
ax.annotate(
    f"China filed ~{cn / us:.0f}x more generative-AI patent families than the US\n"
    "over 2014–2023. WIPO's July 2026 update: China-based inventors\n"
    "published 43,000+ GenAI families in 2024–25 alone — more than their\n"
    "whole 2014–23 total — and global publications reached 37,808 in 2025.\n"
    "Volume ≠ quality: US filings grew faster (1,185 → 4,380, 2023–25).\n\n"
    "Source: WIPO GenAI Patent Landscape Report 2024 (Fig. 17a);\n"
    "WIPO SPARK Patent Trends Update in GenAI (2026).",
    xy=(0.36, 0.42), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/05c_gai_patent_filings.png", dpi=150); plt.close()
print("  saved 05c_gai_patent_filings.png")


# ---------------------------------------------------------------------------
# 5d. Private AI investment by country (USD billions)
# ---------------------------------------------------------------------------
print("Private AI investment by country...")
investment = load("05d_private_ai_investment_usd_bn", index_col="year")
y0, y1 = investment.index.min(), investment.index.max()
last = investment.loc[y1]

fig, ax = plt.subplots(figsize=(13, 5.8))
investment.plot.bar(stacked=True, ax=ax,
                    color=[COLOR_US, COLOR_CN, COLOR_UK, COLOR_OTHER],
                    width=0.65, edgecolor="white", linewidth=0.6)
ax.set_title(f"Private AI Investment — by Country, USD Billion ({y0}–{y1})",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("USD billion")
ax.set_xticklabels(investment.index, rotation=0)
ax.legend(loc="upper left", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
totals = investment.sum(axis=1)
ax.set_ylim(0, totals.max() * 1.12)
for i, t in enumerate(totals):
    ax.text(i, t + totals.max() * 0.01, f"\\${t:.0f}B", ha="center",
            va="bottom", fontsize=10, color="#222", fontweight="bold")
ax.annotate(
    f"The honest counter-case: US private AI investment in {y1}\n"
    f"(\\${fmt_num(last['United States'])}B) was roughly "
    f"{last['United States'] / last['China']:.0f}x China's "
    f"(\\${fmt_num(last['China'])}B).\n"
    "Caveat: Quid data exclude Chinese state guidance funds\n"
    "(est. \\$184B to AI firms, 2000–2023).\n"
    "Pre-2024 'Other' not reconciled to global totals.\n\n"
    "Source: Stanford HAI AI Index 2024, 2025, 2026.\n"
    "See raw-data/05d_*.csv for URLs.",
    xy=(0.27, 0.95), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/05d_private_ai_investment.png", dpi=150); plt.close()
print("  saved 05d_private_ai_investment.png")


print("\nDone — AI charts saved to", OUTPUT)
