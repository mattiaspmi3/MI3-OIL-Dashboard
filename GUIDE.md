# MI3 Energy — US Oil &amp; Gas Intelligence Dashboard
### A complete guide: what it is, how it's built, how it's sourced, and what updates

*Prepared for MI3 Energy. Plain-English throughout — no prior oil or software knowledge needed.*

---

## 1. What this is (in one paragraph)

A single interactive web page that tells the story of U.S. oil &amp; gas — how much
the country produces, which basins and companies produce it, how prices move, how
the drilling engine works, and where it's all heading. It blends **live public
government data** (which refreshes itself) with **hand-checked analyst figures**
(each carrying a citation). It opens in any web browser — no software to install,
no login — and can be shared as one file or a web link.

Two golden rules run through the whole thing:

1. **Every number is labelled** either **🟢 Live** (pulled from an automatic data
   feed) or **🔴 Sourced** (a hand-entered analyst estimate with a citation) or
   **🔵 Projection** (a forecast). You always know what you're looking at.
2. **Nothing is fabricated.** If a number couldn't be verified from a real public
   source, it was corrected or removed — not guessed.

---

## 2. The eight tabs, explained

| Tab | What it shows |
|-----|---------------|
| **Overview** | The headline numbers (oil production, live WTI price), a plain-English oil-only summary, a clickable US map of the basins, and today's basin mix (a donut of who produces the crude right now). |
| **Oil &amp; Gas 101** | A primer for newcomers: upstream/midstream/downstream, conventional vs. shale, horizontal drilling &amp; fracking, "lateral feet," rock tiers, and why any of it matters to an investor. |
| **Production** | How much crude the U.S. pumps — a full century of history (from 1920), a deeper state-by-state view, the by-basin stacked chart, and a "who produces the most US oil" company ranking. |
| **Basins** | The heart of the tool. Click any basin on the map to open its **deep-dive** — every basin uses the *same* layout: a status badge, a 7-metric stat row, three live mini-charts (production, new-well oil per rig, DUC wells), the top operators, inventory &amp; economics, and "what to watch." Plus basin-health cards and a breakeven-vs-price chart. |
| **Inventory &amp; Productivity** | The live drilling engine: rigs, new wells drilled vs. completed, drilled-but-uncompleted (DUC) wells, and how much oil each rig brings on — all by basin. Also the interactive **Permian creaming curve** (drag a price slider to see how many locations are economic). |
| **Production Simulator** | One hub for every projection. A selector switches between **US Total** and each region, all in the *same* layout. Three model types: **Inventory** (Permian, Bakken, Eagle Ford — tier-cascade from remaining drilling inventory), **Trend** (Federal Gulf, Rest of L48, Alaska — extrapolate the live 3–5-yr EIA rate), and **Combined** (US Total — sums the regions into one national line with a stacked breakdown). Every view carries a method badge and a "how it was built" sourcing panel; controls that don't apply are shown disabled with an "N/A" note. |
| **Prices &amp; Markets** | WTI oil price since 1986, inflation-adjusted ("real") vs. nominal, a guided "▶ Play the story" tour of the 8 world events that moved prices, an event-detail pop-up that quantifies each move, and WTI vs. the S&amp;P 500. |
| **Outlook** | Forward-looking projections (clearly labelled): oil near a plateau, and the capital-discipline story. It recomputes from the live data + EIA's forecast each time the data refreshes. Also a **Capital & Consolidation** panel — two sourced charts (upstream capex from IEA, and US upstream M&A deal value from Enverus, inflation-adjusted) that show the "capital discipline" story; these update on a report cycle, not with the daily refresh. |

---

## 3. The signature interactive features

- **Clickable US map** — a real US-states map with the five shale basins as clickable
  markers (plus other plays shown for context). Click one to jump to its deep-dive.
- **Consistent basin deep-dive template** — every basin looks identical so they're
  easy to compare. Live drilling stats sit next to sourced economics, each tagged.
- **Guided "Play the story"** — walks a newcomer through 8 price-moving events
  (Gulf War → 2020 COVID crash → 2022 Ukraine), auto-zooming and narrating each.
- **Event detail pop-up** — click any event for a quantified before/after price move
  computed from the live data, with a mini price chart.
- **Permian creaming curve** — drag a WTI-price slider to see how many Permian
  drilling locations are economic at that price (built on verified Enverus + Novi figures).
