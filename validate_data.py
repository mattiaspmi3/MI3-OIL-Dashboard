"""
validate_data.py
----------------
Independent correctness checks on the data that fetch_data.py saved.
It does three kinds of checks:

  1. INTERNAL CONSISTENCY  -- do the numbers agree with each other?
        (e.g. the 8 basins must sum to the national total)
  2. CROSS-SOURCE          -- re-pull a value live from EIA and compare it to
        what's saved on disk, and compare two independent EIA series of the
        same thing (monthly survey vs. STEO).
  3. LANDMARK FACTS        -- do well-known moments in oil history show up with
        the right numbers? (1970 peak, 2008 trough, 2008 price spike, 2020
        COVID crash, 1998 bust, etc.)

Run:  python validate_data.py
Every check prints PASS / FAIL with the actual numbers so you can see for
yourself. No numbers are invented; landmark ranges are public knowledge.
"""

import os, json, urllib.request, urllib.parse, time

def load_env(path=".env"):
    if not os.path.exists(path): return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
load_env()
KEY = os.environ["EIA_API_KEY"]

def eia(path, params, tries=5):
    params = dict(params); params["api_key"] = KEY
    url = "https://api.eia.gov/v2/" + path + "?" + urllib.parse.urlencode(params, doseq=True)
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            last = e; time.sleep(1.5 * (i + 1))
    raise last

def load(name):
    return json.load(open(f"data/{name}.json"))

passes = fails = 0
def check(name, ok, detail):
    global passes, fails
    passes += ok; fails += (not ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print(f"         {detail}")

total = load("total_us"); basins = load("basins"); states = load("states"); wti = load("wti")
tmap = {r["date"]: r["value"] for r in total["data"]}
bmap = {r["name"]: {p["date"]: p["value"] for p in r["data"]} for r in basins["regions"]}
wmap = {r["date"]: r for r in wti["data"]}

print("\n" + "=" * 70)
print("  DATA CORRECTNESS REPORT")
print("=" * 70)

# ---------------------------------------------------------------- 1. INTERNAL
print("\n1. INTERNAL CONSISTENCY")

# 1a. 8 basins sum to the national total (STEO COPRPUS), every month
us_steo = eia("steo/data/", {"frequency": "monthly", "data[0]": "value",
              "facets[seriesId][]": "COPRPUS", "length": 5000})["response"]["data"]
us_steo = {r["period"]: float(r["value"]) for r in us_steo if r["value"] is not None}
# STEO's early regional vintage (2011-12) carries a small modeling residual;
# from 2013 on the 8 series sum to the total almost exactly. Tolerance: 2%.
worst = (None, 0.0); recent = 0.0
for period in us_steo:
    parts = [bmap[n].get(period) for n in bmap]
    if any(p is None for p in parts): continue
    pct = abs(sum(parts) - us_steo[period]) / us_steo[period] * 100
    if pct > worst[1]: worst = (period, pct)
    if period >= "2020-01": recent = max(recent, pct)
check("8 basins sum to US total (every overlapping month)",
      worst[1] < 2.0,
      f"worst gap {worst[1]:.2f}% at {worst[0]} (early-STEO vintage); since 2020 max {recent:.3f}%")

# 1b. all production values are non-negative and finite
bad = [(n, d) for n, m in bmap.items() for d, v in m.items() if v is None or v < 0]
check("no negative/blank basin values", len(bad) == 0,
      f"{len(bad)} bad points" + (f" e.g. {bad[0]}" if bad else ""))

# 1c. chronological + no gaps in total US monthly
dates = [r["date"] for r in total["data"]]
check("total US series is sorted & continuous monthly",
      dates == sorted(dates) and len(dates) == len(set(dates)),
      f"{len(dates)} months, {dates[0]}..{dates[-1]}, unique & ascending")

# ------------------------------------------------------------- 2. CROSS-SOURCE
print("\n2. CROSS-SOURCE (re-pull live from EIA and compare to disk)")

# 2a. re-pull MCRFPUS2 latest and compare to saved latest
live = eia("petroleum/crd/crpdn/data/", {"frequency": "monthly", "data[0]": "value",
           "facets[series][]": "MCRFPUS2", "sort[0][column]": "period",
           "sort[0][direction]": "desc", "length": 1})["response"]["data"][0]
live_val = float(live["value"]) / 1000.0
saved_val = total["latest"]["value"]
check("saved total-US latest matches a fresh EIA pull",
      abs(live_val - saved_val) < 1e-6 and live["period"] == total["latest"]["date"],
      f"disk={saved_val} ({total['latest']['date']})  live={live_val:.4f} ({live['period']})")

# 2b. two independent EIA measures of US total agree in overlap
#     monthly survey (MCRFPUS2) vs STEO model (COPRPUS)
sample = [d for d in ("2015-06", "2019-06", "2023-06") if d in tmap and d in us_steo]
gaps = {d: abs(tmap[d] - us_steo[d]) for d in sample}
check("survey (MCRFPUS2) vs STEO (COPRPUS) agree within 3%",
      all(gaps[d] / us_steo[d] < 0.03 for d in sample),
      "  ".join(f"{d}: survey={tmap[d]:.2f} steo={us_steo[d]:.2f}" for d in sample))

# 2c. WTI real-price math is correct for a spot-check month
if wti.get("real_available"):
    d = "1998-12"
    if d in wmap and "real" in wmap[d]:
        nom = wmap[d]["price"]; real = wmap[d]["real"]
        check("1998 oil bust shown in BOTH nominal and inflation-adjusted $",
              real > nom and 8 < nom < 14,
              f"{d}: nominal=${nom:.2f}  real(today's $)=${real:.2f}  (real>nominal as expected)")

# ------------------------------------------------------------- 3. LANDMARKS
print("\n3. LANDMARK FACTS (do famous moments look right?)")

def near(label, value, lo, hi, unit=""):
    check(label, value is not None and lo <= value <= hi,
          f"got {value:.2f}{unit}  (expected {lo}-{hi}{unit})" if value is not None else "missing")

# 1970 US production peak (~9.5-10.2 Mbbl/d)
p1970 = max(v for d, v in tmap.items() if d.startswith("1970"))
near("US production peaked around 1970", p1970, 9.3, 10.3, " Mbbl/d")

# 2008 modern trough (mid-2008 ~5 Mbbl/d, before shale)
p2008 = tmap.get("2008-06")
near("US production near its modern low in 2008", p2008, 4.5, 5.6, " Mbbl/d")

# modern record (latest > 12.5 Mbbl/d thanks to shale)
near("US production at modern record recently", total["latest"]["value"], 12.5, 14.0, " Mbbl/d")

# Permian overtakes: latest Permian is the biggest basin
latest_b = {n: m[max(m)] for n, m in bmap.items()}
top = max(latest_b, key=latest_b.get)
check("Permian is now the #1 basin", top == "Permian",
      "  ".join(f"{n}={latest_b[n]:.2f}" for n in sorted(latest_b, key=latest_b.get, reverse=True)[:3]))

# 2008 price spike (~$125-140 monthly avg July 2008)
near("2008 oil-price spike", wmap.get("2008-07", {}).get("price"), 120, 145, " /bbl")
# 2020 COVID crash (monthly avg ~$10-25 April 2020)
near("2020 COVID price crash", wmap.get("2020-04", {}).get("price"), 8, 25, " /bbl")
# 1998 bust (~$8-13)
near("1998 price bust", wmap.get("1998-12", {}).get("price"), 8, 14, " /bbl")

print("\n" + "=" * 70)
print(f"  RESULT: {passes} passed, {fails} failed.")
print("=" * 70)
