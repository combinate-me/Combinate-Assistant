#!/usr/bin/env bash
# lighthouse suite — runs Lighthouse for every configured page on mobile + desktop
#
# Usage: bash lighthouse.sh --config qa-config.json --output /tmp/.../qa-output

set -u

CONFIG="qa-config.json"
OUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config) CONFIG="$2"; shift 2 ;;
    --output) OUT="$2";    shift 2 ;;
    *) shift ;;
  esac
done

if [[ -z "$OUT" ]]; then
  echo "lighthouse.sh: --output is required" >&2
  exit 2
fi

DIR="$OUT/lighthouse"
mkdir -p "$DIR/mobile" "$DIR/desktop"

BASE=$(node -e "console.log(require('./$CONFIG').baseUrl)")
PAGES_JSON=$(node -e "console.log(JSON.stringify(require('./$CONFIG').pages))")

# Default UAs (platformOS staging filters Chrome-Lighthouse UA)
DESKTOP_UA=$(node -e "
const c = require('./$CONFIG');
console.log(c.userAgent?.desktop || 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15');
")
MOBILE_UA=$(node -e "
const c = require('./$CONFIG');
console.log(c.userAgent?.mobile || 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1');
")

# Resolve Chrome path
CHROME=$(node -e "
const c = require('./$CONFIG');
const p = c.lighthouse?.chromePath || 'auto';
if (p !== 'auto') { console.log(p); process.exit(0) }
const candidates = [
  process.env.HOME + '/Library/Caches/ms-playwright/chromium-1217/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing',
  process.env.HOME + '/Library/Caches/ms-playwright/chromium-1148/chrome-mac/Chromium.app/Contents/MacOS/Chromium',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
];
const fs = require('fs');
for (const c of candidates) if (fs.existsSync(c)) { console.log(c); process.exit(0) }
console.log('');
")
if [[ -n "$CHROME" ]]; then
  export CHROME_PATH="$CHROME"
fi

# Locate the lighthouse binary (prefer project-local install)
LH=""
for cand in "./node_modules/.bin/lighthouse" "$(command -v lighthouse 2>/dev/null)"; do
  [[ -x "$cand" ]] && LH="$cand" && break
done
if [[ -z "$LH" ]]; then
  echo "[lighthouse] lighthouse CLI not found. Install: npm i -D lighthouse" >&2
  echo "{\"suite\":\"lighthouse\",\"verdict\":\"n/a\",\"reason\":\"lighthouse not installed\"}" > "$DIR/summary.json"
  exit 0
fi

cleanup_chrome() {
  pkill -9 -f 'Google Chrome for Testing' 2>/dev/null || true
  pkill -9 -f 'chrome-headless-shell' 2>/dev/null || true
  pkill -9 -f 'Chromium' 2>/dev/null || true
  sleep 3
}

run_one() {
  local form="$1" name="$2" path="$3"
  local ua
  if [[ "$form" = "desktop" ]]; then ua="$DESKTOP_UA"; else ua="$MOBILE_UA"; fi
  local extra="--form-factor=mobile"
  [[ "$form" = "desktop" ]] && extra="--preset=desktop"
  echo "[lighthouse] $form/$name"
  for attempt in 1 2; do
    "$LH" "$BASE$path" \
      $extra \
      --only-categories=performance,accessibility,best-practices,seo \
      --emulated-user-agent="$ua" \
      --disable-storage-reset \
      --output=json --output=html \
      --output-path="$DIR/$form/$name" \
      --chrome-flags='--headless=new --disable-dev-shm-usage' \
      --quiet 2>&1 | tail -1
    cleanup_chrome
    local ok
    ok=$(node -e "
try {
  const d = require('$DIR/$form/$name.report.json');
  process.stdout.write(d.runtimeError ? 'NO' : 'YES');
} catch (e) { process.stdout.write('NO'); }
")
    if [[ "$ok" = "YES" ]]; then return 0; fi
    echo "  attempt $attempt failed, retrying"
  done
  return 1
}

# Iterate pages
echo "$PAGES_JSON" | node -e "
const ps = JSON.parse(require('fs').readFileSync(0,'utf8'));
for (const p of ps) console.log(p.name + '\t' + p.path);
" | while IFS=$'\t' read -r name path; do
  for form in mobile desktop; do
    run_one "$form" "$name" "$path"
  done
done

# Build summary.json
node -e "
const fs = require('node:fs');
const path = require('node:path');
const cfg = require('./$CONFIG');
const dir = '$DIR';
const t = cfg.thresholds?.lighthouse || {};
const target = { performance: t.performance ?? 70, accessibility: t.accessibility ?? 95, bestPractices: t.bestPractices ?? 95, seo: t.seo ?? 90 };
const warnBand = t.warnBand ?? 10;

const pages = [];
for (const p of cfg.pages) {
  const row = { name: p.name, mobile: null, desktop: null };
  for (const ff of ['mobile', 'desktop']) {
    const file = path.join(dir, ff, p.name + '.report.json');
    if (!fs.existsSync(file)) continue;
    try {
      const r = JSON.parse(fs.readFileSync(file, 'utf8'));
      if (r.runtimeError) { row[ff] = { error: r.runtimeError.code }; continue; }
      const score = (k) => Math.round((r.categories[k]?.score || 0) * 100);
      row[ff] = {
        performance: score('performance'),
        accessibility: score('accessibility'),
        bestPractices: score('best-practices'),
        seo: score('seo'),
      };
    } catch (e) {
      row[ff] = { error: e.message };
    }
  }

  const verdictOf = (scores) => {
    if (!scores || scores.error) return 'FAIL';
    let v = 'PASS';
    for (const [cat, key] of [['performance','performance'],['accessibility','accessibility'],['bestPractices','bestPractices'],['seo','seo']]) {
      const s = scores[key]; const tgt = target[cat];
      if (s < tgt - warnBand) { v = 'FAIL'; break; }
      if (s < tgt) v = (v === 'FAIL') ? v : 'WARN';
    }
    return v;
  };
  row.verdict = (row.mobile && row.desktop)
    ? (verdictOf(row.mobile) === 'FAIL' || verdictOf(row.desktop) === 'FAIL') ? 'FAIL'
      : (verdictOf(row.mobile) === 'WARN' || verdictOf(row.desktop) === 'WARN') ? 'WARN'
      : 'PASS'
    : 'FAIL';
  pages.push(row);
}

const summary = {
  suite: 'lighthouse',
  thresholds: target,
  warnBand,
  pages,
  verdict: pages.some(p => p.verdict === 'FAIL') ? 'FAIL'
         : pages.some(p => p.verdict === 'WARN') ? 'WARN'
         : 'PASS',
};
fs.writeFileSync(path.join(dir, 'summary.json'), JSON.stringify(summary, null, 2));
console.log('[lighthouse] suite verdict:', summary.verdict);
"
