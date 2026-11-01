import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "state_sync.sh"


@pytest.mark.skipif(not shutil.which("git"), reason="needs git")
def test_the_latest_videos_small_files_survive_a_fresh_runner(tmp_path):
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)

    def run(cwd: Path, action: str):
        return subprocess.run(["bash", str(SCRIPT), action], cwd=cwd, check=True, capture_output=True, text=True,
                              env={"PATH": "/usr/bin:/bin", "STATE_REMOTE": str(remote), "HOME": str(tmp_path)})

    first = tmp_path / "run1"
    (first / "data").mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=first, check=True)
    (first / "data" / "autopilot.db").write_text("db")
    d = first / "output" / "0012-gps"
    d.mkdir(parents=True)
    for name in ("script", "shorts", "credits", "source", "items", "timings"):
        (d / f"{name}.json").write_text(f'{{"{name}": 1}}')
    (first / "data" / "video_maps").mkdir()
    (first / "data" / "video_maps" / "abc123.json").write_text('{"segments": []}')
    run(first, "push")

    second = tmp_path / "run2"                                         # a fresh runner: no output folder at all
    second.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=second, check=True)
    run(second, "pull")
    restored = sorted(p.name for p in (second / "output" / "0012-gps").iterdir())
    assert restored == ["credits.json", "script.json", "shorts.json", "source.json"]      # small files only, not the media lists
    assert (second / "data" / "video_maps" / "abc123.json").exists()                      # the retention maps accumulate across runs

    (second / "run.log").write_text("today's video is already uploaded; nothing to do\n")
    run(second, "push")                                                 # a no-op run keeps them for the next one
    third = tmp_path / "run3"
    third.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=third, check=True)
    run(third, "pull")
    assert (third / "output" / "0012-gps" / "script.json").exists()
    assert (third / "data" / "video_maps" / "abc123.json").exists()


@pytest.mark.skipif(not shutil.which("git"), reason="needs git")
def test_plotline_keeps_the_log_of_the_last_run_that_did_work(tmp_path):
    script = Path(__file__).resolve().parent.parent / "scripts" / "plotline_state.sh"
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)

    def runner(name: str) -> Path:
        d = tmp_path / name
        d.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=d, check=True)
        return d

    def run(cwd: Path, action: str):
        return subprocess.run(["bash", str(script), action], cwd=cwd, check=True, capture_output=True, text=True,
                              env={"PATH": "/usr/bin:/bin", "STATE_REMOTE": str(remote), "HOME": str(tmp_path)})

    first = runner("run1")
    (first / "data" / "plotline" / "2026-11-01").mkdir(parents=True)
    (first / "data" / "plotline" / "state.json").write_text("{}")
    (first / "plotline_run.log").write_text("[sfx] 33 sound effects\nuploaded\n")
    run(first, "push")
    second = runner("run2")
    run(second, "pull")
    (second / "plotline_run.log").write_text("today's Plotline video and Shorts are already up; nothing to do\n")
    run(second, "push")                                                              # the later no-op run must not hide the working run's log
    third = runner("run3")
    run(third, "pull")
    assert "nothing to do" in (third / "data" / "plotline_last_run.log").read_text()
    assert "[sfx] 33 sound effects" in (third / "data" / "plotline_last_work_run.log").read_text()
