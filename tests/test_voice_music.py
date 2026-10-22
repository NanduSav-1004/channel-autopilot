import itertools
import shutil
import subprocess
import wave

import numpy as np
import pytest

from autopilot import music, stages, tts
from autopilot.config import Config


class FakeEngine:
    """1 s of audio per sentence at 8 kHz."""
    name = "fake"

    def synth(self, text):
        return b"\x01\x00" * 8000, 8000


def test_synthesize_script_with_any_engine_gives_exact_sentence_timings(tmp_path):
    script = {"sections": [{"heading": "A", "narration": "One two. Three four."}, {"heading": "B", "narration": "Five six."}]}
    timings = tts.synthesize_script(script, tmp_path / "n.wav", FakeEngine())
    s = timings[0]["sentences"]
    assert s[0]["start"] == 0 and s[0]["end"] == pytest.approx(1.0)
    assert s[1]["start"] == pytest.approx(1.0 + tts.SENTENCE_PAUSE)
    assert timings[1]["start"] == pytest.approx(timings[0]["end"])
    with wave.open(str(tmp_path / "n.wav")) as w:
        assert w.getframerate() == 8000 and w.getnframes() / 8000 == pytest.approx(timings[-1]["end"], abs=0.01)


def test_make_engine_falls_back_to_piper_when_kokoro_is_unavailable(monkeypatch, capsys):
    class Boom:
        def __init__(self, *a, **k):
            raise OSError("model file missing")

    class FakePiper:
        name = "piper"

    monkeypatch.setattr(tts, "KokoroEngine", Boom)
    monkeypatch.setattr(tts, "PiperEngine", FakePiper)
    assert tts.make_engine({"voice_engine": "kokoro"}).name == "piper"
    assert "trying the next option" in capsys.readouterr().out
    assert tts.make_engine({}).name == "piper"  # default stays Piper until config says otherwise


def test_make_engine_uses_kokoro_settings(monkeypatch):
    seen = {}

    class FakeKokoro:
        name = "kokoro"

        def __init__(self, voice, speed):
            seen.update(voice=voice, speed=speed)

    monkeypatch.setattr(tts, "KokoroEngine", FakeKokoro)
    assert tts.make_engine({"voice_engine": "kokoro", "voice_name": "am_michael", "voice_speed": 1.2}).name == "kokoro"
    assert seen == {"voice": "am_michael", "speed": 1.2}


@pytest.mark.parametrize("style", sorted(music.STYLES))
def test_beat_music_has_requested_length_headroom_and_energy(tmp_path, style):
    p = music.generate_beat(12, tmp_path / "m.wav", seed=1, style=style)
    with wave.open(str(p)) as w:
        assert abs(w.getnframes() / music.RATE - 12) < 0.01
        x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2") / 32768
    assert np.abs(x).max() < 0.9 and np.sqrt((x ** 2).mean()) > 0.05  # audible and not clipped


def test_beat_music_is_deterministic_per_seed_and_varies_by_seed_and_style(tmp_path):
    a = music.generate_beat(6, tmp_path / "a.wav", seed=2, style="upbeat").read_bytes()
    assert a == music.generate_beat(6, tmp_path / "b.wav", seed=2, style="upbeat").read_bytes()
    assert a != music.generate_beat(6, tmp_path / "c.wav", seed=3, style="upbeat").read_bytes()
    assert a != music.generate_beat(6, tmp_path / "d.wav", seed=2, style="lofi").read_bytes()


def test_stage_picks_beat_or_ambient_music_from_config(tmp_path, monkeypatch):
    import sqlite3

    calls = []
    monkeypatch.setattr(stages.music, "generate_beat", lambda s, o, seed, style: calls.append(("beat", style)) or o)
    monkeypatch.setattr(stages.audio, "generate_ambient", lambda s, o, seed: calls.append(("ambient",)) or o)
    conn = sqlite3.connect(":memory:")
    for settings, expect in (({"music_style": "pulse"}, ("beat", "pulse")), ({}, ("ambient",)), ({"music_style": "ambient"}, ("ambient",))):
        cfg = Config(niche="s", audience="en", formats={}, audio=settings)
        stages.Stages(conn, cfg, root=tmp_path, work=tmp_path).make_music(tmp_path / "m.wav", 5, 1)
        assert calls[-1] == expect


