"""
Shared helpers for the Romania report scripts (01_…08_).

Every CSV written to raw-data/ starts with `# source:` / `# url:` /
`# retrieved:` header lines (plus optional `# note:` lines). Read them back with
    pd.read_csv(path, comment="#", index_col=0)
or with `read_csv()` below.

Fetch helpers raise on failure — no script silently falls back to stale,
hand-typed numbers. Re-running the scripts picks up whatever the sources
currently publish (e.g. the Eurostat EDP notifications of April and October).
"""

import datetime
import os
import time
import warnings

warnings.filterwarnings("ignore")

import pandas as pd
from matplotlib.ticker import MaxNLocator
import eurostat
import wbgapi as wb

OUTPUT = "charts"
RAW_DATA = "raw-data"
os.makedirs(OUTPUT, exist_ok=True)
os.makedirs(RAW_DATA, exist_ok=True)

TODAY = datetime.date.today().isoformat()

PEERS = ["RO", "PL", "CZ", "HU", "BG"]
PEER_LABELS = {"RO": "Romania", "PL": "Poland", "CZ": "Czechia",
               "HU": "Hungary", "BG": "Bulgaria", "EU27_2020": "EU27", "EU": "EU27"}
COLORS = {"RO": "#c0392b", "PL": "#2980b9", "CZ": "#27ae60",
          "HU": "#8e44ad", "BG": "#e67e22", "EU27_2020": "#7f8c8d", "EU": "#7f8c8d"}
WB_CODES = ["ROU", "POL", "CZE", "HUN", "BGR"]
WB_MAP = dict(zip(WB_CODES, PEERS))


def es_url(code):
    return f"https://ec.europa.eu/eurostat/databrowser/view/{code}/default/table"


def wb_url(indicator):
    return f"https://data.worldbank.org/indicator/{indicator}"


# ---------------------------------------------------------------------------
# CSV I/O
# ---------------------------------------------------------------------------
def save_csv(df, name, source, url, notes=()):
    """Write df to raw-data/<name>.csv with provenance header comments."""
    path = f"{RAW_DATA}/{name}.csv"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# source: {source}\n")
        f.write(f"# url: {url}\n")
        f.write(f"# retrieved: {TODAY}\n")
        for n in notes:
            f.write(f"# note: {n}\n")
        df.to_csv(f)
    print(f"  saved {path}")


def read_csv(name, **kw):
    return pd.read_csv(f"{RAW_DATA}/{name}.csv", comment="#", index_col=0, **kw)


# ---------------------------------------------------------------------------
# Cleaning
# ---------------------------------------------------------------------------
def trim(df):
    """Drop all-NaN columns, then leading/trailing all-NaN rows (interior gaps kept)."""
    if isinstance(df, pd.Series):
        s = df.dropna()
        return df.loc[s.index.min():s.index.max()] if len(s) else df.iloc[0:0]
    df = df.dropna(axis=1, how="all")
    has = df.notna().any(axis=1)
    if not has.any():
        return df.iloc[0:0]
    first, last = has[has].index.min(), has[has].index.max()
    return df.loc[first:last]


def require(df, what, min_rows=1):
    if df is None or len(df.dropna(how="all")) < min_rows:
        raise RuntimeError(f"{what}: fetch returned no usable data")
    return df


# ---------------------------------------------------------------------------
# World Bank
# ---------------------------------------------------------------------------
def wb_series(indicator, economies, start, end, col_map=None, retries=6):
    """Annual WB series for start..end inclusive; year index, trimmed."""
    for attempt in range(retries):
        try:
            df = wb.data.DataFrame(indicator, economy=economies,
                                   time=range(start, end + 1))
            break
        except Exception as e:
            if attempt == retries - 1:
                raise
            print(f"  WB retry {attempt + 1} ({str(e)[:60]})")
            time.sleep(10 * (attempt + 1))
    df = df.T
    df.index = df.index.str.replace("YR", "").astype(int)
    df.index.name = "year"
    if col_map:
        df = df.rename(columns=col_map)
        df = df[[c for c in col_map.values() if c in df.columns]]
    return require(trim(df.astype(float)), indicator)


# ---------------------------------------------------------------------------
# Eurostat
# ---------------------------------------------------------------------------
_ES_CACHE = {}


def eurostat_df(code, retries=3):
    if code not in _ES_CACHE:
        for attempt in range(retries):
            try:
                _ES_CACHE[code] = eurostat.get_data_df(code)
                break
            except Exception as e:
                if attempt == retries - 1:
                    raise
                print(f"  Eurostat retry {attempt + 1} for {code} ({e})")
                time.sleep(5)
    return _ES_CACHE[code]


def geo_col(df):
    return [c for c in df.columns if "geo" in c.lower()][0]


def eurostat_wide(code, filters, geos, start=None, end=None, monthly=False):
    """Return a time x geo DataFrame from a Eurostat dataset.

    filters: dict column -> value; geos: list of geo codes (column order kept).
    Annual: integer year index limited to start..end. Monthly: 'YYYY-MM' index.
    """
    df = eurostat_df(code)
    g = geo_col(df)
    mask = df[g].isin(geos)
    for k, v in filters.items():
        mask &= df[k] == v
    sub = df[mask]
    if sub[g].duplicated().any():
        raise RuntimeError(f"{code}: filters {filters} not unique per geo")
    sub = sub.set_index(g)
    if monthly:
        cols = [c for c in sub.columns if len(str(c)) == 7 and str(c)[4] == "-"]
    else:
        cols = [c for c in sub.columns if str(c).isdigit()
                and (start is None or int(c) >= start)
                and (end is None or int(c) <= end)]
    out = sub[cols].T.astype(float)
    if not monthly:
        out.index = out.index.astype(int)
    out.index.name = "month" if monthly else "year"
    out = out[[x for x in geos if x in out.columns]]
    return require(trim(out), code)


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
def plot_peers(ax, df, labels=PEER_LABELS, colors=COLORS, highlight="RO",
               dashed=("EU27_2020", "EU", "EA", "EA20"), markersize=3):
    for c in df.columns:
        s = df[c].dropna()
        if s.empty:
            continue
        lw = 2.5 if c == highlight else 1.4
        ls = "--" if c in dashed else "-"
        ax.plot(s.index, s.values, label=labels.get(c, c), color=colors.get(c, "#333"),
                linewidth=lw, linestyle=ls, marker="o", markersize=markersize)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))


def year_span(df):
    """'2000–2025' style span from a year-indexed frame/series."""
    idx = df.dropna(how="all").index if isinstance(df, pd.DataFrame) else df.dropna().index
    return f"{idx.min()}–{idx.max()}"


def last_year(df, col=None):
    s = df[col] if col is not None else df
    return int(s.dropna().index.max())
