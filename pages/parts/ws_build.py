#!/usr/bin/env python3
"""Build the live World State page from the static one.

usage: ws_build.py world-state.static.html pub_syn.json pub_open.json pub_settled.json out.html
Drops the inlined edition data, inlines the public snapshot (what anyone may read), adds the live
loader (ws_live.js), the holder-key dialog, the archive bar, the disclaimer footer.
"""
import json, re, sys
src, syn_p, open_p, settled_p, out = sys.argv[1:6]
page = open(src, encoding="utf-8").read()
live_top = open("ws_live_top.js", encoding="utf-8").read(); live_boot = open("ws_live_boot.js", encoding="utf-8").read()
snap = {"synthesis": json.load(open(syn_p)), "open": json.load(open(open_p)), "settled": json.load(open(settled_p))}
for k in ("open", "settled"):
    if isinstance(snap[k], dict) and "data" in snap[k]:
        snap[k] = {"data": snap[k]["data"]}
snap["synthesis"].pop("stills", None)
if "methodology" in snap["synthesis"]:
    snap["synthesis"]["methodology"].pop("sources", None)
SNAP = "const SNAPSHOT=" + json.dumps(snap, ensure_ascii=False, separators=(",", ":")).replace("</script", "<\\/script") + ";\n"

def cut(pat, repl=""):
    global page
    m = re.search(pat, page, re.S)
    if not m: sys.exit("not found: " + pat[:50])
    page = page[:m.start()] + repl + page[m.end():]

# 1. data blocks out; the live module declares them as lets
cut(r"const F = \[\n.*?\n\];\n")
cut(r"const CURRENTS = \[\n.*?\n\];\n")
cut(r"const EDITIONS = \[\n.*?\n\];\n")
cut(r"const TS=\{.*?\};\n")
cut(r"const RESOLVED_AT=\{.*?\};\n")
cut(r"const GEO = \{\n.*?\n\};\n")
cut(r"const AGENT_ED=\{.*?\n\};\n")
cut(r"const LAST_CHANGE=.*?\n")
cut(r"const byId = Object\.fromEntries\(F\.map\(f=>\[f\.id,f\]\)\);\n")
# the first render at the foot of the script and the dated labels in templates
cut(r"renderResolved\(\); renderAll\(\);\n", "")
page = page.replace("EDITION 2026-10-20", "EDITION ${EDITION_DAY}")
page = page.replace("st.textContent=`EDITION ${EDITION_DAY} · LAST CHANGE", "st.textContent=`EDITION ${EDITION_DAY} · ${SHOWING===\"current\"?(LIVE?\"LIVE\":\"SNAPSHOT\"):\"FROM THE ARCHIVE\"} · LAST CHANGE")
page = page.replace('note:"Snapshot of the ubik.gold edition of 2026-10-20, holder view."', 'note:SHOWING==="current"?(LIVE?"Live from ubik.gold through the desk.":"Public snapshot."):"From the desk\'s archive of editions."')
page = page.replace('source:"https://ubik.gold/synthesis?include=all"', 'source:"https://ubik.gold/synthesis?include=all", standing:STANDING')
if not page.lstrip().lower().startswith("<!doctype"):
    page = '<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n<meta name="desk" content="%VITE_DESK%">\n' + page
