#!/usr/bin/env python3
"""The World State on X (@ubikworldstate): the edition when it lands, the forecasts it issues, and what settles.

The edition is a thread: the headline with the first sentences of the day's argument (the thesis, or the lead when
there is none), the questions issued that day, then the counts and an invitation to reply with one's own number. Each post carries a header card (tools/card.py):
the headline on the edition, one post and card per question issued, and the settled question with its score.

  python3 tools/worldstate.py           print what would be posted now (no posting); --cards DIR also writes the header images
  python3 tools/worldstate.py --post    post it (needs WS_X_API_KEY, WS_X_API_SECRET, WS_X_ACCESS_TOKEN, WS_X_ACCESS_SECRET)

Runs every hour from .github/workflows/worldstate.yml. tools/worldstate.log remembers what went out, one line per
item (kind, key, day, post id), so an edition is announced once, a question once, a settlement once. Revisions of
an edition during the day are not announced. Wording: forecasts are issued, resolve, settle, are scored; never bets.
"""
import argparse, datetime as dt, json, os, re, sys, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools")); import card
LOG = os.path.join(ROOT, "tools", "worldstate.log")
SITE = "https://ubikistan.org/world-state/"
NOTICE = "Forecasts are probabilities, not financial advice."
UA = {"User-Agent": "ubikistan-world-state-poster", "Accept": "application/json"}

def get(path):
    with urllib.request.urlopen(urllib.request.Request("https://ubik.gold" + path, headers=UA), timeout=30) as r: return json.load(r)

def posted():
    out = set()
    try:
        for l in open(LOG, encoding="utf-8"):
            if l.strip() and not l.startswith("#"): k = l.rstrip("\n").split("\t"); out.add((k[0], k[1]))
    except FileNotFoundError: pass
    return out

def long_day(iso): d = dt.date.fromisoformat(iso[:10]); return f"{d.day} {d.strftime('%B')}"
def pct(p): return f"{round((p or 0) * 100)}%"
def short_claim(c): return (c or "").strip()   # the question as issued, verbatim
def tlen(text): return len(re.sub(r"https?://\S+", "x" * 23, text))   # X counts every link as 23 characters

def sentences(text):
    """Split prose into sentences, keeping 'Oct. 21', 'U.S.' and the like together."""
    out, cur = [], ""
    for part in re.split(r"(?<=[.!?])\s+", (text or "").strip()):
        cur = (cur + " " + part).strip() if cur else part
        last = cur.split()[-1] if cur.split() else ""
        if re.fullmatch(r"[A-Z][a-z]{0,3}\.|(?:[A-Z]\.)+", last): continue   # an abbreviation, not an end
        out.append(cur); cur = ""
    if cur: out.append(cur)
    return out

def hook(thesis, lead, budget):
    """The first sentences of the day's argument (or of the lead) that fit the budget, at least one."""
    for src in (thesis, lead):
        picked = ""
        for s in sentences(src):
            if picked and tlen(picked + " " + s) > budget: break
            if not picked and tlen(s) > budget: break
            picked = (picked + " " + s).strip()
        if picked: return picked
    return ""

def kicker(f): return f"{f['question_id']} · open · resolves by {long_day(f['deadline'])}"
def issued_text(f, head="Issued today"): return f"{head}: {short_claim(f['claim'])}\n\nUBIK: {pct(f.get('probability'))}. Resolves by {long_day(f['deadline'])}."
def issued_card(f): return (card.forecast_card(f["claim"], f.get("probability") or 0, kicker(f), "ISSUED"), f["claim"])

def chunks(lines, head, limit=270):
    """Group lines into posts under the limit, the first carrying the head."""
    out, cur = [], head
    for l in lines:
        if tlen(cur) + tlen(l) + 1 > limit and cur.strip(): out.append(cur.rstrip()); cur = ""
        cur += ("\n" if cur else "") + l
    if cur.strip(): out.append(cur.rstrip())
    return out

