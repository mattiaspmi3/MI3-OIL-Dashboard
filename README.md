# US Oil &amp; Gas Intelligence — Dashboard 1 (Prepared for MI3 Energy)

An interactive, tabbed dashboard on U.S. oil &amp; gas: production, basins, prices,
natural gas, and the forward outlook — built from public EIA/BLS data with
hand-entered, **cited** analyst estimates clearly separated from live data.

## How it fits together

    fetch_data.py   ->  calls EIA (+ optional FRED), saves each series into  data/
    data/*.js       ->  the saved data (regenerated every run)
    index.html      ->  reads the data/*.js files and draws the dashboard

The page loads data from local `*.js` files (via `<script>` tags), so it works
from a double-click — no server, no `fetch()`. Charts use Chart.js + an
annotation plugin from a CDN (needs internet the first time).

## Tabs

1. **Overview** — headline stats (oil, WTI, gas), state-of-the-industry summary, clickable basin map, today's basin mix.
2. **Oil &amp; Gas 101** — plain-English primer (upstream/midstream/downstream) + Shale &amp; Rock-Tiers 101.
3. **Production** — total US crude (1920+), state-proxy deep history, by-basin stacked chart.
4. **Basins** — clickable map → per-basin deep-dives (Permian, Bakken, Eagle Ford, + Gulf of Mexico &amp; Alaska notes), basin health cards, breakeven-vs-price.
5. **Prices &amp; Markets** — WTI history, real vs nominal, events guided tour, WTI-vs-S&amp;P-500.
6. **Natural Gas** — production (marketed/dry), Henry Hub price, gas basins, LNG &amp; data-center demand.
7. **Outlook** — projections (oil plateau vs gas growth), clearly labeled as forecasts.

## Provenance — every number is tagged

| Tag | Meaning |
|---|---|
| 🟢 **Live** | Pulled from an API (EIA/BLS/FRED). Auto-updates when `fetch_data.py` runs; shows the latest data date. |
| 🔴 **Sourced** | Hand-entered analyst estimate (Novi Labs, Enverus, EIA reports, etc.). Carries a citation + "last reviewed" date; **not** auto-updating. |
| 🔵 **Projection** | A forecast (EIA STEO/AEO, banks). |

The **Data &amp; Sources** panel in the footer lists every metric with its type,
source, and date. Hand-entered figures live in the **`ANALYST_FACTS`** and
**`CITATIONS`** objects near the top of the script in `index.html` — edit there.

### Figures flagged "needs review" (could not be independently verified)
- Permian **~200,000** remaining locations / 130k–70k split — public Enverus figures are lower (~100k total, ~55k sub-$50).
- Permian **~$57 median** breakeven and the 37k-at-$50 / 100k-at-$70 splits — Dallas Fed 2025 ≈ $61 avg.
- "EOG largest in Delaware" — softened to "leading position."
- Bakken privates (Kraken/Phoenix/Zavanna) and the exact "3–4 mile lateral" length.

These are kept (your baseline) but visibly marked in the dashboard and footer.

## Data pulled (`fetch_data.py`)

| Data | Series | Live? | File |
|------|--------|-------|------|
| Total US crude | EIA `MCRFPUS2` (monthly, 1920+) | Live | `total_us.js` |
| By basin/region | EIA STEO `COPRPM/BK/EF/AP/HA/R48`, `PAPRPGLF/PAK` | Live | `basins.js` |
| State proxy | EIA `MCRFPTX1/NM1/ND1…` (annual, 1981+) | Live | `states.js` |
| WTI price + daily spot | EIA `RWTC` (= FRED `DCOILWTICO`) | Live | `wti.js` |
| Real WTI | BLS `CUSR0000SA0` / FRED `CPIAUCSL` | Live | `wti.js` |
| **Natural gas (marketed/dry)** | EIA `N9050US2` / `N9070US2` → Bcf/d | Live | `natgas.js` |
| **Henry Hub gas price** | EIA `RNGWHHD` (monthly + daily spot) | Live | `natgas.js` |
| **S&amp;P 500** | FRED `SP500` (**needs `FRED_API_KEY`**) | Live* | `sp500.js` |

\* **S&amp;P 500 needs a free FRED key.** Without it, the WTI-vs-S&amp;P chart shows a
"add a FRED key to enable" message and everything else still works. Add
`FRED_API_KEY=yourkey` to `.env` and re-run. (FRED's `SP500` only goes back ~10 years.)

## Running it

    python fetch_data.py       # pulls every series into data/  (prints last 12 WTI months + current spot)
    python validate_data.py    # optional correctness checks
    # then open index.html (double-click is fine), or run "Update Oil Prices.bat"

## Notes

- WTI headline = latest **daily spot**; the price chart uses **monthly averages** (which lag ~6 weeks).
- Natural gas production is converted from EIA's MMcf/month to **Bcf/d** (a rate).
- The basin map uses a real US-states SVG; markers are clickable (5 shale basins → deep-dives; others are informational).
- Analyst figures are estimates that vary by price assumption and source; breakevens are half-cycle wellhead unless noted.

## Tabs (8)

Overview · Oil &amp; Gas 101 · Production · Basins · **Inventory &amp; Productivity** · Prices &amp; Markets · Natural Gas · Outlook.

## Inventory &amp; Productivity (new, all LIVE)

Live EIA STEO **Table 10a** drilling metrics, by basin (`data/drilling.js`):

| Metric | EIA series |
|---|---|
| Active rigs | `RIGS{PM,BK,EF,AP,HA,R48}` |
| New wells drilled | `NWD…` |
| New wells completed | `NWC…` |
| DUC (drilled-but-uncompleted) | `DUCS…` *(pulled directly, not derived)* |
| New-well oil per rig | `CONWR…` (thousand bbl/d per rig) |

Charts: per-rig productivity, rig count, drilled-vs-completed, DUC bar + trend, and the **Permian creaming curve**.

## Consistent per-basin template

Every basin deep-dive (Basins tab) now uses one reusable template (`renderBasinProfile` + `BASIN_PROFILE`): header + status badge, a fixed 7-metric key-stats row (share · output · rigs · DUC · oil/rig · breakeven · inventory — “n/a” where missing), three live mini-charts (production / productivity / DUC), top operators, inventory &amp; economics (creaming curve for Permian), and “what to watch.” Each figure is tagged LIVE or SOURCED.

## Permian inventory &amp; creaming curve (SOURCED — verified)

The Permian inventory figure was **verified and corrected** (multi-firm): **~100,000 remaining locations, ~55,000 breaking even below $50/bbl, ~7–10 years** of runway; basin “just over half drilled.” Sources: **Enverus Intelligence Research** (Apr 15 2026, via World Oil) for the location counts; **Novi Labs** (SPE Austin, May 2025) for the years + “half drilled,” and Novi public NPV25 breakevens (Delaware ~$52 / Midland ~$50). The earlier “~200,000” was **not supported** for the Permian alone (that scale is North-America-wide / all-tier) and was removed. The exact Novi *“Permian Staying Power”* webinar numbers (131,465 etc.) are gated/unpublished and are **not used**. The interactive creaming curve is anchored on the verified Enverus + Novi figures.

## Breakevens (SOURCED — Dallas Fed Q1-2025)

Drill breakevens: Permian Midland **$61** / Delaware **$62**, Eagle Ford **$62**, “Other US shale” (Bakken proxy) **$63**. Operating/shut-in: Eagle Ford **$26**, Delaware **$33**, Midland **$35**. Source: Dallas Fed Energy Survey, Q1 2025.

## Branding &amp; theme

- **Theme:** clean white/near-black with MI3 **red** accent and grey borders (corporate report look). Permian = red on every chart.

- **Logo:** `mi3-logo.svg` in this folder is shown top-left. Replace that file with your
  real MI3 Energy logo (keep the name `mi3-logo.svg`, or update the `src` in `index.html`).
  If the file is missing, a red "MI3" mark shows as a fallback. Recommended height ~46px.
- **Fonts:** headings **Space Grotesk**, body **IBM Plex Sans**, numbers **IBM Plex Mono**
  (Google Fonts). Change them in the `<head>` `<link>` and the `font-family` rules.
- **Map:** `data/usmap.js` holds the real US-states SVG (50 states + DC). The five main
  shale basins are clickable markers (`MAP_BASINS`); other US basins/plays (Anadarko,
  DJ/Niobrara, Powder River, Uinta, San Juan, California, Gulf, Alaska) are secondary
  markers (`MAP_EXTRA`).

## Companies &amp; producers (all visuals, all sourced)

- **Top US oil producers** (Production tab) and **top US gas producers** (Natural Gas tab) — bar charts in `OIL_PRODUCERS` / `GAS_PRODUCERS`.
- **Where US gas comes from** — donut of gas by region (`GAS_BY_REGION`, Natural Gas tab).
- **Per-basin operators** — every basin deep-dive (Permian, Bakken, Eagle Ford, Gulf of Mexico, Alaska, Appalachia, Haynesville) has a "Who operates here" bar chart (`OPERATORS`).
- All are **Sourced** 2025 estimates with citations; note that super-majors report **boe/d** (oil+gas+NGLs) while independents report crude **bbl/d**, so the metric is labelled per chart.

## Outlook is data-driven

The Outlook tab blends **live** current figures (crude, gas, WTI, Henry Hub, with YoY change) with the **EIA STEO forecast** (summed from the regional series in `basins.js`). The headline projection and the "history → projection" chart **recompute every time `fetch_data.py` runs**, so the outlook shifts as STEO updates each month.

## Operators &amp; events

- **Operator shares:** each basin deep-dive (Basins tab) shows a "Who operates here"
  bar chart of top producers (Mboe/d). Data is in the `OPERATORS` object — **Sourced**
  2025 estimates (boe/d, mixed gross/net; see citations and the "needs review" notes).
- **Event detail:** on any price-event panel, click **"🔍 More detail"** for a modal that
  quantifies the price move from live WTI data (before/after/% change) plus a sparkline.

## Requirements

Python 3 (standard library only). Internet (EIA/BLS pulls + Chart.js &amp; Google Fonts CDNs).
Optional FRED key for the FRED inflation source &amp; the S&amp;P 500 chart.
