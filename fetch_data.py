"""
fetch_data.py
-------------
Pulls the data for "Dashboard 1: US Crude Oil Production" from the U.S. Energy
Information Administration (EIA) API and saves each series locally for the
dashboard to read.

It pulls five things:
    1. Total US crude oil production, monthly, back to 1920   (series MCRFPUS2)
    2. Production by basin/region, monthly                    (STEO regional series)
    3. State-level crude production, annual, back to 1981     (a "proxy" for deep
       basin history before the basin data begins in 2008)
    4. WTI crude oil spot price, monthly, back to 1986        (series RWTC)
    5. (Optional) inflation-adjusted "real" WTI               (needs a FRED key)

You never type your API key here. It is read from the .env file, so the key
stays in one private place and never ends up in this code, in git, or in a
screenshot.

If any single source fails, the script keeps going, saves everything else, and
tells you plainly at the end what failed. It never invents numbers.

Run it with:
    python fetch_data.py
(or just double-click "Update Oil Prices.bat")
"""

import os
import json
import time
import calendar
import urllib.request
import urllib.parse
from datetime import datetime


# --- Load API keys from .env ----------------------------------------------
# Reads lines like  EIA_API_KEY=abc123  out of a file called .env and makes
# them available without the key ever appearing in this script.
def load_env(path=".env"):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                name, value = line.split("=", 1)
                os.environ.setdefault(name.strip(), value.strip())


load_env()
EIA_API_KEY = os.environ.get("EIA_API_KEY")
FRED_API_KEY = os.environ.get("FRED_API_KEY")  # optional

if not EIA_API_KEY:
    raise SystemExit(
        "No EIA_API_KEY found.\n"
        "Copy .env.example to .env and paste your key after the = sign."
    )


# --- Small HTTP helper with retries ---------------------------------------
# The EIA server occasionally returns a transient 500. We retry a few times
# before giving up, so a momentary hiccup doesn't fail the whole run.
def http_json(url, tries=5):
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                return json.load(response)
        except Exception as e:  # noqa: BLE001  (we want to retry on anything)
            last = e
            time.sleep(1.5 * (i + 1))
    raise last


def eia(path, params):
    """Call the EIA v2 API and return the parsed JSON."""
    params = dict(params)
    params["api_key"] = EIA_API_KEY
    url = "https://api.eia.gov/v2/" + path + "?" + urllib.parse.urlencode(params, doseq=True)
    return http_json(url)


def eia_series(path, series_facet, series_id, frequency):
    """Pull one full EIA series as a list of raw rows (oldest first)."""
    data = eia(path.rstrip("/") + "/data/", {
        "frequency": frequency,
        "data[0]": "value",
        f"facets[{series_facet}][]": series_id,
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
        "offset": 0,
        "length": 5000,
    })
    return data["response"]["data"]


# --- Output helpers --------------------------------------------------------
os.makedirs("data", exist_ok=True)
NOW = datetime.now().strftime("%Y-%m-%d %H:%M")


def save(name, js_var, payload):
    """Save a payload two ways: clean .json and a window.<VAR> .js file.

    The .js file is what lets index.html work from a double-click with no local
    server (the page never has to fetch() a local file)."""
    with open(f"data/{name}.json", "w") as f:
        json.dump(payload, f, indent=2)
    with open(f"data/{name}.js", "w") as f:
        f.write(f"window.{js_var} = " + json.dumps(payload) + ";")


# Track what worked and what didn't, so we can report honestly at the end.
report = []      # list of (label, detail) success lines
failures = []    # list of (label, reason)


