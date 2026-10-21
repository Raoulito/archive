#!/usr/bin/env python3
"""Assemble the pages from their parts into src/, ready for Vite.

  world-state: parts/world-state.static.html + the live modules + the public snapshot
  forecasts:   parts/calls.static.html + the live modules (renders only for holders)
  disclaimer:  parts/disclaimer/index.html as it is

Each page's one inline script becomes src/<page>/main.js, loaded as a module, so Vite bundles it.
"""
import os, re, subprocess, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
PARTS = os.path.join(ROOT, "parts"); SRC = os.path.join(ROOT, "src"); SNAP = os.path.join(PARTS, "snapshot")
snap = [os.path.join(SNAP, f) for f in ("synthesis.json", "open.json", "settled.json")]

def build(script, static, out):
    subprocess.run([sys.executable, script, static, *snap, out], cwd=PARTS, check=True, stdout=subprocess.DEVNULL)

def split_script(page):
    """The last <script>…</script> of the page becomes a module file."""
    i = page.rfind("<script>"); j = page.rfind("</script>")
    if i < 0 or j < i: sys.exit("no inline script found")
    return page[:i] + '<script type="module" src="./main.js"></script>' + page[j + len("</script>"):], page[i + len("<script>"):j]

for name, static, builder in (("world-state", "world-state.static.html", "ws_build.py"), ("forecasts", "calls.static.html", "fc_build.py")):
    d = os.path.join(SRC, name); os.makedirs(d, exist_ok=True)
    tmp = os.path.join(PARTS, f".{name}.built.html")
    build(builder, static, tmp)
    page = open(tmp, encoding="utf-8").read(); os.remove(tmp)
    html, js = split_script(page)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(html)
    open(os.path.join(d, "main.js"), "w", encoding="utf-8").write(js)
    print(f"{name}: {len(html)} bytes html, {len(js)} bytes js")

d = os.path.join(SRC, "disclaimer"); os.makedirs(d, exist_ok=True)
shutil.copy(os.path.join(PARTS, "disclaimer", "index.html"), os.path.join(d, "index.html"))
print("disclaimer: copied")
