"""
Generate a branded Combinate visual regression report.
Reads results.json from OUT_DIR, re-verifies diffs, checks 404s, writes report.html.

Usage:
  python3 generate_report.py --old <url> --new <url> --out <dir>
"""

import argparse
import asyncio
import io
import json
import os
from datetime import datetime

from PIL import Image, ImageChops
from playwright.async_api import async_playwright

LOGO_SVG = """<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 704 162" height="32" style="enable-background:new 0 0 704 162;">
<style>.st0{fill:#FFFFFF;}</style>
<path class="st0" d="M224.9,101.9c-4.3-3.9-6.6-9.5-6.9-16.8v-7.9c0.3-7.2,2.6-12.5,6.9-16.8c4.3-3.9,10.2-5.9,17.5-5.9c5.3,0,9.6,1,13.2,2.6c3.6,2,6.3,3.9,7.9,6.9c1.6,2.6,2.6,5.3,3,7.6c0,0.7,0,1.3-0.7,1.6c-0.3,0.3-1,0.7-1.6,0.7h-8.9c-0.7,0-1.3,0-1.6-0.3c-0.3-0.3-0.7-1-1-1.6c-1-2.6-2.3-4.3-4-5.3c-1.6-1-3.6-1.6-6.3-1.6c-3.3,0-5.9,1-7.9,3.3c-2,2-3,5.3-3,9.5v6.9c0.3,8.5,4,12.8,10.9,12.8c2.6,0,4.6-0.7,6.3-1.6c1.6-1,3-3,4-5.6c0.3-0.7,0.7-1.3,1-1.6c0.3-0.3,1-0.3,1.6-0.3h8.9c0.7,0,1.3,0.3,1.6,0.7c0.3,0.3,0.7,1,0.7,1.6c0,2.3-1,4.9-2.6,7.6c-1.6,2.6-4.3,4.9-7.9,6.9c-3.6,2-7.9,3-13.2,3C235.1,107.8,229.2,105.8,224.9,101.9z"/>
<path class="st0" d="M277.3,101.9c-4.3-3.9-6.6-9.5-6.9-16.4v-8.5c0.3-6.9,2.6-12.2,6.9-16.4c4.3-3.9,10.2-5.9,17.8-5.9c7.6,0,13.5,2,17.8,5.9c4.3,3.9,6.6,9.5,6.9,16.4c0,0.7,0,2.3,0,4.3c0,2,0,3.6,0,4.3c-0.3,6.9-2.6,12.5-6.9,16.4c-4.3,3.9-10.2,5.9-17.8,5.9C287.5,107.8,281.6,105.8,277.3,101.9z M303.4,94.7c2-2.3,3-5.3,3-9.5c0-0.7,0-2,0-3.9c0-2,0-3.3,0-3.9c0-4.3-1-7.6-3-9.5c-2-2.3-4.6-3.3-7.9-3.3c-3.6,0-6.3,1-8.2,3.3c-2,2.3-3,5.3-3,9.5v7.9c0,4.3,1,7.2,3,9.5c2,2.3,4.6,3.3,8.2,3.3C298.7,98,301.7,97,303.4,94.7z"/>
<path class="st0" d="M327.7,106.2c-0.3-0.3-0.7-1-0.7-1.6V58.2c0-0.7,0.3-1.3,0.7-1.6c0.3-0.3,1-0.7,1.6-0.7h7.9c0.7,0,1.3,0.3,1.6,0.7c0.3,0.3,0.7,1,0.7,1.6v3.3c3.6-4.6,8.2-6.6,14.2-6.6c7.3,0,12.5,3,15.2,8.9c1.6-2.6,4-4.6,6.6-6.2c3-1.6,5.9-2.3,9.2-2.3c5.3,0,9.9,2,13.2,5.6c3.3,3.6,5.3,8.9,5.3,16.1v28.3c0,0.7-0.3,1.3-0.7,1.6c-0.3,0.3-1,0.7-1.6,0.7h-8.2c-0.7,0-1.3-0.3-1.6-0.7c-0.3-0.3-0.7-1-0.7-1.6V77.6c0-4.3-1-7.2-2.6-8.9c-1.6-2-4-2.6-6.9-2.6c-2.6,0-4.6,1-6.6,3c-1.6,2-2.6,4.9-2.6,8.9v27.6c0,0.7-0.3,1.3-0.7,1.6c-0.3,0.3-1,0.7-1.6,0.7H361c-0.7,0-1.3-0.3-1.6-0.7c-0.3-0.3-0.7-1-0.7-1.6V77.9c0-3.9-1-6.9-2.6-8.9c-1.6-2-4-3-6.9-3c-2.6,0-4.6,1-6.6,3c-1.6,2-2.6,4.9-2.6,8.9v27.6c0,0.7-0.3,1.3-0.7,1.6c-0.3,0.3-1,0.7-1.6,0.7h-8.2C329.1,106.8,328.4,106.8,327.7,106.2z"/>
<path class="st0" d="M425.3,100.9v3.6c0,0.7-0.3,1.3-0.7,1.6c-0.3,0.3-1,0.7-1.6,0.7h-7.9c-0.7,0-1.3-0.3-1.6-0.7c-0.3-0.3-0.7-1-0.7-1.6V39.5c0-0.7,0.3-1.3,0.7-1.6c0.3-0.3,1-0.7,1.6-0.7h8.6c0.7,0,1.3,0.3,1.6,0.7c0.3,0.3,0.7,1,0.7,1.6v21.7c3.6-4.3,8.6-6.6,15.2-6.6c6.6,0,11.9,2.3,15.5,6.6s5.6,9.9,5.6,16.8c0,0.7,0,2,0,3.3s0,2.3,0,3.3c-0.3,7.2-2.3,12.8-5.6,17.1c-3.6,4.3-8.6,6.2-15.2,6.2C434.2,107.8,428.9,105.5,425.3,100.9z M448.4,84.5c0-0.7,0-1.6,0-3s0-2.3,0-3c-0.3-8.5-4.3-13.1-11.2-13.1c-3.6,0-6.3,1-8.2,3.3c-2,2.3-3,4.9-3,8.2c0,0.7,0,2,0,3.9c0,1.6,0,3,0,3.6c0,3.6,1,6.6,3,8.9c2,2.3,4.6,3.6,8.2,3.6C444.1,97.3,448,93,448.4,84.5z"/>
<path class="st0" d="M469.5,46.7c-0.3-0.3-0.7-1-0.7-1.6v-7.2c0-0.7,0.3-1.3,0.7-1.6c0.3-0.3,1-0.7,1.6-0.7h9.2c0.7,0,1.3,0.3,1.6,0.7c0.3,0.3,0.7,1,0.7,1.6V45c0,0.7-0.3,1.3-0.7,1.6c-0.3,0.3-1,0.7-1.6,0.7h-9.2C470.5,47.3,469.8,47.3,469.5,46.7z M469.8,106.2c-0.3-0.3-0.7-1-0.7-1.6V58.2c0-0.7,0.3-1.3,0.7-1.6c0.3-0.3,1-0.7,1.6-0.7h8.2c0.7,0,1.3,0.3,1.6,0.7c0.3,0.3,0.7,1,0.7,1.6v46.3c0,0.7-0.3,1.3-0.7,1.6c-0.3,0.3-1,0.7-1.6,0.7h-8.2C470.8,106.8,470.1,106.8,469.8,106.2z"/>
<path class="st0" d="M491.9,106.2c-0.3-0.3-0.7-1-0.7-1.6V58.2c0-0.7,0.3-1.3,0.7-1.6c0.3-0.3,1-0.7,1.6-0.7h8.2c0.7,0,1.3,0.3,1.6,0.7c0.3,0.3,0.7,1,0.7,1.6v3.9c4-4.9,9.6-7.2,16.5-7.2c5.9,0,10.9,2,14.5,5.9c3.6,3.9,5.3,9.2,5.3,16.1v27.6c0,0.7-0.3,1.3-0.7,1.6c-0.3,0.3-1,0.7-1.6,0.7h-8.9c-0.7,0-1.3-0.3-1.6-0.7c-0.3-0.3-0.7-1-0.7-1.6V77.6c0-3.9-1-6.9-3-8.9c-2-2-4.6-3.3-7.9-3.3c-3.3,0-5.9,1-8.2,3.3c-2,2.3-3,5.3-3,8.9v26.9c0,0.7-0.3,1.3-0.7,1.6c-0.3,0.3-1,0.7-1.6,0.7h-8.9C492.9,106.8,492.5,106.8,491.9,106.2z"/>
<path class="st0" d="M554.5,105.8c-2.6-1.3-4.9-3.3-6.6-5.6c-1.6-2.3-2.3-4.9-2.3-7.6c0-4.6,1.6-8.2,5.3-10.8s8.6-4.6,14.8-5.6l13.5-2v-2c0-3-0.7-4.9-2.3-6.2c-1.3-1.3-3.6-2.3-6.9-2.3c-2.3,0-4,0.3-5.3,1.3c-1.3,0.7-2.3,1.6-3.3,2.3c-0.7,0.7-1.3,1.3-1.6,1.6c-0.3,0.7-0.7,1.3-1.3,1.3h-7.2c-0.7,0-1-0.3-1.6-0.7c-0.3-0.3-0.7-1-0.7-1.6c0-1.6,1-3.6,2.3-5.6c1.6-2,4-3.9,7.2-5.3c3.3-1.6,7.3-2.3,11.9-2.3c7.9,0,13.5,1.6,17.1,5.3c3.6,3.6,5.3,7.9,5.3,13.8v30.9c0,0.7-0.3,1.3-0.7,1.6c-0.3,0.3-1,0.7-1.6,0.7h-8.2c-0.7,0-1.3-0.3-1.6-0.7c-0.3-0.3-0.7-1-0.7-1.6v-3.9c-1.3,2-3.6,3.9-6.3,5.3c-2.6,1.3-5.9,2-9.9,2C560.4,107.8,557.5,107.2,554.5,105.8z M576.2,95c2.3-2.3,3.3-5.9,3.3-10.2v-2l-9.9,1.6c-7.6,1.3-11.2,3.6-11.2,7.6c0,2,1,3.6,2.6,4.9c1.6,1,4,1.6,6.3,1.6C571,98.6,573.9,97.3,576.2,95z"/>
<path class="st0" d="M610.9,102.2c-3-3-4.6-7.6-4.6-13.8V66.1h-7.9c-0.7,0-1.3-0.3-1.6-0.7c-0.3-0.3-0.7-1-0.7-1.6v-5.9c0-0.7,0.3-1.3,0.7-1.6c0.3-0.3,1-0.7,1.6-0.7h7.9V39.1c0-0.7,0.3-1.3,0.7-1.6c0.3-0.3,1-0.7,1.6-0.7h8.2c0.7,0,1.3,0.3,1.6,0.7c0.3,0.3,0.7,1,0.7,1.6v16.4h12.2c0.7,0,1.3,0.3,1.6,0.7c0.3,0.3,0.7,1,0.7,1.6v5.9c0,0.7-0.3,1.3-0.7,1.6c-0.3,0.3-1,0.7-1.6,0.7h-12.2v21c0,3,0.3,4.9,1.3,6.2s2.6,2.3,4.9,2.3h6.9c0.7,0,1.3,0.3,1.6,0.7c0.3,0.3,0.7,1,0.7,1.6v6.2c0,0.7-0.3,1.3-0.7,1.6c-0.3,0.3-1,0.7-1.6,0.7H624C618.4,106.8,613.8,105.5,610.9,102.2z"/>
<path class="st0" d="M644.1,101.6c-4.3-4.3-6.6-10.2-6.9-18.1v-2.3c0-8.2,2.3-14.8,6.6-19.4c4.3-4.6,10.2-7.2,17.8-7.2c7.9,0,13.8,2.3,18.1,7.2C684,66.4,686,73,686,80.5v2c0,0.7-0.3,1.3-0.7,1.6c-0.3,0.3-1,0.7-1.6,0.7h-32.6v0.7c0,3.6,1,6.6,3,9.2c2,2.3,4.6,3.6,7.9,3.6c3.6,0,6.9-1.6,9.2-4.6c0.7-0.7,1-1.3,1.3-1.3c0.3,0,1-0.3,1.6-0.3h8.6c0.7,0,1,0.3,1.6,0.3c0.3,0.3,0.7,0.7,0.7,1.3c0,1.6-1,3.3-3,5.6c-2,2-4.6,3.9-7.9,5.6c-3.6,1.6-7.6,2.3-12.2,2.3C654.4,107.8,648.4,105.8,644.1,101.6z M672.5,76.9c0-3.9-1-7.2-3-9.5c-2-2.3-4.6-3.6-7.9-3.6c-3.3,0-5.9,1.3-7.9,3.6c-2,2.3-3,5.6-3,9.2v0.3H672.5z"/>
<path class="st0" d="M140,42.6C140,42.5,140,42.5,140,42.6c0-0.2,0-0.3,0-0.4v-0.1c0,0,0,0,0-0.1V42c0-0.1,0-0.2-0.1-0.3v-0.1c0,0,0-0.1-0.1-0.1c0,0,0-0.1-0.1-0.1v-0.1l-0.1-0.1c0,0,0-0.1-0.1-0.1c0-0.1-0.1-0.1-0.1-0.2l-0.1-0.1c0,0,0-0.1-0.1-0.1c0,0,0,0-0.1-0.1l-0.1-0.1l-0.1-0.1l-0.1-0.1l-0.1-0.1l-0.1-0.1c0,0-0.1,0-0.1-0.1l-0.1-0.1c0,0,0,0-0.1-0.1L71.6,1.5c-1-0.6-2.2-0.6-3.3,0L1.6,39.8c0,0-0.1,0-0.1,0.1c0,0-0.1,0-0.1,0.1c0,0-0.1,0-0.1,0.1l-0.1,0.1l-0.1,0.1L1,40.4l-0.1,0.1l-0.1,0.1c0,0,0,0-0.1,0.1l-0.1,0.1l-0.1,0.1c0,0.1-0.1,0.1-0.1,0.2c0,0,0,0.1-0.1,0.1l-0.1,0.1v0.1c0,0,0,0.1-0.1,0.1c0,0,0,0.1-0.1,0.1v0.1c0,0.1-0.1,0.2-0.1,0.3V42c0,0,0,0,0,0.1v0.1c0,0.1,0,0.2,0,0.3v0.1v76.7c0,0.1,0,0.1,0,0.2c0,0,0,0,0,0.1c0,0,0,0,0,0.1c0,0.2,0.1,0.5,0.1,0.7v0.1c0.1,0.2,0.2,0.5,0.3,0.7c0.1,0.2,0.3,0.4,0.5,0.6l0.1,0.1c0.2,0.2,0.4,0.3,0.6,0.4c0,0,0,0,0.1,0l66.8,38.4c0.1,0,0.1,0.1,0.2,0.1s0.1,0.1,0.2,0.1c0,0,0,0,0.1,0h0.1H69c0.1,0,0.1,0,0.2,0.1c0.1,0,0.1,0,0.2,0h0.1h0.1c0.2,0,0.3,0,0.5,0s0.3,0,0.5,0h0.1h0.1c0.1,0,0.1,0,0.2,0s0.1,0,0.2-0.1h0.1h0.1c0,0,0,0,0.1,0s0.1-0.1,0.2-0.1s0.1-0.1,0.2-0.1l66.8-38.4c0,0,0,0,0.1,0c0.2-0.1,0.4-0.3,0.6-0.4l0.1-0.1c0.4-0.4,0.6-0.7,0.7-1.2v-0.1c0.1-0.2,0.1-0.5,0.1-0.7c0,0,0,0,0-0.1c0,0,0,0,0-0.1c0-0.1,0-0.1,0-0.2L140,42.6L140,42.6z M15.4,44.5L64,38.9L49.2,64.3L36.4,86.4L8.9,45.2L15.4,44.5z M44.3,85.9L70,41.4l27.7,47.9H42.2L44.3,85.9z M98.1,95.8L70,150.7l-28-54.9H98.1z M103.6,86.4L76,39l55,6.3L118,64.8L103.6,86.4z M12.2,62l20.1,30L6.5,112.7V53.3L12.2,62z M104.4,97.6l10.2,8.2l16.3,13.2l-53.1,30.6L104.4,97.6z M107.7,91.9l20.1-30l5.7-8.6v59.3L107.7,91.9z M73.2,32.1V9.9l48.3,27.8L73.2,32.1z M66.8,9.9v22.2l-48.3,5.6L66.8,9.9z M9,119l16.3-13.2l10.2-8.2l15.8,30.9l10.8,21.1L9,119z"/>
</svg>"""

