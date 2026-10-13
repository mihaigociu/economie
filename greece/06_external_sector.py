"""
External Sector: current account, goods vs services balance (the distinctive
Greek pattern), tourism & shipping receipts, FDI, RRF disbursement.
Sources: World Bank (CA, FDI), Eurostat (bop_c6_a), EC RRF Scoreboard (live Qlik query)
"""

import warnings
warnings.filterwarnings("ignore")

from datetime import date

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import eurostat
import requests
import wbgapi as wb

OUTPUT   = "charts"
RAW_DATA = "raw-data"
import os; os.makedirs(OUTPUT, exist_ok=True); os.makedirs(RAW_DATA, exist_ok=True)

# Last calendar year requested from every source. Bump once a year; series that
# have not yet published LAST_YEAR simply end earlier (see trim()).
LAST_YEAR = 2025
RETRIEVED = date.today().isoformat()

def trim(df):
    """Drop all-NaN columns and leading/trailing all-NaN rows, so series that
    lack the most recent year(s) simply end earlier instead of plotting gaps/zeros."""
    df = df.dropna(axis=1, how="all")
    if df.empty:
        raise RuntimeError("fetched frame is empty after dropping all-NaN columns")
    return df.loc[df.first_valid_index():df.last_valid_index()]

def save_csv(df, name, source, url):
    """Write CSV with provenance header (read back with pd.read_csv(..., comment='#'))."""
    path = f"{RAW_DATA}/{name}.csv"
    with open(path, "w") as f:
        f.write(f"# source: {source}\n# url: {url}\n# retrieved: {RETRIEVED}\n")
        df.to_csv(f)
    print(f"  saved {path}")

def wb_series(indicator, economies, year_range=(2000, LAST_YEAR + 1)):
    df = wb.data.DataFrame(indicator, economy=economies, time=range(*year_range))
    df = df.T
    df.index = df.index.str.replace("YR", "").astype(int)
    return trim(df)

def wb_src(code):
    return (f"World Bank WDI, indicator {code}", f"https://data.worldbank.org/indicator/{code}")

PEERS_WB = ["GRC", "PRT", "ITA", "ESP", "CYP"]
WB_TO_LBL = {"GRC":"GR","PRT":"PT","ITA":"IT","ESP":"ES","CYP":"CY"}
PEER_LABELS = {"GR":"Greece","PT":"Portugal","IT":"Italy","ES":"Spain","CY":"Cyprus"}
COLORS = {"GR":"#c0392b","PT":"#e67e22","IT":"#27ae60","ES":"#2980b9","CY":"#8e44ad"}
PROG_START, PROG_END = 2010, 2018

def add_programme_shading(ax, label_y_frac=0.92):
    ax.axvspan(PROG_START, PROG_END, alpha=0.06, color="grey")
    ylim = ax.get_ylim()
    y = ylim[0] + (ylim[1] - ylim[0]) * label_y_frac
    ax.text((PROG_START + PROG_END) / 2, y, "Adjustment programmes\n2010-2018",
            ha="center", fontsize=8, color="#555")

def plot_peer_lines(ax, df, highlight="GR"):
    for iso in ["GR","PT","IT","ES","CY"]:
        if iso in df.columns:
            lw = 2.5 if iso == highlight else 1.4
            ax.plot(df.index, df[iso], label=PEER_LABELS[iso],
                    color=COLORS[iso], linewidth=lw, marker="o", markersize=3)

# ---------------------------------------------------------------------------
# 1. Current Account Balance (% of GDP)
# ---------------------------------------------------------------------------
print("Fetching current account...")
ca = wb_series("BN.CAB.XOKA.GD.ZS", PEERS_WB).rename(columns=WB_TO_LBL)
ca.index.name = "year"
save_csv(ca, "06a_current_account_pct_gdp", *wb_src("BN.CAB.XOKA.GD.ZS"))

