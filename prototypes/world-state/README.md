# Ubikistan World State

A single static page built on a snapshot of the pre cog preview API (editions of 12–14 October 2026; market prices read 13 October), to show what the engine's data looks like with a human surface. Not connected to the deployment: every number in it is inlined.

Open `index.html` in a browser; there is no build step and no dependency beyond Google Fonts. The identity (mark, Michroma wordmark, gold/teal/pink on warm dark grey, Archivo and Newsreader) follows ubik.gold. On first arrival a cover asks whether to read as a human or as an agent and remembers the answer (`#cover` shows it again). Five pages, agent first, switched by the tabs in the masthead and addressable by hash: `#agent` (the Agent edition: the day as data, with a JSON view, `llms.txt` and the endpoints, plus Ask UBIK), `#edition` (the Human edition: the board first, every open question sortable with its probability, change, 14-day sparkline, market price and deadline, a What-changed stream with timestamps, then the edition), `#films` (one film per edition, hosted on the Internet Archive and played in place; social copies linked, not archived), `#dashboard` (the numbers), `#ledger` (the record, with sub-tabs Forecasts, Record, History, Mine).

What it shows: the day's synthesis; each current as a digest (lead lines with provenance tags, "why you should care", forecasts) that opens into the full section; a sheet per forecast in the team's schema (gold header with the question, the number and a 100-dot grid; why; folds for Thesis, How the news leads here, Reasoning, Considerations, Would confirm, Would count against, Related markets) with the ledger folded underneath (history, resolution rule, record ID, share card) and previous/next within the edition; UBIK's number next to the market price where a contract exists; the record and ledger; editions history; a signals ticker; world clocks; light, dark and UBIK modes (the last one the identity at night: black, gold, teal, pink); a share card per forecast; a Dashboard view (score tiles, a zoomable world map of where the questions are, a resolution horizon, every open question as a probability row with the market and issue marks, largest moves, UBIK vs market gaps, a calibration plot, questions by theme); a Chat page for the holder MCP endpoint (searches the snapshot for now); a Mine page where each viewer follows themes, places and free-text topics, adds sections to their feed and stars questions, kept in their browser until they sign in (signing in with GitHub or X through the archive's desk, the same sign-in as the Archive; the feed itself stays in the browser for now), and sees only what moved, what resolves next and which sections concern them.

Market prices: the desk reads the YES price of the Polymarket contracts listed in the page's `MKT_MAP` (`/ubik/markets`), every five minutes at most; `adj` marks a neighbouring question and `invert` reads a contract's NO side. The mapping is hand-made and changes with the questions.

Snapshot caveats: Polymarket prices were read on 13 October 2026 and are hard-coded. The crypto section (05, bylined AIXBT) and its three forecasts are sample content written for the prototype, not engine output. The publication window (holders 06:00 UTC, public 18:00 UTC) is proposed, not announced.


## Live, with the public part open and the rest for holders

Since 20 October 2026 the page carries no edition of its own. It renders a public snapshot inlined at build time (what anyone may read), then asks the archive's desk for the current edition and for the desk's archive of earlier editions. The desk passes a reader's own ubik.gold key through to ubik.gold, which decides what that key may see (a wallet holding 200,000 UBIK opens the holder parts); the key stays in the reader's browser and the desk keeps nothing. Everything free on ubik.gold stays free here; everything held for holders stays held. The desk refuses requests from the United States, and the page asks every reader once to confirm they are 18 or over and not in the United States.

The desk keeps one row per edition day (public part, and holder part when the desk has a key of its own as the secret `UBIK_KEY`), looked for at a quarter past every hour. The History tab lists them; opening one renders that day as it was.

`lock.py` is kept for the sealed versions in `archive/`; the live page is not sealed.

## Phones

Below 640px the page is one column: a scrolling tab strip under the wordmark, sign-in top right, the board as cards, the sheet full-bleed, the films stacked, the appearance switch and the social links in the footer. No horizontal scroll anywhere except the tab, clock, filter and ledger strips, which are meant to.

## Archive

- `archive/2026-10-14-editorial-first.html`: the editorial-first version (cover, agent and human editions, films, dashboard, ledger, Mine), frozen before the board-first update of 14 October 2026. (A local tag `world-state-editorial-first` exists; tags cannot be pushed from this environment.)

## Who runs it

A non-commercial, community-run initiative, built on content published by ubik.gold under its terms. Not financial advice; for entertainment and education only; AI-generated; not for persons under 18 or in the United States. The full text is at `../disclaimer/`.

The words the pages use (forecast, issued, resolves, scored; never prediction, call, bet or odds) are set out in `lore/ubik-forecast.md`.


## Built, since 21 October 2026

This file is a build output. The sources are in `pages/` at the root of the repository; `npm run build` there writes this folder. Edit the sources, not this file.
