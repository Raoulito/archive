#!/usr/bin/env python3
"""The World State on X (@ubikworldstate): the edition when it lands, the forecasts it issues, and what settles.

  python3 tools/worldstate.py           print what would be posted now (no posting)
  python3 tools/worldstate.py --post    post it (needs WS_X_API_KEY, WS_X_API_SECRET, WS_X_ACCESS_TOKEN, WS_X_ACCESS_SECRET)

Runs every hour from .github/workflows/worldstate.yml. tools/worldstate.log remembers what went out, one line per
item (kind, key, day, post id), so an edition is announced once, a question once, a settlement once. Revisions of
an edition during the day are not announced. Wording: forecasts are issued, resolve, settle, are scored; never bets.
"""
import argparse, datetime as dt, json, os, sys, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

def chunks(lines, head, limit=270):
    """Group lines into posts under the limit, the first carrying the head."""
    out, cur = [], head
    for l in lines:
        if len(cur) + len(l) + 1 > limit and cur.strip(): out.append(cur.rstrip()); cur = ""
        cur += ("\n" if cur else "") + l
    if cur.strip(): out.append(cur.rstrip())
    return out

def plan():
    """What to post now: a list of threads, each a list of post texts, with the log lines they stand for."""
    done = posted(); items = []
    syn = get("/synthesis"); meta = syn.get("meta", {}); prose = syn.get("prose", "")
    day = (meta.get("updated_at") or "")[:10]
    head = next((l[2:].strip() for l in prose.split("\n") if l.startswith("# ")), "")
    open_ = get("/forecasts?status=open&include=history").get("data", [])
    settled = get("/forecasts?status=settled").get("data", [])
    new_qs = [f for f in open_ if f.get("question_id", "").startswith("q_" + day.replace("-", "")) and ("issued", f["question_id"]) not in done]
    # 1. the edition, once a day, with the questions it issued as replies
    if day and head and ("edition", day) not in done:
        first = f"Edition of {long_day(day)}: {head}\n\n{len(new_qs)} forecast{'s' if len(new_qs) != 1 else ''} issued, {len(open_)} open.\n\n{SITE}"
        lines = [f"• {short_claim(f['claim'])} · {pct(f.get('probability'))} · by {long_day(f['deadline'])}" for f in sorted(new_qs, key=lambda f: f["question_id"])]
        thread = [first] + (chunks(lines, "Issued today:") if lines else [])
        items.append({"thread": thread, "log": [("edition", day, day)] + [("issued", f["question_id"], day) for f in new_qs]})
    elif new_qs:
        # questions issued later in the day, after the edition was announced
        lines = [f"• {short_claim(f['claim'])} · {pct(f.get('probability'))} · by {long_day(f['deadline'])}" for f in sorted(new_qs, key=lambda f: f["question_id"])]
        items.append({"thread": chunks(lines, f"Issued, {long_day(day)}:") + [SITE], "log": [("issued", f["question_id"], day) for f in new_qs]})
    # 2. what settled
    for f in sorted(settled, key=lambda f: f.get("resolved_at") or ""):
        qid = f.get("question_id");
        if not qid or ("settled", qid) in done or not f.get("resolved_at"): continue
        verdict = "YES" if f.get("status") == "yes" else "NO"
        stood = pct(f.get("probability"))
        text = f"Settled {verdict}: {f['claim']}\n\nThe engine had it at {stood}. Brier {f.get('brier', 0):.3f}.\n\n{SITE}#ledger\n\n{NOTICE}"
        items.append({"thread": [text], "log": [("settled", qid, (f.get("resolved_at") or "")[:10])]})
    return items

def session():
    from requests_oauthlib import OAuth1Session
    keys = [(os.environ.get(k) or "").strip() for k in ("WS_X_API_KEY", "WS_X_API_SECRET", "WS_X_ACCESS_TOKEN", "WS_X_ACCESS_SECRET")]
    if not all(keys): sys.exit("World State X credentials missing")
    s = OAuth1Session(keys[0], client_secret=keys[1], resource_owner_key=keys[2], resource_owner_secret=keys[3])
    me = s.get("https://api.x.com/2/users/me")
    if not me.ok: sys.exit(f"X refused the key check: {me.status_code} {me.text[:200]}")
    print("posting as @" + (me.json().get("data") or {}).get("username", "?")); return s

def post_thread(s, texts):
    ids = []; reply_to = None
    for t in texts:
        body = {"text": t}
        if reply_to: body["reply"] = {"in_reply_to_tweet_id": reply_to}
        r = s.post("https://api.x.com/2/tweets", json=body)
        if r.status_code >= 300: sys.exit(f"X refused the post: {r.status_code} {r.text[:300]}")
        reply_to = r.json()["data"]["id"]; ids.append(reply_to)
    return ids

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--post", action="store_true"); a = ap.parse_args()
    s = session() if a.post else None   # the keys are checked even when there is nothing to say
    items = plan()
    if not items: print("nothing new"); sys.exit(0)
    for it in items:
        for t in it["thread"]: print(t); print("  ---")
        print("====")
    if a.post:
        with open(LOG, "a", encoding="utf-8") as f:
            for it in items:
                ids = post_thread(s, it["thread"])
                for kind, key, day in it["log"]: f.write(f"{kind}\t{key}\t{day}\t{ids[0]}\n")
                print("posted", ids[0])
