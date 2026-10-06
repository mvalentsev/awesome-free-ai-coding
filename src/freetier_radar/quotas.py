"""Sourced usage allowances, shared by the existing Limits surfaces and probes."""
from __future__ import annotations

import re
from datetime import date
from typing import TYPE_CHECKING, Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

if TYPE_CHECKING:
    from .models import Entry

UNKNOWN_RECHECK_DAYS = 7


def _numbers(text: str) -> set[float]:
    values = set()
    for m in re.finditer(r'(?<![\w.])([0-9][0-9,]*(?:\.[0-9]+)?(?:e[+-]?[0-9]+)?)\s*(million|thousand|[mk]\b)?', text, re.I):
        scale = {'million':1e6,'m':1e6,'thousand':1e3,'k':1e3}.get((m[2] or '').lower(),1)
        values.add(float(m[1].replace(',',''))*scale)
    return values


class UsageQuota(BaseModel):
    model_config = ConfigDict(extra='forbid')
    amount: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    unit: Literal['requests','tokens','neurons','credits','USD','tasks','one-hour sessions','list-price value','usage']
    period: Literal['minute','hour','day','week','month','one-time']
    window: int = Field(default=1, gt=0, exclude_if=lambda v: v == 1)
    rolling: bool = Field(default=False, exclude_if=lambda v: not v)
    scope: Literal['account','ip','account-model','project','key','unspecified']
    label: str = Field(default='', max_length=120, exclude_if=lambda v: not v)
    condition: str = Field(default='', max_length=200, exclude_if=lambda v: not v)
    condition_quote: str = Field(default='', exclude_if=lambda v: not v)
    reset: str = Field(default='', max_length=200, exclude_if=lambda v: not v)
    source: str
    quote: str = Field(min_length=3)
    value_phrase: str = Field(default='', exclude_if=lambda v: not v)
    read: Literal['page','catalog','constant'] = Field(default='page', exclude_if=lambda v: v == 'page')
    constant: str | None = None
    model_ids: list[str] = Field(default_factory=list, exclude_if=lambda v: not v)
    reviewed_on: date | None = None

    @field_validator('amount', mode='before')
    @classmethod
    def _numeric_amount(cls, value):
        if isinstance(value, bool):
            raise ValueError('quota.amount is a number, not a boolean')
        return value

    @field_validator('source')
    @classmethod
    def _http_source(cls, value):
        p = urlparse(value)
        if p.scheme not in ('http','https') or not p.hostname or p.username or p.password:
            raise ValueError('quota.source needs a public HTTP source without credentials')
        return value

    @model_validator(mode='after')
    def _evidence(self):
        if '…' in self.quote or '...' in self.quote:
            raise ValueError('quota.quote needs one complete source fragment')
        if self.amount is not None and self.amount not in _numbers(self.quote):
            raise ValueError('quota.amount is not a number in its source quote')
        if self.window > 1 and self.window not in _numbers(self.quote):
            raise ValueError('quota.window is not a number in its source quote')
        if bool(self.condition) != bool(self.condition_quote):
            raise ValueError('quota.condition needs its condition_quote')
        if not _numbers(self.condition).issubset(_numbers(self.quote + ' ' + self.condition_quote)):
            raise ValueError('quota condition numbers need source evidence')
        if self.amount is not None and self.read != 'constant':
            phrase = self.value_phrase
            if not phrase:
                numbers = re.findall(r'(?<![\w.])[0-9][0-9,]*(?:\.[0-9]+)?(?:e[+-]?[0-9]+)?', self.quote, re.I)
                if len(numbers) != 1:
                    raise ValueError('a multi-number quota quote needs a specific value_phrase')
                phrase = self.quote
            if ' '.join(phrase.casefold().split()) not in ' '.join(self.quote.casefold().split()):
                raise ValueError('quota.value_phrase must be part of its source quote')
            if self.amount not in _numbers(phrase):
                raise ValueError('quota.amount is not the number in its value_phrase')
            units = {'requests':r'\b(?:requests?|api calls?|req)\b', 'USD':r'\$',
                     'one-hour sessions':r'\bone.hour sessions?\b',
                     'list-price value':r'\b(?:list.price|value.based)\b'}.get(self.unit, r'\b' + self.unit + r'\b')
            periods = {'minute':r'\b(?:minutes?|min|rpm)\b', 'hour':r'\b(?:hours?|rph)\b',
                       'day':r'\b(?:days?|daily|rpd)\b', 'week':r'\b(?:weeks?|weekly)\b',
                       'month':r'\b(?:months?|monthly)\b', 'one-time':r'\b(?:one.time|sign.up|welcome)\b'}[self.period]
            if not re.search(units, phrase, re.I) or not re.search(periods, phrase, re.I):
                raise ValueError('quota unit and period need evidence in their source quote')
        if self.amount is None and self.reviewed_on is None:
            raise ValueError('an unpublished quota amount needs a dated review')
        if self.read == 'catalog' and not self.model_ids:
            raise ValueError('catalog quotas must name exact model_ids')
        if self.read == 'constant':
            if not self.constant or not re.fullmatch(r'[A-Za-z_$][\w$]*', self.constant):
                raise ValueError('constant quotas need a JavaScript constant name')
            if self.amount is None:
                raise ValueError('constant quotas need a numeric amount')
            for suffix, period in (('_RPM', 'minute'), ('_RPD', 'day')):
                if self.constant.endswith(suffix) and (self.unit != 'requests' or self.period != period):
                    raise ValueError('quota units do not match the source constant')
        elif self.constant is not None:
            raise ValueError('quota.constant requires read=constant')
        if self.period == 'one-time' and (self.window != 1 or self.rolling):
            raise ValueError('a one-time grant has no recurring or rolling window')
        return self


