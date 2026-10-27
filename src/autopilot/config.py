from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Config:
    niche: str
    audience: str
    formats: dict
    forbidden_topics: list = field(default_factory=list)
    dry_run: bool = True
    audio: dict = field(default_factory=dict)  # voice_engine, voice_name, voice_speed, music_style
    malayalam: dict = field(default_factory=dict)  # the Malayalam channel: enabled, publish_hour_utc, voices
    render: dict = field(default_factory=dict)  # look options: mascot (false | shorts | all), mascot_style (bulb | atom)


def load_config(path: str | Path = "config/channel.yaml") -> Config:
    data = yaml.safe_load(Path(path).read_text())
    return Config(
        niche=data["niche"],
        audience=data["audience"],
        formats=data["formats"],
        forbidden_topics=data.get("forbidden_topics", []),
        dry_run=data.get("dry_run", True),
        audio=data.get("audio", {}),
        malayalam=data.get("malayalam", {}),
        render=data.get("render", {}),
    )


def mascot_style(cfg: Config, short: bool) -> str | None:
    """Which mascot character to draw on this kind of video, or None: render.mascot is false, "shorts" or "all"."""
    where = (cfg.render or {}).get("mascot")
    if where is True:
        where = "all"
    if where == "all" or (where == "shorts" and short):
        style = (cfg.render or {}).get("mascot_style", "bulb")
        return style if style in ("bulb", "atom") else "bulb"
    return None
