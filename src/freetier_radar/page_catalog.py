"""Read and present a page's credit budgets and complete model picker.

The configurable contract is a headed HTML hours list plus named JSON-LD FAQ
answers. Freebuff publishes this shape at https://freebuff.com/ (read
2026-10-06); the fixture uses different vendor/model names. Framework state and
unrelated model illustrations are deliberately outside the hours table.
"""
from __future__ import annotations

import html
import json
import re
from html.parser import HTMLParser

from .countries import country_name
from .models import Entry, PageCatalog, PageModel, access_words


def clean(text: str) -> str:
    return " ".join(html.unescape(text).split())


class _Page(HTMLParser):
    def __init__(self, body: str):
        super().__init__(convert_charrefs=True)
        self.position = 0
        self.open: list[dict] = []
        self.nodes: list[tuple[int, str, str]] = []
        self.visible: list[str] = []
        self.faq: dict[str, list[str]] = {}
        self.script: list[str] | None = None
        self.structured = False
        self.style = False
        self.feed(body)
        self.close()

    def handle_starttag(self, tag, attrs):
        self.position += 1
        if tag == "script":
            self.script = []
            self.structured = dict(attrs).get("type", "").lower() == "application/ld+json"
        elif tag == "style":
            self.style = True
        elif tag == "li" or re.fullmatch(r"h[1-6]", tag) or tag == "p":
            self.open.append({"tag": tag, "at": self.position, "parts": []})

    def handle_data(self, data):
        if self.script is not None:
            self.script.append(data)
        elif not self.style:
            self.visible.append(data)
            for node in self.open:
                node["parts"].append(data)

    def handle_endtag(self, tag):
        if tag == "script":
            if self.structured and self.script is not None:
                try:
                    self._questions(json.loads("".join(self.script)))
                except (ValueError, TypeError):
                    pass
            self.script = None
            self.structured = False
        elif tag == "style":
            self.style = False
        else:
            for i in range(len(self.open) - 1, -1, -1):
                node = self.open[i]
                if node["tag"] == tag:
                    self.nodes.append((node["at"], tag, clean(" ".join(node["parts"]))))
                    self.open.pop(i)
                    break

    def _questions(self, value):
        if isinstance(value, list):
            for item in value:
                self._questions(item)
        elif isinstance(value, dict):
            if value.get("@type") == "Question" and isinstance(value.get("name"), str):
                answer = value.get("acceptedAnswer")
                if isinstance(answer, dict) and isinstance(answer.get("text"), str):
                    self.faq.setdefault(clean(value["name"]).casefold(), []).append(answer["text"])
            for item in value.values():
                if isinstance(item, (list, dict)):
                    self._questions(item)

    def answer(self, question: str) -> str | None:
        answers = self.faq.get(clean(question).casefold(), [])
        return answers[0] if answers and len(set(answers)) == 1 else None

    def table(self, heading: str) -> list[tuple[int, str, str]] | None:
        headings = [(at, tag, text) for at, tag, text in self.nodes if tag.startswith("h")]
        found = [at for at, _, text in headings if text.casefold() == clean(heading).casefold()]
        if len(found) != 1:
            return None
        start = found[0]
        end = min((at for at, _, _ in headings if at > start), default=self.position + 1)
        return sorted(n for n in self.nodes if start < n[0] < end)


def _budgets(answer: str, catalog: PageCatalog) -> dict[str, int] | None:
    result: dict[str, int] = {}
    saw_unit = False
    for line in answer.splitlines():
        match = re.fullmatch(r"\s*-\s*([^:]+):\s*([0-9]+)(.*)", line)
        if not match:
            continue
        scope, amount, tail = match.groups()
        if scope.casefold() == "everywhere else":
            keys = ["else"]
        elif scope.casefold() == "any vpn or proxy":
            keys = ["vpn"]
        elif re.fullmatch(r"[A-Z]{2}(?:,\s*[A-Z]{2})*", scope):
            keys = scope.split(",")
            keys = [c.strip() for c in keys]
            if tail.strip():
                if not re.fullmatch(rf"\s+{re.escape(catalog.unit)}\s+(?:a|per)\s+{catalog.period}", tail, re.I):
                    return None
                saw_unit = True
        else:
            return None
        for key in keys:
            if key in result:
                return None
            result[key] = int(amount)
    return result if result and saw_unit else None


