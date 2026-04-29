/**
 * WB02 automated acceptance tests.
 * Covers user stories from /tmp/mig-qa/user-stories-WB02.md.
 *
 * Run: npx playwright test tests/wb02.spec.ts
 */
import { test, expect, Page } from '@playwright/test'

async function go(page: Page, path: string) {
  const response = await page.goto(path, { waitUntil: 'networkidle', timeout: 30000 })
  await page.waitForTimeout(1500)
  return response
}

test.describe('Home', () => {
  test('loads with hero heading', async ({ page }) => {
    await go(page, '/')
    await expect(page.locator('h1.mig-hero-heading')).toContainText('We move art')
  })

  test('footer legal links resolve', async ({ page }) => {
    await go(page, '/')
    const hrefs: Record<string, string> = {
      Privacy: '/privacy-policy',
      "T & C's": '/terms-and-conditions',
      Glossary: '/glossary',
    }
    for (const [label, expected] of Object.entries(hrefs)) {
      const link = page.locator('.mig-footer-link', { hasText: label }).first()
      await expect(link).toHaveAttribute('href', expected)
    }
  })
})

test.describe('Artists', () => {
  test('list renders heading + cards', async ({ page }) => {
    await go(page, '/artists')
    await expect(page.locator('h1', { hasText: 'Artists' })).toBeVisible()
    await expect(page.locator('a[href^="/artists/"]').first()).toBeVisible()
  })

  test('detail page shows artist name as h1 and dynamic title', async ({ page }) => {
    await go(page, '/artists/aurora-hayes')
    await expect(page.locator('h1.mig-artist-detail-name')).toContainText('Aurora')
    await expect(page).toHaveTitle(/Aurora Hayes \| Migration Galleries/)
  })

  test('BACK button links to /artists', async ({ page }) => {
    await go(page, '/artists/aurora-hayes')
    const back = page.getByRole('link', { name: /back/i }).first()
    await expect(back).toHaveAttribute('href', '/artists')
  })
})

test.describe('Exhibitions', () => {
  test('list renders heading + map + cards', async ({ page }) => {
    await go(page, '/exhibitions')
    await expect(page.locator('h1', { hasText: 'Exhibitions' })).toBeVisible()
    await expect(page.locator('.mig-exhibitions-map, .mig-exhibitions-map-wrapper, [class*="mig-exhibitions"]').first()).toBeVisible()
  })

  test('detail page shows exhibition or venue name', async ({ page }) => {
    await go(page, '/exhibitions/gallery-35')
    await expect(page.locator('h1').first()).toContainText(/Gallery 35|Bluebird/)
    await expect(page).toHaveTitle(/Gallery 35|Bluebird/)
  })
})

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

  test('OR LEASE CTA is hidden per ce24c36 commit', async ({ page }) => {
    await go(page, '/marketplace/celestial-bloom')
    const orLease = page.getByRole('link', { name: /or lease/i })
    expect(await orLease.count()).toBe(0)
  })

  test('BACK button links to /marketplace', async ({ page }) => {
    await go(page, '/marketplace/celestial-bloom')
    const back = page.getByRole('link', { name: /back/i }).first()
    await expect(back).toHaveAttribute('href', '/marketplace')
  })
})

test.describe('Contact', () => {
  test('form renders with all fields', async ({ page }) => {
    await go(page, '/contact')
    await expect(page.locator('h1', { hasText: 'Contact' })).toBeVisible()
    for (const label of ['NAME', 'EMAIL ADDRESS', 'PHONE NUMBER', 'MESSAGE']) {
      await expect(page.getByText(label, { exact: true }).first()).toBeVisible()
    }
    await expect(page.getByRole('button', { name: /send/i })).toBeVisible()
  })

  test('thank-you page renders', async ({ page }) => {
    await go(page, '/contact/thank-you')
    await expect(page).toHaveTitle(/Thank You \| Migration Galleries/)
  })
})

test.describe('Lease Enquiry', () => {
  test('form renders with all fields', async ({ page }) => {
    await go(page, '/lease-enquiry')
    await expect(page.locator('h1', { hasText: 'Lease Enquiry' })).toBeVisible()
    for (const label of ['NAME', 'EMAIL ADDRESS', 'PHONE NUMBER', 'MESSAGE']) {
      await expect(page.getByText(label, { exact: true }).first()).toBeVisible()
    }
    await expect(page.getByRole('button', { name: /send/i })).toBeVisible()
  })
})

