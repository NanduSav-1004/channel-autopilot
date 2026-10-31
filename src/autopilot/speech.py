"""Numbers as they are SPOKEN. The offline voices (Kokoro, Piper) mangle digits: "1.2" comes out as "one, two" (no "point"), "1,325" as
"one ... three twenty-five" (the comma is a pause), "97.5%" without the point. So the text sent to the voice has its numbers written out
("one point two", "one thousand three hundred twenty-five"). The captions keep the digits: only the voice hears the words."""
import re

ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
TENS = ["_", "_", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
SCALES = [(10**12, "trillion"), (10**9, "billion"), (10**6, "million"), (10**3, "thousand")]


def _below_thousand(n: int) -> str:
    out = []
    if n >= 100:
        out.append(f"{ONES[n // 100]} hundred")
        n %= 100
    if n >= 20:
        out.append(TENS[n // 10] + (f"-{ONES[n % 10]}" if n % 10 else ""))
    elif n or not out:
        out.append(ONES[n])
    return " ".join(out)


def int_words(n: int) -> str:
    """1325 -> "one thousand three hundred twenty-five"."""
    if n < 0:
        return "minus " + int_words(-n)
    if n < 1000:
        return _below_thousand(n)
    parts = []
    for size, name in SCALES:
        if n >= size:
            parts.append(f"{_below_thousand(n // size)} {name}")
            n %= size
    if n:
        parts.append(_below_thousand(n))
    return " ".join(parts)


def year_words(y: int) -> str:
    """1905 -> "nineteen oh five", 1960 -> "nineteen sixty", 2023 -> "twenty twenty-three", 2005 -> "two thousand five"."""
    if 2000 <= y <= 2009:
        return "two thousand" + (f" {ONES[y - 2000]}" if y > 2000 else "")
    hi, lo = divmod(y, 100)
    if lo == 0:
        return f"{int_words(hi)} hundred"
    return f"{int_words(hi)} {'oh ' + ONES[lo] if lo < 10 else int_words(lo)}"


def _decade(y: int) -> str:
    """1960 -> "nineteen sixties", 1900 -> "nineteen hundreds", 2000 -> "two thousands"."""
    if y % 100 == 0:
        return ("two thousands" if y == 2000 else f"{int_words(y // 100)} hundreds")
    tens = TENS[(y % 100) // 10]
    return f"{int_words(y // 100)} {tens[:-1]}ies" if tens.endswith("y") else f"{int_words(y // 100)} {tens}s"


NUMBER = re.compile(r"(?<![\w.])([$£€])?([+\-−])?(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d+))?(%)?(s)?(\s+(?:thousand|million|billion|trillion)\b)?(?![\w])")
CURRENCY = {"$": ("dollar", "cent"), "£": ("pound", "penny"), "€": ("euro", "cent")}


def _sub(m: re.Match) -> str:
    cur, sign, whole, frac, pct, plural, scale = m.groups()
    digits = whole.replace(",", "")
    n = int(digits)
    words = {"-": "minus ", "−": "minus ", "+": "plus "}.get(sign or "", "")
    if not frac and not cur and not pct and not scale and "," not in whole and len(digits) == 4 and 1100 <= n <= 2099 and not sign:
        return _decade(n) if plural else year_words(n)
    if plural:                                            # "3s" is not a number the voice should invent a word for
        return m.group(0)
    if frac:
        spoken = f"{int_words(n)} point {' '.join(ONES[int(c)] for c in frac)}"
    elif cur and not scale:
        unit, sub = CURRENCY[cur]
        return f"{words}{int_words(n)} {unit}{'' if n == 1 else 's'}"
    else:
        spoken = int_words(n)
    if cur and frac and not scale and len(frac) == 2:       # $6.23 -> six dollars and twenty-three cents
        unit, sub = CURRENCY[cur]
        c = int(frac)
        return f"{words}{int_words(n)} {unit}{'' if n == 1 else 's'} and {int_words(c)} {sub}{'' if c == 1 else 's' if sub != 'penny' else 'pence'}"
    out = words + spoken + (scale or "")
    if cur:
        out += f" {CURRENCY[cur][0]}s"
    if pct:
        out += " percent"
    return out


def speech_text(text: str) -> str:
    """The text as the voice should say it (numbers, percentages and money written out)."""
    return NUMBER.sub(_sub, text)
