# Playwright patterns

The spec is a Playwright E2E suite that lives at `tests/{wb}.spec.ts`. These are the patterns to use, the patterns to avoid, and the structure to follow.

## File header

Every generated spec starts with a header tying it back to the doc:

```ts
/**
 * {WB} automated acceptance tests.
 * Covers user stories from docs/qa/user-stories-{WB}.md.
 *
 * Run: npx playwright test tests/{wb}.spec.ts
 */
import { test, expect, Page } from '@playwright/test'
```

## Helper: navigate-and-settle

Most pages need a moment for React to hydrate after Liquid serves the shell. Use a single helper:

```ts
async function go(page: Page, path: string) {
  const response = await page.goto(path, { waitUntil: 'networkidle', timeout: 30000 })
  await page.waitForLoadState('domcontentloaded')
  return response
}
```

Prefer `waitUntil: 'networkidle'` over `waitForTimeout`. If the project genuinely needs a settle delay (e.g. a JS-driven reveal animation), wrap it in a named helper with a comment explaining why.

## Structure: one describe per section

```ts
test.describe('Marketplace', () => {
  test('list renders heading, filters, and cards', async ({ page }) => {
    await go(page, '/marketplace')
    await expect(page.locator('h1.mig-marketplace-page-title')).toHaveText('Marketplace')
    await expect(page.locator('.mig-marketplace-filters')).toBeVisible()
    const cards = page.locator('a[href^="/marketplace/"]')
    expect(await cards.count()).toBeGreaterThan(0)
  })

  test('detail page shows artist name, artwork name, price', async ({ page }) => {
    await go(page, '/marketplace/celestial-bloom')
    await expect(page.locator('h1').first()).toBeVisible()
    await expect(page).toHaveTitle(/Celestial Bloom/)
    await expect(page.getByText(/\$\d/).first()).toBeVisible()
  })
})
```

Section headings in the doc become `describe` names verbatim (or with the section number stripped).

## Selector priority (highest to lowest)

1. **Role + accessible name**: `page.getByRole('button', { name: /send/i })`
2. **Text**: `page.getByText('Marketplace')`, `page.getByText(/Meet the team/i)`
3. **Label** for form fields: `page.getByLabel('Email Address')`
4. **Test ID** if the project uses them: `page.getByTestId('marketplace-grid')`
5. **CSS class** as a last resort: `page.locator('.mig-marketplace-page-title')`

Class-based selectors are fragile when designers refactor classes. Use them only when 1–4 don't work.

## Web-first assertions

Always use these — they auto-retry until the expectation is met or the timeout fires:

```ts
await expect(locator).toBeVisible()
await expect(locator).toHaveText('Marketplace')
await expect(locator).toContainText('We move art')
await expect(locator).toHaveAttribute('href', '/contact')
await expect(locator).toHaveCount(2)
await expect(page).toHaveURL(/\/marketplace\//)
await expect(page).toHaveTitle(/Migration Galleries/)
```

## Banned patterns

| Anti-pattern | Why | Replacement |
|---|---|---|
| `page.waitForTimeout(2000)` for assertions | Flaky and slow | `await expect(...)` web-first matcher |
| `await page.locator(...).innerText()` then plain `expect()` | No retry | `await expect(locator).toHaveText(...)` |
| Hard-coded sleeps to "let animations finish" | Flaky | Wait for the post-animation state explicitly |
| `page.locator('xpath=...')` for everything | Brittle | Role / text / label first |
| Asserting against absolute pixel values for layouts | Breaks on viewport differences | Assert structural properties (`flex-direction`, `display`) |
| `try/catch` around assertions to "make tests resilient" | Hides real bugs | Let the assertion fail; debug the cause |

## Mobile / responsive blocks

Use a separate `describe` and `test.use` for viewport switches:

```ts
test.describe('Responsive - mobile', () => {
  test.use({ viewport: { width: 390, height: 844 } })

  test('marketplace filter stacks above grid', async ({ page }) => {
    await go(page, '/marketplace')
    const content = page.locator('.mig-marketplace-content').first()
    const direction = await content.evaluate((el) =>
      getComputedStyle(el as HTMLElement).flexDirection
    )
    expect(direction).toBe('column')
  })
})
```

For multi-viewport runs, prefer Playwright config-level `projects` (Chromium desktop + Pixel 5 mobile + WebKit) over per-test `test.use`.

## Iterating over pages (metadata, console health)

```ts
test.describe('Metadata / SEO', () => {
  const pages = [
    { path: '/', title: /^Migration Galleries$/ },
    { path: '/about-us', title: /About Us \| Migration Galleries/ },
    { path: '/marketplace', title: /Marketplace \| Migration Galleries/ },
    // ...
  ]

  for (const p of pages) {
    test(`${p.path} has correct title and og tags`, async ({ page }) => {
      await go(page, p.path)
      await expect(page).toHaveTitle(p.title)
      const og = (prop: string) =>
        page.locator(`meta[property="og:${prop}"]`).getAttribute('content')
      expect(await og('title')).toBeTruthy()
      expect(await og('site_name')).toBe('Migration Galleries')
      const canonical = await page.locator('link[rel="canonical"]').getAttribute('href')
      expect(canonical).toMatch(/^https?:\/\//)
    })
  }
})
```

## Console health

```ts
test.describe('Console health', () => {
  const criticalPages = ['/', '/about-us', '/artists', '/marketplace', '/contact']

  for (const path of criticalPages) {
    test(`no console errors on ${path}`, async ({ page }) => {
      const errors: string[] = []
      page.on('pageerror', (e) => errors.push(e.message))
      page.on('console', (m) => {
        if (m.type() === 'error') errors.push(m.text())
      })
      await go(page, path)
      expect(errors, `Console errors on ${path}: ${errors.join('; ')}`).toEqual([])
    })
  }
})
```

## Conditional skips

When a criterion needs manual QA:

```ts
test.skip('autoresponder email fires', async () => {
  // (manual QA) — verified in dev mailbox; cannot assert from a Playwright run.
})
```

Don't delete the test — keep it as a skip so the doc and spec stay aligned.

## Accessibility scan (optional)

If `@axe-core/playwright` is available:

```ts
import AxeBuilder from '@axe-core/playwright'

test.describe('Accessibility', () => {
  for (const path of criticalPages) {
    test(`axe scan: ${path}`, async ({ page }) => {
      await go(page, path)
      const results = await new AxeBuilder({ page }).analyze()
      expect(results.violations, JSON.stringify(results.violations, null, 2)).toEqual([])
    })
  }
})
```

If not installed, document the criterion and add `(manual QA)`. Do not silently skip.

## Test naming

Match the doc heading + the criterion. E.g. doc says:

> Each link navigates to the correct URL

Test:

```ts
test('each menu link navigates to the correct URL', async ({ page }) => { ... })
```

The user can read the test list and recognise it as the doc.

## Config

If the project doesn't have a `playwright.config.ts`, generate one:

```ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: process.env.BASE_URL || 'https://{project-staging-url}',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile', use: { ...devices['Pixel 5'] } },
  ],
})
```

Set `baseURL` from the project's staging URL — every `go(page, path)` then resolves relative.
