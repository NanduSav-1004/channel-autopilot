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


# ---------- word times ----------
def test_estimate_word_times_spread_a_sentence_in_order_over_its_span():
    words = tts.estimate_word_times("Hello there, general Kenobi.", 2.0, 4.0)
    assert [w["w"] for w in words] == ["Hello", "there,", "general", "Kenobi."]
    assert words[0]["s"] == pytest.approx(2.0) and words[-1]["e"] == pytest.approx(4.0)
    assert all(a["e"] == pytest.approx(b["s"]) for a, b in itertools.pairwise(words))
    assert tts.estimate_word_times("", 0, 1) == []


def test_refine_word_times_uses_what_whisper_heard_and_fills_in_what_it_missed():
    script = [{"w": "Dyson", "s": 0, "e": 0}, {"w": "sphere", "s": 0, "e": 0}, {"w": "began,", "s": 0, "e": 0}, {"w": "in", "s": 0, "e": 0}, {"w": "1937.", "s": 0, "e": 0}]
    heard = [{"word": "Dyson", "start": 0.10, "end": 0.40}, {"word": "sphere", "start": 0.45, "end": 0.90},
             {"word": "in", "start": 1.60, "end": 1.70}, {"word": "1937", "start": 1.75, "end": 2.20}]   # "began" was missed
    out = tts.refine_word_times(script, heard, 0.0, 2.5)
    assert out[0]["s"] == pytest.approx(0.10) and out[1]["s"] == pytest.approx(0.45) and out[3]["s"] == pytest.approx(1.60)
    assert 0.90 <= out[2]["s"] < 1.60 and out[2]["e"] <= 1.60 + 1e-6               # the missed word sits in the gap
    assert all(a["s"] <= b["s"] for a, b in itertools.pairwise(out))
    assert tts.refine_word_times(script, [], 0, 1) == script                         # nothing heard: leave the estimate


def test_clamp_words_keeps_them_inside_their_sentence_in_order():
    out = tts.clamp_words([{"w": "a", "s": 0.5, "e": 1.5}, {"w": "b", "s": 0.9, "e": 5.0}, {"w": "c", "s": 9.0, "e": 9.5}], 1.0, 3.0)
    assert out[0]["s"] == 1.0 and all(1.0 <= w["s"] <= 3.0 and w["e"] <= 3.0 + 1e-6 for w in out)
    assert all(a["s"] <= b["s"] for a, b in itertools.pairwise(out))


def test_synthesize_script_adds_word_times_to_every_sentence_even_without_whisper(tmp_path):
    script = {"sections": [{"heading": "A", "narration": "One two three. Four five."}]}
    timings = tts.synthesize_script(script, tmp_path / "n.wav", FakeEngine())      # the network is blocked in tests
    sents = timings[0]["sentences"]
    assert [len(s["words"]) for s in sents] == [3, 2]
    assert sents[0]["words"][0]["s"] == pytest.approx(sents[0]["start"])


def test_synthesize_script_uses_whisper_words_when_available(tmp_path, monkeypatch):
    monkeypatch.setattr(tts, "_whisper_words", lambda wav: [{"word": "One", "start": 0.05, "end": 0.3}, {"word": "two", "start": 0.4, "end": 0.7}, {"word": "three", "start": 0.8, "end": 1.0}])
    timings = tts.synthesize_script({"sections": [{"heading": "A", "narration": "One two three."}]}, tmp_path / "n.wav", FakeEngine())
    w = timings[0]["sentences"][0]["words"]
    assert w[1]["s"] == pytest.approx(0.4) and w[2]["s"] == pytest.approx(0.8)


# ---------- the voice must never be lost in the mix ----------
def _wav(path, seconds, loud=0.3, mute=()):
    """A mono 16 kHz tone; `mute` is a list of (start, end) seconds that are silent."""
    t = np.arange(int(16000 * seconds)) / 16000
    x = np.sin(2 * np.pi * 220 * t) * loud
    for a, b in mute:
        x[int(a * 16000):int(b * 16000)] = 0
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes((x * 32767).astype("<i2").tobytes())
    return path


