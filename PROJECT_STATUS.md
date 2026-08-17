# Project Status — MI3 US Oil Intelligence Dashboard

**Internal working notes** to stay on the same page across computers / sessions. This is
the "where things stand and how to pick up" doc. For the full build guide (architecture,
data sources, rebuild-from-scratch), see **`HOW_THIS_WAS_BUILT.md`**.

> **New computer / new Claude Code session?** Open the repo in VS Code and say:
> *"Read PROJECT_STATUS.md and HOW_THIS_WAS_BUILT.md to get up to speed."*

- **Live site:** https://mattiaspmi3.github.io/MI3-OIL-Dashboard/
- **Repo:** https://github.com/mattiaspmi3/MI3-OIL-Dashboard (GitHub account `mattiaspmi3`)
- **Status:** Live, hosted on GitHub Pages, auto-updating. All features below are deployed.

---

## Where things stand

The dashboard is a **live, oil-only** view of the US oil picture — production, prices,
drilling, the major basins, an interactive simulator, and the outlook. It auto-updates
(price daily, full data quarterly) and opens from a shareable link.

**Architecture (one line):** `fetch_data.py`/`update_wti.py` pull data → `data/*.js` →
`bundle.py` inlines into `publish-online/index.html` → a GitHub Action runs it on a timer →
GitHub Pages serves the link. (Details in `HOW_THIS_WAS_BUILT.md`.)

---

## What's been built / decided (changelog of the major work)

1. **Foundation** — wired to real EIA/market data with a provenance tag on every number.
2. **Simulator** — calibrated the decline/tier model to published benchmarks (Petropt).
3. **Oil-only pivot** — removed all natural-gas *tabs/content* for one clear story.
4. **Live WTI fix** — price is fetched server-side (NYMEX front-month) and served as a tiny
   cache-proof file (`wti-latest.json`) the page re-reads on every open, so it's never stale.
5. **Hosting + auto-refresh** — GitHub Pages + two Actions: `refresh.yml` (daily price +
   publish, and on every push) and `quarterly.yml` (full `fetch_data.py` on the 1st of
   Jan/Apr/Jul/Oct + a review-reminder Issue).
6. **Wording/consistency** — many boss edits; tier labels unified to `Tier-1/2/3`.
7. **Data audit** — caught an impossible operator figure (Exxon Permian > US); ran a full
   verification of every hand-entered operator/analyst number against filings; fixed stale
   figures, the Devon–Coterra merger, and moved breakevens to Dallas Fed Q1-2026.
8. **Industry alignment (peer review)** — adopted MM/M units (MM = million, M = thousand);
   **pure-oil rebase** (all operator leaderboards converted boe/d → crude oil, several are
   sourced estimates marked `est`); gave the basin map real sized shapes (Permian across
   W TX + SE NM; Bakken across ND + E MT; Eagle Ford as the S-TX arc).
9. **Presentation-round additions (Aug 2026):**
   - Event %s recomputed **pre-event → the max/min the event caused** (fixed COVID/Gulf/
     Ukraine signs); added the **2026 Iran conflict** event with a manipulation/risk-premium note.
   - Renamed the metric to **"New-Well IP oil/rig"** everywhere (IP = initial production).
   - Added an **Active rig-count** mini-chart to each basin deep-dive (live EIA).
   - Added a shaded **minimum-profit band** to the Permian creaming/breakeven chart.
   - Oil-vs-market chart now has **NASDAQ + Dow (FRED) + Henry Hub gas (EIA)** alongside
     S&P and WTI, indexed to 100, with a toggleable legend.
   - Wrote **`HOW_THIS_WAS_BUILT.md`** (full build + rebuild guide).

---

## Open items / to-dos

- **SECURITY (decision pending):** the live link is a **public** GitHub Pages site on a
  *personal* account. A colleague (Carlos, via Tadesse) asked that it be **not accessible
  outside MI3**. Data is all public (no confidential data; keys are encrypted secrets), but
  the recommended fix is to **host the self-contained file on MI3's internal server** (or make
  the repo private, which takes the link down). No action taken yet — awaiting the user's call.
- **`FRED_API_KEY` secret:** make sure it's set in the repo's Actions secrets so the quarterly
  job keeps refreshing S&P / NASDAQ / Dow (the local `.env` has it).
- **`data/natgas.js`** is now *used* again (Henry Hub gas line in the oil-vs-market chart) —
  it is bundled (`bundle.py` list + a `<script>` tag in `index.html`). Not a leftover anymore.
- **Presenter files** (`Presenter-Deck.html`, `Presenter-Guide.html`, `How-This-Was-Built.html`)
  live on the user's Desktop / project folder and are **not in the repo** (by request).

---

## How to resume / make a change

The edit loop (non-developer friendly):
1. Edit `index.html` (the dashboard) in VS Code.
2. Run `python bundle.py` to rebuild `publish-online/index.html`.
3. Open `publish-online/index.html` in a browser to check it.
4. Commit & push to `main` — the site republishes within a couple of minutes.

Notes:
- API keys live in `.env` (git-ignored). Recreate it on a new machine only if you need to run
  the data scripts: `EIA_API_KEY=...` and `FRED_API_KEY=...`.
- Editing files under `.github/workflows/` needs the `workflow` permission; if a tool can't
  push them, paste them via the GitHub website and commit to `main`.
- `_push.py` and `_markets.py` are local one-off helpers, not part of the site.

---

*Keep this file current as things change — it's the fastest way for anyone (or Claude Code
on another computer) to get back on the same page.*