def _differences(label: str, expected: set[str], actual: set[str]) -> list[str]:
    out = []
    if expected - actual:
        out.append(f"{label} missing: {', '.join(sorted(expected - actual))}")
    if actual - expected:
        out.append(f"{label} added: {', '.join(sorted(actual - expected))}")
    return out


def check_page_catalog(body: str, catalog: PageCatalog) -> list[str]:
    """Notes for a reviewer; a changed price does not end the whole service."""
    from .quotes import page_texts, quote_found
    page = _Page(body)
    notes = []
    answer = page.answer(catalog.read.budgets_question)
    actual = _budgets(answer, catalog) if answer is not None else None
    expected = {key: b.amount for b in catalog.budgets
                for key in (b.countries if b.scope == "countries" else [b.scope])}
    if actual is None:
        notes.append("budgets unreadable in the configured FAQ answer")
    else:
        notes += _differences("budget scopes", set(expected), set(actual))
        notes += [f"budget {key}: {actual[key]} (recorded {amount})"
                  for key, amount in expected.items() if key in actual and actual[key] != amount]

    table = page.table(catalog.read.table_heading)
    hours = {}
    if table is not None:
        for _, tag, text in table:
            if tag != "li":
                continue
            match = re.fullmatch(r"(?:∞\s*)?(Unlimited|[0-9]+)\s+(?:hrs?|hours?)\s+(.+)", text, re.I)
            if match is None or match[2].casefold() in hours:
                notes.append("hours table has an unreadable or duplicate row")
                continue
            hours[match[2].casefold()] = "unlimited" if match[1].casefold() == "unlimited" else int(match[1])
    if not hours:
        notes.append("hours table unreadable at the configured heading")
    else:
        expected_hours = {m.name.casefold(): m.hours for m in catalog.models if m.hours is not None and not m.expired}
        notes += _differences("hours table models", set(expected_hours), set(hours))
        notes += [f"hours {name}: {hours[name]} (recorded {amount})"
                  for name, amount in expected_hours.items() if name in hours and hours[name] != amount]
        example = next(b for b in catalog.budgets if b.id == catalog.example_budget)
        pattern = rf"\b([0-9]+)\s+{re.escape(catalog.unit)}\s+(?:every|per|a)\s+{catalog.period}\b"
        amounts = [int(m[1]) for _, tag, text in table if tag == "p" for m in re.finditer(pattern, text, re.I)]
        if amounts != [example.amount]:
            notes.append(f"hours example budget: {amounts or 'unreadable'} (recorded {example.amount})")

    answer = page.answer(catalog.read.models_question)
    roster = [clean(line.lstrip()[2:].split(":", 1)[0]).casefold()
              for line in (answer or "").splitlines() if line.lstrip().startswith("- ") and ":" in line]
    if not roster or len(set(roster)) != len(roster):
        notes.append("model picker unreadable in the configured FAQ answer")
    else:
        expected_roster = {m.name.casefold() for m in catalog.models if not m.expired and (
            m.condition is None or catalog.conditions[m.condition].kind != "specialist")}
        notes += _differences("model picker", expected_roster, set(roster))

    answer = page.answer(catalog.read.limited_question)
    before, separator, after = clean(answer or "").casefold().partition(catalog.read.limited_prefix.casefold())
    selected, end, _ = after.partition(catalog.read.limited_suffix.casefold())
    if not separator or not end:
        notes.append("limited-access models unreadable in the configured FAQ answer")
    else:
        limited = {clean(n) for n in re.split(r",\s*|\s+and\s+", selected) if clean(n)}
        notes += _differences("limited-access models", {m.name.casefold() for m in catalog.models
                                                       if m.limited and not m.expired}, limited)
    evidence = [" ".join(page.visible), *[answer for answers in page.faq.values() for answer in answers]]
    pages = [text for part in evidence for text in page_texts(part)]
    notes += [f"{field} no longer evidenced" for field, quote in catalog_quotes(catalog)
              if not quote_found(quote, pages)]
    return notes


def catalog_quotes(catalog: PageCatalog) -> list[tuple[str, str]]:
    return [(f"page_catalog.conditions.{key}.quote", c.quote) for key, c in catalog.conditions.items()] + [
        (f"page_catalog.notes[{i}]", quote) for i, quote in enumerate(catalog.notes)]


def funding(catalog: PageCatalog, model: PageModel) -> str:
    if model.expired:
        return "expired"
    if model.hours == "unlimited":
        return "unmetered"
    if model.hours is not None:
        return "wallet"
    return catalog.conditions[model.condition].kind


