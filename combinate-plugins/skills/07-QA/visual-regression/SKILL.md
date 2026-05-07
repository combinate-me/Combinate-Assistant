---
name: visual-regression
description: Run a full visual regression test between two web environments. Covers public pages, sign-up flow, sign-in flow, portal/authenticated pages, system pages, error pages, and functional QA. Screenshotted at desktop and mobile, pixel-diffed, and compiled into a branded HTML report. Use whenever comparing two staging environments, staging vs production, or before/after a deployment. Trigger on any mention of regression testing, visual comparison between environments, "check what changed", "compare staging", or "regression report".
  intranet_url: https://intranet.combinate.me/presentation/skill-visual-regression
---

# Visual Regression Testing

Full regression coverage between two web environments: visual diffs across all page types, authenticated portal testing, and functional QA.

---

## Arguments

`$ARGUMENTS` — space-separated:

```
/visual-regression [previous-url] [new-url]
/visual-regression [previous-url] [new-url] [output-dir]
```

- `[previous-url]` — the baseline environment (e.g. staging v110)
- `[new-url]` — the environment to compare against (e.g. staging v111)
- `[output-dir]` — optional absolute path for output. Defaults to a timestamped folder inside `output/regression/`

Examples:
```
/visual-regression https://mysite-110.staging.com https://mysite-111.staging.com
/visual-regression https://staging.mysite.com https://mysite.com /tmp/regression-prod
```

---

## Prerequisites

Run once per machine if not already installed:

```bash
pip3 install playwright Pillow
python3 -m playwright install chromium
```

---

## Page Coverage Goals

The regression must cover every page type available on the environment. Aim to test:

| Category | Examples |
|----------|---------|
| **Public pages** | Home, About, Features, News, Products, FAQs, Contact |
| **Sign-up flow** | Each step of the registration form (screenshot per step) |
| **Sign-in flow** | Sign-in page, failed login state, successful redirect |
| **Portal / authenticated pages** | Overview, My Details, My Company, Order History, any dashboard pages |
| **System pages** | Privacy Policy, Terms and Conditions, Forgot Password |
| **Error pages** | 404 page, 500 page (if triggerable) |
| **Thank you / confirmation pages** | Post-registration, post-form-submission confirmation screens |
| **Product / listing pages** | Category pages, filter variants, individual product pages |
| **Search results** | If search is available |

---

## Workflow

### Step 1 — Parse arguments and prepare output directory

Extract `previous_url`, `new_url`, and optional `output_dir` from `$ARGUMENTS`.

If no `output_dir` is given, generate one:
```
[workspace]/output/regression/[YYYY-MM-DD]-[label-from-urls]/
```

Create the output directory.

---

### Step 2 — Crawl and screenshot public pages

```bash
python3 .claude/skills/visual-regression/scripts/crawl_and_diff.py \
  --old "[previous-url]" \
  --new "[new-url]" \
  --out "[output-dir]"
```

This will:
- Crawl all internal pages from the previous URL (up to 100 pages)
- Screenshot each page on both environments at desktop (1440px) and mobile (375px)
- Auto-dismiss cookie banners and overlays before screenshotting
- Pixel-diff every pair and save `old_*.png`, `new_*.png`, `diff_*.png`
- Record HTTP status for every page on both environments
- Record page load time for every page
- Save `results.json` with diff percentages, HTTP status, and load times

---

### Step 3 — Registration (sign-up flow)

Always run the sign-up flow regression unless explicitly told to skip it.

Write and run a Playwright script that:
1. Generates unique test account emails using a timestamp (e.g. `regtest_[env]_[timestamp]@mailinator.com`) to avoid conflicts
2. Completes the full multi-step registration form on both environments, screenshotting every step
3. Saves credentials to `[output-dir]/credentials.json` for re-use in later steps
4. Notes the post-registration redirect URL — this is a key functional check

**Functional checks during sign-up:**
- Required field validation: submit each step with empty fields and screenshot the error state
- Password strength rules: test a weak password and screenshot the error
- Email format validation: test an invalid email format
- Post-registration redirect: confirm it lands on the correct confirmation page (not back on the registration form)

Save sign-up step screenshots as `old_signup_[step].png`, `new_signup_[step].png`, `diff_signup_[step].png`.
Save results to `results_signup.json`.

If the environment requires admin approval before login, note this as a functional finding. Flag if this behaviour differs between environments (e.g. 111 allows immediate login, 110 requires admin activation).

---

### Step 4 — Sign-in flow

Run a dedicated sign-in regression:
1. Navigate to the sign-in page on both environments and screenshot
2. Submit with invalid credentials and screenshot the error state
3. Submit with valid credentials (from `credentials.json`) and screenshot the post-login state
4. Confirm login succeeds — check body text for error messages, not just URL

**Functional checks during sign-in:**
- Error message is shown for wrong password
- Error message is shown for unregistered email
- Redirect after login goes to the expected page
- "Forgot password" link is present and working

---

### Step 5 — Authenticated portal pages

