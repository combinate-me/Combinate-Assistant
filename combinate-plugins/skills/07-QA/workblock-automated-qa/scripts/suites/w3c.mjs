#!/usr/bin/env node
// w3c suite — submits each page URL to validator.w3.org and records results
//
// Usage: node w3c.mjs --config qa-config.json --output /tmp/.../qa-output

import { chromium } from 'playwright'
import fs from 'node:fs'
import path from 'node:path'

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`)
  return i >= 0 ? process.argv[i + 1] : fallback
}

const cfgPath = arg('config', 'qa-config.json')
const out    = arg('output')
if (!out) { console.error('w3c.mjs: --output is required'); process.exit(2) }

const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'))
const t = cfg.thresholds?.w3c ?? {}
const maxErrors = t.maxErrors ?? 0
const maxWarnings = t.maxWarnings ?? 5

const dir = path.join(out, 'w3c')
fs.mkdirSync(dir, { recursive: true })

const browser = await chromium.launch()
const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } })
const page = await ctx.newPage()

const summary = { suite: 'w3c', pages: [] }

for (const p of cfg.pages) {
  const url = cfg.baseUrl + p.path
  console.log(`[w3c] ${p.name}: validating ${url}`)
  try {
    // Hit the JSON endpoint for machine-readable results
    const apiUrl = `https://validator.w3.org/nu/?doc=${encodeURIComponent(url)}&out=json`
    const resp = await page.context().request.get(apiUrl, { timeout: 60000 })
    const data = await resp.json().catch(() => ({}))
    const messages = data.messages ?? []
    const errors = messages.filter(m => m.type === 'error')
    const warnings = messages.filter(m => m.type === 'info' || m.subType === 'warning')

    fs.writeFileSync(path.join(dir, `${p.name}.json`), JSON.stringify(data, null, 2))

    let verdict = 'PASS'
    if (errors.length > maxErrors) verdict = 'FAIL'
    else if (warnings.length > maxWarnings) verdict = 'WARN'

    summary.pages.push({
      name: p.name, url, verdict,
      errors: errors.length, warnings: warnings.length,
      topMessages: messages.slice(0, 5).map(m => ({
        type: m.type, msg: m.message, line: m.lastLine, col: m.lastColumn,
      })),
    })
    console.log(`[w3c] ${p.name}: ${verdict} (errors=${errors.length}, warnings=${warnings.length})`)

    // Take a screenshot of the human view too (handy for the report)
    try {
      const humanUrl = `https://validator.w3.org/nu/?doc=${encodeURIComponent(url)}`
      await page.goto(humanUrl, { waitUntil: 'domcontentloaded', timeout: 90000 })
      await page.waitForTimeout(2500)
      await page.screenshot({ path: path.join(dir, `${p.name}.png`), fullPage: true })
    } catch {}
  } catch (e) {
    summary.pages.push({ name: p.name, url, verdict: 'FAIL', error: e.message })
    console.error(`[w3c] ${p.name}: FAIL ${e.message.slice(0, 100)}`)
  }
  // Throttle for W3C rate limiting
  await page.waitForTimeout(5000)
}
await browser.close()

summary.verdict = summary.pages.some(p => p.verdict === 'FAIL') ? 'FAIL'
                : summary.pages.some(p => p.verdict === 'WARN') ? 'WARN'
                : 'PASS'
fs.writeFileSync(path.join(dir, 'summary.json'), JSON.stringify(summary, null, 2))
console.log(`[w3c] suite verdict: ${summary.verdict}`)
