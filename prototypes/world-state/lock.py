#!/usr/bin/env python3
"""Lock a single-file HTML page behind a passphrase.

The page is encrypted with AES-256-GCM; the key comes from the passphrase through
PBKDF2-SHA256 (300,000 rounds). What is published is a small gate page that holds only
the ciphertext: without the passphrase the content is not in the file at all.

usage: lock.py SOURCE.html OUT.html "passphrase" [--title "UBIK / World State"]
"""
import sys, os, json, base64, hashlib, argparse
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out"); ap.add_argument("passphrase")
ap.add_argument("--title", default="UBIK / World State")
ap.add_argument("--sub", default="World State")
ap.add_argument("--blurb", default="A community edition built on UBIK's public data, not affiliated with the UBIK token, team or platform. Enter the passphrase to open it on this device.")
a = ap.parse_args()

ROUNDS = 300_000
salt = os.urandom(16); iv = os.urandom(12)
key = hashlib.pbkdf2_hmac("sha256", a.passphrase.encode("utf-8"), salt, ROUNDS, dklen=32)
plain = open(a.src, "rb").read()
ct = AESGCM(key).encrypt(iv, plain, None)
b64 = lambda b: base64.b64encode(b).decode()

MARK = '''<svg class="mark" viewBox="0 0 128 128" aria-hidden="true"><circle cx="64" cy="64" r="50" fill="none" stroke="var(--red)" stroke-width="19"/><circle cx="64" cy="64" r="25" fill="none" stroke="var(--gold)" stroke-width="9"/></svg>'''

gate = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<title>{a.title}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900&family=Hanken+Grotesk:wght@400;500&family=Geist+Mono:wght@400;500&display=swap">
<style>
:root{{--bg:#ECEDEA;--ink:#1A1F20;--muted:#566062;--line:#D3D7D4;--rule:#1A1F20;--gold:#B8912E;--red:#C8322A;--hot:#C8322A;--flag:#4A3B7C}}
@media (prefers-color-scheme: dark){{:root{{--bg:#0F1213;--ink:#E3E7E5;--muted:#9AA4A3;--line:#283031;--rule:#364041;--gold:#D2AE4E;--red:#E0473C;--hot:#E0473C}}}}
html,body{{margin:0;min-height:100%;background:var(--bg);color:var(--ink)}}
body{{display:grid;place-items:center;font-family:"Hanken Grotesk",system-ui,sans-serif;padding:24px}}
.gate{{width:min(440px,100%);}}
.head{{display:flex;align-items:center;gap:12px;margin-bottom:28px}}
.head .mark{{width:34px;height:34px}}
.head .wm{{font-family:"Archivo",sans-serif;font-weight:800;font-stretch:125%;font-size:17px;letter-spacing:-.01em}}
.head .ws{{font-family:"Geist Mono",monospace;font-weight:500;font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}}
.k{{font-family:"Archivo",sans-serif;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}}
h1{{font-family:"Archivo",sans-serif;font-weight:800;font-stretch:118%;font-size:clamp(28px,5vw,36px);line-height:1;margin:8px 0 10px;letter-spacing:-.03em;text-transform:lowercase}}
p{{font-size:16px;line-height:1.5;color:var(--muted);margin:0 0 20px}}
form{{display:flex;border:1px solid var(--rule)}}
input{{flex:1;min-width:0;border:0;background:none;color:var(--ink);font-family:"Geist Mono",monospace;font-size:15px;padding:12px 12px;outline:none}}
button{{font-family:"Archivo",sans-serif;font-weight:700;font-size:11px;letter-spacing:.12em;text-transform:uppercase;border:0;border-left:1px solid var(--rule);background:var(--ink);color:var(--bg);padding:0 16px;cursor:pointer}}
button:disabled{{opacity:.6}}
.err{{color:var(--hot);font-family:"Geist Mono",monospace;font-size:11.5px;margin-top:10px;min-height:1.4em}}
.foot{{font-family:"Geist Mono",monospace;font-size:10.5px;color:var(--muted);margin-top:28px;line-height:1.6}}
label.rem{{display:flex;gap:8px;align-items:center;font-family:"Archivo",sans-serif;font-size:12px;color:var(--muted);margin-top:12px}}
</style>
</head>
<body>
<main class="gate">
  <div class="head">{MARK}<span class="wm">UBIK</span><span class="ws">{a.sub} · community</span></div>
  <div class="k">Republic of Ubikistan · community page</div>
  <h1>This page is sealed.</h1>
  <p>{a.blurb}</p>
  <form id="f" autocomplete="off"><input id="p" type="password" placeholder="passphrase" aria-label="Passphrase" autofocus><button type="submit" id="b">Open</button></form>
  <label class="rem"><input type="checkbox" id="rem" checked> Keep it open on this device</label>
  <div class="err" id="e" role="alert"></div>
  <div class="foot">Encrypted in the file itself (AES-256-GCM, PBKDF2 {ROUNDS:,} rounds). Nothing is sent anywhere; the passphrase never leaves your browser.<br>Not affiliated with the UBIK token, team or platform.</div>
</main>
<script>
const SEALED={{salt:"{b64(salt)}",iv:"{b64(iv)}",rounds:{ROUNDS},ct:"{b64(ct)}"}};
const u8=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
async function unseal(pass){{
  const km=await crypto.subtle.importKey("raw",new TextEncoder().encode(pass),"PBKDF2",false,["deriveKey"]);
  const key=await crypto.subtle.deriveKey({{name:"PBKDF2",salt:u8(SEALED.salt),iterations:SEALED.rounds,hash:"SHA-256"}},km,{{name:"AES-GCM",length:256}},false,["decrypt"]);
  const plain=await crypto.subtle.decrypt({{name:"AES-GCM",iv:u8(SEALED.iv)}},key,u8(SEALED.ct));
  return new TextDecoder().decode(plain);
}}
async function open(pass,remember){{
  const b=document.getElementById("b"),e=document.getElementById("e"); b.disabled=true; e.textContent="";
  try{{ const html=await unseal(pass); try{{ if(remember) localStorage.setItem("ubik-seal",pass); else localStorage.removeItem("ubik-seal"); }}catch(_){{}}
    document.open(); document.write(html); document.close(); }}
  catch(err){{ e.textContent="That is not the passphrase."; b.disabled=false; document.getElementById("p").select(); }}
}}
document.getElementById("f").addEventListener("submit",ev=>{{ ev.preventDefault(); open(document.getElementById("p").value,document.getElementById("rem").checked); }});
try{{ const saved=localStorage.getItem("ubik-seal"); if(saved) open(saved,true); }}catch(_){{}}
</script>
</body>
</html>
'''
open(a.out, "w").write(gate)
print(f"sealed {len(plain)//1024} KB -> {a.out} ({len(gate)//1024} KB)")
