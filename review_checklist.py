# -*- coding: utf-8 -*-
"""Print the human review reminder used as a GitHub issue body."""
import datetime

d = datetime.datetime.now(datetime.timezone.utc).date()
q = (d.month - 1) // 3 + 1

print("""**Quarterly sourced-data review — %s (Q%d %d)**

This reminder is assigned to the repository owner. GitHub sends notifications according
to that account's notification settings; email delivery is not controlled by this script.

### What updates automatically
- WTI is refreshed daily by `refresh.yml`.
- The full EIA/BLS/FRED data is refreshed monthly by `quarterly.yml`.
- This issue does **not** run web research or change analyst estimates. Those need source
	verification and a human-approved edit.

### Review due sources
Use the cadence and file locations in [SOURCES.md](https://github.com/mattiaspmi3/MI3-OIL-Dashboard/blob/main/SOURCES.md). Review only items due this quarter.
- [ ] Dallas Fed survey: drill and operating breakevens
- [ ] Company filings and basin/operator production estimates
- [ ] Enverus, Novi Labs, and RBN: basin inventory and economics
- [ ] EIA Today in Energy and STEO/AEO outlook assumptions
- [ ] Petropt or newer decline-curve studies
- [ ] IEA capex and Enverus M&A reports when their annual releases are due

For every change, record the exact source URL, publication date, value, units, and method.
Do not update from search-result snippets or inaccessible reports. If a figure cannot be
verified, leave it unchanged and note why. Update the dashboard and `last_reviewed` date,
then submit the change for review. Close this issue when complete.
""" % (d.isoformat(), q, d.year))
