#!/usr/bin/env python3
"""The State Archive's daily post: one record a day, in the archive's own voice.

  python3 tools/daily.py                 print today's post and the image it goes with (no posting)
  python3 tools/daily.py --post          post it to X (needs X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET)
  python3 tools/daily.py --date 2026-10-25   the post for another day

The week: Monday to Thursday a record from the Archive, rotating through the eras so the timeline shows over a
month; Friday a citizen's work from Culture, credited; Saturday a person on file; Sunday a settled forecast from the
World State, the one day the engine appears. What has been posted is kept in tools/daily.log, one code per line, so
nothing repeats until everything has had its turn. Records under review are skipped. No prices, no token, no hashtags.
"""
import argparse, datetime as dt, io, json, os, re, sys, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "tools", "daily.log")
SITE = os.environ.get("ARCHIVE_SITE", "https://ubikistan.org/archive/")
MIRROR = "https://ubikistan.github.io/archive/"

def lore():
    p = os.path.join(ROOT, "dist", "lore.json")
    if not os.path.exists(p): sys.exit("no dist/lore.json: run python3 tools/build.py build first")
    return json.load(open(p, encoding="utf-8"))

def posted():
    try: return [l.split("\t")[0].strip() for l in open(LOG, encoding="utf-8") if l.strip() and not l.startswith("#")]
    except FileNotFoundError: return []

def slug(code): return re.sub(r"[/ ]", "-", code)
def first_line(text): return (text or "").strip().split("\n")[0].strip()
def caption(r, limit=560):
    """The catalogue text, first paragraph(s), within what fits a post."""
    paras = [p.strip() for p in (r.get("text") or "").split("\n\n") if p.strip()]
    out = ""
    for p in paras:
        if len(out) + len(p) + 1 > limit: break
        out = (out + "\n\n" + p).strip()
    return out or r.get("title", "")

def pick_record(d, day, done):
    """Monday to Thursday: an Archive record with an image, canon or probable, the era least posted lately."""
    recs = [r for r in d["records"] if r.get("kind") == "archive" and r.get("status") in ("CANON", "PROBABLE")
            and not r.get("review") and r.get("access") != "restricted"
            and r.get("institution") != "RES" and r.get("collection") != "currency"   # the Treasury stays boring: no gold, no money in the feed
            and any(m.get("file") and m.get("type") == "image" for m in r.get("media", []))]
    fresh = [r for r in recs if r["code"] not in done] or recs
    # rotate the eras: the era whose last post is longest ago goes first
    last = {}
    for i, c in enumerate(done):
        for r in recs:
            if r["code"] == c: last[r.get("era")] = i
    # within the era, a record with something to say first (a caption of a few lines), then by year and code
    fresh.sort(key=lambda r: (last.get(r.get("era"), -1), 0 if len(r.get("text") or "") >= 90 else 1, r.get("year") or 0, r["code"]))
    return fresh[0]

def pick_culture(d, done):
    recs = [r for r in d["records"] if r.get("kind") == "culture" and not r.get("review")
            and any(m.get("file") and m.get("type") == "image" for m in r.get("media", []))]
    fresh = [r for r in recs if r["code"] not in done] or recs
    fresh.sort(key=lambda r: (r.get("added") or ""), reverse=True)
    return fresh[0] if fresh else None

def pick_person(d, done):
    people = [c for c in d.get("characters", []) if c.get("portrait") or c.get("image")]
    fresh = [c for c in people if "person:" + c.get("id", "") not in done] or people
    return fresh[0] if fresh else None

def settled_forecast():
    """Sunday: the most recently settled forecast on ubik.gold, public data."""
    try:
        with urllib.request.urlopen("https://ubik.gold/forecasts?status=settled", timeout=20) as r: data = json.load(r)["data"]
    except Exception: return None
    data = [f for f in data if f.get("resolved_at")]
    data.sort(key=lambda f: f["resolved_at"], reverse=True)
    return data[0] if data else None

def compose(d, day, done):
    wd = day.weekday()
    if wd == 4:
        r = pick_culture(d, done)
        if r:
            who = r.get("contributor") or "a citizen"
            text = f"{r['code']} · {r.get('date','')} · Culture\n\n{first_line(r.get('text'))}\n\nBy {who}. The Archive keeps what citizens make.\n\n{SITE}#/r/{slug(r['code'])}"
            return {"key": r["code"], "text": text, "image": media_file(r), "alt": media_alt(r)}
    if wd == 5:
        c = pick_person(d, done)
        if c:
            line = first_line(c.get("text") or c.get("role") or "")
            text = f"Persons on file · {c.get('name','')}\n\n{line}\n\n{SITE}#/characters/{c.get('id','')}"
            return {"key": "person:" + c.get("id", ""), "text": text, "image": c.get("portrait") or c.get("image"), "alt": c.get("name", "")}
    if wd == 6:
        f = settled_forecast()
        if f:
            verdict = "Settled YES" if f.get("status") == "yes" else "Settled NO"
            text = f"The world, as the engine saw it.\n\n{f['claim']}\n\n{verdict}. It had stood at {round((f.get('probability') or 0)*100)}%. Brier {f.get('brier', 0):.3f}.\n\nThe ledger keeps every forecast and its score. {SITE.replace('/archive/','/')}world-state/#ledger\n\nForecasts are probabilities, not financial advice."
            return {"key": "forecast:" + f["question_id"], "text": text, "image": None, "alt": ""}
    r = pick_record(d, day, done)
    text = f"{r['code']} · {r.get('date','')} · {r.get('format','')}\n\n{caption(r)}\n\nState Archive → {SITE}#/r/{slug(r['code'])}"
    return {"key": r["code"], "text": text, "image": media_file(r), "alt": media_alt(r)}

