#!/usr/bin/env node
// console suite — captures JS errors, console messages, failed requests, HTTP errors
//
// Usage: node console.mjs --config qa-config.json --output /tmp/.../qa-output

import { chromium } from 'playwright'
import fs from 'node:fs'
import path from 'node:path'

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`)
  return i >= 0 ? process.argv[i + 1] : fallback
}

const cfgPath = arg('config', 'qa-config.json')
const out    = arg('output')
if (!out) { console.error('console.mjs: --output is required'); process.exit(2) }

const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'))
const ignorePatterns = (cfg.thresholds?.console?.ignorePatterns || []).map(p => new RegExp(p))
const maxErrors = cfg.thresholds?.console?.maxErrors ?? 0
const maxFailed = cfg.thresholds?.console?.maxFailedRequests ?? 0

const dir = path.join(out, 'console')
fs.mkdirSync(dir, { recursive: true })

const browser = await chromium.launch()
const summary = { suite: 'console', pages: [] }

for (const p of cfg.pages) {
  const url = cfg.baseUrl + p.path
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } })
  const page = await ctx.newPage()
  const logs = []
  const reqFailures = []

  page.on('console', m => {
    const text = m.text()
    if (ignorePatterns.some(re => re.test(text))) return
    logs.push({ type: m.type(), text })
  })
  page.on('pageerror', e => logs.push({ type: 'pageerror', text: e.message }))
  page.on('requestfailed', r => reqFailures.push({
    url: r.url(),
    method: r.method(),
    failure: r.failure()?.errorText,
  }))
  page.on('response', r => {
    if (r.status() >= 400) {
      logs.push({ type: 'http-error', text: `${r.status()} ${r.url()}` })
    }
  })

  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 })
    await page.waitForTimeout(3000)
  } catch (e) {
    logs.push({ type: 'nav-error', text: e.message })
  }

  const errors = logs.filter(l => l.type === 'error' || l.type === 'pageerror' || l.type === 'http-error' || l.type === 'nav-error')
  const warnings = logs.filter(l => l.type === 'warning' || l.type === 'warn')
  let verdict = 'PASS'
  if (errors.length > maxErrors || reqFailures.length > maxFailed) verdict = 'FAIL'
  else if (warnings.length > (cfg.thresholds?.console?.maxWarnings ?? 10)) verdict = 'WARN'

  fs.writeFileSync(path.join(dir, `${p.name}.json`), JSON.stringify({ url, logs, reqFailures }, null, 2))
  summary.pages.push({
    name: p.name,
    url,
    verdict,
    errors: errors.length,
    warnings: warnings.length,
    failedRequests: reqFailures.length,
    criticalPath: p.criticalPath === true,
  })
  console.log(`[console] ${p.name}: ${verdict} (errors=${errors.length}, failed=${reqFailures.length}, warnings=${warnings.length})`)
  await ctx.close()
}

await browser.close()

summary.verdict = summary.pages.some(p => p.verdict === 'FAIL') ? 'FAIL'
                : summary.pages.some(p => p.verdict === 'WARN') ? 'WARN'
                : 'PASS'

fs.writeFileSync(path.join(dir, 'summary.json'), JSON.stringify(summary, null, 2))
console.log(`[console] suite verdict: ${summary.verdict}`)
