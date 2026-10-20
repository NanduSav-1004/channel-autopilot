import os
from pathlib import Path


def load_env(path: str | Path = ".env") -> None:
    """Load KEY=VALUE lines into os.environ without overriding existing values (CI secrets win)."""
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