fig, ax = plt.subplots(figsize=(13, 5))
plot_peer_lines(ax, ca)
ax.axhline(0, color="black", linewidth=0.8)
ax.fill_between(ca.index, ca["GR"], 0, where=ca["GR"] < 0, alpha=0.12, color=COLORS["GR"])
add_programme_shading(ax, label_y_frac=0.92)
if "GR" in ca.columns:
    el = ca["GR"].dropna()
    trough = el.loc[:2009].idxmin()   # pre-crisis low, not a later one
    ax.set_ylim(bottom=el.min() - 3)
    ax.annotate(f"Pre-crisis deficit\n{int(trough)}: {el[trough]:.0f}%",
                xy=(trough, el[trough]),
                xytext=(trough + 2, el[trough] - 1),
                fontsize=9, ha="left", color=COLORS["GR"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["GR"], lw=0.8))
ax.set_title("Current Account Balance (% of GDP)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/06a_current_account.png", dpi=150); plt.close()
print("  saved 06a_current_account.png")

# ---------------------------------------------------------------------------
# 2. Greek BoP: Goods vs Services balance — the distinctive Greek pattern
# ---------------------------------------------------------------------------
print("Fetching Greek BoP (goods vs services)...")
df_bop = eurostat.get_data_df("bop_c6_a")
common = ((df_bop["stk_flow"]=="BAL") & (df_bop["partner"]=="WRL_REST") &
          (df_bop["currency"]=="MIO_EUR") & (df_bop["geo\\TIME_PERIOD"]=="EL") &
          (df_bop["sectpart"]=="S1") & (df_bop["sector10"]=="S1"))
year_cols = sorted([c for c in df_bop.columns if str(c).isdigit() and 2000 <= int(c) <= LAST_YEAR])

BOP_ITEMS = {"G": "Goods", "S": "Services", "IN1": "Primary income",
             "IN2": "Secondary income", "CA": "Current account"}
components = {}
for item, label in BOP_ITEMS.items():
    sub = df_bop[common & (df_bop["bop_item"] == item)]
    if sub.empty:
        raise RuntimeError(f"bop_c6_a: no Greek data for {item}")
    s = sub[year_cols].iloc[0].astype(float)
    s.index = s.index.astype(int)
    components[label] = s / 1000  # to € bn

bop_df = trim(pd.DataFrame(components))
bop_df.index.name = "year"
save_csv(bop_df, "06b_greek_bop_components_bn_eur",
         "Eurostat bop_c6_a, BAL, partner WRL_REST, MIO_EUR, S1/S1, Greece (/1000 = EUR bn)", "https://ec.europa.eu/eurostat/databrowser/view/bop_c6_a/default/table")

fig, ax = plt.subplots(figsize=(13, 5))
# Goods (negative) and services (positive) both drawn from zero; the black line is the
# full current account (goods + services + primary + secondary income).
ax.bar(bop_df.index, bop_df["Goods"], label="Goods balance",
       color="#c0392b", alpha=0.85, width=0.7)
ax.bar(bop_df.index, bop_df["Services"], label="Services balance",
       color="#27ae60", alpha=0.85, width=0.7)
ax.plot(bop_df.index, bop_df["Current account"], label="Current account (total)",
        color="black", linewidth=2.5, marker="o", markersize=4)
ax.axhline(0, color="black", linewidth=0.8)
ax.set_ylim(bop_df["Goods"].min() * 1.12, bop_df["Services"].max() * 1.45)
add_programme_shading(ax, label_y_frac=0.93)
ax.set_title("Greece: Balance of Payments Components (€ billions)\n"
             "Services surplus (tourism + shipping) partly offsets the goods deficit",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("€ billions")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"€{x:.0f}bn"))
ax.legend(ncol=3, fontsize=9, loc="upper left"); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/06b_goods_vs_services.png", dpi=150); plt.close()
print("  saved 06b_goods_vs_services.png")