ICON_GRID    = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 256 256" fill="currentColor"><path d="M104,32H56A24,24,0,0,0,32,56v48a24,24,0,0,0,24,24h48a24,24,0,0,0,24-24V56A24,24,0,0,0,104,32Zm8,72a8,8,0,0,1-8,8H56a8,8,0,0,1-8-8V56a8,8,0,0,1,8-8h48a8,8,0,0,1,8,8ZM200,32H152a24,24,0,0,0-24,24v48a24,24,0,0,0,24,24h48a24,24,0,0,0,24-24V56A24,24,0,0,0,200,32Zm8,72a8,8,0,0,1-8,8H152a8,8,0,0,1-8-8V56a8,8,0,0,1,8-8h48a8,8,0,0,1,8,8ZM104,128H56a24,24,0,0,0-24,24v48a24,24,0,0,0,24,24h48a24,24,0,0,0,24-24V152A24,24,0,0,0,104,128Zm8,72a8,8,0,0,1-8,8H56a8,8,0,0,1-8-8V152a8,8,0,0,1,8-8h48a8,8,0,0,1,8,8ZM200,128H152a24,24,0,0,0-24,24v48a24,24,0,0,0,24,24h48a24,24,0,0,0,24-24V152A24,24,0,0,0,200,128Zm8,72a8,8,0,0,1-8,8H152a8,8,0,0,1-8-8V152a8,8,0,0,1,8-8h48a8,8,0,0,1,8,8Z"/></svg>'
ICON_DIFF    = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 256 256" fill="currentColor"><path d="M224,48H32a8,8,0,0,0-8,8V192a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A8,8,0,0,0,224,48ZM40,112H80v32H40Zm56,0H216v32H96Zm120-16H40V64H216ZM40,160H80v32H40Zm56,0H216v32H96Z"/></svg>'
ICON_CHECK   = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 256 256" fill="currentColor"><path d="M173.66,98.34a8,8,0,0,1,0,11.32l-56,56a8,8,0,0,1-11.32,0l-24-24a8,8,0,0,1,11.32-11.32L112,148.69l50.34-50.35A8,8,0,0,1,173.66,98.34ZM232,128A104,104,0,1,1,128,24,104.11,104.11,0,0,1,232,128Zm-16,0a88,88,0,1,0-88,88A88.1,88.1,0,0,0,216,128Z"/></svg>'
ICON_WARNING = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 256 256" fill="currentColor"><path d="M236.8,188.09,149.35,36.22a24.76,24.76,0,0,0-42.7,0L19.2,188.09a23.51,23.51,0,0,0,0,23.72A24.35,24.35,0,0,0,40.55,224h174.9a24.35,24.35,0,0,0,21.33-12.19A23.51,23.51,0,0,0,236.8,188.09ZM222.93,204a8.5,8.5,0,0,1-7.48,4H40.55a8.5,8.5,0,0,1-7.48-4,7.59,7.59,0,0,1,0-7.72L120.52,44.41a8.75,8.75,0,0,1,15,0l87.45,151.87A7.59,7.59,0,0,1,222.93,204ZM120,144V104a8,8,0,0,1,16,0v40a8,8,0,0,1-16,0Zm20,36a12,12,0,1,1-12-12A12,12,0,0,1,140,180Z"/></svg>'


