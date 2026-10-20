"""Pipeline stage handlers. Each stage reads/writes artifacts in output/<id>-<slug>/ and is idempotent."""
import json
import re
import shutil
import sqlite3
from pathlib import Path
from typing import ClassVar

from autopilot import audio, metadata, qa, shots, thumbnail, tts, wiki
from autopilot.config import Config
from autopilot.errors import RestartJob
from autopilot.render import render_photo_video
from autopilot.script import generate_script, repair_metadata, repair_sections


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

    # Files each stage reads. If one is missing (fresh CI runner after an interrupted run) the job rewinds.
    NEEDS: ClassVar[dict[str, list[str]]] = {
        "script": [],
        "qa": ["script.json", "source.json"],
        "voice": ["script.json"],
        "visuals": ["script.json", "timings.json"],
        "render": ["script.json", "timings.json", "items.json", "narration.wav"],
        "upload": ["final.mp4", "script.json", "timings.json", "credits.json"],
    }

    def handlers(self) -> dict:
        raw = {"script": self.script, "qa": self.qa, "voice": self.voice,
               "visuals": self.visuals, "render": self.render, "upload": self.upload}
        return {name: self._guarded(name, fn) for name, fn in raw.items()}

    def _guarded(self, stage: str, fn):
        def run(job) -> None:
            need = [] if (stage == "upload" and job["video_id"]) else self.NEEDS[stage]  # already uploaded
            d = self.dir(job)
            missing = [f for f in need if not (d / f).exists()]
            if missing:
                raise RestartJob(f"missing {', '.join(missing)}")
            fn(job)
        return run

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
        _write(d / "script.json", generate_script(
            job["topic"], src, self.cfg.niche, words=self.cfg.formats["long"]["target_words"], feedback=feedback))

    REPAIR_ROUNDS = 2

    def qa(self, job) -> None:
        d = self.dir(job)
        script, source = _read(d / "script.json"), _read(d / "source.json")
        long = self.cfg.formats["long"]
        check = lambda s: qa.check_script(
            s, source, self.cfg.forbidden_topics, min_words=long["min_words"], min_sections=long["min_sections"])
        issues = check(script)
        for _ in range(self.REPAIR_ROUNDS):
            bad = [i.removeprefix("unsupported claim: ") for i in issues if i.startswith("unsupported claim: ")]
            if not bad or len(bad) != len(issues):  # only unsupported claims are repairable in place
                break
            meta = [b for b in bad if b.startswith(("[title]", "[description]"))]
            body = [b for b in bad if b not in meta]
            targets = qa.locate_sections(script, body) if body else []
            if (body and not targets) or not (meta or targets):
                break
            if meta:
                print(f"[job {job['id']}] rewriting title/description ({len(meta)} unsupported statement(s))", flush=True)
                script = repair_metadata(script, source, meta)
            if targets:
                print(f"[job {job['id']}] repairing sections {targets} ({len(body)} unsupported claim(s))", flush=True)
                script = repair_sections(script, source, targets, body)
            _write(d / "script.json", script)
            issues = check(script)
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
        from autopilot import upload  # lazy: needs Google credentials

        video_id = job["video_id"]
        if not video_id:
            script, timings = _read(d / "script.json"), _read(d / "timings.json")
            script["chapters"] = metadata.chapter_marks(timings)
            description = metadata.build_description(script, _read(d / "credits.json"))
            video_id = upload.insert_video(d / "final.mp4", script["title"], description,
                                           script.get("tags", []), privacy=self.privacy)
            # Persist at once: if anything after this fails, a retry must never upload the video again.
            self.conn.execute("UPDATE jobs SET video_id = ? WHERE id = ?", (video_id, job["id"]))
            self.conn.commit()
        self.set_thumbnail(job["id"], video_id, d / "thumbnail.jpg")

    def set_thumbnail(self, job_id: int, video_id: str, thumb: Path) -> bool:
        """Best effort: a thumbnail problem (e.g. channel not yet eligible) must not fail the upload."""
        from autopilot import upload

        try:
            upload.set_thumbnail(video_id, thumb)
        except Exception as exc:  # noqa: BLE001
            print(f"[job {job_id}] thumbnail not set ({type(exc).__name__}); retry with `autopilot thumbnails`", flush=True)
            return False
        self.conn.execute("UPDATE jobs SET thumbnail_set = 1 WHERE id = ?", (job_id,))
        self.conn.commit()
        return True
