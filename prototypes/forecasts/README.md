# Ubikistan Forecasts

A phone-first page that reads the engine's forecasts across contract markets, stocks and crypto: each as leaning yes, leaning no or open, with the gap against the market where a contract exists, what settles it and when, and the names it touches, for reference. A History tab lists every settled forecast with its score. Until 20 October 2026 (branch `forecast-pages-1.22`) it showed positions, entries, exits and venue links; those went in the legal pass of that evening.

The reading: above 60% the engine leans yes, below 40% it leans no, between it calls the question open; the gap is the engine's probability minus the market's where a contract exists. Nothing on the page is a position, a recommendation or a suggestion of what to do.

Data is a snapshot of the preview API (forecasts read 15 Oct 2026, Polymarket 13 Oct, Kalshi via AIXBT 14 Oct, AIXBT topics 16 Oct). The mapping from question to instruments and venues is hand-written in the page. The page was called Ubikistan Calls until 20 October 2026; the words it uses now are in `lore/ubik-forecast.md` (forecast, issued, resolves, scored).

## Live, for holders only

Since the evening of 20 October 2026 the whole page opens only with a ubik.gold key that ubik.gold answers "holder" to; without one it shows the gate and renders nothing.

Since 20 October 2026 the page reads the forecasts from ubik.gold through the archive's desk, as the World State page does (see `../world-state/README.md`); the mapping from question to instruments stays hand-written in the page (`INSTR`). A reader's ubik.gold key opens the holder parts; the page itself holds none.

A non-commercial, community-run initiative, built on content published by ubik.gold under its terms. Not financial advice; for entertainment and education only; AI-generated; not for persons under 18 or in the United States. The full text is at `../disclaimer/`.


## Built, since 21 October 2026

This file is a build output. The sources are in `pages/` at the root of the repository; `npm run build` there writes this folder. Edit the sources, not this file.
