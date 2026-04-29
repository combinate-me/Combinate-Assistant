#!/usr/bin/env node
// axe suite — accessibility (WCAG 2.1 AA) scan via axe-core
//
// Usage: node axe.mjs --config qa-config.json --output /tmp/.../qa-output

import { chromium } from 'playwright'
import fs from 'node:fs'
import path from 'node:path'

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`)
  return i >= 0 ? process.argv[i + 1] : fallback
}

const cfgPath = arg('config', 'qa-config.json')
const out    = arg('output')
if (!out) { console.error('axe.mjs: --output is required'); process.exit(2) }

const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'))
const t = cfg.thresholds?.axe ?? {}
const maxCritical = t.maxCritical ?? 0
const maxSerious  = t.maxSerious ?? 0
const maxModerate = t.maxModerate ?? 5

const dir = path.join(out, 'axe')
fs.mkdirSync(dir, { recursive: true })

// Resolve axe-core source. Try project's node_modules first, then this skill's node_modules.
let axeSrc
const candidates = [
  path.resolve('node_modules/axe-core/axe.min.js'),
  path.resolve(path.dirname(process.argv[1]), '../node_modules/axe-core/axe.min.js'),
]
for (const c of candidates) {
  if (fs.existsSync(c)) { axeSrc = fs.readFileSync(c, 'utf8'); break }
}
if (!axeSrc) {
  console.error('[axe] axe-core not found. Install with: npm i -D axe-core')
  fs.writeFileSync(path.join(dir, 'summary.json'), JSON.stringify({
    suite: 'axe', verdict: 'n/a', reason: 'axe-core not installed'
  }, null, 2))
  process.exit(0)
}

const browser = await chromium.launch()
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } })
const page = await ctx.newPage()

const summary = { suite: 'axe', pages: [] }

for (const p of cfg.pages) {
  const url = cfg.baseUrl + p.path
  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 })
    await page.waitForTimeout(2000)
    await page.evaluate(axeSrc)
    const results = await page.evaluate(async () => {
      // eslint-disable-next-line no-undef
      return await axe.run(document, {
        runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice'] }
      })
    })
    fs.writeFileSync(path.join(dir, `${p.name}.json`), JSON.stringify(results, null, 2))

    const v = results.violations
    const counts = {
      critical: v.filter(x => x.impact === 'critical').length,
      serious:  v.filter(x => x.impact === 'serious').length,
      moderate: v.filter(x => x.impact === 'moderate').length,
      minor:    v.filter(x => x.impact === 'minor').length,
    }
    let verdict = 'PASS'
    if (counts.critical > maxCritical) verdict = 'FAIL'
    else if (counts.serious > maxSerious) verdict = 'FAIL'
    else if (counts.moderate > maxModerate) verdict = 'WARN'

    summary.pages.push({
      name: p.name, url, verdict, counts,
      topViolations: v.slice(0, 5).map(x => ({
        id: x.id,
        impact: x.impact,
        nodes: x.nodes.length,
        help: x.help,
        helpUrl: x.helpUrl,
      })),
    })
    console.log(`[axe] ${p.name}: ${verdict} (crit=${counts.critical}, serious=${counts.serious}, moderate=${counts.moderate})`)
  } catch (e) {
    summary.pages.push({ name: p.name, url, verdict: 'FAIL', error: e.message })
    console.error(`[axe] ${p.name}: FAIL ${e.message.slice(0, 100)}`)
  }
}

await browser.close()

summary.verdict = summary.pages.some(p => p.verdict === 'FAIL') ? 'FAIL'
                : summary.pages.some(p => p.verdict === 'WARN') ? 'WARN'
                : 'PASS'

// Deduplicate violations across pages
const dedup = {}
for (const p of summary.pages) {
  for (const v of p.topViolations ?? []) {
    if (!dedup[v.id]) dedup[v.id] = { ...v, occurrences: 0, pages: [] }
    dedup[v.id].occurrences += v.nodes
    dedup[v.id].pages.push(p.name)
  }
}
summary.uniqueViolations = Object.values(dedup).sort((a, b) => b.occurrences - a.occurrences)

fs.writeFileSync(path.join(dir, 'summary.json'), JSON.stringify(summary, null, 2))
console.log(`[axe] suite verdict: ${summary.verdict}`)
