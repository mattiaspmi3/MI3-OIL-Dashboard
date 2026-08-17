# How the MI3 US Oil Intelligence Dashboard was built

A complete, plain-English guide to how this dashboard works and how to rebuild it
from scratch. **You do not need to be a developer to follow this** — every step is
spelled out. If you can copy files, run a couple of commands, and paste text into a
website, you can maintain or rebuild the whole thing.

- **Live site:** https://mattiaspmi3.github.io/MI3-OIL-Dashboard/
- **What it is:** a live, auto-updating dashboard of the US oil picture — production,
  prices, drilling, the major basins, an interactive simulator, and the outlook.

---

## 1. The big picture (how the pieces fit)

Three small programs and one automation service do everything:

```
   ┌─────────────────┐     writes      ┌──────────────┐    inlines into    ┌────────────┐
   │  fetch_data.py  │ ──────────────▶ │  data/*.js   │ ─────────────────▶ │ bundle.py  │
   │  update_wti.py  │  (the numbers)  │ (JS globals) │                    └─────┬──────┘
   └─────────────────┘                 └──────────────┘                          │ builds
        ▲  pulls from                                                            ▼
   EIA · FRED · BLS · the oil market                                  publish-online/index.html
                                                                       (one self-contained file)
                                                                               │ served by
                                                                               ▼
   GitHub Action (a timer on GitHub's servers)  ───────────────────▶   GitHub Pages  →  the live link
```

In words:
1. **`fetch_data.py`** downloads the raw numbers from government/market sources and
   writes them into small data files (`data/*.js` and `data/*.json`).
2. **`update_wti.py`** is a tiny version that refreshes *only* the live oil price.
3. **`bundle.py`** takes the page (`index.html`) plus those data files and stitches
   them into one self-contained file in `publish-online/`.
4. A **GitHub Action** runs those scripts on a timer on GitHub's own computers, then
   publishes the result to **GitHub Pages** (the free web host behind the link).

Nothing runs on your laptop after it's set up — GitHub does it all on a schedule.

---

## 2. The files

| File / folder | What it is |
|---|---|
| `index.html` | The dashboard itself — all the layout, charts, and logic. The working file you edit. |
| `data/*.js` | The data, as JavaScript globals (`window.WTI_DATA`, `window.BASINS_DATA`, …). Loaded by the page. |
| `data/*.json` | The same data as plain JSON (a downloadable/inspectable copy). |
| `fetch_data.py` | Pulls **all** the data (production, basins, states, drilling, trade, prices, S&P/NASDAQ/Dow, gas). |
| `update_wti.py` | Pulls **only** the live WTI oil price (small, fast — the daily job). |
| `bundle.py` | Inlines the data into `US-Oil-Gas-Dashboard.html` and `publish-online/index.html`. |
| `publish-online/` | The finished, self-contained site that GitHub Pages serves. |
| `.github/workflows/refresh.yml` | The **daily** automation (price + publish). |
| `.github/workflows/quarterly.yml` | The **four-times-a-year** automation (full data + a review reminder). |
| `.env` | Your secret API keys, **never committed** (git-ignored). |
| `SOURCES.md` | Where each figure comes from + the quarterly human-review checklist. |

---

## 3. Every data source (with the exact series IDs)

**Live / automatic (pulled by the scripts):**

| What | Source | Series ID(s) | Cadence |
|---|---|---|---|
| US crude production (history + latest) | EIA | `MCRFPUS2` | monthly |
| Production by basin/region | EIA STEO | `COPRPM, COPRBK, COPREF, COPRAP, COPRHA, COPRR48, PAPRPGLF, PAPRPAK` | monthly |
| State-level crude (deep-history proxy) | EIA | `MCRFPTX1, MCRFPNM1, MCRFPND1, …` | annual |
| WTI oil price (monthly avg + live spot) | EIA `RWTC` + NYMEX front-month (CME/Yahoo) | `RWTC` (= FRED `DCOILWTICO`) | monthly + **daily** |
| Real (inflation-adjusted) WTI | BLS CPI (or FRED) | `CUSR0000SA0` / `CPIAUCSL` | monthly |
| Drilling: rigs, wells drilled/completed, DUCs, oil/rig | EIA STEO Table 10a | `RIGS/NWD/NWC/DUCS/CONWR` ×6 regions | monthly |
| Crude imports & exports | EIA | `MCREXUS2, MCRIMUS2, MCRIMUSCA2` | monthly |
| Stock indices (oil-vs-market chart) | FRED | `SP500, NASDAQCOM, DJIA` | monthly |
| Natural gas price (Henry Hub) | EIA | `RNGWHHD` | monthly + spot |

**Sourced / analyst (hand-entered, tagged & dated, reviewed quarterly — not auto):**

| What | Source |
|---|---|
| Basin breakevens | Dallas Fed Energy Survey (Q1 2026) |
| Remaining drilling locations / inventory tiers | Enverus & Novi Labs |
| Operator oil production | Company FY2025 filings (10-Ks / earnings) |
| Simulator decline benchmarks | Petropt "Permian Basin Decline Curve Benchmarks" |
| Capex & M&A (Outlook) | IEA World Energy Investment; Enverus |

Every number on the page carries a tag — **Live**, **Sourced**, or **Projection** —
so a reader always knows which is which.

---

## 4. How the auto-refresh works (the GitHub Action)

The automation lives in two files under `.github/workflows/`. They're not AI — they're
**recipes on a timer** that run on GitHub's servers.

