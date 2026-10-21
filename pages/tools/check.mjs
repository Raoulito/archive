#!/usr/bin/env node
// Every outside call the built pages make, pinged once. Exit 1 if any is dead.
// Run after `npm run build`; pass --site https://ubikistan.org to also check the deployed copy.
import { readFileSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const out = resolve(here, "../../prototypes");
const DESK = "https://ubikistan-guest-desk.ubikistan-archive.workers.dev";
const site = (process.argv.find((a, i) => process.argv[i - 1] === "--site") || "").replace(/\/$/, "");
let bad = 0;
const ok = (name, note = "") => console.log(`  ok    ${name}${note ? "  (" + note + ")" : ""}`);
const fail = (name, why) => { bad++; console.log(`  DEAD  ${name}: ${why}`); };

async function ping(name, url, { headers = {}, allow = [] } = {}) {
  try {
    const r = await fetch(url, { headers, signal: AbortSignal.timeout(20000) });
    if (r.ok) return ok(name, `${r.status}`);
    if (allow.includes(r.status)) return ok(name, `${r.status}, expected from here`);
    fail(name, `HTTP ${r.status}`);
  } catch (e) { fail(name, String(e.message || e)); }
}

console.log("Built files");
for (const p of ["world-state/index.html", "forecasts/index.html", "disclaimer/index.html"]) {
  const f = resolve(out, p); if (!existsSync(f)) { fail(p, "missing; run npm run build"); continue; }
  const html = readFileSync(f, "utf8");
  // every relative asset the page references must exist in the build
  const refs = [...html.matchAll(/(?:src|href)="(\.\.?\/[^"]+)"/g)].map((m) => m[1]).filter((u) => !u.endsWith("/"));
  const missing = refs.filter((u) => !existsSync(resolve(dirname(f), u)));
  if (missing.length) fail(p, "missing assets " + missing.join(", ")); else ok(p, `${refs.length} assets present`);
  if (p !== "disclaimer/index.html" && !/<meta name="desk"/.test(html)) fail(p, "no desk meta tag");
}

console.log("Outside calls");
const o = { Origin: "https://ubikistan.org" };
await ping("desk: ubik.gold pass-through", `${DESK}/ubik/llms.txt`, { headers: o, allow: [451] });          // 451 = the desk refuses the United States, which is where CI often runs
await ping("desk: editions archive", `${DESK}/ubik/editions`, { headers: o, allow: [451] });
await ping("desk: market prices", `${DESK}/ubik/markets?pm=2364962`, { headers: o, allow: [451] });
await ping("desk: sign-in (GitHub)", `${DESK}/auth/github?nonce=check&return=https%3A%2F%2Fubikistan.org%2Fworld-state%2F`, { allow: [302, 303] });
await ping("ubik.gold: synthesis", "https://ubik.gold/synthesis");
await ping("ubik.gold: forecasts", "https://ubik.gold/forecasts?status=open");
await ping("ubik.gold: llms.txt", "https://ubik.gold/llms.txt");
await ping("Polymarket gamma (read by the desk)", "https://gamma-api.polymarket.com/markets/2364962");
await ping("Internet Archive embeds (films)", "https://archive.org/embed/ubikistan", { allow: [404] });
if (site) {
  console.log(`Deployed copy at ${site}`);
  for (const p of ["/world-state/", "/forecasts/", "/disclaimer/"]) await ping(`site ${p}`, site + p);
  try {
    const r = await fetch(site + "/world-state/", { signal: AbortSignal.timeout(20000) });
    const html = await r.text(); const m = /<meta name="desk" content="([^"]*)"/.exec(html); const desk = m ? m[1] : "";
    const csp = r.headers.get("content-security-policy") || "";
    const connect = /connect-src ([^;]*)/.exec(csp); const allowed = connect ? connect[1] : "(no CSP)";
    if (desk === "" && csp && !allowed.includes(DESK)) fail("site CSP", `connect-src does not allow the desk: ${allowed}`);
    else ok("site CSP", desk ? `desk at ${desk} (same origin)` : `connect-src allows the desk`);
    if (desk) await ping("site same-origin proxy", site + desk + "/ubik/llms.txt", { allow: [451] });
    for (const a of [...html.matchAll(/(?:src|href)="(\.\.?\/[^"]+)"/g)].map((x) => x[1]).slice(0, 6)) await ping(`site asset ${a}`, new URL(a, site + "/world-state/").href);
  } catch (e) { fail("site", String(e.message || e)); }
}
console.log(bad ? `\n${bad} dead` : "\nall alive");
process.exit(bad ? 1 : 0);
