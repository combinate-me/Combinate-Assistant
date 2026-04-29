#!/usr/bin/env node
// meta suite — metadata, og tags, canonical, h1 audit
//
// Usage: node meta.mjs --config qa-config.json --output /tmp/.../qa-output

import { chromium } from 'playwright'
import fs from 'node:fs'
import path from 'node:path'

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`)
  return i >= 0 ? process.argv[i + 1] : fallback
}

const cfgPath = arg('config', 'qa-config.json')
const out    = arg('output')
if (!out) { console.error('meta.mjs: --output is required'); process.exit(2) }

const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'))
const dir = path.join(out, 'meta')
fs.mkdirSync(dir, { recursive: true })

const browser = await chromium.launch()
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } })
const page = await ctx.newPage()

const records = []
const summary = { suite: 'meta', pages: [] }

for (const p of cfg.pages) {
  const url = cfg.baseUrl + p.path
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 })
  } catch (e) {
    summary.pages.push({ name: p.name, url, verdict: 'FAIL', error: e.message })
    continue
  }

  const meta = await page.evaluate(() => {
    const get = (sel) => document.querySelector(sel)?.content ?? null
    const getAttr = (sel, attr) => document.querySelector(sel)?.getAttribute(attr) ?? null
    return {
      title:           document.title,
      description:     get('meta[name="description"]'),
      ogTitle:         get('meta[property="og:title"]'),
      ogDescription:   get('meta[property="og:description"]'),
      ogImage:         get('meta[property="og:image"]'),
      ogUrl:           get('meta[property="og:url"]'),
      ogType:          get('meta[property="og:type"]'),
      ogSiteName:      get('meta[property="og:site_name"]'),
      twitterCard:     get('meta[name="twitter:card"]'),
      canonical:       getAttr('link[rel="canonical"]', 'href'),
      favicon:         getAttr('link[rel="icon"]', 'href') ?? getAttr('link[rel="shortcut icon"]', 'href'),
      viewport:        get('meta[name="viewport"]'),
      robots:          get('meta[name="robots"]'),
      lang:            document.documentElement.lang,
      h1Count:         document.querySelectorAll('h1').length,
      h1Text:          Array.from(document.querySelectorAll('h1')).map(h => h.textContent?.trim().slice(0, 80)),
    }
  })

  records.push({ name: p.name, url, meta })

  // Verdict
  let verdict = 'PASS'
  const reasons = []
  if (!meta.title)        { verdict = 'FAIL'; reasons.push('missing <title>') }
  if (meta.h1Count === 0) { verdict = 'FAIL'; reasons.push('no <h1>') }
  if (meta.h1Count > 1)   { verdict = 'FAIL'; reasons.push(`${meta.h1Count} <h1> elements`) }
  if (!meta.description)  { verdict = verdict === 'PASS' ? 'WARN' : verdict; reasons.push('missing meta description') }
  if (!meta.canonical)    { verdict = verdict === 'PASS' ? 'WARN' : verdict; reasons.push('missing canonical') }
  const ogMissing = ['ogTitle', 'ogDescription', 'ogImage', 'ogUrl', 'ogType', 'ogSiteName']
    .filter(k => !meta[k])
  if (ogMissing.length) { verdict = verdict === 'PASS' ? 'WARN' : verdict; reasons.push(`missing og: ${ogMissing.join(', ')}`) }

  summary.pages.push({ name: p.name, url, verdict, h1Count: meta.h1Count, reasons })
  console.log(`[meta] ${p.name}: ${verdict}${reasons.length ? ` (${reasons.join('; ')})` : ''}`)
}

await browser.close()

fs.writeFileSync(path.join(dir, 'metadata.json'), JSON.stringify(records, null, 2))
summary.verdict = summary.pages.some(p => p.verdict === 'FAIL') ? 'FAIL'
                : summary.pages.some(p => p.verdict === 'WARN') ? 'WARN'
                : 'PASS'
fs.writeFileSync(path.join(dir, 'summary.json'), JSON.stringify(summary, null, 2))
console.log(`[meta] suite verdict: ${summary.verdict}`)