# ===========================================================================
# 1. TOTAL US CRUDE PRODUCTION  (MCRFPUS2, monthly, back to 1920)
#    EIA reports this in thousand barrels/day; we convert to million bbl/day
#    so every production chart on the dashboard shares one unit.
# ===========================================================================
total_actuals_cutoff = None
try:
    rows = eia_series("petroleum/crd/crpdn", "series", "MCRFPUS2", "monthly")
    series = [
        {"date": r["period"], "value": round(float(r["value"]) / 1000.0, 4)}
        for r in rows if r.get("value") is not None
    ]
    series.sort(key=lambda r: r["date"])
    total_actuals_cutoff = series[-1]["date"] if series else None
    save("total_us", "TOTAL_US_DATA", {
        "series_name": "U.S. Field Production of Crude Oil",
        "units": "million barrels per day",
        "source": "U.S. Energy Information Administration (EIA)",
        "series_id": "MCRFPUS2",
        "frequency": "monthly",
        "last_updated": NOW,
        "latest": series[-1] if series else None,
        "data": series,
    })
    report.append(("Total US production (MCRFPUS2)",
                   f"{len(series)} months, {series[0]['date']}..{series[-1]['date']}"))
except Exception as e:  # noqa: BLE001
    failures.append(("Total US production (MCRFPUS2)", str(e)))


# ===========================================================================
# 2. PRODUCTION BY BASIN / REGION  (STEO regional series, monthly)
#    These 8 regions sum to the national total. The 5 named shale basins plus
#    "Rest of L48" begin in 2008-12; Alaska and the Federal Gulf go back to
#    1990. STEO also publishes an 18-month forecast, so any month AFTER the
#    last actual total-US month is flagged "forecast" (the dashboard draws it
#    dashed) -- we never present a projection as history.
# ===========================================================================
BASIN_SERIES = [
    ("Permian",      "COPRPM"),
    ("Bakken",       "COPRBK"),
    ("Eagle Ford",   "COPREF"),
    ("Appalachia",   "COPRAP"),
    ("Haynesville",  "COPRHA"),
    ("Rest of L48 (Conventional)",  "COPRR48"),
    ("Federal Gulf", "PAPRPGLF"),
    ("Alaska",       "PAPRPAK"),
]
try:
    regions = []
    earliest, latest = None, None
    cutoff = total_actuals_cutoff or "2026-03"
    for name, sid in BASIN_SERIES:
        rows = eia_series("steo", "seriesId", sid, "monthly")
        pts = []
        for r in rows:
            if r.get("value") is None:
                continue
            period = r["period"]
            pts.append({
                "date": period,
                "value": round(float(r["value"]), 5),
                "forecast": period > cutoff,
            })
        pts.sort(key=lambda r: r["date"])
        if pts:
            earliest = min(earliest, pts[0]["date"]) if earliest else pts[0]["date"]
            latest = max(latest, pts[-1]["date"]) if latest else pts[-1]["date"]
        regions.append({"name": name, "series_id": sid, "data": pts})

    save("basins", "BASINS_DATA", {
        "series_name": "U.S. Crude Oil Production by Region",
        "units": "million barrels per day",
        "source": "U.S. Energy Information Administration (EIA), Short-Term Energy Outlook (STEO)",
        "frequency": "monthly",
        "actuals_through": cutoff,
        "note": ("The 5 named basins and 'Rest of L48' begin Dec 2008; Alaska "
                 "and the Federal Gulf go back to 1990. Months after "
                 f"{cutoff} are STEO forecast, shown dashed."),
        "last_updated": NOW,
        "regions": regions,
    })
    named = ", ".join(n for n, _ in BASIN_SERIES)
    report.append(("Production by basin (STEO)",
                   f"8 regions [{named}], {earliest}..{latest}; actuals through {cutoff}"))
except Exception as e:  # noqa: BLE001
    failures.append(("Production by basin (STEO)", str(e)))


