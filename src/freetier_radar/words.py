"""How the pages and the checks put things into words: a count, an ordinal, a
span of days, a run of names, and a sentence cut to the room it has.

The render prints a rule's figure from its constant ("where two rows or more
serve it free"), and `claims` holds a hand-written sentence to the same
constant. Both take their words from here, so a figure is spelled one way on
the pages and in CONTRIBUTING. A page's description, a post and a line of the
scout's PR cut a long sentence here too, so each cut reads the same.
"""
from __future__ import annotations

__all__ = ["number", "ordinal", "weeks", "series", "clip"]

_NUMBERS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
            8: "eight", 9: "nine", 10: "ten"}
_ORDINALS = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth",
             7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth"}
_WEEKS = {7: "a week", 14: "two weeks", 21: "three weeks", 28: "four weeks"}


def number(n: int) -> str:
    """"two"; a figure past ten as digits."""
    return _NUMBERS.get(n, str(n))


def ordinal(n: int) -> str:
    """"eighth"; past ten as digits with their suffix — 21st, 112th."""
    if n in _ORDINALS:
        return _ORDINALS[n]
    suffix = "th" if n % 100 in (11, 12, 13) else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def weeks(days: int) -> str:
    """"two weeks"; a span that is not whole weeks as days."""
    return _WEEKS.get(days, f"{days} days")


def series(names: list[str], conjunction: str = "and") -> str:
    """"a", "a and b", "a, b and c" — or "or" in place of "and"."""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + f" {conjunction} " + names[-1]


def clip(text: str, room: int) -> str:
    """`text` with its whitespace collapsed, in at most `room` characters: cut
    at the last word that fits beside the "…" marking the cut, without the
    punctuation the cut leaves dangling. A first word longer than the room is
    cut where the room ends."""
    text = " ".join(text.split())
    if len(text) <= room:
        return text
    if room <= 1:
        return "…"
    cut = text.rfind(" ", 0, room - 1)
    return text[:cut if cut > 0 else room - 1].rstrip(" ,;:.—-") + "…"
