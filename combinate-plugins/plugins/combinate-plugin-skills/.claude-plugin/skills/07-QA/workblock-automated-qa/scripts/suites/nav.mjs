#!/usr/bin/env node
// nav suite — navigation crawl: menu, footer, logo, BACK buttons
//
// Usage: node nav.mjs --config qa-config.json --output /tmp/.../qa-output

import { chromium } from 'playwright'
import fs from 'node:fs'
import path from 'node:path'

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`)
  return i >= 0 ? process.argv[i + 1] : fallback
}

const cfgPath = arg('config', 'qa-config.json')
const out    = arg('output')
if (!out) { console.error('nav.mjs: --output is required'); process.exit(2) }

const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'))
const navCfg = cfg.navigation
if (!navCfg) {
  console.log('[nav] no navigation config — suite is no-op')
  fs.mkdirSync(path.join(out, 'nav'), { recursive: true })
  fs.writeFileSync(
    path.join(out, 'nav', 'summary.json'),
    JSON.stringify({ suite: 'nav', verdict: 'n/a', reason: 'no navigation config' }, null, 2)
  )
  process.exit(0)
}

const dir = path.join(out, 'nav')
const shotDir = path.join(dir, 'screenshots')
fs.mkdirSync(shotDir, { recursive: true })

const browser = await chromium.launch()
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } })
const page = await ctx.newPage()

const report = { pass: [], fail: [] }

async function openMenuIfNeeded() {
  if (!navCfg.menuToggleSelector) return
  try {
    const toggle = await page.$(navCfg.menuToggleSelector)
    if (toggle) {
      await toggle.click()
      await page.waitForTimeout(500)
    }
  } catch {}
}

async function clickAndVerify(label, expectedPath, opts = {}) {
  const fromPath = opts.from ?? '/'
  await page.goto(cfg.baseUrl + fromPath, { waitUntil: 'networkidle', timeout: 30000 })
  await page.waitForTimeout(1000)
  if (opts.openMenu !== false) await openMenuIfNeeded()
  try {
    const link = await page.getByRole('link', { name: label, exact: true }).first()
    await link.click({ timeout: 8000 })
    await page.waitForLoadState('networkidle', { timeout: 15000 })
    const url = new URL(page.url())
    const ok = url.pathname === expectedPath
    if (ok) report.pass.push({ label, expectedPath, from: fromPath })
    else    report.fail.push({ label, expectedPath, actualPath: url.pathname, from: fromPath })
    console.log(`[nav] ${ok ? 'OK' : 'FAIL'} ${label} (from ${fromPath}) → ${url.pathname}`)
  } catch (e) {
    console.log(`[nav] FAIL ${label}: ${e.message.slice(0, 100)}`)
    report.fail.push({ label, expectedPath, error: e.message, from: fromPath })
  }
}

// 1. Menu links
console.log('[nav] --- menu links ---')
for (const link of (navCfg.menuLinks ?? [])) {
  await clickAndVerify(link.label, link.expectedPath)
}

// 2. Footer links (don't open menu)
console.log('[nav] --- footer links ---')
for (const link of (navCfg.footerLinks ?? [])) {
  await clickAndVerify(link.label, link.expectedPath, { openMenu: false })
}

// 3. Logo → home
if (navCfg.logoSelector || navCfg.logoLabel) {
  console.log('[nav] --- logo ---')
  // Pick a non-home start path
  const startPath = (cfg.pages.find(p => p.path !== '/') || {}).path ?? '/about-us'
  await page.goto(cfg.baseUrl + startPath, { waitUntil: 'networkidle' })
  await page.waitForTimeout(1000)
  try {
    const logo = navCfg.logoLabel
      ? await page.getByRole('link', { name: navCfg.logoLabel, exact: true }).first()
      : await page.locator(navCfg.logoSelector).first()
    await logo.click({ timeout: 8000 })
    await page.waitForLoadState('networkidle', { timeout: 15000 })
    const url = new URL(page.url())
    const ok = url.pathname === '/'
    if (ok) report.pass.push({ label: 'logo', expectedPath: '/' })
    else    report.fail.push({ label: 'logo', expectedPath: '/', actualPath: url.pathname })
    console.log(`[nav] ${ok ? 'OK' : 'FAIL'} logo → ${url.pathname}`)
  } catch (e) {
    report.fail.push({ label: 'logo', error: e.message })
    console.log(`[nav] FAIL logo: ${e.message.slice(0, 100)}`)
  }
}

// 4. BACK buttons
if (Array.isArray(navCfg.backButtons)) {
  console.log('[nav] --- BACK buttons ---')
  for (const b of navCfg.backButtons) {
    await page.goto(cfg.baseUrl + b.from, { waitUntil: 'networkidle' })
    await page.waitForTimeout(1000)
    try {
      const back = await page.getByRole('link', { name: /back/i }).first()
      await back.click({ timeout: 5000 })
      await page.waitForLoadState('networkidle', { timeout: 15000 })
      const url = new URL(page.url())
      const ok = url.pathname === b.expectedPath
      if (ok) report.pass.push({ label: `back/${b.from}`, expectedPath: b.expectedPath })
      else    report.fail.push({ label: `back/${b.from}`, expectedPath: b.expectedPath, actualPath: url.pathname })
      console.log(`[nav] ${ok ? 'OK' : 'FAIL'} back from ${b.from} → ${url.pathname}`)
    } catch (e) {
      report.fail.push({ label: `back/${b.from}`, error: e.message })
      console.log(`[nav] FAIL back/${b.from}: ${e.message.slice(0, 100)}`)
    }
  }
}

// 5. Screenshots: home closed, menu open, one detail page with BACK visible
try {
  await page.goto(cfg.baseUrl + '/', { waitUntil: 'networkidle' })
  await page.waitForTimeout(1500)
  await page.screenshot({ path: path.join(shotDir, '01-home-closed.png') })
  if (navCfg.menuToggleSelector) {
    await page.click(navCfg.menuToggleSelector)
    await page.waitForTimeout(800)
    await page.screenshot({ path: path.join(shotDir, '02-menu-open.png') })
  }
  if (navCfg.backButtons?.[0]?.from) {
    await page.goto(cfg.baseUrl + navCfg.backButtons[0].from, { waitUntil: 'networkidle' })
    await page.waitForTimeout(1500)
    await page.screenshot({ path: path.join(shotDir, '03-detail-with-back.png') })
  }
} catch {}

await browser.close()

const verdict = report.fail.length === 0 ? 'PASS' : 'FAIL'
const summary = {
  suite: 'nav',
  verdict,
  passed: report.pass.length,
  failed: report.fail.length,
  failures: report.fail,
}
fs.writeFileSync(path.join(dir, 'report.json'), JSON.stringify(report, null, 2))
fs.writeFileSync(path.join(dir, 'summary.json'), JSON.stringify(summary, null, 2))
console.log(`[nav] suite verdict: ${verdict} (${report.pass.length} pass, ${report.fail.length} fail)`)