def recompute_diff(out_dir: str, slug: str, viewport: str) -> float | None:
    old_path = os.path.join(out_dir, f"old_{viewport}_{slug}.png")
    new_path = os.path.join(out_dir, f"new_{viewport}_{slug}.png")
    if not os.path.exists(old_path) or not os.path.exists(new_path):
        return None
    try:
        ia = Image.open(old_path).convert("RGB")
        ib = Image.open(new_path).convert("RGB")
        w, h = max(ia.width, ib.width), max(ia.height, ib.height)
        ca = Image.new("RGB", (w, h), (255, 255, 255))
        cb = Image.new("RGB", (w, h), (255, 255, 255))
        ca.paste(ia, (0, 0))
        cb.paste(ib, (0, 0))
        from PIL import ImageChops
        diff = ImageChops.difference(ca, cb)
        pixels = list(diff.getdata())
        changed = sum(1 for r, g, b in pixels if r + g + b > 10)
        return round(changed / (w * h) * 100, 2)
    except Exception as e:
        print(f"  [warn] recompute failed {viewport}/{slug}: {e}")
        return None


async def check_statuses(paths: list[str], old_base: str, new_base: str) -> dict:
    statuses = {}
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context()
        page = await ctx.new_page()
        for path in paths:
            entry = {"old": 200, "new": 200}
            for label, base in [("old", old_base), ("new", new_base)]:
                try:
                    resp = await page.goto(base + path, wait_until="domcontentloaded", timeout=15000)
                    entry[label] = resp.status if resp else 0
                except Exception:
                    entry[label] = 0
            statuses[path] = entry
            flag = " ** 404/ERROR **" if entry["old"] not in (200,) or entry["new"] not in (200,) else ""
            print(f"  {path}: old={entry['old']} new={entry['new']}{flag}")
        await ctx.close()
        await browser.close()
    return statuses


