#!/usr/bin/env node
// aggregate — combine every suite's summary.json into report.html, summary.md, summary.json
//
// Usage: node aggregate.mjs --config qa-config.json --output /tmp/.../qa-output --started-at ISO --finished-at ISO --duration N

import fs from 'node:fs'
import path from 'node:path'

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`)
  return i >= 0 ? process.argv[i + 1] : fallback
}

const cfgPath = arg('config', 'qa-config.json')
const out    = arg('output')
const startedAt = arg('started-at', new Date().toISOString())
const finishedAt = arg('finished-at', new Date().toISOString())
const duration = parseInt(arg('duration', '0'), 10)

const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'))

// ----- collect each suite's summary -----
const suites = ['console', 'meta', 'nav', 'axe', 'screenshots', 'lighthouse', 'w3c', 'playwright']
const suiteResults = {}
const REQUIRED_SUITES = new Set(['console', 'nav', 'playwright'])

for (const s of suites) {
  const f = path.join(out, s, 'summary.json')
  if (fs.existsSync(f)) {
    try { suiteResults[s] = JSON.parse(fs.readFileSync(f, 'utf8')) }
    catch (e) { suiteResults[s] = { suite: s, verdict: 'FAIL', error: 'unreadable summary' } }
  }
}

// Special case: playwright doesn't produce summary.json — read its raw results
if (!suiteResults.playwright) {
  const f = path.join(out, 'playwright', 'results.json')
  if (fs.existsSync(f)) {
    try {
      const r = JSON.parse(fs.readFileSync(f, 'utf8'))
      const total = r.stats?.expected ?? 0
      const failed = r.stats?.unexpected ?? 0
      const skipped = r.stats?.skipped ?? 0
      suiteResults.playwright = {
        suite: 'playwright',
        verdict: failed > 0 ? 'FAIL' : 'PASS',
        total, failed, skipped,
      }
    } catch (e) {
      suiteResults.playwright = { suite: 'playwright', verdict: 'FAIL', error: e.message }
    }
  }
}

// ----- compute overall verdict -----
let overallVerdict = 'PASS'
for (const [name, r] of Object.entries(suiteResults)) {
  const v = r.verdict
  if (v === 'FAIL' && REQUIRED_SUITES.has(name)) { overallVerdict = 'FAIL'; break }
  if (v === 'FAIL') overallVerdict = 'WARN' // non-required FAIL → WARN
  if (v === 'WARN' && overallVerdict === 'PASS') overallVerdict = 'WARN'
}

// ----- build page matrix -----
const pageNames = (cfg.pages ?? []).map(p => p.name)
const matrix = {}
for (const pn of pageNames) {
  matrix[pn] = {}
  for (const [s, r] of Object.entries(suiteResults)) {
    if (!Array.isArray(r.pages)) { matrix[pn][s] = r.verdict ?? 'n/a'; continue }
    const row = r.pages.find(p => p.name === pn)
    matrix[pn][s] = row?.verdict ?? 'n/a'
  }
}

// ----- collect issues -----
const issues = []
for (const [s, r] of Object.entries(suiteResults)) {
  if (s === 'axe' && Array.isArray(r.uniqueViolations)) {
    for (const v of r.uniqueViolations.filter(v => v.impact === 'critical' || v.impact === 'serious')) {
      issues.push({
        severity: v.impact === 'critical' ? 'fail' : 'fail',
        suite: 'axe',
        title: v.help,
        detail: `${v.id} (${v.occurrences} occurrences across ${v.pages.join(', ')})`,
        helpUrl: v.helpUrl,
      })
    }
  }
  if (s === 'console' && Array.isArray(r.pages)) {
    for (const p of r.pages.filter(p => p.verdict === 'FAIL')) {
      issues.push({ severity: 'fail', suite: 'console', page: p.name,
        title: `JS errors or failed requests on ${p.name}`,
        detail: `errors=${p.errors}, failedRequests=${p.failedRequests}` })
    }
  }
  if (s === 'nav' && Array.isArray(r.failures)) {
    for (const f of r.failures) {
      issues.push({ severity: 'fail', suite: 'nav',
        title: `Navigation: ${f.label} → expected ${f.expectedPath}`,
        detail: f.actualPath ? `actual: ${f.actualPath}` : (f.error || '') })
    }
  }
  if (s === 'lighthouse' && Array.isArray(r.pages)) {
    for (const p of r.pages.filter(p => p.verdict === 'FAIL' || p.verdict === 'WARN')) {
      issues.push({ severity: p.verdict === 'FAIL' ? 'fail' : 'warn',
        suite: 'lighthouse', page: p.name,
        title: `Lighthouse below thresholds on ${p.name}`,
        detail: `mobile ${JSON.stringify(p.mobile)} desktop ${JSON.stringify(p.desktop)}` })
    }
  }
}

// ----- write summary.json -----
const finalSummary = {
  project: cfg.project,
  workblock: cfg.workblock,
  baseUrl: cfg.baseUrl,
  mode: cfg.mode || 'dev',
  startedAt, finishedAt, durationSeconds: duration,
  verdict: overallVerdict,
  verdictsBySuite: Object.fromEntries(Object.entries(suiteResults).map(([k, v]) => [k, v.verdict || 'n/a'])),
  pageMatrix: matrix,
  issues,
  config: cfg,
}
fs.writeFileSync(path.join(out, 'summary.json'), JSON.stringify(finalSummary, null, 2))

// ----- write summary.md -----
const verdictBadge = (v) => v === 'PASS' ? 'PASS' : v === 'WARN' ? 'WARN' : v === 'FAIL' ? 'FAIL' : 'n/a'

let md = `# QA Report — ${cfg.project} · ${cfg.workblock}

