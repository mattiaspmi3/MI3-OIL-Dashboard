# -*- coding: utf-8 -*-
"""Prints a plain-English QUARTERLY REVIEW reminder (used as a GitHub issue body).

This NEVER edits any sourced/analyst figure. It only reminds a human to check whether
the hand-entered, paid-report / judgment-based numbers (and any major oil news) need
updating. The live API data is refreshed automatically by the jobs; these are not.
"""
import datetime

d = datetime.date.today()
q = (d.month - 1) // 3 + 1

print("""**Quarterly review — %s (Q%d %d)**

The live API data (production, prices, drilling, trade, S&P 500) was just auto-refreshed
by the quarterly job. The items below are **sourced / analyst estimates and human
judgment** — they come from paid reports and are **deliberately NOT auto-updated**.
Please check whether any need updating; if so, edit `index.html` at the location shown in
`SOURCES.md`, bump its `last_reviewed` date, and push (the site republishes on push).
**Never guess — if a figure can't be verified from a real source, leave it unchanged.**

### Sourced figures to check (see `SOURCES.md` for exact file locations)
- [ ] **Basin drill & shut-in breakevens** — Dallas Fed Energy Survey (new quarterly survey?)
- [ ] **Permian / Bakken / Eagle Ford inventory** estimates — Enverus / Novi Labs / RBN
- [ ] **Simulator decline assumptions** — terminal decline, tier step-downs, type curve (Petropt, or a newer benchmark)
- [ ] **Per-basin operators & top US producers** — after quarterly earnings
- [ ] **Basin shares & US share of world crude** — EIA Today-in-Energy
- [ ] **Capex & M&A charts** — IEA World Energy Investment; Enverus upstream M&A (annual)

### Scan recent oil news for anything that changes the model
- [ ] Major M&A / consolidation, big project sanctions, shut-ins, or discoveries
- [ ] OPEC+ policy shifts, sanctions, or a clear change in the price regime
- [ ] New basin inventory or decline studies worth citing

When finished, update the `last_reviewed` dates in `SOURCES.md` and close this issue.
""" % (d.isoformat(), q, d.year))
