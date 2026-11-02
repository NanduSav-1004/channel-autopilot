"""A last check of a finished video file before it is uploaded (idea taken from OpenMontage's composition validator; written from scratch).

One ffmpeg pass looks for black stretches, frozen picture and dead audio, and ffprobe checks the streams, the size and the length; a second
pass measures the loudness. Findings are either WARNINGS (logged, so we learn what normal looks like) or ERRORS, which are only the clearly
broken cases: no picture or no sound, picture and sound of very different lengths, a long black or frozen stretch, a long dead-silent stretch,
the wrong frame size, an absurd length. An error stops the upload of that attempt; the stage is run again (a re-render usually fixes a glitch)."""
import json
import re
import subprocess
from pathlib import Path

LIMITS = {"long": (150.0, 1500.0), "short": (8.0, 61.0)}      # plausible length range in seconds
EDGE = 1.2                                                    # black or silence this close to the start or end is a fade, not a fault


class VideoCheckError(RuntimeError):
    """The finished video failed the pre-upload check."""


def probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)], check=True, capture_output=True, text=True).stdout
    info = json.loads(out)
    streams = info.get("streams", [])
    v = next((s for s in streams if s.get("codec_type") == "video"), None)
    a = next((s for s in streams if s.get("codec_type") == "audio"), None)
    dur = lambda s: float(s["duration"]) if s and s.get("duration") not in (None, "N/A") else None
    return {"video": v, "audio": a, "v_dur": dur(v), "a_dur": dur(a), "dur": float(info.get("format", {}).get("duration") or 0.0),
            "size": (int(v["width"]), int(v["height"])) if v else None}


def scan(path: Path) -> dict:
    """Black, frozen and silent stretches as (start, end) seconds, from a single ffmpeg pass over a small copy of the picture."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vf", "scale=320:-2,blackdetect=d=0.5:pix_th=0.10,freezedetect=n=-55dB:d=6",
                        "-af", "silencedetect=n=-45dB:d=3", "-f", "null", "-"], capture_output=True, text=True, check=True).stderr
    black = [(float(a), float(b)) for a, b in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", r)]
    freeze_s = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", r)]
    freeze_d = [float(x) for x in re.findall(r"freeze_duration: ([\d.]+)", r)]
    sil_s = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]
    sil_e = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    return {"black": black, "freeze": [(s, s + d) for s, d in zip(freeze_s, freeze_d, strict=False)],
            "silence": [(s, e) for s, e in zip(sil_s, sil_e, strict=False)], "silence_open": sil_s[len(sil_e):]}


def loudness(path: Path) -> tuple[float, float] | None:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-vn", "-i", str(path), "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True, check=False).stderr
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r, re.DOTALL)
    if not m:
        return None
    d = json.loads(m.group(0))
    return float(d["input_i"]), float(d["input_tp"])


def judge(info: dict, found: dict, loud: tuple[float, float] | None, kind: str, size: tuple[int, int] | None) -> dict:
    """The verdict from the measurements: {"errors": [...], "warnings": [...], "stats": {...}}. Pure, so it is tested on made-up measurements."""
    errors: list[str] = []
    warnings: list[str] = []
    dur = info["v_dur"] or info["dur"]
    if not info["video"]:
        errors.append("no picture stream")
    if not info["audio"]:
        errors.append("no sound stream")
    if size and info["size"] and info["size"] != tuple(size):
        errors.append(f"frame size {info['size']} instead of {tuple(size)}")
    if info["v_dur"] and info["a_dur"]:
        gap = abs(info["v_dur"] - info["a_dur"])
        (errors if gap > 2.5 else warnings).append(f"picture {info['v_dur']:.1f}s and sound {info['a_dur']:.1f}s differ by {gap:.1f}s") if gap > 1.0 else None
    lo, hi = LIMITS[kind]
    if not lo <= dur <= hi:
        errors.append(f"length {dur:.0f}s is outside {lo:.0f} to {hi:.0f}s")
    inner_black = [(a, b) for a, b in found["black"] if a > EDGE and b < dur - EDGE + 0.01]
    black_total = sum(b - a for a, b in inner_black)
    if inner_black and (black_total >= 4.0 or max(b - a for a, b in inner_black) >= 2.5):
        errors.append(f"black picture for {black_total:.1f}s (first at {inner_black[0][0]:.0f}s)")
    elif inner_black:
        warnings.append(f"black picture for {black_total:.1f}s (first at {inner_black[0][0]:.0f}s)")
    frozen = max(((b - a) for a, b in found["freeze"]), default=0.0)
    if frozen >= 15.0:
        errors.append(f"picture frozen for {frozen:.0f}s")
    elif frozen:
        warnings.append(f"picture still for {frozen:.0f}s")
    quiet = [(a, b) for a, b in found["silence"] if a > EDGE and b < dur - 3.0]
    quiet += [(a, dur) for a in found["silence_open"] if a > EDGE and a < dur - 3.0]
    longest = max(((b - a) for a, b in quiet), default=0.0)
    if longest >= 8.0:
        errors.append(f"dead silence for {longest:.0f}s")
    elif quiet:
        warnings.append(f"silence for {longest:.0f}s")
    if loud:
        if not -18.0 <= loud[0] <= -11.0:
            warnings.append(f"loudness {loud[0]:.1f} LUFS is far from -14")
        if loud[1] > -0.5:
            warnings.append(f"true peak {loud[1]:.1f} dBTP is close to clipping")
    return {"errors": errors, "warnings": warnings, "stats": {"seconds": round(dur, 1), "lufs": loud[0] if loud else None, "black_s": round(black_total, 1),
                                                                 "longest_still_s": round(frozen), "longest_silence_s": round(longest)}}


def gate(path: Path, kind: str, size: tuple[int, int] | None = None, log=print) -> dict:
    """Check the finished video. Logs the result; raises VideoCheckError on an error. A problem with the CHECK itself (ffmpeg missing, odd output)
    is only logged: the check must never be the reason a good video is lost."""
    try:
        result = judge(probe(path), scan(path), loudness(path), kind, size)
    except Exception as exc:  # noqa: BLE001
        log(f"[qa-video] could not check {path.name} ({type(exc).__name__}: {str(exc)[:120]})")
        return {"errors": [], "warnings": [], "stats": {}}
    s = result["stats"]
    log(f"[qa-video] {kind} {s.get('seconds')}s, {s.get('lufs')} LUFS: " + ("ok" if not result["errors"] and not result["warnings"] else
        "; ".join([f"ERROR {e}" for e in result["errors"]] + [f"warning {w}" for w in result["warnings"]])))
    if result["errors"]:
        raise VideoCheckError("the finished video failed its check: " + "; ".join(result["errors"]))
    return result