**Verdict:** ${verdictBadge(overallVerdict)}

**Run:** ${startedAt} → ${finishedAt} (${Math.round(duration / 60)} min)
**Base URL:** ${cfg.baseUrl}
**Mode:** ${cfg.mode || 'dev'}

## Suite verdicts

| Suite | Result | Detail |
|---|---|---|
`

for (const s of suites) {
  const r = suiteResults[s]
  if (!r) { md += `| ${s} | n/a | suite not run |\n`; continue }
  let detail = '—'
  if (s === 'console' && Array.isArray(r.pages)) {
    const totalErr = r.pages.reduce((a, p) => a + (p.errors || 0), 0)
    const totalReq = r.pages.reduce((a, p) => a + (p.failedRequests || 0), 0)
    detail = `${totalErr} errors, ${totalReq} failed requests across ${r.pages.length} pages`
  } else if (s === 'meta' && Array.isArray(r.pages)) {
    detail = `${r.pages.filter(p => p.verdict === 'PASS').length}/${r.pages.length} pages pass full metadata audit`
  } else if (s === 'nav') {
    detail = `${r.passed ?? '?'}/${(r.passed || 0) + (r.failed || 0)} links resolve`
  } else if (s === 'axe' && Array.isArray(r.pages)) {
    const crit = r.pages.reduce((a, p) => a + (p.counts?.critical || 0), 0)
    const ser = r.pages.reduce((a, p) => a + (p.counts?.serious || 0), 0)
    const mod = r.pages.reduce((a, p) => a + (p.counts?.moderate || 0), 0)
    detail = `${crit} critical, ${ser} serious, ${mod} moderate violations`
  } else if (s === 'screenshots') {
    detail = `${r.captures || 0} captures (${(r.viewports || []).join(' · ')})`
  } else if (s === 'lighthouse' && Array.isArray(r.pages)) {
    detail = `${r.pages.filter(p => p.verdict === 'PASS').length}/${r.pages.length} pages pass thresholds`
  } else if (s === 'w3c' && Array.isArray(r.pages)) {
    const e = r.pages.reduce((a, p) => a + (p.errors || 0), 0)
    detail = `${e} HTML errors across ${r.pages.length} pages`
  } else if (s === 'playwright') {
    detail = r.total ? `${r.total - r.failed}/${r.total} tests pass${r.skipped ? `, ${r.skipped} skipped` : ''}` : '—'
  }
  md += `| ${s} | ${verdictBadge(r.verdict)} | ${detail} |\n`
}

md += `\n## Issues to action\n\n`
if (issues.length === 0) {
  md += `_No outstanding issues._\n`
} else {
  for (const [i, x] of issues.entries()) {
    md += `${i + 1}. **${x.suite}${x.page ? ` / ${x.page}` : ''}** — ${x.title}\n   ${x.detail}${x.helpUrl ? ` ([help](${x.helpUrl}))` : ''}\n`
  }
}

const critPages = (cfg.pages || []).filter(p => p.criticalPath).map(p => p.name)
if (critPages.length) {
  md += `\n## Critical-path pages\n\n`
  for (const cp of critPages) {
    const verdicts = matrix[cp] || {}
    const worst = Object.values(verdicts).includes('FAIL') ? 'FAIL'
                 : Object.values(verdicts).includes('WARN') ? 'WARN' : 'PASS'
    md += `- **${cp}**: ${verdictBadge(worst)}\n`
  }
}

