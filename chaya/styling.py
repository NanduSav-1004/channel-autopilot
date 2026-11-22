"""The look of the first beat: two people react to the topic, with a big floating topic icon. Applied to every video before its scenes are planned,
so the storyboards in content_*.py stay about the facts and the people are decided here."""
import copy

from chaya.dsl import GROUND, PT, C, I

# video id -> (topic icon, background, (who, mood, prop) left, (who, mood, prop) right)
HOOKS = {
    "petrichor_s": ("drop", "dusk", ("man", "wow", None), ("kid", "smile", None)),
    "alerts_long": ("cloudDark", "storm", ("man", "wow", None), ("woman", "think", None)),
    "goli_s": ("bottle", "dusk", ("kid", "wow", None), ("man", "smile", "bottle")),
    "firefly_s": ("firefly", "night", ("kid", "wow", None), ("woman", "smile", None)),
    "lightning_long": ("bolt", "storm", ("woman", "wow", None), ("kid", "wow", None)),
    "chenda_s": ("chenda", "dusk", ("man", "point", None), ("shopkeeper", "smile", None)),
    "banana_s": ("banana", "dusk", ("woman", "think", None), ("kid", "wow", None)),
    "memories_long": ("bulb", "dusk", ("man", "smile", None), ("woman", "smile", None)),
    "zeroshadow_s": ("sun", "sky", ("student", "point", None), ("kid", "wow", None)),
    "thumba_long": ("rocket", "night", ("man", "point", None), ("student", "wow", None)),
    "tea_long": ("cup", "dusk", ("woman", "smile", "cup"), ("man", "smile", None)),
    "idli_s": ("bowl", "dusk", ("woman", "think", None), ("kid", "wow", None)),
    "curd_s": ("bowl", "dusk", ("woman", "smile", None), ("kid", "think", None)),
    "kitchen_long": ("cooker", "dusk", ("woman", "point", None), ("man", "wow", None)),
    "onion_s": ("onion", "dusk", ("man", "wow", None), ("woman", "smile", None)),
    "coconutoil_s": ("bottle", "dusk", ("woman", "think", None), ("man", "wow", None)),
    "cooker_s": ("cooker", "dusk", ("woman", "point", None), ("kid", "wow", None)),
    "backwaters_long": ("boat", "sky", ("man", "smile", None), ("shopkeeper", "point", None)),
    "fan_s": ("fan", "sky", ("man", "wow", None), ("woman", "smile", None)),
    "snakeboat_s": ("boat", "sky", ("man", "point", None), ("kid", "wow", None)),
    "elephants_long": ("elephant", "sky", ("kid", "wow", None), ("woman", "smile", None)),
    "electricity_long": ("bulb", "dusk", ("woman", "smile", None), ("man", "wow", None)),
    "electricity_s1": ("meter", "dusk", ("man", "wow", None), ("woman", "think", None)),
    "electricity_s2": ("dam", "dusk", ("student", "point", None), ("kid", "wow", None)),
    "electricity_s3": ("bird", "sky", ("kid", "wow", None), ("man", "think", None)),
    "monsoon_s3": ("cup", "dusk", ("woman", "smile", "cup"), ("kid", "wow", None)),
    "tendercoconut_s": ("coconut", "dusk", ("man", "smile", None), ("kid", "wow", None)),
}


def hook_scene(vid: str, wide: bool) -> dict | None:
    if vid not in HOOKS:
        return None
    icon, bg, left, right = HOOKS[vid]
    xl, xr, y, s, iy, isz = (0.2, 0.8, 0.36, 1.9, 0.22, 4.2) if wide else (0.27, 0.73, 0.52, 1.75, 0.2, 4.4)
    layers = [GROUND({"night": "#12301f", "storm": "#2f4a36"}.get(bg, "#3f8f4f"), 0.86)]
    if bg == "storm":
        layers.append(PT("rain", 45, [0.05, 0.1, 0.95, 0.86], "#a8d4f0", 5))
    layers.append(I(icon, 0.5, iy if not wide else 0.4, isz, anim="float", glow="#ffe27a" if bg in ("night", "storm") else None))
    for (who, mood, prop), x in ((left, xl), (right, xr)):
        layers.append({"t": "char", "who": who, "mood": mood, "x": x, "y": y, "s": s, **({"hold": prop} if prop else {})})
    return C(layers, bg=bg)


def apply(video: dict) -> dict:
    """A copy of the video whose first beat shows the hook scene (the first beat's own scene is replaced)."""
    scene = hook_scene(video["id"], video["orient"] == "wide")
    if not scene:
        return video
    out = copy.deepcopy(video)
    out["beats"][0]["scene"] = scene
    return out
