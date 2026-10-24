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
    run(first, "push")

    second = tmp_path / "run2"                                         # a fresh runner: no output folder at all
    second.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=second, check=True)
    run(second, "pull")
    restored = sorted(p.name for p in (second / "output" / "0012-gps").iterdir())
    assert restored == ["credits.json", "script.json", "shorts.json", "source.json"]      # small files only, not the media lists

    (second / "run.log").write_text("today's video is already uploaded; nothing to do\n")
    run(second, "push")                                                 # a no-op run keeps them for the next one
    third = tmp_path / "run3"
    third.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=third, check=True)
    run(third, "pull")
    assert (third / "output" / "0012-gps" / "script.json").exists()
