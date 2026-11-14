from PIL import Image, ImageDraw

from autopilot import imaging, render


def diagram(line=(0, 0, 0, 255)):
    img = Image.new("RGBA", (400, 300), (0, 0, 0, 0))                         # a Wikimedia-style diagram: lines on a transparent background
    ImageDraw.Draw(img).line([(20, 20), (380, 280)], fill=line, width=12)
    return img


def test_transparent_diagrams_are_put_on_a_background_that_shows_their_lines():
    flat = imaging.to_rgb(diagram())
    assert flat.mode == "RGB" and flat.getpixel((5, 290)) == (255, 255, 255) and flat.getpixel((200, 150)) == (0, 0, 0)
    old = diagram().convert("RGB")
    assert old.getpixel((5, 290)) == (0, 0, 0) and old.getpixel((200, 150)) == (0, 0, 0)          # what used to happen: black on black
    light = imaging.to_rgb(diagram((255, 255, 255, 255)))                                          # white lines: a dark background keeps them visible
    assert light.getpixel((5, 290)) != (255, 255, 255) and light.getpixel((200, 150)) == (255, 255, 255)
    p = Image.new("P", (10, 10))
    assert imaging.to_rgb(p).mode == "RGB" and imaging.to_rgb(Image.new("RGB", (4, 4), (9, 9, 9))).getpixel((1, 1)) == (9, 9, 9)


def test_the_renderers_prepare_a_transparent_diagram_without_turning_it_black(tmp_path):
    src, dst = tmp_path / "d.png", tmp_path / "out.jpg"
    diagram().save(src)
    render._prep_image(src, dst)
    import numpy as np

    mean = float(np.asarray(Image.open(dst).convert("L")).mean())
    assert mean > 150                                                                                # mostly white background, not black
