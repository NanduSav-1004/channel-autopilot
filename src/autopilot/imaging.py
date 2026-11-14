"""Picture helpers shared by the renderers.

`Image.convert("RGB")` on a picture with transparency keeps whatever colour sits UNDER the transparent pixels, which is usually black. Wikimedia
diagrams (black lines on a transparent background) therefore came out as black on black: on 13-14 Nov 2026 a Moon video had dozens of 3.5 s
clips that were simply black. `to_rgb` puts such pictures on a white background (or a dark one when their content is light)."""
import numpy as np
from PIL import Image


def has_alpha(img: Image.Image) -> bool:
    return img.mode in ("RGBA", "LA", "PA") or (img.mode == "P" and "transparency" in img.info)


def to_rgb(img: Image.Image) -> Image.Image:
    if not has_alpha(img):
        return img.convert("RGB")
    rgba = img.convert("RGBA")
    alpha = rgba.getchannel("A")
    # the content is the opaque part: if it is mostly light, a white background would hide it, so use a dark one
    lum = np.asarray(rgba.convert("L").resize((64, 64)), dtype=float)
    opaque = lum[np.asarray(alpha.resize((64, 64))) > 128]
    light = opaque.size > 0 and float(opaque.mean()) > 170
    bg = Image.new("RGB", rgba.size, (24, 28, 40) if light else (255, 255, 255))
    bg.paste(rgba, mask=alpha)
    return bg


def open_rgb(path) -> Image.Image:
    with Image.open(path) as img:
        img.load()
        return to_rgb(img)
