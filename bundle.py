# -*- coding: utf-8 -*-
"""Bundle index.html + data/*.js + logo into the self-contained shareable file and
refresh publish-online/. Run after fetch_data.py so the shared/published copies stay current."""
import io, os, base64

html = io.open("index.html", encoding="utf-8").read()
for name in ["wti", "total_us", "basins", "states", "natgas", "sp500", "drilling", "trade", "usmap"]:
    tag = '<script src="data/%s.js"></script>' % name
    path = os.path.join("data", name + ".js")
    if tag in html and os.path.exists(path):
        html = html.replace(tag, "<script>\n/* data/%s.js */\n%s\n</script>"
                            % (name, io.open(path, encoding="utf-8").read()))

if os.path.exists("mi3-logo.svg"):
    uri = "data:image/svg+xml;base64," + base64.b64encode(
        io.open("mi3-logo.svg", encoding="utf-8").read().encode("utf-8")).decode("ascii")
    html = html.replace('src="mi3-logo.svg"', 'src="%s"' % uri)

io.open("US-Oil-Gas-Dashboard.html", "w", encoding="utf-8").write(html)
os.makedirs("publish-online", exist_ok=True)
io.open(os.path.join("publish-online", "index.html"), "w", encoding="utf-8").write(html)
print("Bundled US-Oil-Gas-Dashboard.html + publish-online/index.html "
      "(external data refs left: %d)" % html.count('src="data/'))
