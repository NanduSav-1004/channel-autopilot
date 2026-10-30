"""Open data for the Plotline channel: the catalogue (config/plotline_catalog.yaml), downloads from FRED and Our World in
Data (no API keys needed), and the FACTS a script may quote. Every number in a Plotline video comes from `facts()`, never
from a language model."""
import csv
import io
import time
import urllib.request
from datetime import date
from pathlib import Path

import yaml

CATALOG = Path(__file__).resolve().parents[2] / "config" / "plotline_catalog.yaml"
CACHE = Path("work/data")
STATES = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
STATE_NAMES = dict(zip(STATES, [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Washington, D.C.", "Florida",
    "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
    "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
    "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming"], strict=True))
SOURCES = {"fred": "FRED, Federal Reserve Bank of St. Louis", "owid": "Our World in Data"}
UA = {"User-Agent": "PlotlineData/1.0 (YouTube data explainers)"}


def catalog() -> dict:
    return yaml.safe_load(CATALOG.read_text())


def _get(url: str, tries: int = 3) -> str:
    headers = UA if "ourworldindata" in url else {}     # FRED refuses some custom user agents; its default one works
    for attempt in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60).read().decode("utf-8")
        except OSError:
            if attempt == tries - 1:
                raise
            time.sleep(3 * (attempt + 1))
    raise AssertionError


def _cached(name: str, url: str) -> str:
    path = CACHE / f"{date.today():%Y%m%d}-{name}.csv"   # one download per series per day
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_get(url))
    return path.read_text()


