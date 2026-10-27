"""On-screen callouts: when the narrator says a key number ("319 terabits per second", "1911", "-269 °C") it pops up at the
top of the screen, so the viewer SEES the figure while hearing it. Found in the narration itself (no model needed), timed from
the word times already used for the captions."""
import re

UNITS = {
    "km", "kilometer", "kilometers", "kilometre", "kilometres", "m", "meter", "meters", "metre", "metres", "cm", "mm", "nm",
    "micrometers", "nanometers", "miles", "mile", "kg", "kilograms", "tonnes", "tons", "ton", "g", "grams", "percent", "%",
    "°c", "°f", "°", "k", "kelvin", "degrees", "volts", "v", "kv", "amps", "a", "watts", "w", "kw", "mw", "gw", "tw", "hz",
    "khz", "mhz", "ghz", "thz", "ev", "mev", "gev", "tev", "joules", "j", "pascals", "pa", "bar", "atm", "seconds", "second",
    "s", "ms", "minutes", "hours", "days", "years", "year", "months", "billion", "million", "thousand", "trillion", "bits",
    "bytes", "kb", "mb", "gb", "tb", "terabits", "gigabits", "megabits", "gigabytes", "terabytes", "megabytes", "per",
    "light-years", "tb/s", "gb/s", "mb/s", "m/s", "km/h", "mph", "times", "x", "fold", "cores", "transistors", "photons",
    "electrons", "atoms", "people", "households", "stars", "planets",
}
MAX_CHARS = 26
_NUM = re.compile(r"^[\(\[“\"']*([\-–−‑]?\d[\d,.]*)")
_UNIT_STRIP = re.compile(r"^[\(\[“\"']+|[\)\]”\"'.,;:!?]+$")


def _unit(word: str) -> str | None:
    w = _UNIT_STRIP.sub("", word)
    return w if w.lower() in UNITS else None


def callout_for(words: list[dict], i: int) -> str | None:
    """The text to show for the number at words[i]: the figure plus up to two unit words, or a bare year."""
    m = _NUM.match(words[i]["w"])
    if not m:
        return None
    figure = m.group(1).rstrip(",.").replace("‑", "-")
    rest = words[i]["w"][m.end():]
    parts = [figure]
    if rest and _unit(rest):                   # "35K", "4.2kelvin" written together, or "°C" attached
        parts[0] += _UNIT_STRIP.sub("", rest)
    else:
        j = i + 1
        while j < len(words) and len(parts) < 4:      # "319 terabits per second", "5 billion kilometers"
            u = _unit(words[j]["w"])
            if not u or (u.lower() == "per" and (j + 1 >= len(words) or not _unit(words[j + 1]["w"]))):
                break
            parts.append(u)
            if words[j]["w"].rstrip()[-1:] in ".,;:!?":
                break
            if u.lower() != "per" and sum(1 for x in parts[1:] if x.lower() != "per") >= 2:
                break                                  # figure + two unit words is plenty
            j += 1
    bare = len(parts) == 1 and parts[0] == figure
    digits = re.sub(r"\D", "", figure)
    if bare and not (len(digits) == 4 and "." not in figure and 1000 <= int(digits) <= 2100):
        return None                            # a bare number that is not a year says little on its own
    text = " ".join(parts)
    return text if len(text) <= MAX_CHARS else None


def find_callouts(timings: list[dict], min_gap: float = 7.0, hold: float = 2.8) -> list[dict]:
    """[{start, end, text}] in time order, never closer together than `min_gap` seconds."""
    out: list[dict] = []
    for sec in timings:
        for sent in sec["sentences"]:
            words = sent.get("words") or []
            for i, w in enumerate(words):
                text = callout_for(words, i)
                if not text:
                    continue
                start = max(sent["start"], w["s"] - 0.05)
                if out and start - out[-1]["start"] < min_gap:
                    continue
                out.append({"start": round(start, 2), "end": round(start + hold, 2), "text": text})
    return out
