import pytest

from autopilot.speech import int_words, speech_text, year_words


@pytest.mark.parametrize("text,spoken", [
    ("Jupiter is 1.2 times wider.", "Jupiter is one point two times wider."),
    ("It has 1,325 moons.", "It has one thousand three hundred twenty-five moons."),
    ("142,976 kilometers across.", "one hundred forty-two thousand nine hundred seventy-six kilometers across."),
    ("Saltwater is 97.5% of it.", "Saltwater is ninety-seven point five percent of it."),
    ("It fell -54%.", "It fell minus fifty-four percent."),
    ("An egg cost $6.23.", "An egg cost six dollars and twenty-three cents."),
    ("$1.5 trillion in debt.", "one point five trillion dollars in debt."),
    ("1.386 billion cubic kilometres", "one point three eight six billion cubic kilometres"),
    ("0.3% of it", "zero point three percent of it"),
])
def test_numbers_are_written_out_for_the_voice(text, spoken):
    assert speech_text(text) == spoken


def test_years_and_decades_are_read_as_years():
    assert year_words(1905) == "nineteen oh five" and year_words(1960) == "nineteen sixty" and year_words(2023) == "twenty twenty-three"
    assert year_words(2005) == "two thousand five" and year_words(1900) == "nineteen hundred"
    assert speech_text("In 1905 and the 1960s and the 2000s.") == "In nineteen oh five and the nineteen sixties and the two thousands."


def test_codes_and_words_with_digits_are_left_alone():
    assert speech_text("H2O and CO2 and 3D") == "H2O and CO2 and 3D"
    assert speech_text("No numbers here.") == "No numbers here."


def test_int_words_covers_big_numbers():
    assert int_words(0) == "zero" and int_words(21) == "twenty-one" and int_words(100) == "one hundred"
    assert int_words(1_000_000) == "one million" and int_words(2_500_000_300) == "two billion five hundred million three hundred"