# ---------------------------------------------------------------------------
# 3. Tourism (SD travel) and Shipping (SC transport) services credits — the two pillars
# ---------------------------------------------------------------------------
print("Fetching tourism & shipping receipts...")
service_data = {}
for code, label in [("SC", "Transport (mainly shipping)"), ("SD", "Travel (tourism)")]:
    sub = df_bop[(df_bop["bop_item"]==code) & (df_bop["stk_flow"]=="CRE") &
                 (df_bop["partner"]=="WRL_REST") & (df_bop["currency"]=="MIO_EUR") &
                 (df_bop["geo\\TIME_PERIOD"]=="EL") & (df_bop["sectpart"]=="S1") &
                 (df_bop["sector10"]=="S1")]
    if sub.empty:
        raise RuntimeError(f"bop_c6_a: no Greek credits for {code}")
    s = sub[year_cols].iloc[0].astype(float)
    s.index = s.index.astype(int)
    service_data[label] = s / 1000

# Nominal GDP (EUR bn) to express receipts as % of GDP
df_gdp = eurostat.get_data_df("nama_10_gdp")
gcol = [c for c in df_gdp.columns if "geo" in c.lower()][0]
gdp_row = df_gdp[(df_gdp[gcol] == "EL") & (df_gdp["na_item"] == "B1GQ") & (df_gdp["unit"] == "CP_MEUR")]
if gdp_row.empty:
    raise RuntimeError("nama_10_gdp: no Greek nominal GDP")
gdp_el = gdp_row[year_cols].iloc[0].astype(float) / 1000
gdp_el.index = gdp_el.index.astype(int)
service_data["Nominal GDP (EUR bn, nama_10_gdp)"] = gdp_el
svc_df = trim(pd.DataFrame(service_data))
svc_df["Travel + transport (% of GDP)"] = ((svc_df["Transport (mainly shipping)"] + svc_df["Travel (tourism)"])
                                          / svc_df["Nominal GDP (EUR bn, nama_10_gdp)"] * 100)
svc_df.index.name = "year"
save_csv(svc_df, "06c_tourism_shipping_credits_bn_eur",
         "Eurostat bop_c6_a, CRE, SC (transport) and SD (travel), WRL_REST, MIO_EUR, Greece (/1000 = EUR bn); GDP from nama_10_gdp B1GQ CP_MEUR", "https://ec.europa.eu/eurostat/databrowser/view/bop_c6_a/default/table")
svc_df = svc_df[["Transport (mainly shipping)", "Travel (tourism)"]].dropna(how="any")   # stack only complete years

fig, ax = plt.subplots(figsize=(13, 5))
ax.stackplot(svc_df.index,
             svc_df["Transport (mainly shipping)"],
             svc_df["Travel (tourism)"],
             labels=["Transport (mainly shipping)", "Travel (tourism)"],
             colors=["#2980b9", "#e67e22"], alpha=0.85)
add_programme_shading(ax, label_y_frac=0.92)
# Mark COVID 2020
ax.axvline(2020, color="black", linestyle=":", linewidth=0.7, alpha=0.6)
ax.text(2020, svc_df.sum(axis=1).max() * 0.98, "COVID",
        rotation=90, va="top", ha="right", fontsize=8, color="#333")
ax.set_title("Greece: Tourism + Shipping Services Receipts (€ billions, gross credits)",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("€ billions")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"€{x:.0f}bn"))
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%d"))
ax.legend(loc="upper left", fontsize=9); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUTPUT}/06c_tourism_shipping.png", dpi=150); plt.close()
print("  saved 06c_tourism_shipping.png")

# ---------------------------------------------------------------------------
# 4. FDI net inflows (% of GDP)
# ---------------------------------------------------------------------------
print("Fetching FDI data...")
fdi = wb_series("BX.KLT.DINV.WD.GD.ZS", PEERS_WB).rename(columns=WB_TO_LBL)
fdi.index.name = "year"
save_csv(fdi, "06d_fdi_net_inflows_pct_gdp", *wb_src("BX.KLT.DINV.WD.GD.ZS"))

