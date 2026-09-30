"""The words a figure is put in, shared by the pages and the checks."""
from freetier_radar.words import clip, number, ordinal, series, weeks


def test_a_figure_is_a_word_up_to_ten_and_digits_past_it():
    assert [number(n) for n in (1, 2, 10, 11)] == ["one", "two", "ten", "11"]
    assert [ordinal(n) for n in (1, 8, 12)] == ["first", "eighth", "12th"]
    assert [ordinal(n) for n in (21, 22, 23, 24, 111, 112, 113, 101)] == [
        "21st", "22nd", "23rd", "24th", "111th", "112th", "113th", "101st"]


def test_a_span_is_weeks_where_it_is_whole_weeks():
    assert [weeks(d) for d in (7, 14, 10)] == ["a week", "two weeks", "10 days"]


def test_a_run_of_names_joins_the_last_with_its_conjunction():
    assert series(["a"]) == "a"
    assert series(["a", "b"]) == "a and b"
    assert series(["a", "b", "c"], "or") == "a, b or c"


def test_a_sentence_is_cut_at_a_word_within_its_room():
    """The whitespace collapses, a sentence that fits is left whole, and one
    that does not ends at a word with "…", the dangling comma dropped, in no
    more than the room."""
    assert clip("  one\n two  ", 20) == "one two"
    assert clip("alpha beta, gamma delta", 15) == "alpha beta…"
    assert all(len(clip("alpha beta, gamma delta", room)) <= room for room in range(1, 25))
    assert clip("supercalifragilistic", 8) == "superca…"
    assert clip("anything at all", 1) == "…"