- **Production Simulator hub** — one tab holding every projection, with a selector for
  **US Total** plus each oil region in an **identical** layout (title + method badge on
  top, chart in the middle, sliders always in the same spot, sourcing panel at the bottom).
  Three model types:
  - **Inventory** (Permian, Bakken, Eagle Ford) — a tier-cascade from remaining drilling
    inventory. Controls: WTI price, drilling pace, a per-tier productivity slider each,
    well-decline rate, and Base/Upside/Downside presets. Sourced from Enverus/Novi
    (Permian), Enverus + RBN + Dallas-Fed proxy (Bakken), Dallas Fed + estimate (Eagle Ford).
  - **Trend** (Federal Gulf, Alaska) and **Rest of L48** (rig/DUC) — project each
    region forward at its **own live 3–5-yr EIA growth/decline rate**. Controls: a forward
    growth/decline slider (defaults to the observed rate), a trend-persistence (taper)
    slider, WTI sensitivity, and presets. A momentum projection — reliable near-term,
    weaker long-term; the only data source is live EIA, the forward rate is an assumption.
  - **Combined** (US Total) — sums the regional projections into one national crude
    line with a **stacked-area breakdown** beneath, flexed by master WTI-price and
    global-intensity sliders. It plainly states it *mixes* methods and inherits every
    basin's assumptions.

  The starting production for every view is **live from EIA**, and each carries a
  **"How this simulation was built"** panel tagging inputs **Live / Sourced / Derived /
  Assumption**. Controls that don't apply to a given model (e.g. per-tier sliders on a
  trend region) are shown **disabled with an "N/A" note** rather than hidden, so the panel
  feels identical everywhere. The hub opens on **US Total** so the big picture greets you first.

  **Three production streams (the core mechanics).** Every chart is a stacked area showing
  the three things that actually drive output:
  1. **Legacy** (grey) — today's production, *always declining*. Two-segment decline:
     recent wells fade steeply (~80% of a shale well's output is in its first ~2 years, per
     SPE/JPT), older wells settle into a slow **terminal decline that never stops**
     (~6%/yr shale, ~5%/yr conventional — an assumption, adjustable).
  2. **New drilled wells** (colour) — driven by the **active rig count** (default = live
     from EIA Table 10a). Rigs × drilling efficiency = wells drilled per year; a
     **completion rate** decides how many get completed now vs banked.
  3. **DUC completions** (tan) — DUCs are wells already drilled but never fracked;
     completing them adds oil *without drilling*. Each basin's **DUC backlog** is live from
     EIA and depletes over the forecast (shown as a dashed line on the chart's right axis).
     A **DUC completion rate** controls the drawdown.

  Every new well and completed DUC follows an explicit **modified-hyperbolic type curve**
  (ramp to a peak, high early b-factor, then a switch to exponential at the terminal rate —
  editable peak, b-factor, months-to-peak & steepness). The decline defaults are calibrated
  to published benchmarks — **Petropt "Permian Basin Decline Curve Benchmarks" (Mar 2026)**,
  from Texas RRC / New Mexico OCD / TGS / Enverus data: Year-1 ~70% decline from peak,
  **terminal ~13%/yr for shale** (~5%/yr conventional), and a steeper tier EUR step-down
  (Tier 2 ~27% below Tier 1, Tier 3 ~45% below). Controls are
  identical across every view — **rig count, completion rate, DUC drawdown, type-curve peak,
  terminal decline, young-well steepness, per-tier productivity, WTI price, and the
  scenario preset** — with anything that doesn't apply shown disabled ("N/A", e.g. rigs/DUCs
  for offshore Gulf & Alaska, which have no EIA rig data and stay on the trend method). The
  **US Total** sums the corrected basin curves, so the national picture is bottom-up. Sanity-
  checked: set rigs = 0 and DUC completions = 0 and every basin declines smoothly toward zero.

---

## 4. How it was built (the plumbing)

Three simple pieces, in order:

1. **`fetch_data.py`** (a Python script) calls the free public data APIs — the U.S.
   Energy Information Administration (EIA), the Bureau of Labor Statistics (BLS, for
   inflation), and the Federal Reserve (FRED, for the S&amp;P 500) — and saves the
   results into small files in the `data/` folder. This is where the **live** numbers
   come from. It uses only Python's built-in libraries (nothing to install) and
   never stores your API keys in the code — they live in a private `.env` file.

2. **`index.html`** is the dashboard itself. It reads the `data/` files and draws
   everything with **Chart.js**, a charting library loaded from the internet. The
   hand-entered **sourced** figures live in clearly-marked config objects near the
   top of its script (e.g. `OPERATORS`, `CREAM`, `BASIN_PROFILE`) so they're easy to edit.

3. **`bundle.py`** packs `index.html` + all the `data/` files + the logo into **one
   self-contained file**, `US-Oil-Gas-Dashboard.html`, that you can email or host.
   (It also refreshes `publish-online/index.html` for web hosting.)

**How the numbers were checked.** Every sourced figure was verified with live web
research across multiple firms (EIA, Enverus, Novi Labs, Wood Mackenzie, Rystad,
the Dallas Fed) before it went in. Where estimates disagreed, the most defensible
public figure was used and the disagreement noted. The clearest example: the Permian
"remaining inventory" was corrected from an unsupported "~200,000 locations" down to
the verified **~100,000** (Enverus, Apr 2026) — because 200,000 turned out to be a
North-America-wide / all-tier figure, not Permian-only.

---

## 5. Where every number comes from — and whether it updates

### 🟢 LIVE (updates automatically)