@pytest.mark.skipif(not (shutil.which("ffmpeg") and shutil.which("ffprobe")), reason="needs ffmpeg")
def test_final_pass_with_music_produces_video_with_balanced_audio(tmp_path):
    from autopilot.render import _final_pass, write_ass

    music.generate_beat(6, tmp_path / "music.wav", seed=1, style="upbeat")
    with wave.open(str(tmp_path / "nar.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(22050)
        t = np.arange(22050 * 4) / 22050
        w.writeframes((np.sin(2 * np.pi * 220 * t) * 0.3 * 32767).astype("<i2").tobytes())
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "color=c=navy:s=320x180:d=4:r=24", "-pix_fmt", "yuv420p", str(tmp_path / "v.mp4")], check=True)
    (tmp_path / "clips.txt").write_text("file 'v.mp4'\n")
    write_ass([{"heading": "h", "start": 0, "end": 4, "sentences": [{"text": "Hi there.", "start": 0, "end": 2}]}], tmp_path / "c.ass")
    out = tmp_path / "out.mp4"
    _final_pass(tmp_path / "clips.txt", tmp_path / "nar.wav", tmp_path / "c.ass", out, tmp_path / "music.wav")
    info = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(out)], capture_output=True, text=True, check=True).stdout
    assert "audio" in info and "video" in info
    # measure the loudness actually delivered: the mix must land near the -16 LUFS target (and not clip)
    r = subprocess.run(["ffmpeg", "-i", str(out), "-af", "ebur128=peak=true", "-f", "null", "-"], check=False, capture_output=True, text=True)
    lufs = float(r.stderr.split("I:")[-1].split("LUFS")[0])
    assert -22 < lufs < -11


# ---------- voice rotation ----------
VOICES = [{"engine": "kokoro", "name": "bm_george"}, {"engine": "kokoro", "name": "am_michael"}, {"engine": "gemini", "name": "Sadachbia"}]


def test_pick_voice_is_deterministic_never_repeats_the_previous_video_and_uses_every_voice():
    picks = [tts.pick_voice(i, VOICES)["name"] for i in range(1, 61)]
    assert picks == [tts.pick_voice(i, VOICES)["name"] for i in range(1, 61)]      # same video, same voice
    assert all(a != b for a, b in itertools.pairwise(picks))             # never twice in a row
    assert set(picks) == {"bm_george", "am_michael", "Sadachbia"}                  # all three get used
    assert tts.pick_voice(5, VOICES[:1]) == VOICES[0]                              # a single voice is fine


def test_make_engine_picks_from_the_voices_list_and_falls_back_when_the_pick_cannot_start(monkeypatch, capsys):
    built = []

    class K:
        name = "kokoro"

        def __init__(self, voice, speed):
            built.append(("kokoro", voice))

    class G:
        name = "gemini"

        def __init__(self, voice):
            raise OSError("GEMINI_API_KEY is not set")

    monkeypatch.setattr(tts, "KokoroEngine", K)
    monkeypatch.setattr(tts, "GeminiEngine", G)
    settings = {"voices": VOICES, "fallback": {"engine": "kokoro", "name": "am_michael", "speed": 1.12}}
    for root in range(1, 25):
        engine = tts.make_engine(settings, root)
        assert engine.name == "kokoro"                                              # gemini picks degrade to kokoro
    assert {v for _, v in built} == {"bm_george", "am_michael"}
    assert "[tts] voice for this video:" in capsys.readouterr().out


# ---------- sentence timing for whole-section voices ----------
def test_align_sentences_places_boundaries_by_spoken_letters():
    sentences = ["Aaaa.", "Bbbbbbbb."]                                            # 4 and 8 letters -> boundary at 1/3
    words = [{"word": "aaaa", "start": 0.0, "end": 1.0}, {"word": "bbbb", "start": 1.2, "end": 2.2}, {"word": "bbbb", "start": 2.2, "end": 3.0}]
    spans = tts.align_sentences(sentences, words, 3.2)
    assert spans[0] == (0.0, 1.0) and spans[1][0] == 1.0 and spans[1][1] == 3.0


def test_align_sentences_without_words_falls_back_to_a_proportional_split():
    spans = tts.align_sentences(["Aaaa.", "Bbbbbbbb."], [], 3.0)
    assert spans[0][1] == pytest.approx(1.0) and spans[1] == (pytest.approx(1.0), pytest.approx(3.0))