FUNDING_WORDS = {"wallet": "Shared daily credits", "unmetered": "Unmetered offer",
                 "free-session": "Free session with conditions", "paid": "Paid plan",
                 "specialist": "Specialist tasks only", "expired": "Offer ended"}


PERIOD_WORDS = {"day": "Daily", "week": "Weekly", "month": "Monthly"}


def funding_words(catalog: PageCatalog, model: PageModel) -> str:
    if funding(catalog, model) == "wallet":
        return f"Shared {PERIOD_WORDS[catalog.period].lower()} credits"
    return FUNDING_WORDS[funding(catalog, model)]


def offer_access(catalog: PageCatalog, model: PageModel) -> str:
    access = catalog.model_access.get(model.name)
    if not access:
        return ""
    text = access_words(access)
    if model.expired:
        text = text.replace("free until ", "offer ended ")
    return f"{text} ([terms]({access.source}))"


def budget_scope(budget) -> str:
    return (", ".join(country_name(c) for c in budget.countries) if budget.scope == "countries" else
            "Other countries" if budget.scope == "else" else "VPN or proxy")


def catalog_words(catalog: PageCatalog) -> str:
    """One text presentation, reused by the site, JSON, browse and llms.txt."""
    budgets = []
    for b in catalog.budgets:
        budgets.append(f"{budget_scope(b)}: {b.amount} {catalog.unit} per {catalog.period}")
    example = next(b for b in catalog.budgets if b.id == catalog.example_budget)
    scope = budget_scope(example)
    offers = []
    for m in catalog.models:
        kind = funding(catalog, m)
        text = f"{m.name}: {funding_words(catalog, m).lower()}"
        if m.hours is not None and not m.expired:
            text += "; unlimited hours" if m.hours == "unlimited" else f"; {m.hours} hours with the whole {example.amount}-{catalog.unit} allowance"
        if kind in ("wallet", "unmetered"):
            text += "; available in limited mode" if m.limited else "; full access only"
        if access := offer_access(catalog, m):
            text += "; " + access
        offers.append(text)
    out = (PERIOD_WORDS[catalog.period] + " allowance — " + "; ".join(budgets) + ".\n\n"
           f"Credit-funded hour examples use the whole {scope} allowance on one model; they are not added together. "
           + "; ".join(offers) + ".")
    if catalog.conditions:
        out += "\n\n" + " ".join(c.quote for c in catalog.conditions.values())
    if catalog.notes:
        out += "\n\n" + " ".join(catalog.notes)
    return out + f" ([source]({catalog.source}))."


def catalog_markdown(catalog: PageCatalog) -> list[str]:
    """Provider-page tables from the same facts as the text presentation."""
    example = next(b for b in catalog.budgets if b.id == catalog.example_budget)
    out = [f"## {PERIOD_WORDS[catalog.period]} allowance", "", f"| Where | {catalog.unit} per {catalog.period} |", "| --- | ---: |"]
    out += [f"| {budget_scope(b)} | {b.amount} |" for b in catalog.budgets]
    out += ["", "## Models and access", "",
            f"Hours for credit-funded models use the entire {PERIOD_WORDS[catalog.period].lower()} allowance "
            f"for {budget_scope(example)} ({example.amount} {catalog.unit}) on one model. "
            "They are alternative choices, not separate grants.", "",
            "| Model | Access | Hours | Free limited mode |", "| --- | --- | ---: | --- |"]
    for m in catalog.models:
        kind = funding(catalog, m)
        access = funding_words(catalog, m)
        if detail := offer_access(catalog, m):
            access += "; " + detail
        hours = "Unlimited" if m.hours == "unlimited" else str(m.hours) if m.hours else "—"
        if m.expired:
            hours = "—"
        limited = "Yes" if m.limited and not m.expired else "—"
        out.append(f"| {m.name} | {access} | {hours} | {limited} |")
    out += ["", *[c.quote + "\n" for c in catalog.conditions.values()],
            *[quote + "\n" for quote in catalog.notes], f"[Source and current selection]({catalog.source}).", ""]
    return out


def limits_text(entry: Entry) -> str:
    return "\n\n".join(t for t in (entry.limits, catalog_words(entry.page_catalog) if entry.page_catalog else "") if t)


def family_condition(entry: Entry, family: str) -> str:
    if entry.page_catalog:
        for m in entry.page_catalog.models:
            if m.model and m.model.family == family and m.listed and m.condition:
                return entry.page_catalog.conditions[m.condition].quote
    return ""