# ===========================================================================
# 3. STATE-LEVEL CRUDE PRODUCTION  (annual, back to 1981)
#    Used as a DEEP-HISTORY PROXY for basin trends before the basin data
#    starts in 2008 -- e.g. Texas + New Mexico stand in for the Permian, North
#    Dakota + Montana for the Bakken. EIA reports these as thousand barrels for
#    the year; we convert to an annual-average million bbl/day so they line up
#    with the other production charts. This is clearly labeled a proxy on the
#    dashboard and is never presented as exact basin data.
# ===========================================================================
STATE_SERIES = [
    ("Texas",        "MCRFPTX1"),   # Permian (+ Eagle Ford, Gulf Coast)
    ("New Mexico",   "MCRFPNM1"),   # Permian
    ("North Dakota", "MCRFPND1"),   # Bakken
    ("Montana",      "MCRFPMT1"),   # Bakken
    ("Oklahoma",     "MCRFPOK1"),   # Anadarko / mid-continent
    ("Alaska",       "MCRFPAK1"),   # North Slope
    ("California",   "MCRFPCA1"),   # legacy conventional
    ("Louisiana",    "MCRFPLA1"),   # Gulf Coast / Haynesville
    ("Colorado",     "MCRFPCO1"),   # DJ Basin (Rest of L48)
    ("Wyoming",      "MCRFPWY1"),   # Rocky Mountain
]
try:
    states = []
    rng_lo, rng_hi = None, None
    for name, sid in STATE_SERIES:
        rows = eia_series("petroleum/crd/crpdn", "series", sid, "annual")
        pts = []
        for r in rows:
            if r.get("value") is None:
                continue
            year = r["period"]
            # thousand barrels for the YEAR -> annual-average million bbl/day
            days = 366 if (int(year) % 4 == 0 and (int(year) % 100 != 0 or int(year) % 400 == 0)) else 365
            mbpd = float(r["value"]) / days / 1000.0
            pts.append({"year": year, "value": round(mbpd, 5)})
        pts.sort(key=lambda r: r["year"])
        if pts:
            rng_lo = min(rng_lo, pts[0]["year"]) if rng_lo else pts[0]["year"]
            rng_hi = max(rng_hi, pts[-1]["year"]) if rng_hi else pts[-1]["year"]
        states.append({"name": name, "series_id": sid, "data": pts})

    save("states", "STATES_DATA", {
        "series_name": "State-Level Crude Oil Production (deep-history proxy)",
        "units": "million barrels per day (annual average)",
        "source": "U.S. Energy Information Administration (EIA)",
        "frequency": "annual",
        "note": ("State-level proxy. EIA's state crude history begins in 1981. "
                 "Texas+New Mexico approximate the Permian, North Dakota+Montana "
                 "the Bakken, etc. Approximate, not exact basin data."),
        "last_updated": NOW,
        "states": states,
    })
    report.append(("State-level proxy (annual)",
                   f"{len(STATE_SERIES)} states, {rng_lo}..{rng_hi}"))
except Exception as e:  # noqa: BLE001
    failures.append(("State-level proxy (annual)", str(e)))


# --- Consumer Price Index (CPI) for the inflation-adjusted "real" price ----
# Two sources, in order of preference:
#   (a) FRED series CPIAUCSL  -- used only if FRED_API_KEY is set in .env.
#   (b) BLS series CUSR0000SA0 -- the same CPI measure, no key required.
# This means the "real" price line works out of the box (via BLS), and
# automatically upgrades to FRED if you add a key. Returns {"YYYY-MM": level}.
def fetch_cpi_fred(key):
    url = ("https://api.stlouisfed.org/fred/series/observations"
           f"?series_id=CPIAUCSL&api_key={key}&file_type=json")
    obs = http_json(url)["observations"]
    return {o["date"][:7]: float(o["value"])
            for o in obs if o["value"] not in (".", "", None)}


