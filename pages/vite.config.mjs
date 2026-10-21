import { defineConfig } from "vite";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
// The desk (the archive's Cloudflare Worker): the pages call it for ubik.gold's editions, market prices and sign-in.
const DESK = "https://ubikistan-guest-desk.ubikistan-archive.workers.dev";
// Same-origin proxy for development: the page calls /api/..., Vite forwards it to the desk with an origin the desk accepts.
const proxy = { "/api": { target: DESK, changeOrigin: true, rewrite: (p) => p.replace(/^\/api/, ""), headers: { Origin: "http://localhost:8765" } } };

export default defineConfig({
  root: resolve(here, "src"),
  envDir: here,                     // .env and .env.local live beside this file
  base: "./",                       // relative asset paths: the same build serves ubikistan.org/ and ubikistan.github.io/archive/prototypes/
  publicDir: resolve(here, "public"),
  build: {
    outDir: resolve(here, "../prototypes"),
    emptyOutDir: false,             // prototypes/ also holds the READMEs and the sealed archive
    rollupOptions: {
      input: {
        "world-state": resolve(here, "src/world-state/index.html"),
        forecasts: resolve(here, "src/forecasts/index.html"),
        disclaimer: resolve(here, "src/disclaimer/index.html"),
      },
    },
  },
  server: { port: 5173, proxy },
  preview: { port: 4173, proxy },
});