def quota_changes(body: str, quota: UsageQuota) -> list[str]:
    from .quotes import flatten, page_texts
    from .prober import _catalog_items, _model_id
    import httpx
    def found(text):
        return flatten(quota.quote) in flatten(text)
    if quota.read == 'catalog':
        try:
            response = httpx.Response(200, text=body)
            items = _catalog_items(response) or []
        except (ValueError, TypeError):
            items = []
        by_id = {_model_id(m): m for m in items}
        def evidenced(model):
            text = str(model.get('description') or model.get('desc') or '')
            return (found(text) and (not quota.reset or flatten(quota.reset) in flatten(text))
                    and (not quota.condition_quote or flatten(quota.condition_quote) in flatten(text)))
        return [f'{mid}: quota quote no longer in this model description' for mid in quota.model_ids
                if mid not in by_id or not evidenced(by_id[mid])]
    notes = []
    if not any(flatten(quota.quote) in text for text in page_texts(body)):
        notes.append('quota quote no longer on its source')
    if quota.reset and not any(flatten(quota.reset) in text for text in page_texts(body)):
        notes.append('quota reset no longer on its source')
    if quota.condition_quote and not any(flatten(quota.condition_quote) in text for text in page_texts(body)):
        notes.append('quota condition no longer on its source')
    if quota.read == 'constant':
        values = re.findall(r'\bconst\s+' + re.escape(quota.constant) + r'\s*=\s*([0-9]+(?:\.[0-9]+)?(?:e[+-]?[0-9]+)?)\s*[;,]', body, re.I)
        if not values:
            notes.append(f'quota constant {quota.constant} unreadable')
        elif any(float(value) != quota.amount for value in values):
            notes.append(f'quota constant {quota.constant}={", ".join(dict.fromkeys(values))} (recorded {quota.amount:g})')
    return notes


async def quota_moved(client, entry: Entry, probed, attempts: int, backoff: float, today: date) -> list[str]:
    from .prober import _page_beside
    pages, notes = {}, []
    for i, q in enumerate(entry.quotas):
        if q.source not in pages:
            pages[q.source] = await _page_beside(client, q.source, entry, probed, attempts, backoff)
        page, failure = pages[q.source]
        if page is None:
            notes.append(f'quotas[{i}] could not be checked against {q.source}: {failure}')
        else:
            notes.extend(f'quotas[{i}]: {n}' for n in quota_changes(page.text, q))
        if q.amount is None and (today - q.reviewed_on).days >= UNKNOWN_RECHECK_DAYS:
            notes.append(f'quotas[{i}]: unpublished amount needs a fresh dated review')
    return notes


SCOPE_WORDS = {'account':'per account','ip':'per IP','account-model':'per account per model',
               'project':'per project','key':'per key','unspecified':'scope not published'}
PERIOD_ADJECTIVES = {'minute':'Per-minute','hour':'Hourly','day':'Daily','week':'Weekly',
                     'month':'Monthly','one-time':'One-time'}


def quota_value(q: UsageQuota) -> str:
    periods = q.period if q.window == 1 else f'{q.window} {q.period}s'
    if q.rolling:
        periods = 'rolling ' + periods
    if q.amount is None:
        window = ('Rolling ' if q.rolling else '') + (f'{q.window}-{q.period}' if q.window != 1 else PERIOD_ADJECTIVES[q.period])
        return window + ' ' + q.unit + ' allowance: amount not published'
    amount = f'{q.amount:,.15g}'
    value = '$' + amount if q.unit == 'USD' else amount + ' ' + q.unit
    value += '' if q.period == 'one-time' else (' per ' if q.unit == 'one-hour sessions' else '/') + periods
    return value


def quota_words(q: UsageQuota) -> str:
    value = quota_value(q) + ('; ' if q.scope == 'unspecified' else ' ') + SCOPE_WORDS[q.scope]
    if q.label:
        value = q.label + ': ' + value
    if q.condition:
        value += ' (' + q.condition + ')'
    if q.reset:
        value += '. ' + q.reset
    return value


def structured_quotas(entry: Entry) -> list[dict]:
    rows = [{**q.model_dump(mode='json', exclude_none=True), 'amount': q.amount}
            for q in entry.quotas]
    if entry.page_catalog and entry.page_catalog.limited_allowance:
        quote = entry.page_catalog.limited_allowance
        m = re.fullmatch(r'(\d+) one-hour sessions per (day|week|month)', quote)
        if m:
            rows.append({'amount':int(m[1]),'unit':'one-hour sessions','period':m[2],
                         'scope':'account','label':'Session-based limited mode',
                         'source':entry.page_catalog.source,'quote':quote})
    return rows


def quota_summary(entry: Entry) -> str:
    groups = {}
    for row in structured_quotas(entry):
        q = UsageQuota.model_validate(row)
        key = (q.label, q.scope, q.condition, q.reset, tuple(q.model_ids))
        groups.setdefault(key, []).append(q)
    paragraphs = []
    for (label, scope, condition, reset, _), quotas in groups.items():
        words = []
        for q in quotas:
            words.append(quota_value(q))
        scoped = SCOPE_WORDS[scope]
        text = (label + ': ' if label else '') + '; '.join(words) + ('; ' if scope == 'unspecified' else ' ') + scoped
        if condition:
            text += ' (' + condition + ')'
        if reset:
            text += '. ' + reset
        paragraphs.append(text)
    return '\n\n'.join(paragraphs)