def fred_raw(series_id: str) -> list[tuple[str, float]]:
    rows = list(csv.reader(io.StringIO(_cached(series_id, f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"))))
    return [(r[0], float(r[1])) for r in rows[1:] if len(r) > 1 and r[1] not in ("", ".")]


def monthly(points: list[tuple[str, float]]) -> list[tuple[str, float]]:
    """Daily or weekly data averaged to months (a chart cannot show 10,000 points, and months read well)."""
    if len(points) < 2 or (date.fromisoformat(points[1][0]) - date.fromisoformat(points[0][0])).days >= 28:
        return points
    out: dict[str, list[float]] = {}
    for d, v in points:
        out.setdefault(d[:7] + "-01", []).append(v)
    return [(k, sum(v) / len(v)) for k, v in out.items()]


ORIGINS = [(("APU", "CPI", "CUSR", "UNRATE", "PAYEMS", "MANEMP", "US", "CIVPART", "JTS", "AHETPI", "LES"), "U.S. Bureau of Labor Statistics"),
           (("MSPUS", "HOUST", "RSAFS", "RSNSR", "ECOMPCTSA", "MEHOINUS", "POPTHM", "RRVR", "MSACSR", "TOTALSA"), "U.S. Census Bureau"),
           (("PSAVERT",), "U.S. Bureau of Economic Analysis"), (("GFDEBTN", "FYFSD"), "U.S. Treasury"),
           (("MORTGAGE30US",), "Freddie Mac"), (("CSUSHPINSA",), "S&P Cotality Case-Shiller"),
           (("FEDFUNDS", "DGS10", "CCLAC", "TDSP", "M2SL"), "Federal Reserve"), (("GASREGW", "DCOILWTICO"), "U.S. Energy Information Administration"),
           (("FEDMINNFRWG",), "U.S. Department of Labor"), (("SP",), "World Bank"), (("LRHUT",), "OECD"), (("QGBN",), "Bank for International Settlements")]


def origin(series_id: str) -> str:
    """Who publishes a FRED series (FRED re-publishes it); videos name the original agency."""
    for prefixes, name in ORIGINS:
        if series_id.startswith(prefixes):
            return f"{name} via FRED"
    return SOURCES["fred"]


def series(series_id: str) -> dict:
    """A catalogue series with its data, scaled into its unit: {"id", "name", "unit", "fmt", "index", "points": [(date, value)]}."""
    meta = catalog()["fred"][series_id]
    scale = float(meta.get("scale", 1))
    pts = [(d, v * scale) for d, v in monthly(fred_raw(series_id))]
    return {"id": series_id, "source": origin(series_id), **meta, "points": pts}


def state_values(key: str) -> dict:
    """The latest value for every state of a `states:` dataset: {"name", "fmt", "year", "values": {ST: value}}."""
    meta = catalog()["states"][key]
    scale, values, years = float(meta.get("scale", 1)), {}, set()
    for st in STATES:
        try:
            pts = fred_raw(meta["pattern"].replace("{ST}", st))
        except OSError:
            continue
        if pts:
            values[st] = pts[-1][1] * scale
            years.add(pts[-1][0][:4])
    return {"key": key, "source": origin(meta["pattern"].replace("{ST}", "")), **meta, "year": max(years) if years else "", "values": values}


def owid(slug: str) -> dict:
    """An Our World in Data chart: {"name", "fmt", "rows": {country: [(year, value)]}} (countries only, no regions)."""
    meta = catalog()["owid"][slug]
    text = _cached("owid-" + slug, f"https://ourworldindata.org/grapher/{slug}.csv?v=1&csvType=full&useColumnShortNames=true")
    rows = list(csv.reader(io.StringIO(text)))
    rows_by: dict[str, list[tuple[int, float]]] = {}
    for r in rows[1:]:
        if len(r) < 4 or not r[1] or r[1].startswith("OWID_") or r[3] == "":    # a code like OWID_WRL is a region
            continue
        rows_by.setdefault(r[0], []).append((int(r[2]), float(r[3])))
    return {"slug": slug, "source": SOURCES["owid"], **meta, "rows": rows_by}


# ---- formatting: the same text is shown on screen and checked against the narration ---------------------------------
def fmt(value: float, f: dict) -> str:
    d = f.get("decimals", 0)
    if f.get("compact"):
        for size, word in ((1e12, " trillion"), (1e9, " billion"), (1e6, " million")):
            if abs(value) >= size:
                return f"{f.get('prefix', '')}{value / size:,.{max(d, 1)}f}{word}{f.get('suffix', '')}"
    return f"{f.get('prefix', '')}{value:,.{d}f}{f.get('suffix', '')}"


def month_name(d: str) -> str:
    return date.fromisoformat(d).strftime("%B %Y") if len(d) >= 10 else d


def pct(a: float, b: float) -> float:
    return (b / a - 1) * 100 if a else 0.0


def window(points: list[tuple[str, float]], start: str | None = None, end: str | None = None) -> list[tuple[str, float]]:
    return [p for p in points if (not start or p[0] >= start) and (not end or p[0] <= end + "-12-31")]


def at(points: list[tuple[str, float]], when: str) -> tuple[str, float]:
    """The first point on or after `when` ("2020" or "2020-03"), else the last one."""
    for p in points:
        if p[0] >= when:
            return p
    return points[-1]


def spikes(pts: list[tuple[str, float]], n: int = 3, gap_months: int = 18) -> list[tuple[str, float]]:
    """The biggest local peaks, at least `gap_months` apart (a story is often several spikes, not one)."""
    peaks = [pts[i] for i in range(1, len(pts) - 1) if pts[i][1] >= pts[i - 1][1] and pts[i][1] > pts[i + 1][1]]
    peaks.sort(key=lambda p: -p[1])
    chosen: list[tuple[str, float]] = []
    month = lambda d: int(d[:4]) * 12 + int(d[5:7])
    for p in peaks:
        if all(abs(month(p[0]) - month(c[0])) >= gap_months for c in chosen):
            chosen.append(p)
        if len(chosen) == n:
            break
    return sorted(chosen)


def facts(s: dict, start: str | None = None) -> list[str]:
    """Plain-English facts about one series that a script may quote (and nothing else)."""
    pts = window(s["points"], start)
    f, name = s["fmt"], s["name"]
    first, last = pts[0], pts[-1]
    hi, lo = max(pts, key=lambda p: p[1]), min(pts, key=lambda p: p[1])
    out = [f"{name} [{s['unit']}], data from {month_name(first[0])} to {month_name(last[0])} (source: {s['source']})"]
    if not s.get("index"):
        out += [f"Latest value ({month_name(last[0])}): {fmt(last[1], f)}",
                f"Value in {month_name(first[0])}: {fmt(first[1], f)}",
                f"Highest: {fmt(hi[1], f)} in {month_name(hi[0])}", f"Lowest: {fmt(lo[1], f)} in {month_name(lo[0])}"]
    else:
        out.append("This is an index: quote only its percent changes, never its raw values")
    out += [f"Change from {month_name(first[0])} to {month_name(last[0])}: {pct(first[1], last[1]):+.0f}%",
            f"Change from the high in {month_name(hi[0])} to {month_name(last[0])}: {pct(hi[1], last[1]):+.0f}%"]
    if last[1] and first[1] and last[1] / first[1] >= 1.8:
        out.append(f"{month_name(last[0])} value is {last[1] / first[1]:.1f} times the {month_name(first[0])} value")
    for d, v in spikes(pts):
        if d != hi[0]:
            out.append(f"An earlier spike: {fmt(v, f) if not s.get('index') else ''} in {month_name(d)}".replace(":  in", " in")
                       + f" ({pct(at(pts, str(int(d[:4]) - 1) + d[4:])[1], v):+.0f}% in the year before it)")
    year_ago = at(pts, f"{int(last[0][:4]) - 1}{last[0][4:]}")
    if year_ago != last:
        out.append(f"Change over the last year ({month_name(year_ago[0])} to {month_name(last[0])}): {pct(year_ago[1], last[1]):+.1f}%")
    for y in range(int(first[0][:4]) + 5 - int(first[0][:4]) % 5, int(last[0][:4]), 5):   # milestone years: 1990, 1995, ...
        p = at(pts, str(y))
        if p[0][:4] == str(y):
            out.append(f"{month_name(p[0])}: " + (f"{fmt(p[1], f)}; " if not s.get("index") else "")
                       + f"change from then to {month_name(last[0])}: {pct(p[1], last[1]):+.0f}%")
    return out
