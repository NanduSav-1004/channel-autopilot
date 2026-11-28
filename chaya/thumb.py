"""Science Chaya long-video thumbnails (1280x720): a drawn poster, not a video frame.
Deep chai-brown with a sunburst, a big hero picture from the video's own icon set on the right, two lines of huge Malayalam on the left
(white, then the hook word in yellow) with a thick dark outline, a small English line, and a curiosity badge. Text is fitted by measuring
in the page, so nothing can overlap or run off the picture.
usage: python chaya/thumb.py <out folder>   (writes <id>_thumb_new.png for every long video in ART)"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
from autopilot import motion

MOTION = ROOT / "assets" / "motion"

# id -> two Malayalam lines (white, yellow), English line, badge text, hero icons [(icon, x, y, size, rotation)] in the 560x640 art box
ART = {
    "electricity_long": ("ഡാം മുതൽ", "ബൾബ് വരെ", "HOW ELECTRICITY REACHES YOU", "?", [("pylon", 250, 380, 380, 0), ("bulb", 110, 190, 190, -10), ("bolt", 440, 250, 170, 12)]),
    "alerts_long": ("ഓറഞ്ച് അലർട്ട്", "എന്നാൽ?", "WEATHER ALERTS EXPLAINED", "!", [("cloudDark", 290, 200, 330, 0), ("drop", 140, 440, 130, -8), ("drop", 300, 500, 150, 6), ("drop", 450, 430, 120, 10), ("bolt", 400, 330, 140, 8)]),
    "monsoon_long": ("മഴയ്ക്ക്", "തീയതി!", "HOW THE MONSOON ARRIVES", "?", [("cloudDark", 270, 190, 320, 0), ("drop", 140, 420, 150, -8), ("drop", 330, 470, 170, 6), ("mountain", 250, 540, 200, 0)]),
    "lightning_long": ("മിന്നൽ", "എങ്ങനെ?", "THE SCIENCE OF LIGHTNING", "?", [("cloudDark", 280, 170, 340, 0), ("bolt", 290, 440, 330, 6)]),
    "tea_long": ("ചായയുടെ", "ശാസ്ത്രം", "THE SCIENCE OF TEA", "?", [("cup", 280, 330, 330, 0), ("drop", 120, 120, 110, -12), ("leaf", 450, 130, 140, 14)]),
    "kitchen_long": ("അടുക്കളയിലെ", "ശാസ്ത്രം", "KITCHEN SCIENCE", "?", [("cooker", 260, 340, 330, 0), ("onion", 450, 160, 160, 10), ("salt", 110, 150, 140, -10)]),
    "elephants_long": ("ആന കാലുകൊണ്ട്", "കേൾക്കുമോ?", "ELEPHANT SCIENCE", "!", [("elephant", 280, 350, 400, 0), ("moon", 450, 90, 110, 0)]),
    "backwaters_long": ("കായലും", "ചാകരയും", "TIDES AND CHAKARA", "?", [("boat", 280, 350, 360, 0), ("coconut", 110, 160, 130, -10), ("drop", 450, 160, 130, 10)]),
    "thumba_long": ("പള്ളിമുറ്റത്ത് നിന്ന്", "ബഹിരാകാശത്തേക്ക്", "THE STORY OF THUMBA", "!", [("rocket", 300, 300, 400, 20), ("church", 140, 480, 220, 0)]),
    "memories_long": ("ആ ഓർമ്മകളുടെ", "ശാസ്ത്രം", "THE SCIENCE OF CHILDHOOD", "?", [("marble", 150, 200, 190, 0), ("cassette", 330, 310, 270, -8), ("bicycle", 300, 500, 250, 0)]),
    "landslide_long": ("ഉരുൾപൊട്ടൽ", "എങ്ങനെ?", "HOW LANDSLIDES HAPPEN", "?", [("mountain", 270, 400, 380, 0), ("cloudDark", 250, 150, 300, 0), ("drop", 130, 320, 120, -8), ("drop", 440, 300, 130, 8)]),
    "chandrayaan_long": ("ചന്ദ്രനിൽ", "ഇറങ്ങിയത് എങ്ങനെ?", "CHANDRAYAAN-3 LANDING", "!", [("rocket", 290, 340, 430, 20), ("satellite", 120, 150, 170, -15)]),
    "fever_long": ("പനി വരുന്നത്", "എന്തിന്?", "WHY WE GET FEVER", "?", [("thermo", 280, 340, 420, 0), ("drop", 130, 200, 130, -10), ("drop", 440, 480, 120, 10)]),
    "pepper_long": ("കറുത്ത", "പൊന്ന്!", "THE SCIENCE OF PEPPER", "!", [("leaf", 220, 330, 340, -15), ("boat", 330, 520, 280, 0), ("sun", 450, 130, 140, 0)]),
    "ghats_long": ("പശ്ചിമഘട്ടത്തിന്റെ", "രഹസ്യം", "WESTERN GHATS SECRET", "?", [("mountain", 270, 400, 380, 0), ("tree", 110, 480, 190, 0), ("elephant", 430, 520, 220, 0), ("leaf", 300, 130, 130, 15)]),
    "phonecall_long": ("ഫോൺ കോൾ", "എങ്ങനെ?", "HOW A PHONE CALL TRAVELS", "?", [("phone", 300, 380, 420, 8), ("satellite", 150, 130, 200, -10), ("pylon", 450, 190, 200, 0)]),
    "madhava_long": ("യൂറോപ്പിന് മുൻപ്", "250 വർഷം!", "MADHAVA OF KERALA", "π", [("pi", 280, 340, 420, 0), ("person", 120, 520, 190, 0), ("leaf", 450, 520, 150, 15)]),
    "waves_long": ("തിരമാലയുടെ", "ശക്തി!", "THE POWER OF WAVES", "!", [("boat", 270, 420, 400, -6), ("cloudDark", 250, 150, 280, 0), ("drop", 450, 300, 140, 10)]),
}

PAGE = """<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{m}/theme.css">
<script src="{m}/vendor/d3.min.js"></script><script src="{m}/motion.js"></script><script src="{m}/chaya.js"></script>
<style>
html,body{{margin:0;width:1280px;height:720px;overflow:hidden;background:#2b150a;font-family:'Noto Sans Malayalam','Noto Sans',sans-serif}}
#bg{{position:absolute;inset:0}}
#brand{{position:absolute;left:40px;top:30px;background:#fff7e8;color:#7b4a2b;font-weight:800;font-size:38px;line-height:1.5;padding:0 24px;border-radius:30px;box-shadow:0 6px 0 #c45a2a}}
#text{{position:absolute;left:40px;top:128px;width:650px;height:440px;display:flex;flex-direction:column;justify-content:center}}
.l{{white-space:nowrap;font-weight:900;line-height:1.28;-webkit-text-stroke:14px #2b150a;paint-order:stroke fill;text-shadow:0 8px 0 #2b150a}}
#l1{{color:#fff}}#l2{{color:#ffd23f}}
#en{{position:absolute;left:40px;bottom:36px;background:#ffd23f;color:#2b150a;font-weight:900;font-size:34px;letter-spacing:4px;padding:6px 26px;border-radius:12px;box-shadow:0 6px 0 #2b150a;transform:rotate(-1.5deg)}}
#art{{position:absolute;left:720px;top:60px;width:560px;height:620px;overflow:visible;filter:drop-shadow(5px 0 0 #fff) drop-shadow(-5px 0 0 #fff) drop-shadow(0 5px 0 #fff) drop-shadow(0 -5px 0 #fff) drop-shadow(0 14px 14px rgba(0,0,0,.5))}}
#badge{{position:absolute;left:1086px;top:30px;width:130px;height:130px;border-radius:50%;background:#e23b2e;color:#fff;font-weight:900;font-size:104px;line-height:1.1;text-align:center;border:8px solid #fff;box-shadow:0 8px 0 #2b150a;transform:rotate(10deg)}}
</style></head><body>
<svg id="bg" width="1280" height="720"></svg><div id="brand">സയൻസ് ചായ</div>
<div id="text"><div class="l" id="l1">{l1}</div><div class="l" id="l2">{l2}</div></div>
<div id="en">{en}</div><svg id="art" width="560" height="640"></svg><div id="badge">{badge}</div>
<script>
const d3=window.d3, bg=d3.select('#bg');
const defs=bg.append('defs');
const rg=defs.append('radialGradient').attr('id','glow').attr('cx','78%').attr('cy','50%').attr('r','75%');
rg.append('stop').attr('offset','0').attr('stop-color','#ff9d2e');rg.append('stop').attr('offset','.55').attr('stop-color','#c4501f');rg.append('stop').attr('offset','1').attr('stop-color','#3a1a0b');
bg.append('rect').attr('width',1280).attr('height',720).attr('fill','url(#glow)');
const cx=1000, cy=380; // sunburst behind the picture
for(let i=0;i<24;i++){{const a0=i*Math.PI/12, a1=a0+Math.PI/24;bg.append('path').attr('d',`M${{cx}} ${{cy}} L${{cx+1400*Math.cos(a0)}} ${{cy+1400*Math.sin(a0)}} L${{cx+1400*Math.cos(a1)}} ${{cy+1400*Math.sin(a1)}} Z`).attr('fill','#ffe29a').attr('opacity',.13);}}
bg.append('circle').attr('cx',cx).attr('cy',cy).attr('r',255).attr('fill','#ffe9b8').attr('opacity',.28);
bg.append('circle').attr('cx',cx).attr('cy',cy).attr('r',255).attr('fill','none').attr('stroke','#fff7e8').attr('stroke-width',8).attr('opacity',.6);
const art=d3.select('#art');
for(const [n,x,y,s,r] of {icons}){{
  const g=window.MOTION.chayaIcon(art,n,x,y,s/100*100);
  g.attr('transform',`translate(${{x}},${{y}}) rotate(${{r}}) scale(${{s/100}})`);
}}
// fit each line: shrink the font until both lines fit the box
let fs=170; const box=document.getElementById('text'), ls=[...document.querySelectorAll('.l')];
for(;fs>40;fs-=2){{ls.forEach(l=>l.style.fontSize=fs+'px');if(ls.every(l=>l.scrollWidth<=box.clientWidth)&&box.scrollHeight<=box.clientHeight&&ls.every(l=>l.getClientRects().length&&l.offsetHeight<fs*2.7))break;}}
window.READY=true;
</script></body></html>"""


def render(vid: str, out_png: Path) -> Path:
    l1, l2, en, badge, icons = ART[vid]
    html = out_png.with_suffix(".html")
    html.write_text(PAGE.format(m=MOTION.as_uri(), l1=l1, l2=l2, en=en, badge=badge, icons=json.dumps(icons)))
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=motion._chrome(), args=["--allow-file-access-from-files"]) if motion._chrome() else p.chromium.launch(args=["--allow-file-access-from-files"])
        pg = b.new_page(viewport={"width": 1280, "height": 720})
        pg.goto(html.as_uri())
        pg.wait_for_function("window.READY === true", timeout=15000)
        pg.wait_for_timeout(400)
        pg.screenshot(path=str(out_png))
        b.close()
    html.unlink()
    return out_png


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for vid in (sys.argv[2:] or ART):
        print(render(vid, out / f"{vid}_thumb_new.png"))