def media_file(r):
    for m in r.get("media", []):
        if m.get("file") and m.get("type") == "image": return m["file"]
        if m.get("poster"): return m["poster"]
    return None
def media_alt(r):
    for m in r.get("media", []):
        if m.get("alt"): return m["alt"]
    return r.get("title", "")

def image_bytes(path):
    """The image as X wants it: JPEG, under 5 MB, 1600 px on the long side."""
    from PIL import Image
    im = Image.open(os.path.join(ROOT, path)).convert("RGB"); im.thumbnail((1600, 1600))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=86, optimize=True); return buf.getvalue()

def post_to_x(text, image_path, alt):
    """X API v2 with OAuth 1.0a user context: media upload, alt text, then the post."""
    from requests_oauthlib import OAuth1Session
    keys = [(os.environ.get(k) or "").strip() for k in ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET")]
    if not all(keys): sys.exit("X credentials missing")
    s = OAuth1Session(keys[0], client_secret=keys[1], resource_owner_key=keys[2], resource_owner_secret=keys[3])
    def fail(what, r): sys.exit(f"X refused the {what}: HTTP {r.status_code} {r.text[:400]}")
    # who am I: proves the four keys belong together before anything is sent (lengths only, never the keys)
    print("key lengths (api key, api secret, access token, access secret):", [len(k) for k in keys], "| access token starts with a number:", keys[2][:1].isdigit())
    me = s.get("https://api.x.com/2/users/me")
    if me.status_code >= 300:
        v1 = s.get("https://api.x.com/1.1/account/verify_credentials.json")
        print("v1.1 verify_credentials answered", v1.status_code, v1.text[:200])
        fail("key check (the four keys do not fit together, or the app lacks write access)", me)
    print("posting as @" + (me.json().get("data") or {}).get("username", "?"), "| key lengths", [len(k) for k in keys])
    body = {"text": text}
    if image_path:
        up = s.post("https://api.x.com/2/media/upload", data={"media_category": "tweet_image"},
                    files={"media": ("image.jpg", image_bytes(image_path), "image/jpeg")})
        if up.status_code >= 300: fail("image", up)
        j = up.json(); media_id = (j.get("data") or j).get("id") or (j.get("data") or j).get("media_id_string")
        if not media_id: sys.exit(f"no media id in {up.text[:300]}")
        if alt:
            md = s.post("https://api.x.com/2/media/metadata", json={"id": media_id, "metadata": {"alt_text": {"text": alt[:1000]}}})
            if md.status_code >= 300: print("alt text not set:", md.status_code, md.text[:200])
        body["media"] = {"media_ids": [media_id]}
    r = s.post("https://api.x.com/2/tweets", json=body)
    if r.status_code >= 300: fail("post", r)
    return r.json()["data"]["id"]

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--post", action="store_true"); ap.add_argument("--date"); ap.add_argument("--delete", help="take a post down by its id"); a = ap.parse_args()
    if a.delete:
        from requests_oauthlib import OAuth1Session
        keys = [(os.environ.get(k) or "").strip() for k in ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET")]
        if not all(keys): sys.exit("X credentials missing")
        s = OAuth1Session(keys[0], client_secret=keys[1], resource_owner_key=keys[2], resource_owner_secret=keys[3])
        r = s.delete("https://api.x.com/2/tweets/" + a.delete); print("delete", a.delete, r.status_code, r.text[:200]); sys.exit(0 if r.ok else 1)
    day = dt.date.fromisoformat(a.date) if a.date else dt.datetime.now(dt.timezone(dt.timedelta(hours=2))).date()
    d = lore(); done = posted(); p = compose(d, day, done)
    print(p["text"]); print("\n[image]", p["image"] or "none", "|", p["alt"][:80])
    if a.post:
        pid = post_to_x(p["text"], p["image"], p["alt"])
        with open(LOG, "a", encoding="utf-8") as f: f.write(f"{p['key']}\t{day.isoformat()}\t{pid}\n")
        print("posted", pid)
