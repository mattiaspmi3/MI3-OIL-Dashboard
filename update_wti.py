# -*- coding: utf-8 -*-
"""DAILY JOB — refresh ONLY the WTI front-month price.

Updates just `spot_latest` (the headline number) in data/wti.json + data/wti.js and
touches nothing else — production, basins, drilling, trade, S&P are left exactly as the
last quarterly pull wrote them. Designed to be tiny and reliable: if the price can't be
fetched it keeps the existing value and still exits 0 (so the build/deploy never breaks).
"""
import io, os, json, urllib.request, datetime


def load_env(path=".env"):
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


load_env()
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def front_month_wti():
    # 1) NYMEX front-month WTI futures — the current market price ("the WTI price"). No key needed.
    for host in ("query1", "query2"):
        try:
            u = ("https://%s.finance.yahoo.com/v8/finance/chart/CL=F"
                 "?interval=1d&range=5d" % host)
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            m = json.load(urllib.request.urlopen(req, timeout=30))["chart"]["result"][0]["meta"]
            px, ts = m.get("regularMarketPrice"), m.get("regularMarketTime")
            if px:
                d = (datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
                     if ts else NOW[:10])
                return {"date": d, "price": round(float(px), 2),
                        "source": "NYMEX front-month (CME/Yahoo)"}
        except Exception:
            continue
    # 2) fallback: EIA daily spot (official but lags ~a week)
    key = os.environ.get("EIA_API_KEY")
    if key:
        try:
            u = ("https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=%s&frequency=daily"
                 "&data[0]=value&facets[series][]=RWTC&sort[0][column]=period"
                 "&sort[0][direction]=desc&length=1" % key)
            row = json.load(urllib.request.urlopen(u, timeout=30))["response"]["data"][0]
            if row.get("value") is not None:
                return {"date": row["period"], "price": round(float(row["value"]), 2),
                        "source": "EIA spot RWTC (fallback)"}
        except Exception:
            pass
    return None


def main():
    path = "data/wti.json"
    if not os.path.exists(path):
        print("data/wti.json missing — run fetch_data.py (quarterly job) first.")
        return
    payload = json.load(open(path, encoding="utf-8"))
    new = front_month_wti()
    if new:
        old = (payload.get("spot_latest") or {}).get("price")
        payload["spot_latest"] = new
        payload["last_updated"] = NOW
        io.open(path, "w", encoding="utf-8").write(json.dumps(payload, indent=2))
        io.open("data/wti.js", "w", encoding="utf-8").write(
            "window.WTI_DATA = " + json.dumps(payload) + ";")
        print("WTI price updated: $%.2f on %s (was $%s) via %s"
              % (new["price"], new["date"], old, new["source"]))
    else:
        print("Could not fetch a WTI price this run; kept the existing value.")


main()
