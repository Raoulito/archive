# UBIK / WORLD STATE — front-door prototype

A single static page built on a snapshot of the pre cog preview API (editions of 12–14 October 2026; market prices read 13 October), to show what the engine's data looks like with a human surface. Not an official page, and not connected to the deployment: every number in it is inlined.

Open `index.html` in a browser; there is no build step and no dependency beyond Google Fonts. Four pages, agent first, switched by the tabs in the masthead and addressable by hash: `#agent` (the Agent edition: the day as data, with a JSON view, `llms.txt` and the endpoints, plus Ask UBIK), `#edition` (the Human edition), `#dashboard` (the numbers), `#ledger` (the record, with sub-tabs Forecasts, Record, History, Mine).

What it shows: the day's synthesis; each current as a digest (lead lines with provenance tags, "why you should care", forecasts) that opens into the full section; a dossier per forecast with the probability history, resolution rule and editorial history; UBIK's number next to the market price where a contract exists; the record and ledger; editions history; a signals ticker; world clocks; light, dark and neon modes; a share card per forecast; a Dashboard view (score tiles, a zoomable world map of where the questions are, a resolution horizon, every open question as a probability row with the market and issue marks, largest moves, UBIK vs market gaps, a calibration plot, questions by theme); a Chat page for the holder MCP endpoint (searches the snapshot for now); a Mine page where each viewer follows themes, places and free-text topics, adds sections to their feed and stars questions, kept in their browser until they sign in (a prototype sign-in with GitHub, X or a wallet handle, local only), and sees only what moved, what resolves next and which sections concern them.

Snapshot caveats: Polymarket prices were read on 13 October 2026 and are hard-coded. The crypto section (05, bylined AIXBT) and its three forecasts are sample content written for the prototype, not engine output. The publication window (holders 06:00 UTC, public 18:00 UTC) is proposed, not announced.

Headroom, October 2026.
