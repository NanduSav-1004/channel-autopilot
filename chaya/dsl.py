"""Short constructors for storyboards: C(layers) is a 'compose' scene; the layer helpers take positions as 0..1 of the stage."""


def C(layers, bg="sky", **extra):
    return {"kind": "compose", "p": {"bg": bg, "layers": layers, **extra}}


def I(icon, x, y, s=2.5, **k):
    return {"t": "icon", "icon": icon, "x": x, "y": y, "s": s, **k}


def R(x, y, w, h, fill, **k):
    return {"t": "rect", "x": x, "y": y, "w": w, "h": h, "fill": fill, **k}


def O(x, y, r, fill, **k):
    return {"t": "circle", "x": x, "y": y, "r": r, "fill": fill, **k}


def T(ml, x=0.5, y=0.5, size=90, col="#2a1a10", **k):
    return {"t": "text", "ml": ml, "x": x, "y": y, "size": size, "col": col, **k}


def PT(kind, n, area, col, r=6, **k):
    return {"t": "particles", "kind": kind, "n": n, "area": area, "col": col, "r": r, **k}


def FL(x, y, to, col, n=12, r=8, **k):
    return {"t": "flow", "x": x, "y": y, "to": to, "col": col, "n": n, "r": r, **k}


def BOLT(x, y, to, atb, seed=1, **k):
    return {"t": "bolt", "x": x, "y": y, "to": to, "atb": atb, "seed": seed, **k}


def RINGS(x, y, col, **k):
    return {"t": "rings", "x": x, "y": y, "col": col, **k}


def SPIRAL(x, y, r, **k):
    return {"t": "spiral", "x": x, "y": y, "r": r, **k}


def LB(ml, en=None, col="#7b4a2b", w=330, dy=1.3, dx=0):
    return {"ml": ml, "en": en, "col": col, "w": w, "dy": dy, "dx": dx}


GROUND = lambda col="#2f7d4f", y=0.82: R(0, y, 1, 1 - y, col)