needs_ffmpeg = pytest.mark.skipif(not (shutil.which("ffmpeg") and shutil.which("ffprobe")), reason="needs ffmpeg")


@needs_ffmpeg
def test_voice_losses_finds_the_moments_where_the_mix_dropped_the_voice(tmp_path):
    from autopilot import render

    ref = _wav(tmp_path / "ref.wav", 10)
    bad = _wav(tmp_path / "bad.wav", 10, mute=[(3.0, 5.0)])
    lost = render.voice_losses(ref, bad)
    assert lost and all(2.5 <= t <= 5.0 for t in lost) and len(lost) >= 3
    assert render.voice_losses(ref, _wav(tmp_path / "ok.wav", 10)) == []
    assert render.voice_losses(ref, _wav(tmp_path / "louder.wav", 10, loud=0.9)) == []   # extra music on top is fine
    # silence in the REFERENCE (no speech there) is never counted as a loss
    assert render.voice_losses(_wav(tmp_path / "r2.wav", 10, mute=[(3.0, 5.0)]), bad) == []


@needs_ffmpeg
def test_mix_audio_returns_a_verified_mix_the_length_of_the_narration(tmp_path):
    from autopilot import render

    nar = _wav(tmp_path / "n.wav", 6)
    music.generate_beat(8, tmp_path / "m.wav", seed=1, style="upbeat")
    how = render.mix_audio(nar, tmp_path / "m.wav", tmp_path / "out.wav")
    assert how == "music ducked"
    with wave.open(str(tmp_path / "out.wav")) as w:
        assert w.getframerate() == 48000 and abs(w.getnframes() / 48000 - 6) < 0.1


@needs_ffmpeg
def test_mix_audio_falls_back_to_a_simpler_mix_then_to_the_voice_alone_when_the_voice_is_lost(tmp_path, monkeypatch, capsys):
    from autopilot import render

    nar = _wav(tmp_path / "n.wav", 5)
    music.generate_beat(7, tmp_path / "m.wav", seed=1, style="lofi")
    verdicts = iter([[1.0, 1.5], []])                      # the first mix loses the voice, the simpler one is clean
    monkeypatch.setattr(render, "voice_losses", lambda ref, mixed: next(verdicts))
    assert render.mix_audio(nar, tmp_path / "m.wav", tmp_path / "a.wav") == "music steady"
    assert "trying a simpler mix" in capsys.readouterr().out
    monkeypatch.setattr(render, "voice_losses", lambda ref, mixed: [2.0])                # every mix loses it
    assert render.mix_audio(nar, tmp_path / "m.wav", tmp_path / "b.wav") == "voice only"
    assert "dropping the music" in capsys.readouterr().out
    assert render.mix_audio(nar, None, tmp_path / "c.wav") == "voice only"               # no music at all is fine too


# ---------- Gemini must not read its own direction aloud ----------
def _heard(spec):
    """[(word, start)] -> Whisper-style word dicts (each lasting 0.3 s)."""
    return [{"word": w, "start": s, "end": s + 0.3} for w, s in spec]


DIRECTION = [("Say", 0.3), ("this", 0.6), ("in", 0.9), ("an", 1.1), ("energetic", 1.3), ("voice", 2.0)]


def test_a_spoken_direction_is_cut_off_the_front_of_the_audio_and_the_words_are_shifted():
    pcm = b"\x01\x00" * 24000 * 6                                  # 6 s at 24 kHz
    words = _heard(DIRECTION + [("Can", 3.4), ("you", 3.7), ("cool", 4.0), ("it", 4.3)])
    out_pcm, out_words = tts.strip_spoken_direction(pcm, 24000, "Can you cool it?", words)
    cut = (len(pcm) - len(out_pcm)) / 2 / 24000
    assert cut == pytest.approx(3.34, abs=0.01)                      # everything before "Can" is gone
    assert out_words[0]["word"] == "Can" and out_words[0]["start"] == pytest.approx(0.06, abs=0.01)
    assert [w["word"] for w in out_words] == ["Can", "you", "cool", "it"]


