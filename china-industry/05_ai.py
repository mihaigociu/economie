"""
05 — Sectoral Deep Dive: Artificial Intelligence

The messiest of the three frontier-sector cases — and the most contested.
The data supports a "China at-or-near frontier in some AI dimensions,
behind in others" picture:

Where China is at the frontier:
- Generative-AI patent filings: China dominant by a large margin
- Top-cited AI publications: China overtook US around 2019
- Open-weight LLMs: DeepSeek, Qwen, GLM, MiniMax now competitive with
  the best US open-weight models

Where China still lags:
- Notable model count overall: US still has more frontier-grade releases
- Private AI investment: US has roughly 5–10x China
- Closed-frontier models (GPT-class, Claude-class): US-only at the top
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


# ---------------------------------------------------------------------------
# 5a. Notable AI models released by lab country, 2018–2024
# ---------------------------------------------------------------------------
print("Notable AI models released by country...")
models = load("05a_notable_ai_models_by_country", index_col="year")

fig, ax = plt.subplots(figsize=(13, 5.5))
models.plot.bar(stacked=True, ax=ax,
                color=[COLOR_US, COLOR_CN, COLOR_UK, COLOR_EU, COLOR_OTHER],
                width=0.65, edgecolor="white", linewidth=0.6)
ax.set_title("Notable AI Models Released — by Lab Country, 2018–2024",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Number of notable AI models released")
ax.set_xticklabels(models.index, rotation=0)
ax.legend(ncol=5, loc="upper left", fontsize=9, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
totals = models.sum(axis=1)
for i, t in enumerate(totals):
    ax.text(i, t + 1.5, f"{t}", ha="center", va="bottom",
            fontsize=10, color="#222", fontweight="bold")
ax.annotate(
    "US still leads in absolute count (40 in 2024 vs China's 15 per the\n"
    "AI Index 2025); all regions released fewer notable models in 2024 than\n"
    "in 2023 as training runs consolidate into bigger, fewer releases.\n\n"
    "\"Notable AI models\" per Epoch AI's compute/impact threshold — broader\n"
    "than LLMs. 2018 examples include BERT, GPT-1, BigGAN, AlphaZero; LLMs\n"
    "as commonly understood emerge with GPT-3 (2020) and ChatGPT (late 2022).\n\n"
    "Source: Stanford HAI AI Index 2024+2025; data from Epoch AI.\n"
    "See raw-data/05a_*.csv for URLs.",
    xy=(0.02, 0.65), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
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
    for x, y in zip(cites.index, cites[col]):
        if x == cites.index[-1]:
            ax.text(x + 0.15, y, f"{y}%", va="center", fontsize=9,
                    color=color, fontweight="bold")
ax.set_title("Top-1% Most-Cited AI Publications — Share by Country/Region",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of top-1% cited AI publications")
ax.set_ylim(0, 40)
ax.legend(loc="upper right", fontsize=9, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
ax.annotate(
    "China overtook the US in top-cited AI publication share around 2019.\n"
    "Caveat: citation-based rankings are partly self-citation patterns;\n"
    "directionally the convergence and crossover are robust across methods.\n\n"
    "Source: NSF S&E Indicators 2024; CSET; Stanford AI Index 2024.\n"
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

fig, ax = plt.subplots(figsize=(13, 5.5))
bars = ax.barh(gai_patents["country"], gai_patents["patent_families_2014_2023"],
               color=colors)
for bar, val in zip(bars, gai_patents["patent_families_2014_2023"]):
    ax.text(val + 400, bar.get_y() + bar.get_height() / 2, f"{val:,}",
            va="center", fontsize=10, fontweight="bold")
ax.set_title("Generative-AI Patent Families — Cumulative 2014–2023, by Inventor Country",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Patent families filed 2014–2023 (cumulative)")
ax.set_xlim(0, 42000)
ax.grid(axis="x", alpha=0.3)
ax.annotate(
    "China filed ~6x more generative-AI patent families than the US over\n"
    "the decade 2014–2023. WIPO notes that since 2017 China has filed\n"
    "more GenAI patent families each year than the rest of the world combined.\n"
    "Volume ≠ quality, but the ramp is consistent with the production-oriented\n"
    "industrial-AI focus of Chinese firms.\n\n"
    "Source: WIPO Patent Landscape Report on Generative AI 2024, Figure 17a.\n"
    "See raw-data/05c_*.csv for URLs.",
    xy=(0.40, 0.40), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/05c_gai_patent_filings.png", dpi=150); plt.close()
print("  saved 05c_gai_patent_filings.png")


# ---------------------------------------------------------------------------
# 5d. Private AI investment by country, 2015–2024 (USD billions)
# ---------------------------------------------------------------------------
print("Private AI investment by country...")
investment = load("05d_private_ai_investment_usd_bn", index_col="year")

fig, ax = plt.subplots(figsize=(13, 5.5))
investment.plot.bar(stacked=True, ax=ax,
                    color=[COLOR_US, COLOR_CN, COLOR_UK, COLOR_OTHER],
                    width=0.65, edgecolor="white", linewidth=0.6)
ax.set_title("Private AI Investment — by Country, USD Billion (2015–2024)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("USD billion")
ax.set_xticklabels(investment.index, rotation=0)
ax.legend(loc="upper left", fontsize=10, framealpha=0.95)
ax.grid(axis="y", alpha=0.3)
totals = investment.sum(axis=1)
for i, t in enumerate(totals):
    ax.text(i, t + 3, f"\\${t:.0f}B", ha="center", va="bottom",
            fontsize=10, color="#222", fontweight="bold")
ax.annotate(
    "The honest counter-case: US private AI investment in 2024 (\\$109B)\n"
    "was roughly 12x China's (\\$9.3B). Closed-frontier model development\n"
    "still concentrates in well-capitalised US labs.\n\n"
    "Source: Stanford HAI AI Index 2024+2025.\n"
    "See raw-data/05d_*.csv for URLs.",
    xy=(0.02, 0.65), xycoords="axes fraction",
    fontsize=9, color="#222", va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
              edgecolor="#888", linewidth=0.8))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/05d_private_ai_investment.png", dpi=150); plt.close()
print("  saved 05d_private_ai_investment.png")


# ---------------------------------------------------------------------------
# 5e. Open-weight frontier-model leaderboard — early 2025 snapshot
# ---------------------------------------------------------------------------
print("Open-weight frontier model leaderboard snapshot...")
leaderboard = load("05e_open_weight_leaderboard_q1_2025").sort_values("arena_score")

color_map = {"China": COLOR_CN, "United States": COLOR_US,
             "European Union": COLOR_EU}
bar_colors = [color_map[c] for c in leaderboard["country"]]
labels = [f"{m}\n({lab}, {c})" for m, lab, c in
          zip(leaderboard["model"], leaderboard["lab"], leaderboard["country"])]

fig, ax = plt.subplots(figsize=(12, 6.5))
y_pos = range(len(leaderboard))
ax.barh(y_pos, leaderboard["arena_score"], color=bar_colors,
        edgecolor="white")
ax.set_yticks(y_pos); ax.set_yticklabels(labels, fontsize=9)
for i, v in enumerate(leaderboard["arena_score"]):
    ax.text(v + 4, i, f"{v}", va="center", fontsize=10, color="#222",
            fontweight="bold")
ax.set_xlim(1150, 1380)
ax.set_xlabel("LMArena / Chatbot Arena score (higher = better; Q1 2025 snapshot)")
ax.set_title("Top Open-Weight LLMs — Leaderboard Snapshot, Q1 2025",
             fontsize=13, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
cn_count = (leaderboard["country"] == "China").sum()
us_count = (leaderboard["country"] == "United States").sum()
eu_count = (leaderboard["country"] == "European Union").sum()
ax.annotate(
    f"Top 10 open-weight models (Q1 2025):\n"
    f"  China:  {cn_count}/10 (DeepSeek, Alibaba/Qwen, Zhipu)\n"
    f"  US:     {us_count}/10 (Meta/Llama, Google/Gemma, Microsoft/Phi)\n"
    f"  EU:     {eu_count}/10 (Mistral)\n\n"
    "Caveat: closed-frontier rankings remain dominated by OpenAI, Anthropic,\n"
    "and Google (GPT-4o / o1 / Claude 3.5 / Gemini 1.5) — not shown here.\n\n"
    "Source: LMArena / Chatbot Arena public leaderboard, Q1 2025 frame.\n"
    "See raw-data/05e_*.csv for URLs.",
    xy=(0.99, 0.04), xycoords="axes fraction",
    fontsize=9, color="#222", va="bottom", ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#fdf2ee",
              edgecolor=COLOR_CN, linewidth=1.0))
plt.tight_layout()
plt.savefig(f"{OUTPUT}/05e_open_weight_leaderboard.png", dpi=150); plt.close()
print("  saved 05e_open_weight_leaderboard.png")


print("\nDone — AI charts saved to", OUTPUT)