# 2. markup: ids, gate, key dialog, archive bar, footer
page = page.replace('<div class="date">The world on 20 October 2026</div>', '<div class="ekick" id="ekick"></div><div class="date" id="edate"></div>', 1)
page = page.replace('<span class="s">${esc(e.sum)}</span></span><span class="n">', '<span class="s">${esc(e.sum)}${(e.current?EDITION_UPDATED:e.updated)?` <span class="upd">${esc(updatedTag(e.current?EDITION_UPDATED:e.updated))}</span>`:""}</span></span><span class="n">', 1)
page = re.sub(r'document\.getElementById\("cover-h"\)\.textContent=`The world on \$\{new Date\(AGENT_ED\.date\+"T12:00:00Z"\)[^;]*;', 'document.getElementById("cover-h").textContent=EDITION_TITLE||`The world on ${EDITION_LONG}`;', page, count=1)
page = page.replace('<h1 id="cover-h"></h1>', '<div class="ekick" id="cover-k"></div><h1 id="cover-h"></h1>', 1)
page = re.sub(r'(<div class="date" id="edate">[^<]*</div>\n\s*)<p>[^<]*</p>', r'\1<p id="elede"></p>', page, count=1)
page = page.replace('<div class="num">AGENT EDITION · 2026-10-20 · FOR MODELS, AGENTS AND THE PEOPLE WHO RUN THEM</div>', '<div class="num" id="agdate">AGENT EDITION · 2026-10-20 · FOR MODELS, AGENTS AND THE PEOPLE WHO RUN THEM</div>', 1)
page = page.replace('<h2 class="t">The world on 20 October 2026, as data.</h2>', '<h2 class="t" id="agtitle">The world on 20 October 2026, as data.</h2>', 1)
page = page.replace('<span class="who" id="who"></span>', '<span class="gate" id="gate"></span><span class="who" id="who"></span>', 1)
page = re.sub(r'<span class="stamp" id="stamp">[^<]*</span>', '<span class="stamp" id="stamp"></span><span class="stamp next" id="nextclock"></span>', page, count=1)
page = page.replace('<div class="counts" id="counts">', '<div class="archivebar hidden" id="archivebar"><b></b><button type="button" id="tocurrent">Back to the current edition →</button></div>\n    <div class="counts" id="counts">', 1)
page = page.replace('  <footer>', open('account.html', encoding='utf-8').read() + '  <footer>', 1)
FOOT = '''<span class="legal"><a href="../disclaimer/" class="disc">Disclaimer</a> · <a href="https://ubik.gold/terms" target="_blank" rel="noopener">ubik.gold terms</a>. Not financial advice. For entertainment and education only. Built on content published by ubik.gold; a non-commercial, community-run initiative. AI-generated. Not for persons under 18 or in the United States.</span>'''
page = re.sub(r'<span>Run by the UBIK team under .*?</span>\n', FOOT + "\n", page, count=1, flags=re.S)
page = page.replace('<span>The Archive remembers. UBIK forms a view.</span>', '<span>The Archive remembers. UBIK forms a view.</span>', 1)
# 3. styles
page = page.replace("</style>", open('account.css', encoding='utf-8').read() + '''
.gate{margin-right:10px}
.ekick{font-family:var(--kick);font-weight:500;letter-spacing:.09em;text-transform:uppercase;font-size:11px;color:var(--muted);margin-bottom:8px}
#cover .ekick{color:var(--muted);margin-bottom:10px}
.hrow .upd{font-family:var(--mono);font-size:10.5px;color:var(--muted);margin-left:6px}
.mast .stamp.next{margin-left:14px;color:var(--ring-text)}
.mast .stamp.next.overdue{color:var(--gold)}
.mast .stamp.next .due{display:inline-block;width:6px;height:6px;border-radius:50%;background:currentColor;margin-right:6px;vertical-align:1px;animation:duepulse 1.6s ease-in-out infinite}
@keyframes duepulse{0%,100%{opacity:1}50%{opacity:.25}}
</style>''', 1)
# 4. the live module goes in before the first render would have happened: at the end of the script
j = page.index("const THEMES = {")
page = page[:j] + SNAP + open("markets.js", encoding="utf-8").read() + open("nextclock.js", encoding="utf-8").read() + live_top + "\n" + page[j:]
page = page.replace("\nif(!route()){", "\nif(false&&!route()){", 1)
i = page.rfind("</script>")
page = page[:i] + "\n" + live_boot + '\ndocument.getElementById("tocurrent").addEventListener("click",()=>{ loadCurrent().then(loadEditions).catch(()=>applyEdition(SNAPSHOT,"current")); });\n' + page[i:]
# selectEdition: open an archived day from the desk
page = re.sub(r"function selectEdition\(d\)\{.*?\n\}\n", '''function selectEdition(d){
  if(d===EDITION_DAY&&SHOWING==="current"){ go("edition",true); return; }
  const e=EDITIONS.find(x=>x.d===d);
  if(e&&e.live){ loadCurrent().then(loadEditions).catch(()=>{}); go("edition",true); return; }
  openEdition(d).then(()=>{ go("edition",true); window.scrollTo({top:0,behavior:"smooth"}); }).catch(()=>{ alert_=null; });
}
let alert_=null;
''', page, count=1, flags=re.S)
page = page.replace('<p style="font-size:13px;color:var(--muted)">Full text of this edition is not in the snapshot. The forecasts it issued are, with their histories.</p>', '')
page = page.replace("<footer>", open("attest.html", encoding="utf-8").read() + "<footer>", 1)
page = page.replace("</style>", open("attest.css", encoding="utf-8").read() + "</style>", 1)
i = page.rfind("</script>")
page = page[:i] + "\n" + open("gate_common.js", encoding="utf-8").read() + page[i:]
open(out, "w", encoding="utf-8").write(page)
print("built", out, len(page))