def plan():
    """What to post now: a list of threads, each a list of post texts, with the log lines they stand for."""
    done = posted(); items = []
    syn = get("/synthesis?include=thesis"); meta = syn.get("meta", {}); prose = syn.get("prose", "")
    day = (meta.get("updated_at") or "")[:10]
    paras = [p.strip() for p in prose.split("\n") if p.strip()]
    head = next((p[2:].strip() for p in paras if p.startswith("# ")), "")
    lead = next((p for p in paras if not p.startswith("#")), "")
    thesis = (syn.get("methodology") or {}).get("thesis", "")
    open_ = get("/forecasts?status=open&include=history").get("data", [])
    settled = get("/forecasts?status=settled").get("data", [])
    new_qs = [f for f in open_ if f.get("question_id", "").startswith("q_" + day.replace("-", "")) and ("issued", f["question_id"]) not in done]
    # 1. the edition, once a day: the headline and the argument, the questions it issued, and a word to the reader
    if day and head and ("edition", day) not in done:
        top = f"Edition of {long_day(day)}\n{head}\n\n"
        first = top + hook(thesis, lead, 276 - tlen(top) - tlen("\n\n" + SITE)) + "\n\n" + SITE
        qs = sorted(new_qs, key=lambda f: f["question_id"]); n = len(qs)
        last = (f"{n} forecast{'s' if n != 1 else ''} issued today, {len(open_)} open. Each one is dated, and each one is scored in public when it settles.\n\n"
                f"Think the engine is wrong? Reply with your own number.\n\n{SITE}")
        thread = [first] + [issued_text(f) for f in qs] + [last]
        media = [[(card.edition_card(head, f"Edition of {long_day(day)} · {n} issued · {len(open_)} open"), head)]] + [[issued_card(f)] for f in qs]
        items.append({"thread": thread, "media": media, "log": [("edition", day, day)] + [("issued", f["question_id"], day) for f in new_qs]})
    elif new_qs:
        # questions issued later in the day, after the edition was announced
        qs = sorted(new_qs, key=lambda f: f["question_id"])
        items.append({"thread": [issued_text(f, f"Issued, {long_day(day)}") for f in qs] + [SITE], "media": [[issued_card(f)] for f in qs],
                      "log": [("issued", f["question_id"], day) for f in new_qs]})
    # 2. what settled
    for f in sorted(settled, key=lambda f: f.get("resolved_at") or ""):
        qid = f.get("question_id");
        if not qid or ("settled", qid) in done or not f.get("resolved_at"): continue
        verdict = "YES" if f.get("status") == "yes" else "NO"
        stood = pct(f.get("probability"))
        text = f"Settled {verdict}: {f['claim']}\n\nThe engine had it at {stood}. Brier {f.get('brier', 0):.3f}.\n\n{SITE}#ledger\n\n{NOTICE}"
        im = card.forecast_card(f["claim"], f.get("probability") or 0, f"{qid} · settled {verdict} · {long_day(f['resolved_at'])} · Brier {f.get('brier', 0):.3f}", "SETTLED")
        items.append({"thread": [text], "media": [[(im, f["claim"])]], "log": [("settled", qid, (f.get("resolved_at") or "")[:10])]})
    return items

def session():
    from requests_oauthlib import OAuth1Session
    keys = [(os.environ.get(k) or "").strip() for k in ("WS_X_API_KEY", "WS_X_API_SECRET", "WS_X_ACCESS_TOKEN", "WS_X_ACCESS_SECRET")]
    if not all(keys): sys.exit("World State X credentials missing")
    s = OAuth1Session(keys[0], client_secret=keys[1], resource_owner_key=keys[2], resource_owner_secret=keys[3])
    me = s.get("https://api.x.com/2/users/me")
    if not me.ok: sys.exit(f"X refused the key check: {me.status_code} {me.text[:200]}")
    print("posting as @" + (me.json().get("data") or {}).get("username", "?")); return s

def upload(s, im, alt):
    up = s.post("https://api.x.com/2/media/upload", data={"media_category": "tweet_image"}, files={"media": ("card.png", card.png(im), "image/png")})
    if up.status_code >= 300: sys.exit(f"X refused the image: {up.status_code} {up.text[:300]}")
    j = up.json(); mid = (j.get("data") or j).get("id") or (j.get("data") or j).get("media_id_string")
    if not mid: sys.exit(f"no media id in {up.text[:300]}")
    s.post("https://api.x.com/2/media/metadata", json={"id": mid, "metadata": {"alt_text": {"text": alt[:1000]}}})
    return mid

def post_thread(s, texts, media=()):
    """Post the texts as a thread; media[i] is a list of (image, alt) for post i, up to four."""
    ids = []; reply_to = None
    for i, t in enumerate(texts):
        body = {"text": t}
        if i < len(media) and media[i]: body["media"] = {"media_ids": [upload(s, im, alt) for im, alt in media[i][:4]]}
        if reply_to: body["reply"] = {"in_reply_to_tweet_id": reply_to}
        r = s.post("https://api.x.com/2/tweets", json=body)
        if r.status_code >= 300: sys.exit(f"X refused the post: {r.status_code} {r.text[:300]}")
        reply_to = r.json()["data"]["id"]; ids.append(reply_to)
    return ids

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--post", action="store_true"); ap.add_argument("--cards", help="also write the cards as PNGs into this folder"); a = ap.parse_args()
    s = session() if a.post else None   # the keys are checked even when there is nothing to say
    items = plan()
    if not items: print("nothing new"); sys.exit(0)
    for it in items:
        for i, t in enumerate(it["thread"]):
            print(t); m = it.get("media", [])
            if i < len(m) and m[i]: print(f"  [{len(m[i])} card{'s' if len(m[i]) != 1 else ''}]")
            print("  ---")
        print("====")
    if a.cards:
        os.makedirs(a.cards, exist_ok=True); k = 0
        for it in items:
            for ms in it.get("media", []):
                for im, alt in ms: k += 1; im.save(os.path.join(a.cards, f"card-{k:02d}.png"))
        print(f"{k} cards written to {a.cards}")
    if a.post:
        with open(LOG, "a", encoding="utf-8") as f:
            for it in items:
                ids = post_thread(s, it["thread"], it.get("media", []))
                for kind, key, day in it["log"]: f.write(f"{kind}\t{key}\t{day}\t{ids[0]}\n")
                print("posted", ids[0])
