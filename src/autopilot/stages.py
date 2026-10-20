"""Pipeline stage handlers. Each stage reads/writes artifacts in output/<id>-<slug>/ and is idempotent."""
import json
import re
import shutil
import sqlite3
from pathlib import Path

from autopilot import audio, metadata, qa, shots, thumbnail, tts, wiki
from autopilot.config import Config
from autopilot.render import render_photo_video
from autopilot.script import generate_script


class StageError(RuntimeError):
    pass


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40] or "video"


def _read(path: Path):
    return json.loads(path.read_text())


def _write(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=1))


class Stages:
    def __init__(self, conn: sqlite3.Connection, cfg: Config, root: Path = Path("output"),
                 work: Path = Path("work"), privacy: str = "private"):
        self.conn, self.cfg, self.root, self.work, self.privacy = conn, cfg, root, work, privacy

    def handlers(self) -> dict:
        return {"script": self.script, "qa": self.qa, "voice": self.voice,
                "visuals": self.visuals, "render": self.render, "upload": self.upload}

    def dir(self, job) -> Path:
        d = self.root / f"{job['id']:04d}-{slugify(job['topic'])}"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def script(self, job) -> None:
        d = self.dir(job)
        if (d / "script.json").exists():
            return
        src = wiki.fetch_source(job["source_title"] or job["topic"])
        if not src:
            raise StageError(f"no Wikipedia source for {job['topic']!r}")
        feedback = _read(d / "qa_issues.json") if (d / "qa_issues.json").exists() else None
        _write(d / "source.json", src)
        _write(d / "script.json", generate_script(job["topic"], src, self.cfg.niche, feedback=feedback))

    def qa(self, job) -> None:
        d = self.dir(job)
        issues = qa.check_script(_read(d / "script.json"), _read(d / "source.json"), self.cfg.forbidden_topics)
        if not issues:
            return
        _write(d / "qa_issues.json", issues)
        (d / "script.json").unlink()  # force a regeneration (with the issues as feedback) on retry
        self.conn.execute("UPDATE jobs SET stage = 'new' WHERE id = ?", (job["id"],))
        self.conn.commit()
        raise StageError("QA rejected script: " + "; ".join(issues[:3]))

    def voice(self, job) -> None:
        d = self.dir(job)
        if (d / "timings.json").exists() and (d / "narration.wav").exists():
            return
        _write(d / "timings.json", tts.synthesize_script(_read(d / "script.json"), d / "narration.wav"))

    def visuals(self, job) -> None:
        d = self.dir(job)
        if (d / "items.json").exists():
            return
        plan = shots.plan_shots(_read(d / "timings.json"))
        items, credits = shots.gather_images(_read(d / "script.json"), plan, self.work / "assets", job["topic"])
        _write(d / "items.json", [[{"kind": i["kind"], "path": str(i["path"])} for i in sec] for sec in items])
        _write(d / "credits.json", credits)

    def render(self, job) -> None:
        d = self.dir(job)
        if (d / "final.mp4").exists():
            return
        script, timings = _read(d / "script.json"), _read(d / "timings.json")
        items = [[{"kind": i["kind"], "path": Path(i["path"])} for i in sec] for sec in _read(d / "items.json")]
        music = audio.generate_ambient(timings[-1]["end"] + 5, d / "music.wav", seed=job["id"])
        wd = self.work / d.name
        render_photo_video(script, timings, items, shots.plan_shots(timings), d / "narration.wav",
                           d / "final.mp4", wd, music=music)
        first_image = next((i["path"] for sec in items for i in sec if i["kind"] == "image"), None)
        thumbnail.make_thumbnail(script, first_image, d / "thumbnail.jpg")
        shutil.rmtree(wd, ignore_errors=True)

    def upload(self, job) -> None:
        d = self.dir(job)
        if self.cfg.dry_run:
            print(f"[dry_run] would upload {d / 'final.mp4'}")
            return
        if job["video_id"]:
            return
        from autopilot.upload import upload_video  # lazy: needs Google credentials

        script, timings = _read(d / "script.json"), _read(d / "timings.json")
        script["chapters"] = metadata.chapter_marks(timings)
        description = metadata.build_description(script, _read(d / "credits.json"))
        video_id = upload_video(d / "final.mp4", script["title"], description, script.get("tags", []),
                                d / "thumbnail.jpg", privacy=self.privacy)
        self.conn.execute("UPDATE jobs SET video_id = ? WHERE id = ?", (video_id, job["id"]))
        self.conn.commit()
