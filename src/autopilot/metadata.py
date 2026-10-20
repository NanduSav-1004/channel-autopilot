"""Upload metadata: title, description (with attributions) and tags, within YouTube's limits."""

EDU_CATEGORY = "27"  # YouTube category "Education"
DESC_LIMIT = 5000
TAG_LIMIT = 450  # YouTube allows 500 chars total; keep a margin


def build_description(script: dict, credits: list[str], source_url: str | None = None) -> str:
    parts = [script.get("description", "").strip()]
    chapters = script.get("chapters")
    if chapters:
        parts.append("\n".join(f"{ts} {name}" for ts, name in chapters))
    src = source_url or script.get("source_url")
    if src:
        parts.append(f"Source: {src}")
    parts.append("This video uses AI-assisted scripting and a synthetic voice.")
    text = "\n\n".join(p for p in parts if p)
    if credits:
        header, kept = "\n\nImage and video credits:\n", []
        room = DESC_LIMIT - len(text) - len(header) - 40  # 40 = room for the "and N more" line
        for i, line in enumerate(credits):
            if len(line) + 1 > room:
                kept.append(f"...and {len(credits) - i} more (see the source pages)")
                break
            kept.append(line)
            room -= len(line) + 1
        text += header + "\n".join(kept)
    return text[:DESC_LIMIT]


def chapter_marks(timings: list[dict]) -> list[tuple[str, str]]:
    """YouTube chapters need the first at 0:00 and each at least 10 s long."""
    marks = []
    for sec in timings:
        s = int(sec["start"])
        marks.append((f"{s // 60}:{s % 60:02d}", sec["heading"]))
    return marks if len(marks) >= 3 else []


def clean_tags(tags: list[str]) -> list[str]:
    out, total = [], 0
    for tag in tags:
        tag = tag.strip().replace("<", "").replace(">", "")
        if tag and total + len(tag) + 1 <= TAG_LIMIT and tag.lower() not in {t.lower() for t in out}:
            out.append(tag)
            total += len(tag) + 1
    return out


def clean_title(title: str) -> str:
    return title.replace("<", "").replace(">", "").strip()[:100]