def fetch_cpi_bls(start_year=1986):
    end_year = datetime.now().year
    cpi = {}
    # BLS's free (unregistered) API allows up to ~10 years of data per request.
    yr = start_year
    while yr <= end_year:
        hi = min(yr + 9, end_year)
        payload = json.dumps({
            "seriesid": ["CUSR0000SA0"],
            "startyear": str(yr), "endyear": str(hi),
        }).encode()
        req = urllib.request.Request(
            "https://api.bls.gov/publicAPI/v2/timeseries/data/",
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
        last = None
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    out = json.load(r)
                break
            except Exception as e:  # noqa: BLE001
                last = e
                time.sleep(1.5 * (attempt + 1))
        else:
            raise last
        for d in out["Results"]["series"][0]["data"]:
            val = d.get("value", "")
            if d["period"].startswith("M") and d["period"] != "M13":
                try:
                    cpi[f"{d['year']}-{d['period'][1:]}"] = float(val)
                except (ValueError, TypeError):
                    continue  # skip blanks / placeholder '-' values
        yr = hi + 1
    return cpi


def get_cpi():
    """Return ({YYYY-MM: cpi}, source_label). Tries FRED then BLS; raises if both fail."""
    if FRED_API_KEY:
        try:
            return fetch_cpi_fred(FRED_API_KEY), "FRED series CPIAUCSL"
        except Exception as e:  # noqa: BLE001
            failures.append(("CPI via FRED (falling back to BLS)", str(e)))
    return fetch_cpi_bls(), "BLS series CUSR0000SA0 (CPI-U, seasonally adjusted)"


# ===========================================================================
# 4. WTI CRUDE SPOT PRICE  (RWTC, monthly, back to 1986)
#    The original working pull, preserved. Saved to data/wti.js as
#    window.WTI_DATA exactly as before so nothing that relied on it breaks.
#    We also attach an inflation-adjusted "real" price using CPI (see above).
# ===========================================================================
try:
    rows = eia(
        "petroleum/pri/spt/data/", {
            "frequency": "monthly",
            "data[0]": "value",
            "facets[series][]": "RWTC",
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "offset": 0,
            "length": 5000,
        })["response"]["data"]

    series = [
        {"date": r["period"], "price": float(r["value"])}
        for r in rows if r.get("value") is not None
    ]
    series.sort(key=lambda r: r["date"])
    wti_tail = series[-12:]  # captured for the sanity-check print at the end

    # --- Latest DAILY spot price -------------------------------------------
    # The monthly RWTC value is a MONTHLY AVERAGE and lags ~6 weeks, so the
    # "latest month" can sit well above (or below) the current market. We pull
    # the same RWTC series at DAILY frequency (this is exactly FRED's
    # DCOILWTICO) so the dashboard can headline the real current spot price.
    spot_latest = None
    spot_recent = []
    try:
        drows = eia("petroleum/pri/spt/data/", {
            "frequency": "daily", "data[0]": "value", "facets[series][]": "RWTC",
            "sort[0][column]": "period", "sort[0][direction]": "desc", "length": 60,
        })["response"]["data"]
        dclean = [{"date": r["period"], "price": float(r["value"])}
                  for r in drows if r.get("value") is not None]
        if dclean:
            spot_latest = dclean[0]                      # most recent trading day
            spot_recent = list(reversed(dclean[:30]))    # oldest->newest, ~30 days
    except Exception as e:  # noqa: BLE001
        failures.append(("WTI daily spot (RWTC daily)", str(e)))

    real_note = "Inflation-adjusted price unavailable (CPI source could not be reached)."
    real_available = False
    cpi_source = None

    # --- 5. Inflation-adjusted WTI (real price) via CPI ---------------------
    try:
        cpi, cpi_source = get_cpi()
        base_month = max(cpi) if cpi else None       # most-recent CPI = "today's dollars"
        base = cpi.get(base_month) if base_month else None
        if base:
            for pt in series:
                c = cpi.get(pt["date"])
                if c:
                    pt["real"] = round(pt["price"] * base / c, 2)
            real_available = True
            real_note = (f"Real prices in {base_month} dollars, "
                         f"inflation-adjusted via {cpi_source}.")
    except Exception as e:  # noqa: BLE001
        real_note = f"Inflation adjustment skipped: {e}"
        failures.append(("Real (inflation-adjusted) WTI", str(e)))

    save("wti", "WTI_DATA", {
        "series_name": "WTI Crude Oil Spot Price (Cushing, OK)",
        "units": "dollars per barrel",
        "source": "U.S. Energy Information Administration (EIA), series RWTC",
        "series_id": "RWTC",
        "frequency": "monthly",
        "last_updated": NOW,
        "real_available": real_available,
        "real_note": real_note,
        "latest": series[-1] if series else None,        # latest MONTHLY average
        "spot_latest": spot_latest,                       # latest DAILY spot (current price)
        "spot_recent": spot_recent,                       # ~30 recent daily points
        "data": series,
    })
    extra = " (+ real $)" if real_available else " (nominal only)"
    report.append(("WTI spot price (RWTC)",
                   f"{len(series)} months, {series[0]['date']}..{series[-1]['date']}{extra}"))
    if spot_latest:
        report.append(("WTI daily spot (current)",
                       f"${spot_latest['price']:.2f} on {spot_latest['date']} "
                       f"(vs latest monthly avg ${series[-1]['price']:.2f} for {series[-1]['date']})"))
except Exception as e:  # noqa: BLE001
    failures.append(("WTI spot price (RWTC)", str(e)))


# ===========================================================================
# 6. NATURAL GAS  (production + Henry Hub spot price) -- all LIVE EIA data
#    Production: US marketed (N9050US2) & dry (N9070US2), monthly, reported in
#    MMcf/month -> converted to Bcf/d so it reads as a rate.
#    Price: Henry Hub spot (RNGWHHD), monthly for the chart + daily for the
#    current-price headline (same idea as WTI).
# ===========================================================================
def days_in_month(period):
    return calendar.monthrange(int(period[:4]), int(period[5:7]))[1]

natgas = {"last_updated": NOW,
          "sources": "EIA Natural Gas: marketed N9050US2, dry N9070US2, Henry Hub spot RNGWHHD",
          "production": {}, "henry_hub": {}}
try:
    prod = {}
    for sid, key in [("N9050US2", "marketed"), ("N9070US2", "dry")]:
        rows = eia_series("natural-gas/prod/sum", "series", sid, "monthly")
        pts = []
        for r in rows:
            if r.get("value") is None:
                continue
            bcfd = float(r["value"]) / 1000.0 / days_in_month(r["period"])  # MMcf/mo -> Bcf/d
            pts.append({"date": r["period"], "value": round(bcfd, 3)})
        pts.sort(key=lambda x: x["date"])
        prod[key] = pts
    natgas["production"] = {
        "marketed": prod.get("marketed", []), "dry": prod.get("dry", []),
        "units": "billion cubic feet per day (Bcf/d)",
        "series_ids": {"marketed": "N9050US2", "dry": "N9070US2"},
        "latest_marketed": prod["marketed"][-1] if prod.get("marketed") else None,
        "latest_dry": prod["dry"][-1] if prod.get("dry") else None,
    }
    mk = prod.get("marketed", [])
    report.append(("Natural gas production (EIA)",
                   f"marketed {len(mk)} mo + dry {len(prod.get('dry', []))} mo; "
                   f"latest {mk[-1]['date']} = {mk[-1]['value']} Bcf/d marketed" if mk else "no data"))
except Exception as e:  # noqa: BLE001
    failures.append(("Natural gas production (EIA)", str(e)))

try:
    mrows = eia("natural-gas/pri/fut/data/", {
        "frequency": "monthly", "data[0]": "value", "facets[series][]": "RNGWHHD",
        "sort[0][column]": "period", "sort[0][direction]": "asc", "length": 5000,
    })["response"]["data"]
    hh = [{"date": r["period"], "price": float(r["value"])} for r in mrows if r.get("value") is not None]
    hh.sort(key=lambda x: x["date"])

    hh_spot, hh_recent = None, []
    try:
        drows = eia("natural-gas/pri/fut/data/", {
            "frequency": "daily", "data[0]": "value", "facets[series][]": "RNGWHHD",
            "sort[0][column]": "period", "sort[0][direction]": "desc", "length": 60,
        })["response"]["data"]
        dclean = [{"date": r["period"], "price": float(r["value"])} for r in drows if r.get("value") is not None]
        if dclean:
            hh_spot = dclean[0]
            hh_recent = list(reversed(dclean[:30]))
    except Exception:  # noqa: BLE001
        pass

    natgas["henry_hub"] = {
        "monthly": hh, "spot_latest": hh_spot, "spot_recent": hh_recent,
        "units": "dollars per million Btu ($/MMBtu)", "series_id": "RNGWHHD",
        "latest": hh[-1] if hh else None,
    }
    detail = (f"{len(hh)} months {hh[0]['date']}..{hh[-1]['date']}"
              + (f"; spot ${hh_spot['price']:.2f} on {hh_spot['date']}" if hh_spot else "")) if hh else "no data"
    report.append(("Henry Hub gas price (RNGWHHD)", detail))
except Exception as e:  # noqa: BLE001
    failures.append(("Henry Hub gas price (RNGWHHD)", str(e)))

save("natgas", "NATGAS_DATA", natgas)


# ===========================================================================
# 7. S&P 500 via FRED (optional; needs FRED_API_KEY) -- for the WTI vs S&P chart.
#    FRED's SP500 series only goes back ~10 years. If no key, skip gracefully.
# ===========================================================================
sp_payload = {
    "available": False, "last_updated": NOW,
    "source": "FRED series SP500 (S&P 500 index)",
    "note": "Add FRED_API_KEY=yourkey to .env to enable the WTI vs S&P 500 comparison (FRED series SP500).",
    "data": [],
}
if FRED_API_KEY:
    try:
        url = ("https://api.stlouisfed.org/fred/series/observations"
               f"?series_id=SP500&api_key={FRED_API_KEY}&file_type=json&frequency=m")
        obs = http_json(url)["observations"]
        data = [{"date": o["date"][:7], "value": float(o["value"])}
                for o in obs if o["value"] not in (".", "", None)]
        if data:
            sp_payload = {
                "available": True, "last_updated": NOW,
                "source": "FRED series SP500 (S&P 500 index, monthly)",
                "note": f"FRED series SP500, monthly, {data[0]['date']}..{data[-1]['date']} (FRED history ~10 years).",
                "data": data,
            }
            report.append(("S&P 500 (FRED SP500)", f"{len(data)} months, {data[0]['date']}..{data[-1]['date']}"))
    except Exception as e:  # noqa: BLE001
        sp_payload["note"] = f"FRED key present but SP500 fetch failed: {e}"
        failures.append(("S&P 500 (FRED SP500)", str(e)))
save("sp500", "SP500_DATA", sp_payload)


# ===========================================================================
# 8. DRILLING PRODUCTIVITY (EIA STEO Table 10a) -- all LIVE, per region.
#    Active rigs, new wells drilled/completed, DUC count, new-well oil/rig.
#    DUC is pulled directly (DUCS* series), not derived. Months after the last
#    total-US actual are flagged "forecast" (STEO projects ~18 months out).
# ===========================================================================
DRILL_REGIONS = [
    ("Permian", "PM"), ("Bakken", "BK"), ("Eagle Ford", "EF"),
    ("Appalachia", "AP"), ("Haynesville", "HA"), ("Rest of L48 (Conventional)", "R48"),
]
DRILL_METRICS = [
    ("rigs",            "RIGS",  "active rigs (count)"),
    ("wells_drilled",   "NWD",   "new wells drilled per month (count)"),
    ("wells_completed", "NWC",   "new wells completed per month (count)"),
    ("duc",             "DUCS",  "drilled-but-uncompleted wells (count)"),
    ("oil_per_rig",     "CONWR", "new-well oil production per rig (bbl/d per rig)"),
]
drill_cutoff = total_actuals_cutoff or "2026-03"
drilling = {
    "last_updated": NOW,
    "source": "U.S. EIA Short-Term Energy Outlook (STEO) Table 10a / Drilling Productivity",
    "actuals_through": drill_cutoff,
    "regions": [name for name, _ in DRILL_REGIONS],
    "units": {key: unit for key, _, unit in DRILL_METRICS},
    "series_ids": {},
    "metrics": {key: {} for key, _, _ in DRILL_METRICS},
}
try:
    pulled = 0
    for key, prefix, _unit in DRILL_METRICS:
        for region, suf in DRILL_REGIONS:
            sid = prefix + suf
            drilling["series_ids"].setdefault(key, {})[region] = sid
            try:
                rows = eia_series("steo", "seriesId", sid, "monthly")
            except Exception as e:  # noqa: BLE001
                failures.append((f"Drilling {key} {region} ({sid})", str(e)))
                drilling["metrics"][key][region] = []
                continue
            pts = []
            for r in rows:
                if r.get("value") is None:
                    continue
                pts.append({"date": r["period"], "value": round(float(r["value"]), 4),
                            "forecast": r["period"] > drill_cutoff})
            pts.sort(key=lambda x: x["date"])
            drilling["metrics"][key][region] = pts
            pulled += 1
    # latest-actual snapshot per region/metric (for key-stat rows + DUC bar)
    snap = {}
    for region, _ in DRILL_REGIONS:
        snap[region] = {}
        for key, _, _ in DRILL_METRICS:
            series = drilling["metrics"][key].get(region, [])
            actual = [p for p in series if not p["forecast"]]
            snap[region][key] = actual[-1] if actual else (series[-1] if series else None)
    drilling["latest"] = snap
    save("drilling", "DRILLING_DATA", drilling)
    # national DUC = sum of regions at latest actual
    nat_duc = 0
    for region, _ in DRILL_REGIONS:
        s = snap[region].get("duc")
        if s:
            nat_duc += s["value"]
    report.append(("Drilling productivity (STEO Table 10a)",
                   f"{pulled}/{len(DRILL_METRICS)*len(DRILL_REGIONS)} series; "
                   f"national DUC ~{int(round(nat_duc))} at {drill_cutoff} (RIGS/NWD/NWC/DUCS/CONWR x 6 regions)"))
except Exception as e:  # noqa: BLE001
    failures.append(("Drilling productivity (STEO Table 10a)", str(e)))


try:
    wti_tail
except NameError:
    wti_tail = []


# ===========================================================================
# Plain-English summary
# ===========================================================================
print("\n" + "=" * 64)
print("  Dashboard 1: US Crude Oil Production -- data refresh")
print("=" * 64)
print(f"  Run at: {NOW}\n")

# Sanity-check print: the last 12 months of the WTI series, exactly as EIA
# returned it (the latest ~$102 is the real RWTC value -- not adjusted here).
if wti_tail:
    print("  WTI (RWTC) last 12 months [sanity check, raw from EIA]:")
    for pt in wti_tail:
        real = f"   real ${pt['real']:.2f}" if "real" in pt else ""
        print(f"    {pt['date']}   nominal ${pt['price']:.2f}{real}")
    print("")

print("  PULLED OK:")
if report:
    for label, detail in report:
        print(f"    - {label}: {detail}")
else:
    print("    (nothing succeeded)")

if not FRED_API_KEY:
    print("\n  NOTE:")
    print("    - Inflation-adjusted 'real' WTI uses the free BLS CPI (no key needed).")
    print("      Add FRED_API_KEY=yourkey to .env to use FRED's CPIAUCSL instead,")
    print("      and to enable the WTI vs S&P 500 chart (FRED series SP500).")

if failures:
    print("\n  FAILED (everything else was still saved):")
    for label, reason in failures:
        print(f"    - {label}: {reason}")
else:
    print("\n  No failures.")

print("\n  Files written to ./data/ : total_us, basins, states, wti, natgas, sp500, drilling  (.json + .js)")
print("  Open  index.html  in your browser to view the dashboard.")
print("=" * 64)
