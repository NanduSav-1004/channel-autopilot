"""Logo and banner for the data channel, drawn in the same "Signal" theme as its videos (headless Chrome, see motion.py).
Usage: python scripts/make_data_brand.py "Plotline Data" "Every number has a story." """
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from autopilot.motion import STAGE, Browser

OUT = ROOT / "assets" / "brand_data"
# The mark: a line that climbs in steps, ending in a glowing dot. Points are in a 100 x 100 box.
MARK = [(14, 74), (32, 58), (46, 66), (64, 36), (78, 44), (88, 22)]

STYLE = """
<style>
@font-face { font-family: "Space Grotesk"; src: url("%(stage)s/fonts/SpaceGrotesk.ttf"); font-weight: 300 700; }
@font-face { font-family: "Inter"; src: url("%(stage)s/fonts/Inter.ttf"); font-weight: 100 900; }
html, body { margin: 0; background: #0b0d17; }
</style>"""

DEFS = """
<defs>
  <filter id="glow" x="-50%%" y="-50%%" width="200%%" height="200%%"><feGaussianBlur stdDeviation="%(blur)s" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <radialGradient id="bgA" cx="25%%" cy="20%%" r="70%%"><stop offset="0" stop-color="#39d2ff" stop-opacity=".30"/><stop offset="1" stop-color="#39d2ff" stop-opacity="0"/></radialGradient>
  <radialGradient id="bgB" cx="85%%" cy="85%%" r="60%%"><stop offset="0" stop-color="#ff5c7a" stop-opacity=".25"/><stop offset="1" stop-color="#ff5c7a" stop-opacity="0"/></radialGradient>
  <radialGradient id="bgC" cx="70%%" cy="10%%" r="45%%"><stop offset="0" stop-color="#d4ff3a" stop-opacity=".18"/><stop offset="1" stop-color="#d4ff3a" stop-opacity="0"/></radialGradient>
</defs>"""


def _bg(w: int, h: int, grid: int) -> str:
    lines = "".join(f'<line x1="{x}" x2="{x}" y1="0" y2="{h}"/>' for x in range(0, w + 1, grid))
    lines += "".join(f'<line y1="{y}" y2="{y}" x1="0" x2="{w}"/>' for y in range(0, h + 1, grid))
    return (f'<rect width="{w}" height="{h}" fill="#0b0d17"/><rect width="{w}" height="{h}" fill="url(#bgA)"/>'
            f'<rect width="{w}" height="{h}" fill="url(#bgB)"/><rect width="{w}" height="{h}" fill="url(#bgC)"/>'
            f'<g stroke="#2a3048" stroke-width="{max(1, grid // 60)}" opacity=".45">{lines}</g>')


def _mark(x: float, y: float, s: float, stroke: float) -> str:
    pts = [(x + px * s / 100, y + py * s / 100) for px, py in MARK]
    path = " ".join(f"{'M' if i == 0 else 'L'}{a:.1f},{b:.1f}" for i, (a, b) in enumerate(pts))
    ex, ey = pts[-1]
    return (f'<path d="{path}" fill="none" stroke="#d4ff3a" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)"/>'
            f'<circle cx="{ex}" cy="{ey}" r="{stroke * 2.6}" fill="none" stroke="#d4ff3a" stroke-width="{stroke * 0.45}" opacity=".55"/>'
            f'<circle cx="{ex}" cy="{ey}" r="{stroke * 1.25}" fill="#f5f3ee" filter="url(#glow)"/>')


def page(w: int, h: int, body: str, blur: float) -> str:
    return (f'<!doctype html><html><head><meta charset="utf-8">{STYLE % {"stage": STAGE.as_uri()}}</head><body>'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">{DEFS % {"blur": blur}}{body}</svg></body></html>')


def shoot(html: str, w: int, h: int, out: Path, browser: Browser) -> None:
    tmp = OUT / "_tmp.html"
    tmp.write_text(html)
    p = browser._b.new_page(viewport={"width": w, "height": h})
    p.goto(tmp.as_uri())
    p.evaluate("document.fonts.ready")
    p.wait_for_timeout(300)
    p.screenshot(path=str(out), type="png" if out.suffix == ".png" else "jpeg", **({} if out.suffix == ".png" else {"quality": 95}))
    p.close()
    tmp.unlink()


def main(name: str, tagline: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with Browser() as b:
        # Profile picture: YouTube shows it as a circle, so the mark sits well inside the middle.
        logo = _bg(800, 800, 100) + _mark(145, 150, 500, 36)
        shoot(page(800, 800, logo, 14), 800, 800, OUT / "logo.png", b)
        # Banner 2560 x 1440; everything that matters stays inside the 1546 x 423 middle (what phones show).
        W, H = 2560, 1440
        base, _, extra = name.partition(" ")            # "Plotline Data": "Plot" + lime "line", then a lighter "Data"
        accent = "line" if base.lower().endswith("line") else ""
        word = f'<tspan>{base[: len(base) - len(accent)]}</tspan><tspan fill="#d4ff3a">{accent}</tspan>'
        if extra:
            word += f'<tspan font-weight="300" fill="#f5f3ee"> {extra}</tspan>'
        body = _bg(W, H, 120)
        body += ('<path d="M0,980 C300,960 420,1010 640,900 S1000,860 1180,940 S1600,780 1900,700 S2350,560 2560,520" fill="none" '
                 'stroke="#d4ff3a" stroke-width="5" opacity=".35" filter="url(#glow)"/>')
        body += _mark(560, 530, 340, 22)
        body += (f'<text x="950" y="725" font-family="Space Grotesk" font-weight="700" font-size="150" fill="#f5f3ee" letter-spacing="-3">{word}</text>'
                 f'<text x="958" y="805" font-family="Inter" font-weight="500" font-size="54" fill="#8a8fa8">{tagline}</text>')
        shoot(page(W, H, body, 12), W, H, OUT / "banner.jpg", b)
    print("wrote", OUT / "logo.png", OUT / "banner.jpg")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
