# Handoff — MI3 US Oil Dashboard

One page so anyone at MI3 can keep this running after the original author leaves.

---

## What this is
An interactive US oil dashboard. It's a set of files in this GitHub repo. A daily
job on GitHub's servers pulls fresh government data, rebuilds the page, and
publishes it to a permanent link. **No personal computer is involved once it's set up.**

## The live link
**https://mattiaspmi3.github.io/MI3-OIL-Dashboard/** — updates itself daily.

## Who owns / controls it
- **GitHub account that owns the repo:** `mattiaspmi3` (registered under an MI3 company email).
- **Repo:** `MI3-OIL-Dashboard` (public).
- **Admins with access:** `________________`  ← **ADD A COMPANY ACCOUNT HERE.**

> ⚠️ If the owning account is ever deleted and no one else is an admin, the live
> site and auto-updates stop. Make sure at least one **company** account is an
> **admin** of the repo (or move the repo into a company **Organization**).

## The API key (how the data gets pulled)
- **EIA_API_KEY** — required. Free, from https://www.eia.gov/opendata/register.php
  (registered under a company email). Stored as a repo **Secret**
  (Settings → Secrets and variables → Actions), **not** in the code.
- **FRED_API_KEY** — optional (only for one inflation line; works without it).
- There is also a second, **public read-only** EIA key embedded in the page for
  live prices — that one is meant to be visible and is safe.

## How it auto-updates
- The file `.github/workflows/refresh.yml` runs **daily on GitHub's servers**.
- It runs `python fetch_data.py` (get data) → `python bundle.py` (rebuild) →
  publishes to the live link, and commits a "Daily data refresh (auto)" each day.
- To refresh **on demand**: repo → **Actions** tab → "Refresh & publish dashboard"
  → **Run workflow**.

## How to change a hand-entered ("Sourced") number
- Sourced figures live in `index.html` (in clearly labelled config blocks) and are
  mapped in **`SOURCES.md`** (which figure, its source, and where it is in the file).
- Edit `index.html`, commit, push. The daily job (or a manual run) republishes it.
- Full explanation of everything is in **`GUIDE.md`**.

## To refresh manually on a laptop (optional, not required)
1. Put the EIA key in a file named `.env`:  `EIA_API_KEY=yourkey`
2. `python fetch_data.py`  then  `python bundle.py`
3. Open `US-Oil-Gas-Dashboard.html` (the self-contained shareable file).

## If the daily job stops working
- Check repo → **Actions** tab for a red (failed) run; open it to see the error.
- Most common causes: the API key Secret is missing/expired, or GitHub Pages was
  turned off. Re-add the Secret / re-enable Pages (Settings → Pages → Source:
  GitHub Actions).