test.describe('About', () => {
  test('renders heading + Meet the team', async ({ page }) => {
    await go(page, '/about-us')
    await expect(page.locator('h1', { hasText: 'About us' })).toBeVisible()
    await expect(page.getByText(/Meet the team/i).first()).toBeVisible()
  })
})

test.describe('Navigation (Slide menu)', () => {
  test('menu opens and all nav links navigate', async ({ page }) => {
    await go(page, '/')
    await page.click('.mig-menu-toggle')
    await page.waitForTimeout(500)
    const menu = page.locator('.mig-menu-panel')
    await expect(menu).toBeVisible()

    // Each link points to the right URL
    const expected: Record<string, string> = {
      HOME: '/',
      ARTISTS: '/artists',
      MARKETPLACE: '/marketplace',
      EXHIBITIONS: '/exhibitions',
      'ABOUT US': '/about-us',
      CONTACT: '/contact',
    }
    for (const [label, href] of Object.entries(expected)) {
      const link = page.getByRole('link', { name: label, exact: true }).first()
      await expect(link).toHaveAttribute('href', href)
    }
  })

  test('logo link returns home', async ({ page }) => {
    await go(page, '/artists')
    const logo = page.getByRole('link', { name: 'Migration Galleries home' }).first()
    await expect(logo).toHaveAttribute('href', '/')
  })
})

test.describe('Metadata / SEO', () => {
  const pages = [
    { path: '/', title: /^Migration Galleries$/ },
    { path: '/about-us', title: /About Us \| Migration Galleries/ },
    { path: '/artists', title: /Artists \| Migration Galleries/ },
    { path: '/exhibitions', title: /Exhibitions \| Migration Galleries/ },
    { path: '/marketplace', title: /Marketplace \| Migration Galleries/ },
    { path: '/contact', title: /Contact \| Migration Galleries/ },
    { path: '/lease-enquiry', title: /Lease Enquiry \| Migration Galleries/ },
    { path: '/glossary', title: /Glossary \| Migration Galleries/ },
  ]

  for (const p of pages) {
    test(`${p.path} has Migration Galleries title + og tags`, async ({ page }) => {
      await go(page, p.path)
      await expect(page).toHaveTitle(p.title)
      const og = async (prop: string) =>
        page.locator(`meta[property="og:${prop}"]`).getAttribute('content')
      expect(await og('title')).toBeTruthy()
      expect(await og('type')).toBe('website')
      expect(await og('site_name')).toBe('Migration Galleries')
      expect(await og('image')).toMatch(/OG-Banner-Default/)
      const canonical = await page.locator('link[rel="canonical"]').getAttribute('href')
      expect(canonical).toMatch(/^https?:\/\//)
    })
  }
})

test.describe('Console health', () => {
  const criticalPages = ['/', '/about-us', '/artists', '/artists/aurora-hayes', '/exhibitions', '/exhibitions/gallery-35', '/marketplace', '/marketplace/celestial-bloom', '/contact', '/contact/thank-you', '/glossary']
  for (const path of criticalPages) {
    test(`no console errors on ${path}`, async ({ page }) => {
      const errors: string[] = []
      page.on('pageerror', (e) => errors.push(e.message))
      page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) })
      await go(page, path)
      expect(errors, `Console errors on ${path}: ${errors.join('; ')}`).toEqual([])
    })
  }
})

test.describe('Responsive - mobile', () => {
  test.use({ viewport: { width: 390, height: 844 } })

  test('marketplace filter stacks above grid', async ({ page }) => {
    await go(page, '/marketplace')
    const content = page.locator('.mig-marketplace-content').first()
    const direction = await content.evaluate((el) => getComputedStyle(el as HTMLElement).flexDirection)
    expect(direction).toBe('column')
  })

  test('mobile menu opens and closes', async ({ page }) => {
    await go(page, '/')
    await page.click('.mig-menu-toggle')
    await page.waitForTimeout(400)
    await expect(page.locator('.mig-menu-panel')).toBeVisible()
  })
})
