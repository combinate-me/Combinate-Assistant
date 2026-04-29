#!/usr/bin/env bash
# workblock-automated-qa — orchestrator
#
# Reads qa-config.json, runs the configured suites, aggregates the results.
#
# Usage:
#   bash run-qa.sh [--config qa-config.json] [--suites s1,s2] [--mode dev|support] [--open] [--no-comment]
#
# Exit codes:
#   0 — PASS (or WARN with --strict=false)
#   1 — FAIL
#   2 — environment / config error

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="qa-config.json"
SUITES_OVERRIDE=""
MODE_OVERRIDE=""
OPEN=false
NO_COMMENT=false
STRICT=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config)      CONFIG="$2"; shift 2 ;;
    --suites)      SUITES_OVERRIDE="$2"; shift 2 ;;
    --mode)        MODE_OVERRIDE="$2"; shift 2 ;;
    --open)        OPEN=true; shift ;;
    --no-comment)  NO_COMMENT=true; shift ;;
    --strict)      STRICT=true; shift ;;
    -h|--help)
      sed -n '2,12p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown flag: $1" >&2
      exit 2
      ;;
  esac
done

if [[ ! -f "$CONFIG" ]]; then
  echo "Config not found: $CONFIG" >&2
  echo "Run scaffold-config.mjs first or pass --config <path>." >&2
  exit 2
fi

# ----- read config -----
PROJECT=$(node -e "console.log(require('./$CONFIG').project)" 2>/dev/null || echo "")
WORKBLOCK=$(node -e "console.log(require('./$CONFIG').workblock)" 2>/dev/null || echo "")
BASE_URL=$(node -e "console.log(require('./$CONFIG').baseUrl)" 2>/dev/null || echo "")
MODE=$(node -e "console.log(require('./$CONFIG').mode || 'dev')" 2>/dev/null || echo "dev")
[[ -n "$MODE_OVERRIDE" ]] && MODE="$MODE_OVERRIDE"

OUT_DIR=$(node -e "
const c = require('./$CONFIG');
let o = c.outputDir || '/tmp/{project}-qa/{workblock}';
const slug = (c.project||'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
o = o.replace('{project}', slug).replace('{workblock}', c.workblock || 'wb');
console.log(o);
" 2>/dev/null)

if [[ -z "$PROJECT" || -z "$WORKBLOCK" || -z "$BASE_URL" || -z "$OUT_DIR" ]]; then
  echo "Config missing required fields (project, workblock, baseUrl, outputDir)" >&2
  exit 2
fi

mkdir -p "$OUT_DIR"

# ----- decide which suites to run -----
DEV_SUITES="console meta nav axe screenshots lighthouse w3c playwright"
SUPPORT_SUITES="console nav screenshots playwright"

if [[ -n "$SUITES_OVERRIDE" ]]; then
  SUITES="${SUITES_OVERRIDE//,/ }"
elif [[ "$MODE" = "support" ]]; then
  SUITES="$SUPPORT_SUITES"
else
  SUITES="$DEV_SUITES"
fi

# Honour config.suites if set and no override
CONFIG_SUITES=$(node -e "
const c = require('./$CONFIG');
console.log(Array.isArray(c.suites) ? c.suites.join(' ') : '');
" 2>/dev/null)
if [[ -n "$CONFIG_SUITES" && -z "$SUITES_OVERRIDE" ]]; then
  SUITES="$CONFIG_SUITES"
fi

echo "==============================================="
echo "  workblock-automated-qa"
echo "==============================================="
echo "  Project:    $PROJECT"
echo "  Workblock:  $WORKBLOCK"
echo "  Base URL:   $BASE_URL"
echo "  Mode:       $MODE"
echo "  Suites:     $SUITES"
echo "  Output:     $OUT_DIR"
echo "==============================================="
echo ""

STARTED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)
START_EPOCH=$(date +%s)

# ----- preflight: check tools -----
echo "[preflight] checking tools..."
if ! command -v node >/dev/null; then echo "  node: missing" >&2; exit 2; fi
if ! command -v npx  >/dev/null; then echo "  npx: missing"  >&2; exit 2; fi
echo "  node: $(node --version)"
echo "  npx:  $(npx --version)"
echo ""

# ----- run each suite -----
SUITE_DIR="$SCRIPT_DIR/suites"
SUITE_RESULTS=()

run_suite() {
  local suite="$1"
  local script
  case "$suite" in
    lighthouse) script="$SUITE_DIR/lighthouse.sh" ;;
    *)          script="$SUITE_DIR/$suite.mjs"     ;;
  esac

  if [[ ! -f "$script" ]]; then
    echo "[$suite] no runner at $script — skipping"
    SUITE_RESULTS+=("$suite:skipped")
    return
  fi

  echo "==============================================="
  echo "  $suite"
  echo "==============================================="

  local suite_start=$(date +%s)
  local exit_code=0
  if [[ "$script" == *.sh ]]; then
    bash "$script" --config "$CONFIG" --output "$OUT_DIR" || exit_code=$?
  else
    node "$script" --config "$CONFIG" --output "$OUT_DIR" || exit_code=$?
  fi
  local suite_end=$(date +%s)
  local suite_seconds=$((suite_end - suite_start))

  if [[ $exit_code -eq 0 ]]; then
    echo "[$suite] completed in ${suite_seconds}s"
    SUITE_RESULTS+=("$suite:ran")
  else
    echo "[$suite] RUNNER FAILED (exit $exit_code) — recording and continuing" >&2
    SUITE_RESULTS+=("$suite:runner-failed")
  fi
  echo ""
}

