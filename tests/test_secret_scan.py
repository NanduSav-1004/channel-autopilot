import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("secret_scan", Path(__file__).parent.parent / "scripts" / "secret_scan.py")
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)


def test_finds_key_shaped_strings():
    # built at run time on purpose: a key-shaped literal in this file would trip the scanner on its own test
    text = "x " + "AIza" + "S" * 35 + " y " + "gsk" + "_" + "a" * 48 + " z " + "GOCSPX" + "-" + "b" * 28
    names = {n for n, _ in scan.find_secrets(text)}
    assert {"Google API key", "Groq API key", "Google OAuth client secret"} <= names


def test_ignores_ordinary_text_and_short_look_alikes():
    assert scan.find_secrets("AIza too short, gsk" + "_abc, 1//" + "0 nope, plain prose about keys") == []


def test_flags_files_that_must_never_be_tracked_but_allows_the_example():
    bad = scan.forbidden_files([".env", "secrets/token.json", "client_secret.json", "x/token_abc.json", ".env.example", "src/a.py"])
    assert bad == [".env", "secrets/token.json", "client_secret.json", "x/token_abc.json"]