**`refresh.yml` — the daily job (and on every change):**
- **Trigger:** every day at 12:00 UTC (~6 AM Mountain), on every push to `main`, and a manual "Run workflow" button.
- **Steps:** check out the files → set up Python → load the API key from an encrypted secret →
  run `update_wti.py` (fetch the live price) → run `bundle.py` (rebuild) → commit the refreshed
  files → publish to GitHub Pages.

**`quarterly.yml` — the heavy job (4× a year):**
- **Trigger:** 08:00 UTC on the 1st of **January, April, July, October** (cron `0 8 1 1,4,7,10 *`), plus a manual button.
- **Steps:** same as above, but it runs the **full** `fetch_data.py` (all data), and at the
  end it **opens a GitHub Issue** — a reminder for a human to review the sourced/analyst figures.
  It never changes those on its own.

**How GitHub actually does it:** when a trigger fires, GitHub spins up a brand-new
temporary computer ("a runner") in its cloud, runs the steps, and throws the computer
away. The timer format is called **cron**. `GitHub Pages` is the free hosting that serves
the finished files at the URL.

> **Note:** editing files under `.github/workflows/` requires the `workflow` permission,
> which a normal token doesn't have. If a tool can't push them, add/edit them through the
> GitHub website (paste the file contents, commit to `main`).

---

## 5. Keys & secrets (kept safe)

The scripts need two free API keys: **`EIA_API_KEY`** (energy data) and **`FRED_API_KEY`**
(stock indices + inflation). They live in two places, **never in the public code**:

- **Locally:** in a file named `.env` (git-ignored, so it's never committed):
  ```
  EIA_API_KEY=your_eia_key
  FRED_API_KEY=your_fred_key
  ```
- **On GitHub:** as **encrypted repository secrets** (Settings → Secrets and variables →
  Actions). The workflow writes them into a temporary `.env` at run time and they're never
  exposed in logs or the public files.

Get the keys free at: EIA — https://www.eia.gov/opendata/ · FRED — https://fred.stlouisfed.org/docs/api/api_key.html

---

## 6. How the simulator works

The Production Simulator projects a basin's oil output forward under a scenario you set.
It's a transparent planning model — **not** a reservoir-engineering forecast — and every
assumption is an adjustable slider.

It **stacks three streams** on top of the live EIA starting number:

1. **Legacy (existing wells) — declining.** Shale wells drop fast: a modified-hyperbolic
   type curve, ~70% decline in year one, tapering to a terminal ~13%/yr fade.
2. **New wells — from drilling.** The rig count drives how many new wells come on. Drilling
   works **best-rock-first** through Tier 1 → 2 → 3 → 4, and lower tiers recover less
   (Tier 2 ≈ 27% less than Tier 1, Tier 3 ≈ 45% less), so growth gets harder over time.
3. **DUC completions.** Finishing "drilled-but-uncompleted" wells adds oil without new
   drilling, until that backlog runs down.

**Legacy (down) + New (rigs, by tier) + DUCs = projected production.**

The decline shape and tier step-downs come from **Petropt's** Permian decline-curve
benchmarks (built on Texas RRC / New Mexico OCD / TGS / Enverus data); breakevens from the
Dallas Fed survey; inventory tiers from Enverus/Novi Labs. Base production, rigs, and DUCs
are **live from EIA**. Scenario buttons (Base / Upside / Downside) set every input at once.

There are two model types: an **inventory model** (the shale basins, with tiers) and a
**trend/rig model** (US total and conventional plays, where there's no public tier data).

---

## 7. Rebuild it from scratch (step by step)

You need: a computer with **Python 3** installed, a free **GitHub** account, and the two
API keys from Section 5.

**A. Get the project onto your computer**
1. Put all the project files in one folder (or `git clone` the repo).
2. In that folder, create a file named `.env` with your two keys (see Section 5).

**B. Pull the data and build it locally**
3. Open a terminal in the folder and run:
   ```
   python fetch_data.py     # downloads all the data into data/*.js and data/*.json
   python bundle.py         # builds publish-online/index.html (the finished site)
   ```
4. Open `publish-online/index.html` in a browser — that's the dashboard. If it looks right,
   you're ready to publish.

**C. Put it online (GitHub Pages + auto-refresh)**
5. Create a new GitHub repository and upload the whole folder (or `git push`).
6. **Settings → Pages → Source:** choose **GitHub Actions**.
7. **Settings → Secrets and variables → Actions:** add `EIA_API_KEY` and `FRED_API_KEY`.
8. Add the two workflow files under `.github/workflows/` (`refresh.yml`, `quarterly.yml`).
   If your tool can't push them, paste them in via the GitHub website and commit to `main`.
9. **Actions tab → Run workflow** on "Daily WTI price + publish" once to do the first
   publish. Your site is now live at `https://<your-username>.github.io/<repo-name>/`.

**D. From then on**
- The price refreshes **every morning**; the full data **four times a year**; and every
  quarter you get a GitHub Issue reminding you to review the analyst figures by hand
  (see `SOURCES.md` for the checklist). Any edit you push republishes within a couple of
  minutes.

**To change a chart or wording:** edit `index.html`, run `python bundle.py`, check
`publish-online/index.html` in a browser, then push. That's the whole loop.

---

## 8. Adding a new data series (worked example)

Say you want to add another market index. The pattern (used for NASDAQ/Dow) is:
1. In `fetch_data.py`, fetch the series (e.g. from FRED with its series ID) and attach it
   to the relevant payload.
2. Run `python fetch_data.py` (or just that fetch) so the new numbers land in `data/*.js`.
3. In `index.html`, read the new field and add it to the chart.
4. `python bundle.py`, check in a browser, push. The auto-refresh keeps it current.

---

*Compiled for MI3 Energy. Every figure on the dashboard is tagged and dated; the sourced
figures are reviewed on the quarterly cycle described above.*