Once logged in with valid test accounts, crawl all pages accessible behind the auth gate.

1. Log in on both environments using credentials from `credentials.json`
2. Crawl all internal links found while logged in
3. Identify pages that are portal-only (not in the public crawl results)
4. Screenshot every portal page at desktop and mobile
5. Diff and record results to `results_auth.json`
6. Also record:
   - Pages present on old env only
   - Pages present on new env only

Save portal screenshots as `auth_old_*.png`, `auth_new_*.png`, `auth_diff_*.png`.

If credentials require admin activation before they work, pause and notify the user with the test account emails so they can activate them in the admin panel.

---

### Step 6 — Functional QA sweep

Run a functional QA pass on both environments covering:

**Links and navigation**
- All `<a href>` links resolve without 404
- Navigation menu links work correctly
- Footer links work correctly

**Images**
- No broken `<img>` tags (check for failed network requests)
- No empty `src` or `alt` attributes where they should exist

**Forms**
- All visible form fields are focusable and fillable
- Required field validation triggers correctly
- Form submission error messages are visible and readable

**Console errors**
- Capture all JavaScript console errors during page load
- Flag pages with errors as findings in the QA report

**HTTP status sweep**
- Check the HTTP status of every crawled URL on both environments
- Flag any 4xx or 5xx responses

**Page performance**
- Record load time per page
- Flag pages where load time on new env is more than 2x slower than old env

**Popup and overlay handling**
- Auto-dismiss cookie consent banners before screenshotting
- Auto-dismiss any modals or overlays that appear on load

Save all QA findings to `results_qa.json`.

---

### Step 7 — Generate the unified report

Build a single branded HTML report combining all test results.

The report must:
- Use the Combinate visual regression template (dark header #181818, Combinate logo SVG, Phosphor icons, diff bar charts)
- Have 2 tabs:
  - **Regression Report** — one combined table with all rows grouped by section (Public Pages, Sign-up Flow, Sign-in Flow, Portal Pages) with section divider rows
  - **Functional QA** — findings table with Severity, Area, Affects, and Finding columns
- Table columns: HTTP (old) | Page/Step (old) | HTTP (new) | Page/Step (new) | Status | Visual Diff | Screenshots
- Row highlighting: `row-404` class for 404 pages, `changed` for visual differences, `same` for unchanged
- Summary cards at the top: Total Comparisons, Changed, Unchanged, 404/Errors

All screenshots must be saved in the same output directory as the report so the folder can be packaged and shared without broken links.

```bash
python3 .claude/skills/visual-regression/scripts/generate_report.py \
  --old "[previous-url]" \
  --new "[new-url]" \
  --out "[output-dir]"
```

---

### Step 8 — Open and present results

```bash
open "[output-dir]/report.html"
```

Summarise:
- Total comparisons across all sections
- Changed vs unchanged
- Any 404s or HTTP errors (flag which environment)
- Critical functional QA findings
- Pages present on one environment only
- Path to the report

---

## Output structure

```
[output-dir]/
├── report.html                  — full branded report (open this)
├── results.json                 — public pages diff data
├── results_signup.json          — sign-up flow step data
├── results_auth.json            — portal pages diff data
├── results_qa.json              — functional QA findings
├── credentials.json             — test account emails and password
├── old_desktop_*.png            — public pages: old env desktop
├── new_desktop_*.png            — public pages: new env desktop
├── diff_desktop_*.png           — public pages: pixel diff desktop
├── old_mobile_*.png
├── new_mobile_*.png
├── diff_mobile_*.png
├── old_signup_desktop_*.png     — sign-up steps
├── new_signup_desktop_*.png
├── diff_signup_desktop_*.png
├── auth_old_desktop_*.png       — portal pages
├── auth_new_desktop_*.png
└── auth_diff_desktop_*.png
```

All screenshots in one folder — no subfolders — so the entire output directory can be zipped and shared.

---

## Credential storage convention

Test account credentials are always saved to `[output-dir]/credentials.json`:

```json
{
  "old_email": "regtest_old_[timestamp]@mailinator.com",
  "new_email": "regtest_new_[timestamp]@mailinator.com",
  "password": "Test@12345!"
}
```

On re-runs, check if `credentials.json` already exists and the accounts are still active before creating new ones. This avoids unnecessary registrations.

If the project uses Teamwork, the test credentials should also be noted in a comment on the Teamwork task so the team can activate accounts in the admin panel if needed.

---

## Suggestions for improving test coverage

- **Seed data consistency** — ensure both environments have the same product/content data before running. Differences in data cause false positives in diffs.
- **State isolation** — run each environment in a fresh browser context to prevent session bleed between tests.
- **Deduplication by template** — for environments with many filter/query variants of the same template (e.g. `/products?category=X`), test one representative URL per template to reduce noise.
- **Re-run on flaky diffs** — dynamic content (carousels, timestamps, live data) causes noise. Re-screenshot and re-diff any page with an unexpectedly high diff before flagging it as changed.
- **Staging data reset** — before a regression run, confirm that both staging environments were seeded from the same data snapshot.
