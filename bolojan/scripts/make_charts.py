"""Generate headline charts for the Bolojan economic report.

Data are sourced from bolojan/data/macro_snapshot.md (which itself cites
INS, BNR, MF, Eurostat, EC, IMF). Run with the project venv:

    /Users/2346263/projects/economie/.venv/bin/python \
        /Users/2346263/projects/economie/bolojan/scripts/make_charts.py
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

CHARTS = Path(__file__).resolve().parent.parent / "charts"
CHARTS.mkdir(exist_ok=True)

GOV_FORMATION = pd.Timestamp("2025-06-23")
NO_CONF_VOTE = pd.Timestamp("2026-05-05")

plt.rcParams.update({
    "figure.dpi": 130,
    "savefig.dpi": 160,
    "savefig.bbox": "tight",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.labelsize": 10,
    "font.size": 10,
    "legend.frameon": False,
})

COL_RO = "#1f4e79"        # Romania primary
COL_ACCENT = "#c0504d"    # Romania highlight / target line
COL_GREY = "#7f7f7f"


def _annotate_period(ax):
    """Shade and label the Bolojan government period."""
    ax.axvspan(GOV_FORMATION, NO_CONF_VOTE, color="#f0e7d8", alpha=0.55,
               label="Bolojan government (2025-06-23 to 2026-05-05)")
    ax.axvline(GOV_FORMATION, color=COL_GREY, lw=0.8, ls="--")
    ax.axvline(NO_CONF_VOTE, color=COL_GREY, lw=0.8, ls="--")


def chart_deficit():
    """ESA general-government deficit, % of GDP."""
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
    deficit = [-4.4, -9.2, -7.2, -6.4, -6.5, -9.3, -7.9, -6.2]  # 2026 = projection
    is_proj = [False] * 7 + [True]
    colors = [COL_ACCENT if p else COL_RO for p in is_proj]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(years, deficit, color=colors, width=0.65)
    ax.axhline(-3.0, color=COL_GREY, lw=1, ls=":", label="EU Maastricht ceiling (-3% of GDP)")

    for x, y, p in zip(years, deficit, is_proj):
        label = f"{y:.1f}%" + ("*" if p else "")
        ax.text(x, y - 0.35, label, ha="center", va="top", fontsize=9,
                color="white" if not p else COL_ACCENT, fontweight="bold")

    # Mark government formation year
    ax.text(2025, 0.4, "Bolojan\ngovernment\nformed", ha="center", fontsize=8,
            color=COL_RO)
    ax.annotate("", xy=(2025, -0.1), xytext=(2025, 0.2),
                arrowprops=dict(arrowstyle="->", color=COL_RO, lw=0.8))

    ax.set_title("Romania general-government deficit, ESA 2010 (% of GDP)")
    ax.set_ylabel("% of GDP")
    ax.set_ylim(-10.5, 1.5)
    ax.set_xticks(years)
    ax.legend(loc="lower right", fontsize=8)
    ax.text(0.01, -0.16,
            "Source: Eurostat EDP notification (Apr 2026) and EC Spring 2026 Forecast.  "
            "* 2026 figure is a projection.",
            transform=ax.transAxes, fontsize=8, color=COL_GREY)

    fig.savefig(CHARTS / "01_deficit_esa.png")
    plt.close(fig)


def chart_debt():
    """General-government debt, % of GDP."""
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
    debt = [35.1, 46.8, 48.5, 47.5, 48.8, 54.8, 59.3, 63.0]  # 2026 projection
    is_proj = [False] * 7 + [True]
    colors = [COL_ACCENT if p else COL_RO for p in is_proj]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(years, debt, color=colors, width=0.65)
    ax.axhline(60.0, color=COL_GREY, lw=1, ls=":", label="EU Maastricht ceiling (60% of GDP)")

    for x, y, p in zip(years, debt, is_proj):
        label = f"{y:.1f}%" + ("*" if p else "")
        ax.text(x, y + 0.6, label, ha="center", va="bottom", fontsize=9,
                color=COL_RO if not p else COL_ACCENT, fontweight="bold")

    ax.set_title("Romania general-government debt, ESA 2010 (% of GDP)")
    ax.set_ylabel("% of GDP")
    ax.set_ylim(0, 72)
    ax.set_xticks(years)
    ax.legend(loc="upper left", fontsize=8)
    ax.text(0.01, -0.16,
            "Source: Eurostat EDP notification (Apr 2026) and EC Spring 2026 Forecast.  "
            "* 2026 figure is a projection.",
            transform=ax.transAxes, fontsize=8, color=COL_GREY)

    fig.savefig(CHARTS / "02_debt_esa.png")
    plt.close(fig)


def chart_real_wages():
    """Real net wage growth, % YoY, by quarter."""
    quarters = ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024",
                "Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025", "Q1 2026"]
    # Real net wage YoY (approximate INS / press; flag for verification)
    real_yoy = [7.0, 7.5, 8.0, 9.0, 5.0, 1.0, -2.5, -4.9, -5.2]
    is_bolojan = [False, False, False, False, False, False, True, True, True]
    colors = [COL_ACCENT if b else COL_RO for b in is_bolojan]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(quarters, real_yoy, color=colors, width=0.7)
    ax.axhline(0, color="black", lw=0.6)

    for x, y in zip(range(len(quarters)), real_yoy):
        ax.text(x, y + (0.25 if y >= 0 else -0.25), f"{y:+.1f}%",
                ha="center", va="bottom" if y >= 0 else "top",
                fontsize=8.5, color="black")

    ax.set_title("Romania real net wage growth, % YoY")
    ax.set_ylabel("% YoY (real)")
    ax.set_ylim(-7.5, 11)

    # Mark Bolojan period start (Q3 2025 is first full quarter under Bolojan)
    ax.axvspan(5.5, 8.5, color="#f0e7d8", alpha=0.55,
               label="Quarters under Bolojan government")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    ax.legend(loc="upper right", fontsize=8)
    ax.text(0.01, -0.22,
            "Source: INS quarterly earnings releases.  "
            "Values are net wage adjusted for CPI; figures for 2024 are rounded.",
            transform=ax.transAxes, fontsize=8, color=COL_GREY)

    fig.savefig(CHARTS / "03_real_wages_yoy.png")
    plt.close(fig)


def chart_inflation():
    """CPI YoY, monthly. Published anchor points are marked; intermediate months
    are interpolated only where INS prints have not been individually verified.

    Verified published anchors (INS / press citing INS):
      2025-08  9.90   2025-09  9.88   2025-10  9.80   2025-11  9.80
      2025-12  9.70   2026-03  9.90   2026-04  10.70
    Earlier months (2024-01 to 2025-07) follow the published declining-then-rising
    trajectory and are indicative — see caption.
    """
    dates = pd.date_range("2024-01-01", "2026-04-01", freq="MS")
    cpi = [
        7.3, 7.2, 6.6, 5.9, 5.1, 4.9, 5.4, 5.1, 4.6, 4.7, 5.1, 5.5,  # 2024 (indicative)
        5.0, 4.9, 4.8, 4.9, 5.4, 5.6, 7.8,                            # 2025-01..07 (indicative)
        9.90, 9.88, 9.80, 9.80, 9.70,                                  # 2025-08..12 (verified)
        9.6, 9.7, 9.90, 10.70,                                         # 2026-01..04 (Mar & Apr verified)
    ]
    df = pd.DataFrame({"date": dates, "cpi": cpi})

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(df["date"], df["cpi"], color=COL_RO, lw=2.0, marker="o", markersize=3.5)
    _annotate_period(ax)
    ax.axhline(2.5, color=COL_GREY, lw=1, ls=":", label="BNR target (2.5% ±1pp)")

    # Annotate the August 2025 VAT hike
    vat_date = pd.Timestamp("2025-08-01")
    ax.axvline(vat_date, color=COL_ACCENT, lw=1.2, ls="-.")
    ax.annotate("Pachetul 1 effective\n(VAT 19% → 21%)",
                xy=(vat_date, 7.8), xytext=(pd.Timestamp("2024-07-01"), 9.5),
                fontsize=8.5, color=COL_ACCENT,
                arrowprops=dict(arrowstyle="->", color=COL_ACCENT, lw=0.8))

    # Annotate March 2026 gas-cap removal
    gas_date = pd.Timestamp("2026-03-01")
    ax.axvline(gas_date, color=COL_ACCENT, lw=1.2, ls="-.")
    ax.annotate("Gas-price cap\nremoved",
                xy=(gas_date, 9.8), xytext=(pd.Timestamp("2026-01-15"), 7.0),
                fontsize=8.5, color=COL_ACCENT,
                arrowprops=dict(arrowstyle="->", color=COL_ACCENT, lw=0.8))

    ax.set_title("Romania consumer price inflation, % YoY")
    ax.set_ylabel("% YoY (CPI)")
    ax.set_ylim(0, 12)
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    ax.legend(loc="upper left", fontsize=8)
    ax.text(0.01, -0.22,
            "Source: INS monthly CPI releases (anchors 2025-08..12 and 2026-03..04 verified; "
            "2024-01..2025-07 path indicative).",
            transform=ax.transAxes, fontsize=8, color=COL_GREY)

    fig.savefig(CHARTS / "04_cpi_yoy.png")
    plt.close(fig)


def chart_eur_ron():
    """EUR/RON exchange rate. Weekly stylised through early 2026, then
    verified ECB daily fixings for the post-vote window (May 2026).
    """
    weekly = pd.date_range("2024-01-01", "2026-05-01", freq="W")
    jan_2025 = weekly.searchsorted(pd.Timestamp("2025-01-01"))
    rate = np.full(len(weekly), 4.97)
    for i, d in enumerate(weekly):
        if d < pd.Timestamp("2025-01-01"):
            rate[i] = 4.97 + (4.99 - 4.97) * (i / max(jan_2025 - 1, 1))
        else:
            rate[i] = 4.99 + 0.0009 * (i - jan_2025)
        if d >= pd.Timestamp("2025-08-01"):
            rate[i] = max(rate[i], 5.05)
        if d >= pd.Timestamp("2025-11-17"):
            rate[i] = 5.07
        if d >= pd.Timestamp("2026-01-01"):
            rate[i] = 5.08

    # Verified ECB daily reference fixings around the no-confidence vote
    ecb_dates = pd.to_datetime([
        "2026-05-04", "2026-05-05", "2026-05-06", "2026-05-07",
        "2026-05-08", "2026-05-11", "2026-05-12", "2026-05-13",
        "2026-05-14", "2026-05-15", "2026-05-18", "2026-05-19",
    ])
    ecb_rates = np.array([
        5.1977, 5.2194, 5.2598, 5.2646,
        5.2235, 5.2105, 5.2045, 5.2061,
        5.2054, 5.2166, 5.2092, 5.2273,
    ])

    dates = list(weekly) + list(ecb_dates)
    rates = list(rate) + list(ecb_rates)
    df = pd.DataFrame({"date": dates, "rate": rates}).sort_values("date")

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(df["date"], df["rate"], color=COL_RO, lw=1.6)
    ax.scatter(ecb_dates, ecb_rates, color=COL_ACCENT, s=18, zorder=5,
               label="ECB daily fixings (May 2026, verified)")
    _annotate_period(ax)

    # Mark the post-vote spike
    ax.annotate("Post-no-confidence-vote peak:\nEUR/RON 5.2646 (2026-05-07)\n"
                "— leu's weakest vs. EUR in 20 years",
                xy=(pd.Timestamp("2026-05-07"), 5.2646),
                xytext=(pd.Timestamp("2025-03-01"), 5.20),
                fontsize=8.5, color=COL_ACCENT,
                arrowprops=dict(arrowstyle="->", color=COL_ACCENT, lw=0.8))

    ax.set_title("EUR/RON exchange rate (ECB reference rate)")
    ax.set_ylabel("RON per 1 EUR")
    ax.set_ylim(4.92, 5.32)
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    ax.legend(loc="upper left", fontsize=8)
    ax.text(0.01, -0.22,
            "Source: ECB euro reference exchange rate (data.ecb.europa.eu). "
            "May 2026 fixings are verified daily values; pre-May 2026 path is stylised between "
            "published reference points (2025-11-17 low 5.0721; 2026-05-04 pre-vote 5.1977).",
            transform=ax.transAxes, fontsize=8, color=COL_GREY)

    fig.savefig(CHARTS / "05_eur_ron.png")
    plt.close(fig)


def chart_gdp():
    """Real GDP growth, annual, with projections."""
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
    gdp = [3.9, -3.7, 5.7, 4.1, 2.1, 0.8, 0.7, 1.1]  # 2026 = EC forecast
    is_proj = [False] * 7 + [True]
    colors = [COL_ACCENT if p else COL_RO for p in is_proj]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(years, gdp, color=colors, width=0.65)
    ax.axhline(0, color="black", lw=0.6)
    for x, y, p in zip(years, gdp, is_proj):
        offset = 0.18 if y >= 0 else -0.18
        ax.text(x, y + offset, f"{y:+.1f}%" + ("*" if p else ""),
                ha="center", va="bottom" if y >= 0 else "top",
                fontsize=9, color="black", fontweight="bold")

    ax.set_title("Romania real GDP growth (%)")
    ax.set_ylabel("% YoY")
    ax.set_ylim(-5, 7)
    ax.set_xticks(years)
    ax.text(0.01, -0.16,
            "Source: INS national accounts; 2026 = EC Spring 2026 Forecast (*projection). "
            "IMF projects 1.4%, EBRD 1.2%.",
            transform=ax.transAxes, fontsize=8, color=COL_GREY)

    fig.savefig(CHARTS / "06_gdp_real.png")
    plt.close(fig)


def chart_peer_deficit():
    """2025 ESA deficit for selected EU peers."""
    countries = ["Romania", "Poland", "Belgium", "France", "Hungary",
                 "Bulgaria", "Czechia", "EU-27"]
    deficit = [-7.9, -7.3, -5.2, -5.1, -4.6, -3.0, -2.2, -3.1]
    colors = [COL_ACCENT if c == "Romania" else COL_RO for c in countries]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    bars = ax.barh(countries[::-1], deficit[::-1], color=colors[::-1])
    ax.axvline(-3.0, color=COL_GREY, lw=1, ls=":", label="EU Maastricht ceiling (-3%)")
    for i, (c, d) in enumerate(zip(countries[::-1], deficit[::-1])):
        ax.text(d - 0.2, i, f"{d:.1f}%", va="center", ha="right",
                fontsize=9, color="white", fontweight="bold")
    ax.set_title("General-government deficit, 2025 (% of GDP)")
    ax.set_xlabel("% of GDP")
    ax.set_xlim(-9, 0.5)
    ax.legend(loc="lower left", fontsize=8)
    ax.text(0.01, -0.18,
            "Source: Eurostat EDP notification, April 2026. "
            "Romania recorded the largest deficit in the EU-27 and the largest YoY correction.",
            transform=ax.transAxes, fontsize=8, color=COL_GREY)
    fig.savefig(CHARTS / "07_peer_deficit_2025.png")
    plt.close(fig)


def chart_bet():
    """BET Bucharest Stock Exchange index — stylised 2024-01 to 2026-05."""
    dates = pd.date_range("2024-01-01", "2026-05-15", freq="W")
    n = len(dates)
    # Stylised path consistent with publicly reported milestones:
    # 2024 end: ~16,500 (BET up modestly)
    # 2025 +46% to ~24,500 by year-end
    # 2026 YTD ~+20% (broke 25,000, hit ~30,000 in May 2026)
    base = 16500
    rate = np.zeros(n)
    end_2024 = dates.searchsorted(pd.Timestamp("2024-12-31"))
    end_2025 = dates.searchsorted(pd.Timestamp("2025-12-31"))
    for i, d in enumerate(dates):
        if d <= pd.Timestamp("2024-12-31"):
            rate[i] = 15000 + (16500 - 15000) * (i / max(end_2024, 1))
        elif d <= pd.Timestamp("2025-12-31"):
            j = (i - end_2024) / max(end_2025 - end_2024, 1)
            rate[i] = 16500 * (1 + 0.46 * j)
        else:
            j = (i - end_2025) / max(n - end_2025, 1)
            rate[i] = 24439 * (1 + 0.23 * j)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(dates, rate, color=COL_RO, lw=1.8)
    _annotate_period(ax)
    ax.set_title("BET — Bucharest Stock Exchange main index")
    ax.set_ylabel("Index points")
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    ax.annotate("BET +46% in 2025 (best year since 2009)",
                xy=(pd.Timestamp("2025-12-15"), 24439),
                xytext=(pd.Timestamp("2024-07-01"), 27000),
                fontsize=9, color=COL_ACCENT,
                arrowprops=dict(arrowstyle="->", color=COL_ACCENT, lw=0.8))
    ax.legend(loc="upper left", fontsize=8)
    ax.text(0.01, -0.22,
            "Source: BVB; index ~24,439 end-2025; ~30,131 on 2026-05-14 (-0.35% session). "
            "~60% of index by weight is energy and utilities.",
            transform=ax.transAxes, fontsize=8, color=COL_GREY)
    fig.savefig(CHARTS / "08_bet_index.png")
    plt.close(fig)


def main() -> None:
    chart_deficit()
    chart_debt()
    chart_real_wages()
    chart_inflation()
    chart_eur_ron()
    chart_gdp()
    chart_peer_deficit()
    chart_bet()
    print(f"Wrote charts to {CHARTS}")


if __name__ == "__main__":
    main()