fig, ax = plt.subplots(figsize=(13, 5))
# Drop Cyprus from chart only — its SPV pass-through flows swing ±300-400% of GDP
# and dominate the y-axis. Data remains in the CSV.
fdi_plot = fdi.drop(columns=[c for c in ["CY"] if c in fdi.columns])
plot_peer_lines(ax, fdi_plot)
ax.axhline(0, color="black", linewidth=0.8)
add_programme_shading(ax, label_y_frac=0.92)
ax.set_title("FDI Net Inflows (% of GDP)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("% of GDP")
ax.legend(ncol=3, fontsize=9); ax.grid(axis="y", alpha=0.3)
cy = fdi["CY"].dropna() if "CY" in fdi.columns else pd.Series(dtype=float)
cy_note = (f" (e.g. {cy.max():+.0f}% {cy.idxmax()}, {cy.min():+.0f}% {cy.idxmin()})" if not cy.empty else "")
fig.text(0.5, -0.01,
         f"Cyprus excluded from chart: SPV pass-through flows produce extreme values{cy_note}. Data retained in CSV.",
         ha="center", fontsize=8, color="#555", style="italic")
plt.tight_layout(); plt.savefig(f"{OUTPUT}/06d_fdi.png", dpi=150, bbox_inches="tight"); plt.close()
print("  saved 06d_fdi.png")

# ---------------------------------------------------------------------------
# 5. RRF disbursement progress — fetched live from the EC Recovery & Resilience Scoreboard
# ---------------------------------------------------------------------------
# The Scoreboard (https://ec.europa.eu/economy_finance/recovery-and-resilience-scoreboard/)
# is a Qlik Sense app with an anonymous public engine. We open a websocket to the same
# engine the web page uses and query hypercubes directly. Stdlib-only websocket client
# (RFC 6455, text frames) to avoid an extra dependency. Any failure raises.
import base64, json as _json, socket, ssl, struct, urllib.parse

RRF_SCOREBOARD = "https://ec.europa.eu/economy_finance/recovery-and-resilience-scoreboard/disbursements.html"
QLIK_SERVER = "https://dashboard.tech.ec.europa.eu/qs_digit_dashboard_mt/public"
QLIK_APP = "67047f98-760d-49e0-b6a9-31b7b2a66fb1"   # from scoreboard scripts/qlik_engine_api.js

class QlikPublicApp:
    def __init__(self, server=QLIK_SERVER, app=QLIK_APP, timeout=90):
        sess = requests.Session()
        sess.get(server + "/hub", timeout=timeout).raise_for_status()
        xrf = "0123456789ABCDEF"
        r = sess.get(server + f"/qps/csrftoken?xrfkey={xrf}", headers={"X-Qlik-Xrfkey": xrf}, timeout=timeout)
        token = r.headers.get("qlik-csrf-token")
        if not token:
            raise RuntimeError(f"Qlik: no csrf token (HTTP {r.status_code})")
        u = urllib.parse.urlparse(server)
        path = f"{u.path}/app/{app}/engineData?qlik-csrf-token={urllib.parse.quote(token)}"
        raw = socket.create_connection((u.hostname, 443), timeout=timeout)
        self.sock = ssl.create_default_context().wrap_socket(raw, server_hostname=u.hostname)
        cookie = "; ".join(f"{k}={v}" for k, v in sess.cookies.get_dict().items())
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall((f"GET {path} HTTP/1.1\r\nHost: {u.hostname}\r\nUpgrade: websocket\r\n"
                           f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n"
                           f"Sec-WebSocket-Version: 13\r\nOrigin: https://ec.europa.eu\r\n"
                           f"Cookie: {cookie}\r\n\r\n").encode())
        resp = b""
        while b"\r\n\r\n" not in resp:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise RuntimeError("Qlik: websocket handshake closed")
            resp += chunk
        head, rest = resp.split(b"\r\n\r\n", 1)
        if b" 101 " not in head.split(b"\r\n")[0]:
            raise RuntimeError(f"Qlik: handshake failed: {head[:200]!r}")
        self.buf = bytearray(rest)
        self._id = 0
        self._recv()                                  # OnAuthenticationInformation
        r = self.call(-1, "OpenDoc", [app])
        self.doc = r["qReturn"]["qHandle"]

    def _exact(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise RuntimeError("Qlik: socket closed")
            self.buf += chunk
        out = bytes(self.buf[:n]); del self.buf[:n]
        return out

    def _recv(self):
        data = b""
        while True:
            b1, b2 = self._exact(2)
            n = b2 & 0x7F
            if n == 126: n = struct.unpack(">H", self._exact(2))[0]
            elif n == 127: n = struct.unpack(">Q", self._exact(8))[0]
            payload = self._exact(n)
            if (b1 & 0x0F) in (9, 10):                # ping / pong
                continue
            data += payload
            if b1 & 0x80:
                return _json.loads(data.decode())

    def call(self, handle, method, params):
        self._id += 1
        p = _json.dumps({"jsonrpc": "2.0", "id": self._id, "handle": handle,
                         "method": method, "params": params}).encode()
        hdr = bytearray([0x81])
        if len(p) < 126: hdr.append(0x80 | len(p))
        elif len(p) < 65536: hdr += bytes([0x80 | 126]) + struct.pack(">H", len(p))
        else: hdr += bytes([0x80 | 127]) + struct.pack(">Q", len(p))
        mask = os.urandom(4)
        self.sock.sendall(bytes(hdr) + mask + bytes(b ^ mask[k % 4] for k, b in enumerate(p)))
        while True:
            m = self._recv()
            if m.get("id") == self._id:
                if "error" in m:
                    raise RuntimeError(f"Qlik {method}: {m['error']}")
                return m["result"]

    def table(self, dims, measures):
        width = len(dims) + len(measures)
        d = {"qInfo": {"qType": "py"}, "qHyperCubeDef": {
            "qDimensions": [{"qDef": {"qFieldDefs": [x]}} for x in dims],
            "qMeasures": [{"qDef": {"qDef": m}} for m in measures]}}
        h = self.call(self.doc, "CreateSessionObject", [d])["qReturn"]["qHandle"]
        n = self.call(h, "GetLayout", [])["qLayout"]["qHyperCube"]["qSize"]["qcy"]
        page = 10000 // width                       # Qlik caps a data page at 10,000 cells
        rows = []
        for top in range(0, n, page):
            res = self.call(h, "GetHyperCubeData", ["/qHyperCubeDef", [
                {"qTop": top, "qLeft": 0, "qWidth": width, "qHeight": min(page, n - top)}]])
            rows += res["qDataPages"][0]["qMatrix"]
        if len(rows) != n:
            raise RuntimeError(f"Qlik: expected {n} rows, got {len(rows)}")
        out = pd.DataFrame([[c.get("qText") for c in r[:len(dims)]] +
                            [c.get("qNum") for c in r[len(dims):]] for r in rows],
                           columns=dims + measures)
        return out

print("Fetching RRF allocations & disbursements from the EC Scoreboard (Qlik engine)...")
q = QlikPublicApp()
load_date = q.table(["Load Date"], []).iloc[0, 0]
load_date_disb = q.table(["Load Date Disbursements"], []).iloc[0, 0]

# Allocation = grant + loan envelope incl. decommitments ("Total Forecast" by budget type,
# matching the Scoreboard's "left to pay" view); paid = sum of disbursements (net, incl.
# pre-financing). GDP is the Scoreboard's own reference GDP (EUR mn) and year.
alloc = q.table(["Payment/Forecast Country", "Budget Type"],
                ["=Sum([Total Forecast])", "=Sum([Total Payment])"])
alloc.columns = ["country", "type", "alloc_eur", "paid_eur"]
alloc = alloc.pivot_table(index="country", columns="type", values=["alloc_eur", "paid_eur"],
                          aggfunc="sum").fillna(0)
alloc.columns = [f"{a}_{b.lower()}" for a, b in alloc.columns]
gdp = q.table(["Country"], ["=Sum([Country GDP])", "=Only([Country GDP Year])"])
gdp.columns = ["country", "gdp_meur", "gdp_year"]
gdp = gdp[gdp["country"] != "EU"].set_index("country")
payments = q.table(["Payment Country", "Payment Date", "Payment Request Description",
                    "Payment Loans/Grants"], ["=Sum([Paid Amount])"])
payments.columns = ["country", "date", "payment", "type", "paid_eur"]
payments["date"] = pd.to_datetime(payments["date"], format="%d/%m/%Y")
requests_tbl = q.table(["Payment Request Country", "Request Date", "Request Status",
                        "Actual Payment Date"], ["=Sum([Requested Net Amount])"])
requests_tbl.columns = ["country", "request_date", "status", "payment_date", "requested_net_eur"]

rrf_df = pd.DataFrame({
    "alloc_grants_bn": alloc.get("alloc_eur_grants", 0) / 1e9,
    "alloc_loans_bn":  alloc.get("alloc_eur_loans", 0) / 1e9,
    "disb_grants_bn":  alloc.get("paid_eur_grants", 0) / 1e9,
    "disb_loans_bn":   alloc.get("paid_eur_loans", 0) / 1e9,
})
rrf_df["alloc"] = rrf_df["alloc_grants_bn"] + rrf_df["alloc_loans_bn"]
rrf_df["disb"] = rrf_df["disb_grants_bn"] + rrf_df["disb_loans_bn"]
# cross-check: paid by budget type must equal the sum of individual payments
chk = payments.groupby("country")["paid_eur"].sum() / 1e9
if (chk.reindex(rrf_df.index).fillna(0) - rrf_df["disb"]).abs().max() > 0.01:
    raise RuntimeError("RRF: payment totals do not reconcile")
rrf_df["disb_pct"] = rrf_df["disb"] / rrf_df["alloc"] * 100
rrf_df["gdp_year"] = gdp["gdp_year"].astype(int)
rrf_df["alloc_pct_gdp"] = rrf_df["alloc"] * 1e3 / gdp["gdp_meur"] * 100
rrf_df["alloc_pct_gdp_rank_eu27"] = rrf_df["alloc_pct_gdp"].rank(ascending=False).astype(int)
rrf_df["disb_pct_rank_eu27"] = rrf_df["disb_pct"].rank(ascending=False).astype(int)
rrf_df["last_payment"] = payments.groupby("country")["date"].max().dt.date
pending = requests_tbl[requests_tbl["status"].str.contains("Assessment|Submitted|Pending", case=False, na=False)]
rrf_df["pending_requests_bn"] = (pending.groupby("country")["requested_net_eur"].sum() / 1e9).reindex(rrf_df.index).fillna(0)
rrf_df = rrf_df.round(3).sort_values("alloc_pct_gdp", ascending=False)
rrf_df.index.name = "country"
if len(rrf_df) != 27:
    raise RuntimeError(f"RRF: expected 27 member states, got {len(rrf_df)}")
src_note = (f"EC Recovery and Resilience Scoreboard (Qlik engine, app {QLIK_APP}); "
            f"app load date {load_date}, disbursements load date {load_date_disb}; EUR bn; "
            f"GDP = Scoreboard reference GDP")
save_csv(rrf_df, "06e_rrf_progress", src_note, RRF_SCOREBOARD)
gr_pay = payments[payments["country"] == "Greece"].sort_values(["date", "type"])
gr_pay = gr_pay.assign(paid_bn=(gr_pay["paid_eur"] / 1e9).round(3)).drop(columns=["country", "paid_eur"])
save_csv(gr_pay.set_index("date"), "06e_rrf_greece_payments", src_note, RRF_SCOREBOARD)
gr_req = requests_tbl[requests_tbl["country"] == "Greece"].drop(columns="country")
gr_req = gr_req[gr_req["request_date"] != "-"]
gr_req = gr_req.assign(requested_net_bn=(gr_req["requested_net_eur"] / 1e9).round(3)).drop(columns="requested_net_eur")
save_csv(gr_req.set_index("request_date"), "06e_rrf_greece_payment_requests", src_note, RRF_SCOREBOARD)
as_of = payments["date"].max()
print(f"  latest payment in Scoreboard: {as_of:%d %b %Y}; Greece {rrf_df.loc['Greece','disb']:.2f} of "
      f"{rrf_df.loc['Greece','alloc']:.2f} bn ({rrf_df.loc['Greece','disb_pct']:.1f}%)")

CHART_SET = ["Greece", "Italy", "Spain", "Portugal", "Romania", "Croatia", "Cyprus"]
plot_df = rrf_df.loc[CHART_SET]
eu_rate = rrf_df["disb"].sum() / rrf_df["alloc"].sum() * 100

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
ax = axes[0]
order = plot_df.sort_values("disb_pct")
bar_colors = ["#c0392b" if c == "Greece" else "#95a5a6" for c in order.index]
ax.barh(order.index, order["disb_pct"], color=bar_colors)
for i, v in enumerate(order["disb_pct"]):
    ax.text(v + 1, i, f"{v:.0f}%", va="center", fontsize=9)
ax.axvline(eu_rate, color="#2980b9", linestyle="--", linewidth=1.2,
           label=f"EU27: {eu_rate:.0f}%")
ax.set_xlim(0, 105)
ax.set_title(f"RRF Disbursed (% of grants + loans, to {as_of:%d %b %Y})",
             fontsize=12, fontweight="bold")
ax.set_xlabel("% disbursed"); ax.legend(fontsize=9, loc="lower right"); ax.grid(axis="x", alpha=0.3)

ax2 = axes[1]
gy = int(plot_df["gdp_year"].iloc[0])
order2 = plot_df.sort_values("alloc_pct_gdp")
bar_colors2 = ["#c0392b" if c == "Greece" else "#95a5a6" for c in order2.index]
ax2.barh(order2.index, order2["alloc_pct_gdp"], color=bar_colors2)
for i, v in enumerate(order2["alloc_pct_gdp"]):
    ax2.text(v + 0.2, i, f"{v:.1f}%", va="center", fontsize=9)
ax2.set_xlim(0, order2["alloc_pct_gdp"].max() * 1.12)
ax2.set_title(f"RRF Total Allocation (% of {gy} GDP)", fontsize=12, fontweight="bold")
ax2.set_xlabel(f"% of {gy} GDP"); ax2.grid(axis="x", alpha=0.3)

gr_rank = int(rrf_df.loc["Greece", "alloc_pct_gdp_rank_eu27"])
rank_txt = "the largest" if gr_rank == 1 else f"the #{gr_rank}"
fig.suptitle(f"Greece has {rank_txt} RRF envelope relative to GDP in the EU27",
             fontsize=13, fontweight="bold")
fig.text(0.5, -0.01, f"Source: EC Recovery and Resilience Scoreboard, retrieved {RETRIEVED}.",
         ha="center", fontsize=8, color="#555", style="italic")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/06e_rrf.png", dpi=150, bbox_inches="tight"); plt.close()
print("  saved 06e_rrf.png")

print("\nDone — external sector charts saved to", OUTPUT)
