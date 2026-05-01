"""
Visual regression: crawl all pages from OLD_BASE, screenshot both environments,
pixel-diff every pair. Saves PNGs and results.json to OUT_DIR.

Usage:
  python3 crawl_and_diff.py --old <url> --new <url> --out <dir> [--max-pages N]
"""

import argparse
import asyncio
import io
import json
import os
import re
from urllib.parse import urlparse

from PIL import Image, ImageChops, ImageEnhance
from playwright.async_api import async_playwright

VIEWPORTS = [
    {"name": "desktop", "width": 1440, "height": 900},
    {"name": "mobile",  "width": 375,  "height": 812},
]


async def crawl_pages(page, base_url: str, max_pages: int) -> list[str]:
    visited = set()
    to_visit = ["/"]
    found = []

    while to_visit and len(found) < max_pages:
        path = to_visit.pop(0)
        if path in visited:
            continue
        visited.add(path)

        url = base_url + path
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
        except Exception as e:
            print(f"  [skip] {path} — {e}")
            continue

        found.append(path)
        print(f"  [crawl] {path}")

        links = await page.eval_on_selector_all(
            "a[href]",
            "els => els.map(el => el.getAttribute('href'))"
        )
        for href in links:
            if not href:
                continue
            if href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue
            parsed = urlparse(href)
            if parsed.netloc and parsed.netloc not in urlparse(base_url).netloc:
                continue
            clean = parsed.path
            if parsed.query:
                clean += "?" + parsed.query
            if clean and clean not in visited and clean not in to_visit:
                to_visit.append(clean)

    return found


async def screenshot_page(page, url: str) -> bytes | None:
    try:
        await page.goto(url, wait_until="networkidle", timeout=30000)
        return await page.screenshot(full_page=True)
    except Exception as e:
        print(f"  [error] {url}: {e}")
        return None


def diff_images(img_a: bytes, img_b: bytes) -> tuple[float, bytes]:
    ia = Image.open(io.BytesIO(img_a)).convert("RGB")
    ib = Image.open(io.BytesIO(img_b)).convert("RGB")
    w = max(ia.width, ib.width)
    h = max(ia.height, ib.height)
    ca = Image.new("RGB", (w, h), (255, 255, 255))
    cb = Image.new("RGB", (w, h), (255, 255, 255))
    ca.paste(ia, (0, 0))
    cb.paste(ib, (0, 0))
    diff = ImageChops.difference(ca, cb)
    amplified = ImageEnhance.Brightness(diff).enhance(5)
    pixels = list(diff.getdata())
    changed = sum(1 for r, g, b in pixels if r + g + b > 10)
    pct = round(changed / (w * h) * 100, 2)
    buf = io.BytesIO()
    amplified.save(buf, format="PNG")
    return pct, buf.getvalue()


async def main(old_base: str, new_base: str, out_dir: str, max_pages: int):
    os.makedirs(out_dir, exist_ok=True)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()

        print(f"\n[1/3] Crawling {old_base} ...")
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await ctx.new_page()
        paths = await crawl_pages(page, old_base, max_pages)
        await ctx.close()
        print(f"  Found {len(paths)} pages")

        results = []

        for vp in VIEWPORTS:
            print(f"\n[2/3] Screenshotting at {vp['name']} ({vp['width']}px)...")
            ctx = await browser.new_context(viewport={"width": vp["width"], "height": vp["height"]})
            page = await ctx.new_page()

            for path in paths:
                slug = re.sub(r"[^a-z0-9]", "_", path.strip("/")) or "home"
                old_ss = await screenshot_page(page, old_base + path)
                new_ss = await screenshot_page(page, new_base + path)

                if old_ss and new_ss:
                    diff_pct, diff_img = diff_images(old_ss, new_ss)
                    print(f"  {vp['name']} | {path} | {diff_pct}%")

                    with open(f"{out_dir}/old_{vp['name']}_{slug}.png", "wb") as f:
                        f.write(old_ss)
                    with open(f"{out_dir}/new_{vp['name']}_{slug}.png", "wb") as f:
                        f.write(new_ss)
                    with open(f"{out_dir}/diff_{vp['name']}_{slug}.png", "wb") as f:
                        f.write(diff_img)

                    entry = next((r for r in results if r["path"] == path), None)
                    if entry is None:
                        entry = {"path": path, "slug": slug, "desktop_diff": 0, "mobile_diff": 0, "max_diff": 0}
                        results.append(entry)
                    entry[f"{vp['name']}_diff"] = diff_pct
                    entry["max_diff"] = max(entry["max_diff"], diff_pct)
                else:
                    print(f"  [skip] {path} — screenshot failed on one side")

            await ctx.close()

        await browser.close()

    print("\n[3/3] Saving results...")
    with open(f"{out_dir}/results.json", "w") as f:
        json.dump(results, f, indent=2)

    changed = sum(1 for r in results if r["max_diff"] > 0.5)
    print(f"\nDone. {changed}/{len(results)} pages changed.")
    print(f"Results: {out_dir}/results.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--old", required=True, help="Previous environment base URL")
    parser.add_argument("--new", required=True, help="New environment base URL")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--max-pages", type=int, default=100, help="Max pages to crawl (default 100)")
    args = parser.parse_args()

    # Strip trailing slashes
    old_base = args.old.rstrip("/")
    new_base = getattr(args, "new").rstrip("/")

    asyncio.run(main(old_base, new_base, args.out, args.max_pages))
