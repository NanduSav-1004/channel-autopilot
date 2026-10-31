"""Pipeline stage handlers. Each stage reads/writes artifacts in output/<id>-<slug>/ and is idempotent."""
import json
import re
import shutil
import sqlite3
from pathlib import Path
from typing import ClassVar

from autopilot import (
    audio,
    closing,
    datashots,
    db,
    metadata,
    music,
    qa,
    schedule,
    shorts,
    shots,
    thumbnail,
    topics,
    tts,
    wiki,
)
from autopilot.config import Config, cta_on, data_shots_on, mascot_style, music_mood
from autopilot.errors import RestartJob, TransientError
from autopilot.render import render_photo_video, render_short
from autopilot.script import (
    COLD_WORDS,
    fit_title,
    generate_script,
    opening_numbers,
    repair_metadata,
    repair_sections,
    shorten_title,
    style_stats,
)


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
        self._engines: dict = {}
        self._fallback = None

    # Files each stage reads. If one is missing (fresh CI runner after an interrupted run) the job rewinds.
    NEEDS: ClassVar[dict[str, list[str]]] = {
        "script": [],
        "qa": ["script.json", "source.json"],
        "voice": ["script.json"],
        "visuals": ["script.json", "timings.json"],
        "render": ["script.json", "timings.json", "items.json", "narration.wav"],
        "upload": ["final.mp4", "script.json", "timings.json", "credits.json"],
        "shorts": [],  # handled inside: if the long video's files are gone, skip (never regenerate it)
        "short_script": [],
        "short_voice": ["script.json"],
        "short_render": ["script.json", "timings.json", "narration.wav"],
        "short_upload": ["final.mp4", "script.json"],
    }

    def engine(self, job):
        """The voice for this video. A long video and its Shorts share one voice (chosen by the long video's id);
        engines are built once per voice, since loading a model is slow."""
        root = job["parent_id"] or job["id"]
        if root not in self._engines:
            self._engines[root] = tts.make_engine(self.cfg.audio, root)
        return self._engines[root]

    def fallback_engine(self):
        """What to use if the chosen voice fails partway (e.g. Gemini quota): the configured fallback, else Piper."""
        if self._fallback is None:
            spec = self.cfg.audio.get("fallback")
            try:
                self._fallback = tts.build_engine(spec) if spec else tts.PiperEngine()
            except (ImportError, OSError, ValueError):
                self._fallback = tts.PiperEngine()
        return self._fallback

    def mood(self, job) -> str:
        """The mood of this video's music: from the topic's category (a Short uses its long video's)."""
        cat = job["category"] if job["kind"] == "long" else (self._parent(job)["category"] if job["parent_id"] else None)
        return music_mood(self.cfg, cat)

    def make_music(self, out: Path, seconds: float, seed: int, mood: str = "plain") -> Path:
        style = self.cfg.audio.get("music_style", "ambient")
        if style in music.STYLES:
            return music.generate_beat(seconds, out, seed=seed, style=style)
        return audio.generate_ambient(seconds, out, seed=seed, mood=mood)

    def handlers(self) -> dict:
        raw = {"script": self.script, "qa": self.qa, "voice": self.voice,
               "visuals": self.visuals, "render": self.render, "upload": self.upload, "shorts": self.shorts,
               "short_script": self.short_script, "short_voice": self.short_voice,
               "short_render": self.short_render, "short_upload": self.short_upload}
        return {name: self._guarded(name, fn) for name, fn in raw.items()}

    def _guarded(self, stage: str, fn):
        def run(job) -> None:
            uploaded = stage in ("upload", "short_upload") and job["video_id"]
            need = [] if uploaded else self.NEEDS[stage]  # an uploaded video needs no files
            d = self.dir(job)
            missing = [f for f in need if not (d / f).exists()]
            if missing:
                raise RestartJob(f"missing {', '.join(missing)}")
            fn(job)
        return run

    def dir(self, job) -> Path:
        if job["kind"] == "short":  # a Short lives inside its parent's folder
            parent = self.conn.execute("SELECT * FROM jobs WHERE id = ?", (job["parent_id"],)).fetchone()
            d = self.dir(parent) / f"short{job['short_idx']}"
        else:
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
        script = generate_script(
            job["topic"], src, self.cfg.niche, series=topics.series_for(job["category"]),
            words=self.cfg.formats["long"]["target_words"], feedback=feedback)
        _write(d / "script.json", script)
        if script.get("sections"):
            print(f"[job {job['id']}] opening: {opening_numbers(script['sections'][0]['narration'])} number(s) in the first {COLD_WORDS} words", flush=True)
        st = style_stats(" ".join(s["narration"] for s in script.get("sections", [])))
        print(f"[job {job['id']}] style: avg {st['avg']:.1f} words/sentence, longest {st['longest']}, "
              f"{100 * st['long_share']:.0f}% over 22 words, hook {st['hook']} words, "
              f"'you' x{st['you_per_1000']:.0f} per 1000 words", flush=True)

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
            note = fit_title(script, job["topic"])
            if note:
                _write(d / "script.json", script)
                print(f"[job {job['id']}] {note}", flush=True)
            old = script["title"]
            if shorten_title(script):
                _write(d / "script.json", script)
                print(f"[job {job['id']}] title shortened: {old!r} -> {script['title']!r}", flush=True)
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
        if cta_on(self.cfg, "long_closing"):          # a varied closing line, written before the voice is made (once per script)
            script = closing.add_closing(_read(d / "script.json"), job["id"])
            _write(d / "script.json", script)
            if script.get("closing"):
                print(f"[job {job['id']}] closing line: {script['closing']}", flush=True)
        _write(d / "timings.json", tts.synthesize_script(_read(d / "script.json"), d / "narration.wav",
                                                                 self.engine(job), self.fallback_engine()))

    def visuals(self, job) -> None:
        d = self.dir(job)
        if (d / "items.json").exists():
            return
        plan = shots.plan_shots(_read(d / "timings.json"))
        items, credits = shots.gather_images(_read(d / "script.json"), plan, self.work / "assets", job["topic"],
                                            use_nasa=job["category"] == "space")
        with_media = sum(1 for sec in items if sec)
        n_img = sum(i["kind"] == "image" for sec in items for i in sec)
        n_vid = sum(i["kind"] == "video" for sec in items for i in sec)
        print(f"[job {job['id']}] visuals: {n_img} images and {n_vid} videos; "
              f"{with_media}/{len(items)} sections have media", flush=True)
        floor = self.cfg.formats["long"].get("min_media_sections", 0)
        if items and with_media / len(items) < floor:  # never publish a slideshow of title cards
            raise StageError(f"only {with_media}/{len(items)} sections found images or footage "
                             "(media sources unavailable or topic hard to illustrate)")
        _write(d / "items.json", [[{"kind": i["kind"], "path": str(i["path"])} for i in sec] for sec in items])
        _write(d / "credits.json", credits)

    def render(self, job) -> None:
        d = self.dir(job)
        if (d / "final.mp4").exists():
            return
        script, timings = _read(d / "script.json"), _read(d / "timings.json")
        items = shots.fill_sparse_sections(
            [[{"kind": i["kind"], "path": Path(i["path"])} for i in sec] for sec in _read(d / "items.json")])
        music = self.make_music(d / "music.wav", timings[-1]["end"] + 5, job["id"], self.mood(job))
        wd = self.work / d.name
        wd.mkdir(parents=True, exist_ok=True)
        data = []
        if data_shots_on(self.cfg, short=False):
            data = datashots.shots_for([{"heading": sec["heading"], "narration": sec["narration"], "sentences": tm["sentences"]}
                                        for sec, tm in zip(script["sections"], timings, strict=False)], (1280, 720), wd)
        render_photo_video(script, timings, items, shots.plan_cuts(timings, [len(s) for s in items]), d / "narration.wav",
                           d / "final.mp4", wd, music=music, data_shots=data or None,
                           mascot=mascot_style(self.cfg, short=False))
        images = [i["path"] for sec in items for i in sec if i["kind"] == "image"]
        thumbnail.make_thumbnail(script, images, d / "thumbnail.jpg", pick=thumbnail.pick_with_vision)
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
            publish_at = None
            hour = self.cfg.formats["long"].get("publish_hour_utc")
            if self.privacy == "public" and hour is not None:  # go live at US/UK prime time, not at run time
                publish_at = schedule.rfc3339(schedule.next_slot(hour))
            video_id = upload.insert_video(d / "final.mp4", script["title"], description,
                                           script.get("tags", []), privacy=self.privacy, publish_at=publish_at)
            # Persist at once: if anything after this fails, a retry must never upload the video again.
            self.conn.execute("UPDATE jobs SET video_id = ?, publish_at = ? WHERE id = ?",
                              (video_id, publish_at, job["id"]))
            self.conn.commit()
            if publish_at:
                print(f"[job {job['id']}] scheduled to go public at {publish_at}", flush=True)
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

    # ---------- Shorts ----------
    def shorts(self, job) -> None:
        """Last stage of a long job: plan its Shorts and queue each as its own job."""
        n = self.cfg.formats.get("short", {}).get("per_day", 0)
        if not n:
            return
        added = self.queue_shorts(job, n)
        if added:
            print(f"[job {job['id']}] queued {added} Short(s)", flush=True)

    def queue_shorts(self, job, n: int) -> int:
        """Make sure the long video has n Shorts queued: plan the missing ones (strictly: the planner never returns fewer than n while the
        script has enough sections) and add their jobs. Returns how many jobs were added."""
        d = self.dir(job)
        existing = self.conn.execute("SELECT COUNT(*) FROM jobs WHERE parent_id = ?", (job["id"],)).fetchone()[0]
        if existing >= n:
            return 0
        if not (d / "script.json").exists() or not (d / "source.json").exists():
            print(f"[job {job['id']}] shorts skipped: the long video's files are gone", flush=True)
            return 0
        plans = _read(d / "shorts.json") if (d / "shorts.json").exists() else []
        if len(plans) < n:
            plans += shorts.plan_shorts_strict(_read(d / "script.json"), _read(d / "source.json"), n, have=plans)
            if plans:                                    # an empty plan is not saved: it would block a later retry
                _write(d / "shorts.json", plans)
        if len(plans) < n:
            print(f"[job {job['id']}] WARNING: only {len(plans)} of {n} Shorts could be planned", flush=True)
        for i in range(existing, min(len(plans), n)):
            db.add_job(self.conn, plans[i]["title"], "short", job["source_title"], parent_id=job["id"], short_idx=i)
        return max(0, min(len(plans), n) - existing)

    def redo_english_shorts(self, indexes: list[int], now=None) -> list[str]:
        """Make today's English Shorts at these positions (0 = first) again, for example after a fix. Each old video is deleted from the
        channel and its job is reset, but ONLY while it is still private and scheduled; a Short that is already public is never touched."""
        from datetime import datetime, timezone

        from autopilot import upload

        now = now or datetime.now(timezone.utc)
        job = self.conn.execute("SELECT id FROM jobs WHERE kind = 'long' AND video_id IS NOT NULL "
                                "ORDER BY id DESC LIMIT 1").fetchone()
        if not job:
            return ["redo: no uploaded long video"]
        lines = []
        yt = upload._client("en")
        for r in self.conn.execute("SELECT * FROM jobs WHERE parent_id = ? AND kind = 'short' ORDER BY short_idx",
                                   (job["id"],)).fetchall():
            if r["short_idx"] not in indexes:
                continue
            if r["video_id"]:
                items = yt.videos().list(part="status", id=r["video_id"]).execute().get("items", [])
                st = items[0]["status"] if items else None
                when = schedule.parse(st["publishAt"]) if st and st.get("publishAt") else None
                if st is not None and not (st["privacyStatus"] == "private" and when and when > now):
                    lines.append(f"Short {r['short_idx'] + 1}: kept (already public or not scheduled)")
                    continue
                if st is not None:
                    upload.delete_video(r["video_id"], "en")
            (self.dir(r) / "final.mp4").unlink(missing_ok=True)  # render again, so the new graphics are in it
            self.conn.execute("UPDATE jobs SET video_id = NULL, thumbnail_set = 0, stage = 'short_render', status = 'pending', attempts = 0, "
                              "error = NULL WHERE id = ?", (r["id"],))
            self.conn.commit()
            lines.append(f"Short {r['short_idx'] + 1}: old scheduled video deleted, will be made again")
        return lines

    def fill_missing_shorts(self) -> int:
        """Today's uploaded long videos that have fewer Shorts than the daily rule: queue the missing ones. Run at the start of every
        daily run, including the backup runs, so a day that came up short is repaired by the next run."""
        n = self.cfg.formats.get("short", {}).get("per_day", 0)
        total = 0
        for job in self.conn.execute("SELECT * FROM jobs WHERE kind = 'long' AND video_id IS NOT NULL "
                                     "AND date(created_at) = date('now') ORDER BY id").fetchall():
            if n:
                total += self.queue_shorts(job, n)
        return total

    def _parent(self, job):
        return self.conn.execute("SELECT * FROM jobs WHERE id = ?", (job["parent_id"],)).fetchone()

    def short_script(self, job) -> None:
        d = self.dir(job)
        if (d / "script.json").exists():
            return
        parent_dir = self.dir(self._parent(job))
        if not (parent_dir / "shorts.json").exists():
            raise StageError("the long video's shorts.json is gone")
        _write(d / "script.json", _read(parent_dir / "shorts.json")[job["short_idx"]])

    def short_voice(self, job) -> None:
        d = self.dir(job)
        if (d / "timings.json").exists() and (d / "narration.wav").exists():
            return
        s = _read(d / "script.json")
        timings = tts.synthesize_script({"sections": [{"heading": s["title"], "narration": s["narration"]}]},
                                        d / "narration.wav", self.engine(job), self.fallback_engine())
        if timings[-1]["end"] > shorts.MAX_SECONDS:
            (d / "narration.wav").unlink()
            raise StageError(f"Short is {timings[-1]['end']:.0f}s, over the {shorts.MAX_SECONDS}s limit")
        _write(d / "timings.json", timings)

    def short_render(self, job) -> None:
        d = self.dir(job)
        if (d / "final.mp4").exists():
            return
        s, timings = _read(d / "script.json"), _read(d / "timings.json")
        parent_dir = self.dir(self._parent(job))
        if not (parent_dir / "items.json").exists():            # a later run on a fresh machine: find media for the same script again
            parent = self._parent(job)
            items, credits = shots.recover_items(_read(parent_dir / "script.json"), parent["topic"], self.work / "assets",
                                                 use_nasa=parent["category"] == "space")
            _write(parent_dir / "items.json", [[{"kind": i["kind"], "path": str(i["path"])} for i in sec] for sec in items])
            if not (parent_dir / "credits.json").exists():
                _write(parent_dir / "credits.json", credits)
            print(f"[job {job['id']}] media found again for this Short", flush=True)
        sections = _read(parent_dir / "items.json")
        pool = shots.short_media_pool(sections, s["section_index"])  # this section's media, then its neighbours'
        items = [{"kind": i["kind"], "path": Path(i["path"])} for i in pool if Path(i["path"]).exists()]
        music = self.make_music(d / "music.wav", timings[-1]["end"] + 3, job["id"] + 1000, self.mood(job))
        wd = self.work / f"{self.dir(self._parent(job)).name}-{d.name}"
        wd.mkdir(parents=True, exist_ok=True)
        data = []
        if data_shots_on(self.cfg, short=True):
            data = datashots.shots_for([{"heading": s["title"], "narration": s["narration"], "sentences": timings[0]["sentences"]}],
                                       (1080, 1920), wd)
        render_short(s, timings, items, d / "narration.wav", d / "final.mp4", wd, music=music, data_shots=data or None,
                     mascot=mascot_style(self.cfg, short=True), cta=closing.SHORT_TAG["en"] if cta_on(self.cfg, "short_tag") else None)
        shutil.rmtree(wd, ignore_errors=True)

    def short_upload(self, job) -> None:
        d = self.dir(job)
        parent = self._parent(job)
        if self.cfg.dry_run:
            print(f"[dry_run] would upload Short {d / 'final.mp4'}")
            return
        if job["video_id"]:
            return
        if not parent["video_id"]:
            raise TransientError("the long video is not uploaded yet, so there is nothing to link to")
        from autopilot import upload

        s = _read(d / "script.json")
        pdir = self.dir(parent)
        credits = _read(pdir / "credits.json") if (pdir / "credits.json").exists() else []
        source_url = _read(pdir / "script.json").get("source_url") if (pdir / "script.json").exists() else None
        sibs = [r["id"] for r in self.conn.execute(
            "SELECT id FROM jobs WHERE parent_id = ? ORDER BY short_idx", (job["parent_id"],))]
        offsets = self.cfg.formats.get("short", {}).get("publish_offsets_hours", [2, 6, 10])
        publish_at = None
        if self.privacy == "public":  # spread them through the day; other privacies upload as asked
            base = schedule.parse(parent["publish_at"]) if parent["publish_at"] else None  # follow the long video
            publish_at = shorts.publish_times(len(sibs), offsets, base)[sibs.index(job["id"])]
        description = shorts.short_description(s["narration"].split(". ")[0] + ".", parent["video_id"], source_url, credits)
        video_id = upload.insert_video(d / "final.mp4", f"{s['title']} #Shorts", description,
                                       ["shorts", "science", "explained"], privacy=self.privacy, publish_at=publish_at)
        self.conn.execute("UPDATE jobs SET video_id = ? WHERE id = ?", (video_id, job["id"]))
        self.conn.commit()
