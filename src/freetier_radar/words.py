"""How the pages and the checks put a figure into words: a count, an ordinal, a
span of days, a run of names.

The render prints a rule's figure from its constant ("where two rows or more
serve it free"), and `claims` holds a hand-written sentence to the same
constant. Each kept its own table of number words until 2026-09-26, and two
tables are two answers: a constant moved to six would have been "six" in
CONTRIBUTING, held there by its claim, and "6" on every page the render
wrote. One table here, for both.
"""
from __future__ import annotations

__all__ = ["number", "ordinal", "weeks", "series"]

_NUMBERS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
            8: "eight", 9: "nine", 10: "ten"}
_ORDINALS = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth",
             7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth"}
_WEEKS = {7: "a week", 14: "two weeks", 21: "three weeks", 28: "four weeks"}


def number(n: int) -> str:
    """"two"; a figure past ten as digits."""
    return _NUMBERS.get(n, str(n))


def ordinal(n: int) -> str:
    return _ORDINALS.get(n, f"{n}th")


def weeks(days: int) -> str:
    """"two weeks"; a span that is not whole weeks as days."""
    return _WEEKS.get(days, f"{days} days")


def series(names: list[str], conjunction: str = "and") -> str:
    """"a", "a and b", "a, b and c" — or "or" in place of "and"."""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + f" {conjunction} " + names[-1]