md += `\n## Files\n\n- HTML report: \`${out}/report.html\`\n- Raw artefacts: \`${out}/\`\n\n---\n\n_Generated by \`workblock-automated-qa\` skill._\n`

fs.writeFileSync(path.join(out, 'summary.md'), md)

// ----- write report.html (self-contained) -----
const verdictColor = { PASS: '#1a8917', WARN: '#c97a00', FAIL: '#c0292a', 'n/a': '#666' }
const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>QA Report — ${cfg.project} · ${cfg.workblock}</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 1100px; margin: 32px auto; padding: 0 16px; color: #111; }
  h1 { margin-bottom: 0; } h1 + p { color: #555; }
  .badge { display: inline-block; padding: 4px 12px; border-radius: 4px; color: white; font-weight: 600; font-size: 14px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin: 24px 0; }
  .card { padding: 16px; border: 1px solid #ddd; border-radius: 6px; }
  .card .v { float: right; }
  table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; }
  th, td { padding: 8px 10px; border: 1px solid #e1e1e1; text-align: left; }
  th { background: #f6f6f6; }
  td.PASS { background: #e8f5e8; }
  td.WARN { background: #fff5e0; }
  td.FAIL { background: #fde8e8; }
  td.NA, td.\\n\\/a { background: #f6f6f6; color: #999; }
  .issue { padding: 12px; border-left: 4px solid #c0292a; background: #fff7f7; margin: 8px 0; border-radius: 4px; }
  .issue.warn { border-color: #c97a00; background: #fffaf0; }
  pre { background: #f6f6f6; padding: 12px; border-radius: 4px; overflow: auto; font-size: 12px; }
  code { background: #f3f3f3; padding: 1px 5px; border-radius: 3px; }
  details { margin: 8px 0; }
  summary { cursor: pointer; font-weight: 600; }
</style>
</head>
<body>

<h1>QA Report — ${cfg.project} · ${cfg.workblock}</h1>
<p>
  <span class="badge" style="background:${verdictColor[overallVerdict]};">${overallVerdict}</span>
  &nbsp; ${startedAt} → ${finishedAt} (${Math.round(duration / 60)} min) · ${cfg.baseUrl} · mode=${cfg.mode || 'dev'}
</p>

<h2>Suites</h2>
<div class="grid">
${suites.map(s => {
  const r = suiteResults[s] || { verdict: 'n/a' }
  return `<div class="card">
    <span class="v badge" style="background:${verdictColor[r.verdict] || '#666'};">${r.verdict}</span>
    <strong>${s}</strong>
  </div>`
}).join('\n')}
</div>

<h2>Page × Suite matrix</h2>
<table>
  <thead><tr><th>Page</th>${suites.map(s => `<th>${s}</th>`).join('')}</tr></thead>
  <tbody>
  ${pageNames.map(pn => `<tr><td><strong>${pn}</strong></td>${
    suites.map(s => {
      const v = matrix[pn]?.[s] || 'n/a'
      return `<td class="${v}">${v}</td>`
    }).join('')
  }</tr>`).join('\n')}
  </tbody>
</table>

<h2>Issues to action</h2>
${issues.length === 0 ? '<p><em>No outstanding issues.</em></p>' : issues.map(i =>
  `<div class="issue ${i.severity === 'warn' ? 'warn' : ''}">
    <strong>${i.suite}${i.page ? ' / ' + i.page : ''}</strong> — ${i.title}<br>
    <span style="color:#555;">${i.detail}</span>
    ${i.helpUrl ? `<br><a href="${i.helpUrl}">help</a>` : ''}
  </div>`
).join('\n')}

<details>
  <summary>Configuration used</summary>
  <pre>${JSON.stringify(cfg, null, 2).replace(/</g, '&lt;')}</pre>
</details>

<p style="margin-top:48px;color:#888;font-size:12px">
  Generated by <code>workblock-automated-qa</code> skill · ${finishedAt}
</p>

</body>
</html>`

fs.writeFileSync(path.join(out, 'report.html'), html)

console.log(`[aggregate] verdict: ${overallVerdict}`)
console.log(`[aggregate] wrote: ${out}/summary.json`)
console.log(`[aggregate] wrote: ${out}/summary.md`)
console.log(`[aggregate] wrote: ${out}/report.html`)
