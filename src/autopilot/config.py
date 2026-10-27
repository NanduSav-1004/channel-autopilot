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
    render: dict = field(default_factory=dict)  # look options: callouts (key numbers pop up on screen)


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