| Data | Source (feed) | Refreshes |
|------|---------------|-----------|
| US crude production (history + latest) | EIA series `MCRFPUS2` | ✅ daily |
| Production by basin/region | EIA STEO regional series | ✅ daily |
| State-level crude (deep history) | EIA state series | ✅ daily |
| WTI oil price (monthly + daily spot) | EIA series `RWTC` | ✅ daily |
| Inflation-adjusted ("real") WTI | BLS CPI (`CUSR0000SA0`) / FRED | ✅ daily |
| S&amp;P 500 (oil-vs-market chart) | FRED series `SP500` | ✅ daily |
| Rigs, wells drilled/completed, DUC, oil-per-rig (by basin) | EIA STEO **Table 10a** | ✅ daily |
| US crude exports / imports / % from Canada (Overview trade line) | EIA `MCREXUS2` / `MCRIMUS2` / `MCRIMUSCA2` | ✅ daily |

All the live data refreshes **every day at 6 AM** via a scheduled task on the PC
(runs `fetch_data.py`, then rebuilds the shareable file). This keeps the **daily WTI
spot price** fresh each day; the monthly series (like
production) simply re-check and update whenever EIA posts a new month. EIA/BLS/FRED
are free, so this costs nothing.

### 🔴 SOURCED (hand-checked analyst figures — refresh on a schedule, see §6)

| Figure | Source | Cadence |
|--------|--------|---------|
| Basin drill breakevens (Midland $61, Delaware $62, Eagle Ford $62, "Other US shale" $63) | Dallas Fed Energy Survey, Q1-2025 | Quarterly |
| Shut-in (operating) breakevens ($26/$33/$35) | Dallas Fed Energy Survey | Quarterly |
| Permian inventory (~100k locations, ~55k sub-$50, ~7–10 yrs) | Enverus (Apr 2026) + Novi Labs (May 2025) | Periodic |
| Permian NPV25 breakevens (Delaware ~$52 / Midland ~$50) | Novi Labs public data | Periodic |
| Creaming-curve anchors | Enverus + Novi (verified) | Periodic |
| Per-basin operators &amp; production shares | Company filings, Enverus, BSEE (Gulf) | Quarterly |
| Top US oil &amp; gas producers | Company Q4/FY results | Quarterly |
| Basin shares of US crude (Permian ~48%, etc.) | EIA Today in Energy | Periodic |
| Outlook projections (oil near plateau; capital discipline) | EIA STEO/AEO; bank forecasts | Monthly-ish |

A full checklist of these — with the exact source URLs and "last reviewed" dates —
lives in **`SOURCES.md`**.

### 🔵 PROJECTIONS
The Outlook tab and the simulator are forecasts/models, clearly labelled as such —
not measured data.

---

## 6. Does it update over time? Yes — two automatic loops

1. **Live data → daily.** A Windows scheduled task ("MI3 Oil Dashboard Refresh")
   runs every day at 6 AM: it pulls the latest EIA/BLS/FRED data — including the
   **daily WTI spot price** — and rebuilds the shareable file.
   Fully automatic, on the PC.

2. **Sourced figures → quarterly.** A cloud agent runs on **Jan 1, Apr 1, Jul 1,
   and Oct 1**. It reads `SOURCES.md`, re-checks each analyst source on the web,
   updates any figure that changed (with a fresh citation and date), rebuilds the
   file in the GitHub repo, and posts a plain-English "what changed" report. It
   **never fabricates** — anything it can't re-verify it leaves alone and flags.

The project lives in a private GitHub repo (`mattiaspmi3/MI3-OIL-Dashboard`) so the
cloud agent can update it. Your API keys are **not** in the repo.

---

## 7. How to use, refresh, and share it

- **Open it:** double-click `index.html` (needs internet for the charts), or open the
  self-contained `US-Oil-Gas-Dashboard.html`.
- **Refresh the data yourself anytime:** double-click `refresh.bat` (or `Update Oil
  Prices.bat` for just the data).
- **Share it:** send `US-Oil-Gas-Dashboard.html` (one file, works offline for the data,
  online for the charts), or host the `publish-online` folder on Netlify for a link.
- **Check the numbers:** the **Data &amp; Sources** panel at the bottom of the dashboard
  lists every metric, whether it's Live/Sourced/Projection, its source, and its date.

---

## 8. Honest caveats

- **Sourced figures are estimates** that vary by firm, price assumption, and date —
  they're cited and dated so you can judge them, but they aren't gospel.
- **The production simulator is a simplified planning model**, not a reservoir
  forecast — it's for exploring "what if the assumptions change," and every
  assumption is listed under it.
- **Breakevens come in flavours:** the "drill a new well" breakeven (Dallas Fed, ~$61)
  is different from the "keep an existing well pumping" shut-in breakeven (~$26–35)
  and from a returns-based NPV25 breakeven (~$50) — the dashboard labels which is which.
- **Some analyst detail is behind paywalls.** Where the exact figures were gated
  (e.g. Novi Labs' full "Permian Staying Power" creaming curve), the dashboard uses
  the best *public* equivalents and says so — it never presents gated numbers it
  couldn't see.

---

*Questions or changes? The whole thing is designed to be edited: live data in
`fetch_data.py`, sourced figures in the config objects in `index.html` (mapped in
`SOURCES.md`), and the look in the CSS at the top of `index.html`.*
