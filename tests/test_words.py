"""The words a figure is put in, shared by the pages and the checks."""
from freetier_radar.words import number, ordinal, series, weeks


def test_a_figure_is_a_word_up_to_ten_and_digits_past_it():
    assert [number(n) for n in (1, 2, 10, 11)] == ["one", "two", "ten", "11"]
    assert [ordinal(n) for n in (1, 8, 12)] == ["first", "eighth", "12th"]


def test_a_span_is_weeks_where_it_is_whole_weeks():
    assert [weeks(d) for d in (7, 14, 10)] == ["a week", "two weeks", "10 days"]


def test_a_run_of_names_joins_the_last_with_its_conjunction():
    assert series(["a"]) == "a"
    assert series(["a", "b"]) == "a and b"
    assert series(["a", "b", "c"], "or") == "a, b or c"
