#!/usr/bin/env node
// screenshots suite — full-page captures across configured viewports
//
// Usage: node screenshots.mjs --config qa-config.json --output /tmp/.../qa-output

import { chromium } from 'playwright'
import fs from 'node:fs'
import path from 'node:path'

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`)
  return i >= 0 ? process.argv[i + 1] : fallback
}

const cfgPath = arg('config', 'qa-config.json')
const out    = arg('output')
if (!out) { console.error('screenshots.mjs: --output is required'); process.exit(2) }

const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'))
const viewports = cfg.viewports ?? [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'tablet',  width: 768,  height: 1024 },
  { name: 'mobile',  width: 390,  height: 844 },
]
const fullPage = cfg.screenshots?.fullPage !== false
const dir = path.join(out, 'screenshots')
fs.mkdirSync(dir, { recursive: true })

const browser = await chromium.launch()
const summary = { suite: 'screenshots', viewports: [], pages: [] }
let captures = 0

for (const vp of viewports) {
  fs.mkdirSync(path.join(dir, vp.name), { recursive: true })
  const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height } })
  const page = await ctx.newPage()
  for (const p of cfg.pages) {
    const url = cfg.baseUrl + p.path
    try {
      await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 })
      await page.waitForTimeout(2500)
      await page.screenshot({
        path: path.join(dir, vp.name, `${p.name}.png`),
        fullPage,
      })
      captures++
      console.log(`[screenshots] ${vp.name}/${p.name} ok`)
    } catch (e) {
      console.error(`[screenshots] ${vp.name}/${p.name} failed: ${e.message.slice(0, 80)}`)
    }
  }
  await ctx.close()
  summary.viewports.push(vp.name)
}
await browser.close()

// Optional: pixel diff against a baseline directory
let diffSummary = null
const baseline = cfg.screenshots?.diffAgainst
if (baseline && fs.existsSync(baseline)) {
  try {
    const pixelmatch = (await import('pixelmatch')).default
    const PNG = (await import('pngjs')).PNG
    const diffDir = path.join(dir, 'diff')
    fs.mkdirSync(diffDir, { recursive: true })
    diffSummary = []

    for (const vp of viewports) {
      for (const p of cfg.pages) {
        const a = path.join(baseline, vp.name, `${p.name}.png`)
        const b = path.join(dir, vp.name, `${p.name}.png`)
        if (!fs.existsSync(a) || !fs.existsSync(b)) continue
        const imgA = PNG.sync.read(fs.readFileSync(a))
        const imgB = PNG.sync.read(fs.readFileSync(b))
        if (imgA.width !== imgB.width || imgA.height !== imgB.height) {
          diffSummary.push({ viewport: vp.name, page: p.name, sizeMismatch: true })
          continue
        }
        const diff = new PNG({ width: imgA.width, height: imgA.height })
        const px = pixelmatch(imgA.data, imgB.data, diff.data, imgA.width, imgA.height, { threshold: 0.1 })
        const pct = (px / (imgA.width * imgA.height)) * 100
        const w = cfg.thresholds?.screenshots?.diffPercentWarn ?? 1
        const f = cfg.thresholds?.screenshots?.diffPercentFail ?? 5
        const verdict = pct > f ? 'FAIL' : pct > w ? 'WARN' : 'PASS'
        diffSummary.push({ viewport: vp.name, page: p.name, diffPct: pct.toFixed(2), verdict })
        if (verdict !== 'PASS') {
          fs.mkdirSync(path.join(diffDir, vp.name), { recursive: true })
          fs.writeFileSync(path.join(diffDir, vp.name, `${p.name}.png`), PNG.sync.write(diff))
        }
      }
    }
  } catch (e) {
    console.log(`[screenshots] diff failed (install pixelmatch + pngjs): ${e.message}`)
  }
}

if (diffSummary) {
  summary.verdict = diffSummary.some(d => d.verdict === 'FAIL') ? 'FAIL'
                  : diffSummary.some(d => d.verdict === 'WARN') ? 'WARN'
                  : 'PASS'
  summary.diffs = diffSummary
} else {
  summary.verdict = 'n/a'
  summary.note = 'archival mode (no baseline configured)'
}
summary.captures = captures

fs.writeFileSync(path.join(dir, 'summary.json'), JSON.stringify(summary, null, 2))
console.log(`[screenshots] suite verdict: ${summary.verdict} (${captures} captures)`)
