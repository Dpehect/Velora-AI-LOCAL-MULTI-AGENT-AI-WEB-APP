/**
 * Vercel build: copy static landing page → public/
 * Avoids Python runtime detection; serves ai-lab-landing as the site.
 */
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const SRC = path.join(ROOT, "ai-lab-landing");
const OUT = path.join(ROOT, "public");

function rmDir(dir) {
  if (!fs.existsSync(dir)) return;
  fs.rmSync(dir, { recursive: true, force: true });
}

function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    // skip docs in deploy output
    if (entry.name === "README.md") continue;
    const from = path.join(src, entry.name);
    const to = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDir(from, to);
    } else {
      fs.copyFileSync(from, to);
    }
  }
}

if (!fs.existsSync(SRC)) {
  console.error("[vercel-build] Missing ai-lab-landing/ directory");
  process.exit(1);
}

rmDir(OUT);
copyDir(SRC, OUT);

const index = path.join(OUT, "index.html");
if (!fs.existsSync(index)) {
  console.error("[vercel-build] public/index.html was not created");
  process.exit(1);
}

console.log("[vercel-build] Static site ready → public/");
for (const f of walk(OUT)) {
  console.log("  ", path.relative(OUT, f).replace(/\\/g, "/"));
}

function walk(dir, acc = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(p, acc);
    else acc.push(p);
  }
  return acc;
}