# Special: playwright runs the project's spec via npx, not a suite script
run_playwright() {
  local spec
  spec=$(node -e "console.log(require('./$CONFIG').playwrightSpec || '')" 2>/dev/null)

  if [[ -z "$spec" ]]; then
    echo "[playwright] no spec configured — skipping"
    SUITE_RESULTS+=("playwright:skipped")
    return
  fi
  if [[ ! -f "$spec" ]]; then
    echo "[playwright] spec not found at $spec — skipping" >&2
    SUITE_RESULTS+=("playwright:missing-spec")
    return
  fi

  echo "==============================================="
  echo "  playwright"
  echo "==============================================="

  mkdir -p "$OUT_DIR/playwright"
  local suite_start=$(date +%s)
  npx playwright test "$spec" --reporter=json > "$OUT_DIR/playwright/results.json" || true
  local suite_end=$(date +%s)
  echo "[playwright] completed in $((suite_end - suite_start))s"
  SUITE_RESULTS+=("playwright:ran")
  echo ""
}

# Run lighthouse and w3c in parallel if both selected (they're slow + independent)
PARALLEL_PIDS=()
for suite in $SUITES; do
  case "$suite" in
    playwright)            run_playwright ;;
    lighthouse|w3c)
      if [[ "$SUITES" == *lighthouse* && "$SUITES" == *w3c* && "$suite" == "lighthouse" ]]; then
        # Run lighthouse in background, w3c will run inline next
        (run_suite lighthouse) &
        PARALLEL_PIDS+=("$!")
      elif [[ "$suite" == "w3c" && ${#PARALLEL_PIDS[@]} -gt 0 ]]; then
        run_suite w3c
        wait "${PARALLEL_PIDS[@]}"
        PARALLEL_PIDS=()
      else
        run_suite "$suite"
      fi
      ;;
    *)                     run_suite "$suite" ;;
  esac
done

# Catch any backgrounded suites that didn't get joined above
[[ ${#PARALLEL_PIDS[@]} -gt 0 ]] && wait "${PARALLEL_PIDS[@]}"

# ----- aggregate -----
echo "==============================================="
echo "  aggregate"
echo "==============================================="

FINISHED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)
END_EPOCH=$(date +%s)
DURATION=$((END_EPOCH - START_EPOCH))

node "$SCRIPT_DIR/aggregate.mjs" \
  --config "$CONFIG" \
  --output "$OUT_DIR" \
  --started-at "$STARTED_AT" \
  --finished-at "$FINISHED_AT" \
  --duration "$DURATION"
AGG_EXIT=$?

VERDICT=$(node -e "
try { console.log(require('$OUT_DIR/summary.json').verdict || 'UNKNOWN') }
catch (e) { console.log('UNKNOWN') }
" 2>/dev/null)

echo ""
echo "==============================================="
echo "  Verdict: $VERDICT"
echo "  Duration: ${DURATION}s"
echo "  Report:  $OUT_DIR/report.html"
echo "  Summary: $OUT_DIR/summary.md"
echo "==============================================="

# Optional: open HTML report in browser
if [[ "$OPEN" = true && "$VERDICT" != "UNKNOWN" ]]; then
  case "$(uname -s)" in
    Darwin) open "$OUT_DIR/report.html" ;;
    Linux)  xdg-open "$OUT_DIR/report.html" 2>/dev/null || true ;;
  esac
fi

# Optional: post Teamwork comment (skill-sharing flow handles this externally;
# the orchestrator only writes summary.md and lets the caller post if they want)
if [[ "$NO_COMMENT" = true ]]; then
  echo "[teamwork] --no-comment set — skipping Teamwork integration."
fi

# ----- exit code per verdict -----
case "$VERDICT" in
  PASS) exit 0 ;;
  WARN)
    if [[ "$STRICT" = true ]]; then exit 1; else exit 0; fi
    ;;
  FAIL) exit 1 ;;
  *)    exit 2 ;;
esac
