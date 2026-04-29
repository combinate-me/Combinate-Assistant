#!/usr/bin/env node
// scaffold-config — generate a starter qa-config.json from a user-stories doc
//
// Usage:
//   node scaffold-config.mjs \
//     --user-stories docs/qa/user-stories-WB02.md \
//     --workblock WB02 \
//     --base-url https://mig-web-dev.staging.oregon.platform-os.com \
//     --project "Migration Galleries" \
//     --output qa-config.json

import fs from 'node:fs'
import path from 'node:path'

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`)
  return i >= 0 ? process.argv[i + 1] : fallback
}

const docPath = arg('user-stories')
const workblock = arg('workblock', 'WB')
const baseUrl = arg('base-url', '')
const project = arg('project', 'Project')
const outPath = arg('output', 'qa-config.json')

if (!docPath || !fs.existsSync(docPath)) {
  console.error(`scaffold-config: --user-stories is required and must exist`)
  process.exit(2)
}
if (!baseUrl) {
  console.error(`scaffold-config: --base-url is required`)
  process.exit(2)
}

const doc = fs.readFileSync(docPath, 'utf8')

// Parse routes from the doc — look for `Page loads at \`/path\`` or backtick paths
const routeMatches = [
  ...doc.matchAll(/Page loads at\s+`?([^`\s,]+)`?/gi),
  ...doc.matchAll(/loads at\s+`([^`]+)`/gi),
]
const routes = new Set()
for (const m of routeMatches) {
  let r = m[1].trim()
  if (r.includes('{')) r = r.replace(/\{[^}]+\}/g, 'first')  // crude default
  if (r.startsWith('/')) routes.add(r)
}

const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
const pages = []
for (const r of [...routes].sort()) {
  const parts = r.split('/').filter(Boolean)
  let name = parts.length === 0 ? 'home' : parts.join('-')
  // Normalise placeholders
  name = name.replace(/first/g, '').replace(/-+/g, '-').replace(/^-|-$/g, '') || 'home'
  pages.push({
    name,
    path: r,
    criticalPath: ['/', '/contact', '/marketplace'].includes(r),
  })
}

// Workblock identifier → spec path guess
const wbLower = workblock.toLowerCase()
const specPath = `tests/${wbLower}.spec.ts`
const playwrightSpec = fs.existsSync(specPath) ? specPath : null

const config = {
  project,
  workblock,
  baseUrl: baseUrl.replace(/\/$/, ''),
  outputDir: '/tmp/{project}-qa/{workblock}',
  mode: 'dev',
  pages,
  viewports: [
    { name: 'desktop', width: 1440, height: 900 },
    { name: 'tablet',  width: 768,  height: 1024 },
    { name: 'mobile',  width: 390,  height: 844 },
  ],
  navigation: {
    menuToggleSelector: '.menu-toggle',
    menuPanelSelector: '.menu-panel',
    logoLabel: 'home',
    menuLinks: [],
    footerLinks: [],
    backButtons: [],
  },
  thresholds: {
    lighthouse: { performance: 70, accessibility: 95, bestPractices: 95, seo: 90, warnBand: 10 },
    axe: { maxCritical: 0, maxSerious: 0, maxModerate: 5 },
    console: { maxErrors: 0, maxFailedRequests: 0, maxWarnings: 10 },
    screenshots: { diffPercentWarn: 1, diffPercentFail: 5 },
    playwright: { maxFailing: 0 },
    w3c: { maxErrors: 0, maxWarnings: 5 },
  },
  playwrightSpec,
  teamwork: { taskId: null, attach: 'summary' },
  ci: { strict: false, skipSlowSuites: false },
}

fs.writeFileSync(outPath, JSON.stringify(config, null, 2) + '\n')
console.log(`Wrote ${outPath}`)
console.log(`  ${pages.length} pages from ${docPath}`)
console.log(`  Playwright spec: ${playwrightSpec ?? '(not found — set after running qa-acceptance-criteria)'}`)
console.log(`\nReview ${outPath}, then run:`)
console.log(`  bash {skill}/scripts/run-qa.sh --config ${outPath}`)
