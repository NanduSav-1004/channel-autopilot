"""Science Chaya brand pictures (profile picture 800x800, banner 2560x1440), drawn as SVG/HTML and captured by headless Chrome (so Malayalam shapes right).
usage: python assets/brand_chaya/make_brand.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from playwright.sync_api import sync_playwright

from autopilot import motion

HERE = Path(__file__).resolve().parent
CREAM, BROWN, DARK, AMBER, LEAF, SEA = "#f7ecd9", "#7b4a2b", "#4a2a17", "#e8a33d", "#2f7d4f", "#1f8aa8"

GLASS = f'''
<g>
  <path d="M -70 -80 L 70 -80 L 54 84 Q 52 100 36 100 L -36 100 Q -52 100 -54 84 Z" fill="{AMBER}"/>
  <path d="M -70 -80 L 70 -80 L 66 -34 L -66 -34 Z" fill="#fff3dc" opacity="0.9"/>
  <path d="M -70 -80 L 70 -80 L 54 84 Q 52 100 36 100 L -36 100 Q -52 100 -54 84 Z" fill="none" stroke="{DARK}" stroke-width="7" stroke-linejoin="round"/>
  <path d="M -32 -10 Q -34 40 -26 80" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" opacity="0.5"/>
  <path d="M -22 -110 Q -42 -150 -20 -185 Q -2 -212 -22 -240" fill="none" stroke="{BROWN}" stroke-width="9" stroke-linecap="round" opacity="0.8"/>
  <path d="M 8 -110 Q -12 -150 10 -185 Q 28 -212 8 -240" fill="none" stroke="{BROWN}" stroke-width="9" stroke-linecap="round" opacity="0.8"/>
  <path d="M 38 -110 Q 18 -150 40 -185 Q 58 -212 38 -240" fill="none" stroke="{BROWN}" stroke-width="9" stroke-linecap="round" opacity="0.8"/>
</g>'''
ORBIT = f'''
<g fill="none" stroke="{LEAF}" stroke-width="9" opacity="0.9">
  <ellipse rx="230" ry="82" transform="rotate(-24)"/>
  <ellipse rx="230" ry="82" transform="rotate(36)"/>
</g>
<circle cx="-200" cy="-120" r="17" fill="{SEA}"/><circle cx="195" cy="132" r="17" fill="{SEA}"/><circle cx="205" cy="-150" r="14" fill="{AMBER}"/>'''

AVATAR = f'''<html><body style="margin:0"><svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" viewBox="-400 -400 800 800">
<rect x="-400" y="-400" width="800" height="800" fill="{CREAM}"/>
<circle r="372" fill="{BROWN}"/><circle r="372" fill="none" stroke="{DARK}" stroke-width="10"/>
<g transform="scale(0.9) translate(0,30)">{ORBIT}</g>
<g transform="translate(0,40) scale(1.25)">{GLASS.replace(f'stroke="{BROWN}"', f'stroke="{CREAM}"')}</g></svg></body></html>'''

def banner() -> str:
    clouds = "".join(f'<g transform="translate({x},{y}) scale({s})" opacity="0.85"><circle r="40" fill="#fff"/><circle cx="46" cy="-16" r="52" fill="#fff"/><circle cx="104" cy="2" r="42" fill="#fff"/></g>' for x, y, s in [(180, 200, 1.4), (700, 140, 0.9), (2380, 220, 1.2), (1500, 130, 0.8)])
    rain = "".join(f'<line x1="{x}" y1="{y}" x2="{x - 12}" y2="{y + 42}" stroke="{SEA}" stroke-width="7" stroke-linecap="round" opacity="0.55"/>' for x, y in [(2020, 700), (2060, 750), (2100, 710), (2140, 770), (2180, 720), (2220, 780)])
    return f'''<html><body style="margin:0;background:{CREAM}"><svg xmlns="http://www.w3.org/2000/svg" width="2560" height="1440" viewBox="0 0 2560 1440">
<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d3ecf6"/><stop offset="1" stop-color="{CREAM}"/></linearGradient></defs>
<rect width="2560" height="1440" fill="url(#sky)"/>
{clouds}{rain}
<path d="M 0 1180 Q 640 1120 1280 1180 T 2560 1180 L 2560 1440 L 0 1440 Z" fill="{SEA}" opacity="0.9"/>
<path d="M 0 1250 Q 640 1190 1280 1250 T 2560 1250 L 2560 1440 L 0 1440 Z" fill="#146a85"/>
<path d="M 1500 1190 Q 1700 1010 1860 1020 Q 1980 880 2080 900 Q 2200 800 2320 940 Q 2460 1010 2560 1190 Z" fill="#8fc4a4" opacity="0.8"/>
<path d="M 1760 1190 L 2000 900 Q 2090 760 2150 720 Q 2230 800 2290 900 L 2560 1190 Z" fill="{LEAF}"/>
<path d="M 2150 720 Q 2230 800 2290 900 L 2560 1190 L 2400 1190 Q 2300 1000 2150 720 Z" fill="#c9a35e" opacity="0.85"/>
{"".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#1f6a41"/>' for x, y, r in [(1850,1110,26),(1910,1060,24),(1960,1000,22),(2010,945,20),(1800,1150,28),(2060,890,18)])}
<g transform="translate(2000,560)"><circle r="62" fill="#fff"/><circle cx="64" cy="-22" r="76" fill="#fff"/><circle cx="140" cy="2" r="60" fill="#fff"/></g>
<g transform="translate(330,800) scale(1.7)">{GLASS}</g>
<text x="1290" y="700" text-anchor="middle" font-family="Noto Sans Malayalam" font-weight="800" font-size="168" fill="{BROWN}">സയൻസ് ചായ</text>
<text x="1290" y="790" text-anchor="middle" font-family="Space Grotesk, Inter, sans-serif" font-weight="700" font-size="58" letter-spacing="22" fill="{DARK}">SCIENCE CHAYA</text>
<text x="1290" y="880" text-anchor="middle" font-family="Noto Sans Malayalam" font-weight="600" font-size="50" fill="{DARK}" opacity="0.85">ശാസ്ത്രം, ഒരു ചായ പോലെ ലളിതം</text>
</svg></body></html>'''

with sync_playwright() as p:
    exe = motion._chrome()
    b = p.chromium.launch(executable_path=exe, args=["--force-color-profile=srgb"]) if exe else p.chromium.launch()
    for name, html, w, h in (("logo.png", AVATAR, 800, 800), ("banner.png", banner(), 2560, 1440)):
        page = b.new_page(viewport={"width": w, "height": h})
        page.set_content(html)
        page.wait_for_timeout(600)
        page.screenshot(path=str(HERE / name))
    b.close()
from PIL import Image

Image.open(HERE / "banner.png").convert("RGB").save(HERE / "banner.jpg", quality=92)
print("done")