def test_gemini_engine_returns_audio_with_aligned_sentence_spans(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    eng = tts.GeminiEngine("Sadachbia")
    monkeypatch.setattr(eng, "_speak", lambda text: b"\x01\x00" * 24000 * 2)       # 2 s of audio
    monkeypatch.setattr(tts, "_whisper_words", lambda wav: [{"word": "one", "start": 0, "end": 1.0}, {"word": "two", "start": 1, "end": 1.9}])
    pcm, rate, spans = eng.synth_section(["One.", "Two."])
    assert rate == 24000 and len(pcm) == 2 * 24000 * 2 and spans[0][1] == pytest.approx(1.0) and spans[1][1] == pytest.approx(1.9)


def test_gemini_engine_needs_a_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(OSError):
        tts.GeminiEngine()


def test_synthesize_script_supports_whole_section_engines_with_exact_offsets(tmp_path):
    class Section:
        name, whole_section = "sec", True

        def synth_section(self, sentences):
            return b"\x01\x00" * 8000 * 2, 8000, [(0.0, 0.9), (0.9, 2.0)]           # 2 s of audio, two sentences

    script = {"sections": [{"heading": "A", "narration": "One. Two."}, {"heading": "B", "narration": "One. Two."}]}
    timings = tts.synthesize_script(script, tmp_path / "n.wav", Section())
    assert timings[0]["sentences"][1]["start"] == pytest.approx(0.9)
    assert timings[1]["start"] == pytest.approx(2.0 + tts.SECTION_PAUSE)
    assert timings[1]["sentences"][0]["start"] == pytest.approx(timings[1]["start"])
    with wave.open(str(tmp_path / "n.wav")) as w:
        assert w.getnframes() / 8000 == pytest.approx(timings[-1]["end"], abs=0.02)


def test_a_failing_voice_redoes_the_whole_narration_with_the_fallback_never_mixing_voices(tmp_path, capsys):
    class Flaky:
        name, calls = "flaky", 0

        def synth(self, text):
            Flaky.calls += 1
            if Flaky.calls == 2:
                raise OSError("quota exhausted")
            return b"\x05\x00" * 8000, 8000

    class Fallback:
        name = "fallback"

        def synth(self, text):
            return b"\x09\x00" * 8000, 8000

    script = {"sections": [{"heading": "A", "narration": "One. Two. Three."}]}
    timings = tts.synthesize_script(script, tmp_path / "n.wav", Flaky(), Fallback())
    with wave.open(str(tmp_path / "n.wav")) as w:
        raw = w.readframes(w.getnframes())
    assert b"\x05\x00" not in raw and b"\x09\x00" in raw and len(timings[0]["sentences"]) == 3
    assert "redoing the whole narration with fallback" in capsys.readouterr().out
    with pytest.raises(OSError):
        Flaky.calls = 1
        tts.synthesize_script(script, tmp_path / "n2.wav", Flaky())                 # no fallback given: the error surfaces


def test_a_long_video_and_its_shorts_share_one_voice(tmp_path, monkeypatch):
    import sqlite3

    from autopilot import db

    seen = []
    monkeypatch.setattr(stages.tts, "make_engine", lambda settings, root: seen.append(root) or type("E", (), {"name": f"v{root}"})())
    conn = db.connect(tmp_path / "t.db")
    long_id = db.add_job(conn, "lasers", "long")
    short_id = db.add_job(conn, "kid", "short", parent_id=long_id, short_idx=0)
    cfg = Config(niche="s", audience="en", formats={}, audio={"voices": VOICES})
    st = stages.Stages(conn, cfg, root=tmp_path, work=tmp_path)
    j_long, j_short = (conn.execute("SELECT * FROM jobs WHERE id = ?", (i,)).fetchone() for i in (long_id, short_id))
    assert st.engine(j_long) is st.engine(j_short) and seen == [long_id]
    assert isinstance(sqlite3.connect(":memory:"), sqlite3.Connection)


def test_channel_config_lists_the_chosen_voices_and_keeps_the_liked_music():
    from autopilot.config import load_config

    cfg = load_config()
    names = [v["name"] for v in cfg.audio["voices"]]
    assert names == ["bm_george", "am_michael", "Sadachbia"] and cfg.audio["music_style"] == "ambient"
    assert cfg.audio["fallback"]["engine"] == "kokoro"


def test_voice_failing_on_the_very_first_call_still_falls_back_and_surfaces_the_real_error(tmp_path):
    """Gemini quota exhausted is exactly this case: nothing was ever written, and the file must close cleanly."""
    class Dead:
        name = "dead"

        def synth(self, text):
            raise OSError("quota exhausted")

    class Fine:
        name = "fine"

        def synth(self, text):
            return b"\x07\x00" * 8000, 8000

    script = {"sections": [{"heading": "A", "narration": "One. Two."}]}
    timings = tts.synthesize_script(script, tmp_path / "n.wav", Dead(), Fine())
    assert len(timings[0]["sentences"]) == 2
    with pytest.raises(OSError, match="quota exhausted"):                            # not a wave.Error in disguise
        tts.synthesize_script(script, tmp_path / "n2.wav", Dead())