def test_a_clean_start_is_left_untouched():
    pcm = b"\x01\x00" * 24000 * 3
    words = _heard([("Can", 0.1), ("you", 0.4), ("cool", 0.7), ("it", 1.0)])
    out_pcm, out_words = tts.strip_spoken_direction(pcm, 24000, "Can you cool it?", words)
    assert out_pcm == pcm and out_words == words


def test_audio_that_never_says_the_script_is_rejected_so_the_fallback_voice_takes_over():
    words = _heard([("Completely", 0.2), ("different", 0.6), ("words", 1.0), ("here", 1.4)])
    with pytest.raises(OSError, match="not found"):
        tts.strip_spoken_direction(b"\x00\x00" * 24000, 24000, "Can you cool it?", words)


def test_gemini_narration_that_cannot_be_verified_is_not_used(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    eng = tts.GeminiEngine("Sadachbia")
    monkeypatch.setattr(eng, "_speak", lambda text: b"\x01\x00" * 24000)
    monkeypatch.setattr(tts, "_whisper_words", lambda wav: [])      # Whisper down: cannot check what was spoken
    with pytest.raises(OSError, match="cannot verify"):
        eng.synth_section(["One two three."])


def test_gemini_section_with_a_spoken_direction_comes_back_clean_and_correctly_timed(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    eng = tts.GeminiEngine("Sadachbia")
    monkeypatch.setattr(eng, "_speak", lambda text: b"\x01\x00" * 24000 * 8)       # 8 s of audio
    heard = _heard(DIRECTION + [("Hot", 3.4), ("water", 3.8), ("freezes.", 4.2), ("Why", 5.4), ("though?", 5.8)])
    monkeypatch.setattr(tts, "_whisper_words", lambda wav: heard)
    pcm, rate, spans = eng.synth_section(["Hot water freezes.", "Why though?"])
    assert len(pcm) / 2 / rate == pytest.approx(8 - 3.34, abs=0.02)
    assert spans[0][0] == 0.0 and 1.0 < spans[0][1] < 2.4 and spans[1][1] == pytest.approx(2.76, abs=0.05)  # ends where the last word ends


def test_the_gemini_direction_is_short_and_ends_with_a_clear_break_before_the_script():
    assert len(tts.GEMINI_STYLE.split()) <= 16 and tts.GEMINI_STYLE.endswith("\n\n")
    assert "Read the following" not in tts.GEMINI_STYLE and "Text:" not in tts.GEMINI_STYLE


def test_sentence_boundaries_follow_the_words_even_when_digits_stand_for_spoken_numbers():
    sentences = ["Saltwater makes up 97.5 percent of that total.", "Fresh water is just 2.5 percent."]
    heard = [("saltwater", 0.0, 0.5), ("makes", 0.5, 0.8), ("up", 0.8, 0.9), ("97.5%", 0.9, 2.7), ("of", 2.7, 2.9), ("that", 2.9, 3.1), ("total.", 3.1, 3.6),
             ("Fresh", 4.0, 4.3), ("water", 4.3, 4.6), ("is", 4.6, 4.7), ("just", 4.7, 4.9), ("2.5%", 4.9, 6.2)]
    words = [{"word": w, "start": s, "end": e} for w, s, e in heard]
    spans = tts.align_sentences(sentences, words, 6.4)
    assert spans[0][0] == 0.0 and spans[0][1] == pytest.approx(3.8, abs=0.05) and spans[1] == (spans[0][1], pytest.approx(6.2))


def test_sentence_boundaries_fall_back_to_letters_when_nothing_matches_or_the_text_is_not_latin():
    words = [{"word": "zzz", "start": 0.0, "end": 1.0}, {"word": "yyy", "start": 1.0, "end": 3.0}]
    assert tts._boundaries_by_words(["Aaaa bbbb.", "Cccc dddd."], words, 3.0) is None
    assert tts._boundaries_by_words(["പൂർണ്ണ വീഡിയോ.", "ചാനലിൽ കാണാം."], words, 3.0) is None
    spans = tts.align_sentences(["Aaaa bbbb.", "Cccc dddd."], words, 3.0)          # still works through the old letter-count path
    assert spans[0][0] == 0.0 and spans[1][1] == 3.0
