# Sourced-figure refresh config

This file is the **single checklist** for keeping the dashboard's SOURCED (hand-entered
analyst) figures current. The LIVE figures (EIA/BLS/FRED) update automatically when
`fetch_data.py` runs — they are **not** listed here.

The scheduled refresh agent (see "How the refresh works" below) reads this file, re-checks
each source, updates the value + `last_reviewed` date in `index.html`, then re-bundles.

Legend: **Cadence** = how often the source publishes something new worth checking.

| # | Figure(s) | Current value | Source | URL | Cadence | Lives in `index.html` | last_reviewed |
|---|-----------|---------------|--------|-----|---------|------------------------|---------------|
| 1 | Basin drill breakevens | Midland $61 · Delaware $62 · Eagle Ford $62 · Other-US-shale $63 | Dallas Fed Energy Survey (special questions) | https://www.dallasfed.org/research/surveys/des | **Quarterly** (breakeven Q the ~March survey) | `ANALYST_FACTS.basins[].breakeven*`, `BASIN_PROFILE[].breakeven/economics`, breakeven-chart callout | 2026-06-26 |
| 2 | Shut-in (operating) breakevens | Eagle Ford $26 · Delaware $33 · Midland $35 | Dallas Fed Energy Survey | https://www.dallasfed.org/research/surveys/des | Quarterly | `BASIN_PROFILE[].economics`, breakeven-chart callout | 2026-06-26 |
| 3 | Permian inventory | ~100,000 locations · ~55,000 sub-$50/bbl · ~7–10 yrs · "half drilled" | Enverus IR (locations) · Novi Labs (years) | https://www.enverus.com/newsroom/ · https://novilabs.com/events/spe-austin-2025/ · https://worldoil.com | Periodic (~annual) | `CREAM`, `BASIN_PROFILE.Permian`, `ANALYST_FACTS.permian`, `ANALYST_FACTS.basins[Permian]` | 2026-06-26 |
| 4 | Permian NPV25 breakevens | Delaware ~$52 · Midland ~$50 · basin avg ~$54 | Novi Labs public corporate reports | https://novilabs.com/blog/ | Periodic | `CREAM.median/average`, `BASIN_PROFILE.Permian.economics` | 2026-06-26 |
| 5 | Creaming-curve anchors | 55k@$50, 100k@$70, cheapest ~$32 | Enverus IR + Novi Labs (see #3/#4) | (as above) | Periodic | `CREAM.anchors` | 2026-06-26 |
| 6 | Per-basin operators (oil) | Permian/Bakken/Eagle Ford/Gulf/Alaska rosters + Mboe/d | Company 10-Ks/investor decks; Enverus/Rystad rank files | (company IR pages; BSEE for Gulf) | **Quarterly** (earnings) | `OPERATORS` | 2026-06-26 |
| 7 | Top US oil producers | Chevron/Exxon/COP/Oxy/EOG… kbbl/d or boe/d | Company Q4/FY results | (company IR) | Quarterly | `OIL_PRODUCERS` | 2026-06-26 |
| 8 | Top US gas producers | Expand/EQT/Antero… Bcf/d | Company results + EIA | (company IR) | Quarterly | `GAS_PRODUCERS` | 2026-06-26 |
| 9 | US gas by region | Appalachia 36.6 · Permian 27.7 · Haynesville 14.9 Bcf/d | EIA Today in Energy | https://www.eia.gov/todayinenergy/ | Periodic (EIA articles) | `GAS_BY_REGION` | 2026-06-26 |
| 10 | Basin shares of US crude + US share of world crude | Permian ~48% · Bakken/Eagle Ford ~9% · **US ~16% of world crude (~20% incl. all liquids), largest of any nation** | EIA Today in Energy (id=67404) | https://www.eia.gov/todayinenergy/ | Periodic | `ANALYST_FACTS.basins[].share` (donut, live) + Overview `#bignum` world-share line | 2026-07-06 |
| 11 | Outlook projections | oil plateau; Henry Hub ~$3.80/2030; LNG ~2x by 2031 | EIA STEO/AEO; bank forecasts | https://www.eia.gov/outlooks/steo/ | Monthly (STEO) | Outlook-tab card text | 2026-06-26 |
| 12 | Events narrative | 8 oil-price events | history (stable) | — | Rarely | `EVENTS` | 2026-06-26 |
| 13 | Simulator basin inventory & breakevens | **Bakken** ~1,400 sub-$50 · ~6,100 economic (RBN) · Dallas-Fed "Other US shale" $63 proxy · **Eagle Ford** $62 breakeven · ~5,500 total *(estimate — ⚠ unverified, no public creaming curve)* | Enverus · RBN Energy · Dallas Fed | https://rbnenergy.com · https://www.dallasfed.org/research/surveys/des | Periodic | `SIMS.bakken` / `SIMS.eagleford` (tiers + methodology panels) | 2026-07-06 |
| 14 | US crude exports / imports / Canada share | **LIVE** — exports `MCREXUS2` · imports `MCRIMUS2` · Canada `MCRIMUSCA2` (share computed) | EIA petroleum/move | https://www.eia.gov/petroleum/ | *(auto — via `fetch_data.py`)* | Overview `#bignum`; `data/trade.js` | live |
| 15 | Simulator decline-curve benchmarks | Year-1 ~70% from peak (Y2 ~45%, Y3 ~30%); **terminal ~13%/yr shale**, ~5%/yr conventional; modified-hyperbolic b≈1.3; tier EUR step-down T2 ~27% / T3 ~45% below T1 | Petropt, "Permian Basin Decline Curve Benchmarks," Mar 2026 (Texas RRC / NM OCD / TGS / Enverus) | (report) | Periodic | `SIMS.*.term/young/b/tiers`, `TRENDS.*`, type-curve method rows | 2026-07-10 |
| 16 | Upstream capex (real) | ~$869B peak 2015 · ~$300B 2020 trough · ~$567B 2025 (−4%, ~35% below peak) | IEA World Energy Investment (Rystad basis), real ~2024 $ | https://www.iea.org/reports/world-energy-investment-2025 | Annual (report) | `CAPEX` (Outlook › Capital & Consolidation) | 2026-07-10 |
| 17 | US upstream M&A deal value | 2023 ~$192B nominal (record) · 2024 ~$105B · 2025 ~$65B; CPI-adjusted to real 2026$ | Enverus Intelligence Research (US upstream M&A) | https://www.enverus.com/newsroom/ | Annual (report) | `MADEAL` (Outlook › Capital & Consolidation); ⚠ 2015–18 = 2015–19 avg, unverified | 2026-07-10 |

## How the refresh works

**🟢 LIVE data (fully automatic — nothing to do).** A daily **GitHub Actions** job
(`.github/workflows/refresh.yml`) runs `fetch_data.py` + `bundle.py` on GitHub's servers
and republishes the live site. This covers everything auto-fed by an API: US & basin
crude production, WTI (and daily spot), rigs / wells / DUCs / oil-per-rig, crude
exports/imports, inflation-adjusted WTI, and the S&P 500 chart. No person or laptop needed.

**🔴 SOURCED data (needs a human, ~once a quarter).** The figures in the table above are
hand-entered analyst estimates. The daily job does **not** touch them — they stay frozen
until someone updates them. They won't be wrong tomorrow, but some drift over 6–12 months.

### Quarterly refresh checklist (≈1 hour, for whoever owns this)
Do this each quarter (or when a boss flags a stale number):

1. **Open this file (`SOURCES.md`)** and go down the table. For each row whose **Cadence**
   is due (see priority below), open its **URL** and find the latest published figure.
2. **If it changed:** edit the value in **`index.html`** at the spot named in the
   "Lives in `index.html`" column, and update the date on that row here + on the dashboard tag.
3. **Commit and push** your edit. The site republishes automatically (or run it now:
   repo → **Actions** tab → "Refresh & publish dashboard" → **Run workflow**).
4. **If you can't verify a figure**, leave it as-is and flag it — never guess. (`GUIDE.md`
   explains where every config block lives if you need context.)

**What changes most often (do these first):** #1–2 Dallas Fed breakevens (quarterly) and
#6–8 operators / top producers (after earnings). Then #16–17 capex & M&A (once a year, when
IEA/Enverus publish). #3–5 inventory a few times a year; #10, #15 occasionally; the rest rarely.

> Not a developer? You can also hand this file to an AI assistant and say *"refresh the
> sourced figures from SOURCES.md — check each source, update only what changed, and never
> fabricate,"* then review its changes before pushing.