def badge(status: int) -> str:
    if status == 200:
        return f'<span class="badge ok">{status}</span>'
    elif status == 404:
        return f'<span class="badge err">404</span>'
    elif status == 0:
        return f'<span class="badge err">ERR</span>'
    return f'<span class="badge warn">{status}</span>'


def build_html(results, statuses, old_base, new_base, out_dir) -> str:
    now = datetime.now().strftime("%d %b %Y, %H:%M")
    total = len(results)
    changed_count = sum(1 for r in results if r["max_diff"] > 0.5)
    any_404 = {p for p, s in statuses.items() if s["old"] not in (200,) or s["new"] not in (200,)}
    unchanged_count = total - changed_count - len(any_404)

    rows = ""
    for r in sorted(results, key=lambda x: -x["max_diff"]):
        path = r["path"]
        slug = r["slug"]
        st = statuses.get(path, {"old": 200, "new": 200})
        is_404 = st["old"] not in (200,) or st["new"] not in (200,)

        if is_404:
            row_class, status_cell = "row-404", '<span class="status-404">404 / Error</span>'
        elif r["max_diff"] > 0.5:
            row_class, status_cell = "changed", '<span class="status-changed">Changed</span>'
        else:
            row_class, status_cell = "same", '<span class="status-same">Same</span>'

        ss_links = "".join(
            f'<a href="diff_{vp}_{slug}.png">Diff</a> &middot; <a href="old_{vp}_{slug}.png">Old</a> &middot; <a href="new_{vp}_{slug}.png">New</a><span class="ss-vp">{vp}</span><br>'
            for vp in ["desktop", "mobile"]
        )

        rows += f"""
        <tr class="{row_class}">
          <td>{badge(st['old'])}</td>
          <td class="url-cell"><a href="{old_base}{path}" target="_blank">{path}</a></td>
          <td>{badge(st['new'])}</td>
          <td class="url-cell"><a href="{new_base}{path}" target="_blank">{path}</a></td>
          <td>{status_cell}</td>
          <td class="diff-cell">
            <div class="diff-row"><span class="diff-vp">Desktop</span><span class="diff-bar-wrap"><span class="diff-bar" style="width:{min(r['desktop_diff'],100)}%"></span></span><span class="diff-num">{r['desktop_diff']}%</span></div>
            <div class="diff-row"><span class="diff-vp">Mobile</span><span class="diff-bar-wrap"><span class="diff-bar" style="width:{min(r['mobile_diff'],100)}%"></span></span><span class="diff-num">{r['mobile_diff']}%</span></div>
          </td>
          <td class="links-cell">{ss_links}</td>
        </tr>"""

    old_label = old_base.split("//")[-1].split(".")[0]
    new_label = new_base.split("//")[-1].split(".")[0]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Visual Regression: {old_label} vs {new_label}</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, "Helvetica Neue", Arial, sans-serif; background: #EFF2F9; color: #181818; min-height: 100vh; }}
    .header {{ background: #181818; padding: 0 40px; height: 72px; display: flex; align-items: center; justify-content: space-between; }}
    .header-left {{ display: flex; flex-direction: column; gap: 3px; }}
    .header-label {{ font-size: 10px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: #4E4E4E; }}
    .header-title {{ font-size: 16px; font-weight: 600; color: #fff; }}
    .header-meta {{ font-size: 11px; color: #4E4E4E; }}
    .content {{ padding: 32px 40px; }}
    .summary-row {{ display: flex; gap: 16px; margin-bottom: 28px; flex-wrap: wrap; }}
    .card {{ background: #fff; border-radius: 8px; padding: 18px 22px; min-width: 150px; border-left: 3px solid #D1D1D1; display: flex; align-items: center; gap: 16px; }}
    .card.accent  {{ border-left-color: #1E43FF; }}
    .card.warn    {{ border-left-color: #e67e22; }}
    .card.success {{ border-left-color: #27ae60; }}
    .card.danger  {{ border-left-color: #e74c3c; }}
    .card-icon {{ width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }}
    .card.accent  .card-icon {{ background: #eef1ff; color: #1E43FF; }}
    .card.warn    .card-icon {{ background: #fff5eb; color: #e67e22; }}
    .card.success .card-icon {{ background: #f0faf0; color: #27ae60; }}
    .card.danger  .card-icon {{ background: #fdecea; color: #e74c3c; }}
    .card-body {{ display: flex; flex-direction: column; gap: 2px; }}
    .card-num {{ font-size: 26px; font-weight: 700; color: #181818; line-height: 1; }}
    .card-label {{ font-size: 11px; color: #4E4E4E; text-transform: uppercase; letter-spacing: 0.06em; }}
    .table-wrap {{ background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }}
    table {{ border-collapse: collapse; width: 100%; table-layout: fixed; }}
    thead tr.group-row th {{ padding: 7px 16px 5px; font-size: 9px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; border-bottom: 1px solid #333; }}
    .col-group-prev  {{ background: #222; color: #aaa; border-right: 1px solid #333; }}
    .col-group-new   {{ background: #1a1a1a; color: #aaa; border-right: 1px solid #333; }}
    .col-group-result {{ background: #111; color: #aaa; }}
    thead tr.header-row th {{ padding: 8px 16px 10px; text-align: left; font-size: 10px; font-weight: 600; letter-spacing: 0.07em; text-transform: uppercase; color: #D1D1D1; background: #181818; }}
    th.sep, td.sep {{ border-right: 1px solid #2e2e2e; }}
    td {{ padding: 11px 16px; border-bottom: 1px solid #EFF2F9; font-size: 13px; vertical-align: middle; }}
    tr.changed:hover td {{ background: #f8f9ff; }}
    tr.same {{ opacity: 0.75; }}
    tr.same:hover td {{ background: #fafafa; opacity: 1; }}
    tr.row-404 td {{ background: #fff9f9; }}
    tr.row-404:hover td {{ background: #fff3f3; }}
    .url-cell {{ width: 26%; }}
    .url-cell a {{ color: #1E43FF; text-decoration: none; font-size: 12px; word-break: break-all; font-weight: 500; }}
    .url-cell a:hover {{ text-decoration: underline; }}
    .diff-cell {{ width: 18%; }}
    .diff-row {{ display: flex; align-items: center; gap: 6px; margin: 3px 0; }}
    .diff-vp {{ font-size: 10px; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; color: #4E4E4E; min-width: 46px; }}
    .diff-bar-wrap {{ flex: 1; height: 6px; background: #EFF2F9; border-radius: 3px; overflow: hidden; }}
    .diff-bar {{ height: 100%; background: #1E43FF; border-radius: 3px; display: block; }}
    tr.row-404 .diff-bar {{ background: #e74c3c; }}
    .diff-num {{ font-size: 11px; font-variant-numeric: tabular-nums; color: #4E4E4E; min-width: 36px; text-align: right; }}
    .badge {{ font-size: 11px; font-weight: 600; padding: 2px 7px; border-radius: 4px; display: inline-block; white-space: nowrap; }}
    .badge.ok   {{ background: #f0faf0; color: #27ae60; }}
    .badge.err  {{ background: #fdecea; color: #e74c3c; }}
    .badge.warn {{ background: #fff3e0; color: #e67e22; }}
    .status-changed {{ background: #fff3e0; color: #e67e22; font-size: 11px; font-weight: 700; padding: 3px 9px; border-radius: 4px; white-space: nowrap; }}
    .status-same    {{ background: #f0faf0; color: #27ae60; font-size: 11px; font-weight: 600; padding: 3px 9px; border-radius: 4px; }}
    .status-404     {{ background: #fdecea; color: #e74c3c; font-size: 11px; font-weight: 700; padding: 3px 9px; border-radius: 4px; white-space: nowrap; }}
    .links-cell {{ width: 10%; font-size: 11px; }}
    .links-cell a {{ color: #1E43FF; text-decoration: none; }}
    .links-cell a:hover {{ text-decoration: underline; }}
    .ss-vp {{ font-size: 9px; color: #4E4E4E; margin-left: 4px; text-transform: uppercase; letter-spacing: 0.06em; }}
    .footer {{ text-align: center; padding: 24px 40px; font-size: 11px; color: #4E4E4E; }}
  </style>
</head>
<body>
  <header class="header">
    <div class="header-left">
      <span class="header-label">Visual Regression Report</span>
      <span class="header-title">{old_label} (Previous) vs {new_label} (New)</span>
      <span class="header-meta">Generated {now} &nbsp;&middot;&nbsp; {total} pages &nbsp;&middot;&nbsp; Desktop 1440px + Mobile 375px</span>
    </div>
    {LOGO_SVG}
  </header>
  <div class="content">
    <div class="summary-row">
      <div class="card accent"><div class="card-icon">{ICON_GRID}</div><div class="card-body"><div class="card-num">{total}</div><div class="card-label">Pages Compared</div></div></div>
      <div class="card warn"><div class="card-icon">{ICON_DIFF}</div><div class="card-body"><div class="card-num">{changed_count}</div><div class="card-label">Pages Changed</div></div></div>
      <div class="card success"><div class="card-icon">{ICON_CHECK}</div><div class="card-body"><div class="card-num">{unchanged_count}</div><div class="card-label">Unchanged</div></div></div>
      <div class="card danger"><div class="card-icon">{ICON_WARNING}</div><div class="card-body"><div class="card-num">{len(any_404)}</div><div class="card-label">404 / Errors</div></div></div>
    </div>
    <div class="table-wrap">
      <table>
        <colgroup><col style="width:4%"><col style="width:26%"><col style="width:4%"><col style="width:26%"><col style="width:8%"><col style="width:22%"><col style="width:10%"></colgroup>
        <thead>
          <tr class="group-row">
            <th colspan="2" class="col-group-prev sep">Previous &mdash; {old_label}</th>
            <th colspan="2" class="col-group-new sep">New &mdash; {new_label}</th>
            <th colspan="3" class="col-group-result">Result</th>
          </tr>
          <tr class="header-row">
            <th>HTTP</th><th class="sep">Page URL</th>
            <th>HTTP</th><th class="sep">Page URL</th>
            <th>Status</th><th>Visual Diff</th><th>Screenshots</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
  </div>
  <div class="footer">combinate.me &nbsp;&mdash;&nbsp; Visual Regression Report &nbsp;&mdash;&nbsp; {now}</div>
</body>
</html>"""


async def main(old_base: str, new_base: str, out_dir: str):
    results_path = os.path.join(out_dir, "results.json")
    with open(results_path) as f:
        results = json.load(f)

    print(f"\nVerifying {len(results) * 2} diff values from saved screenshots...")
    mismatches = 0
    for r in results:
        for vp, key in [("desktop", "desktop_diff"), ("mobile", "mobile_diff")]:
            recomputed = recompute_diff(out_dir, r["slug"], vp)
            if recomputed is not None and abs(recomputed - r[key]) > 0.5:
                print(f"  [updated] {r['path']} {vp}: {r[key]}% -> {recomputed}%")
                r[key] = recomputed
                r["max_diff"] = max(r["desktop_diff"], r["mobile_diff"])
                mismatches += 1
    if mismatches == 0:
        print(f"  All values confirmed accurate.")
    else:
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)

    print(f"\nChecking HTTP status for {len(results)} pages...")
    statuses = await check_statuses([r["path"] for r in results], old_base, new_base)

    print("\nBuilding report...")
    html = build_html(results, statuses, old_base, new_base, out_dir)
    report_path = os.path.join(out_dir, "report.html")
    with open(report_path, "w") as f:
        f.write(html)

    any_404 = {p for p, s in statuses.items() if s["old"] not in (200,) or s["new"] not in (200,)}
    print(f"\nDone.")
    print(f"  404/error pages: {len(any_404)}")
    print(f"  Report: {report_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--old", required=True)
    parser.add_argument("--new", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    asyncio.run(main(args.old.rstrip("/"), getattr(args, "new").rstrip("/"), args.out))
