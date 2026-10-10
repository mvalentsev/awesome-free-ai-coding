"""Sourced usage allowances, shared by the existing Limits surfaces and probes."""
from __future__ import annotations

import re
from html.parser import HTMLParser
from datetime import date
from typing import TYPE_CHECKING, Literal
from .source_urls import valid_source_url

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

if TYPE_CHECKING:
    from .models import Entry

UNKNOWN_RECHECK_DAYS = 7


class QuotaCatalogField(BaseModel):
    model_config = ConfigDict(extra='forbid')
    collection: str = Field(pattern=r'^[A-Za-z_][\w]*$')
    where: dict[str,str] = Field(min_length=1)
    field: Literal['rpm','rpd','tpm','tpd','rps']


class QuotaTable(BaseModel):
    model_config = ConfigDict(extra='forbid')
    headers: list[str] = Field(min_length=2)
    column: str
    rows: list[str] = Field(min_length=1)
    row_column: int = Field(default=0, ge=0)
    where: dict[str,str] = Field(default_factory=dict)
    cell_part: str = ''
    active_tab: str = ''
    active_class: str = ''

    @model_validator(mode='after')
    def _binding(self):
        if len(set(self.headers)) != len(self.headers) or self.column not in self.headers[1:]:
            raise ValueError('quota table needs unique headers and a value column')
        if self.row_column >= len(self.headers):
            raise ValueError('quota table row column is outside the headers')
        if set(self.where) - set(self.headers):
            raise ValueError('quota table row conditions need named columns')
        if bool(self.active_tab) != bool(self.active_class):
            raise ValueError('quota table selected tab needs its exact class')
        return self


class _Tables(HTMLParser):
    """Keep cells, headers and selected tabs together, including split tables."""
    def __init__(self):
        super().__init__()
        self.tables, self.current, self.row, self.cell, self.button = [], None, None, None, None
        self.stack, self.spans = [], {}

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        semantic = {'table':'table','row':'tr','columnheader':'th','cell':'td'}.get(attributes.get('role'),tag)
        if tag not in ('area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'):
            self.stack.append(semantic)
        tag = semantic
        if tag == 'table':
            self.current = {'headers': [], 'rows': [], 'tabs': []}
            self.spans = {}
        elif self.current is not None:
            if tag == 'tr':
                self.row = []
            elif tag in ('th','td') and self.row is not None:
                self.cell = [tag, [], int(attributes.get('rowspan','1')), int(attributes.get('colspan','1'))]
            elif tag == 'button':
                self.button = [dict(attrs).get('class','').split(), []]

    def handle_data(self, data):
        if self.cell is not None:
            self.cell[1].append(data)
        if self.button is not None:
            self.button[1].append(data)

    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in ('area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'):
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        tag = self.stack.pop() if self.stack else tag
        if self.current is None:
            return
        if tag == 'button' and self.button is not None:
            self.current['tabs'].append((self.button[0], ' '.join(''.join(self.button[1]).split())))
            self.button = None
        elif tag in ('th','td') and self.cell is not None:
            self.row.append((self.cell[0], ' '.join(''.join(self.cell[1]).split()),self.cell[2],self.cell[3]))
            self.cell = None
        elif tag == 'tr' and self.row is not None:
            expanded, column = [], 0
            def carried():
                nonlocal column
                while column in self.spans:
                    value, left = self.spans[column]
                    expanded.append(value)
                    if left == 1:del self.spans[column]
                    else:self.spans[column] = (value,left-1)
                    column += 1
            for _,value,rows,cols in self.row:
                carried()
                for _ in range(cols):
                    expanded.append(value)
                    if rows > 1:self.spans[column] = (value,rows-1)
                    column += 1
            carried()
            if self.row and all(cell[0] == 'th' for cell in self.row):
                self.current['headers'] = expanded
            elif expanded:
                self.current['rows'].append(expanded)
            self.row = None
        elif tag == 'table':
            self.tables.append(self.current)
            self.current, self.row, self.cell, self.button = None, None, None, None


def _table_changes(body: str, quota: UsageQuota) -> list[str]:
    parser = _Tables()
    try:parser.feed(body)
    except (ValueError,TypeError):return ['quota table markup is unreadable']
    binding = quota.table
    header, tabs, matches = [], [], []
    tables = parser.tables
    if not tables:
        lines = body.splitlines()
        for i,line in enumerate(lines[:-1]):
            if '|' in line and re.fullmatch(r'[\s|:\-]+',lines[i+1]) and '-' in lines[i+1]:
                def cells(value):return [v.strip().strip('`*') for v in value.strip().strip('|').split('|')]
                rows = []
                for next_line in lines[i+2:]:
                    if '|' not in next_line:break
                    rows.append(cells(next_line))
                tables.append({'headers':cells(line),'rows':rows,'tabs':[]})
    for table in tables:
        if table['headers']:
            header, tabs = table['headers'], table['tabs']
        if header != binding.headers:
            continue
        if binding.active_tab and not any(binding.active_class in classes and text == binding.active_tab
                                          for classes, text in tabs):
            continue
        column = header.index(binding.column)
        for row in table['rows']:
            if any(header.index(name) >= len(row) or row[header.index(name)] != value
                   for name,value in binding.where.items()):
                continue
            if len(row) > binding.row_column and row[binding.row_column] in binding.rows:
                matches.append((row[binding.row_column], row[column] if column < len(row) else ''))
    notes = []
    for row in binding.rows:
        values = [value for name, value in matches if name == row]
        cell = binding.cell_part or (values[0] if len(values) == 1 else '')
        if len(values) != 1 or (binding.cell_part and binding.cell_part not in values[0]) or _numbers(cell) != {quota.amount}:
            notes.append(f'quota table {row} / {binding.column}: changed, ambiguous or unreadable cell')
    return notes


def _numbers(text: str) -> set[float]:
    values = set()
    for m in re.finditer(r'(?<![a-zA-Z0-9_.])([0-9][0-9,]*(?:\.[0-9]+)?(?:e[+-]?[0-9]+)?)\s*(million|thousand|[mk]\b|万)?', text, re.I):
        scale = {'million':1e6,'m':1e6,'thousand':1e3,'k':1e3,'万':1e4}.get((m[2] or '').lower(),1)
        values.add(float(m[1].replace(',',''))*scale)
    words = {'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,
             'nine':9,'ten':10,'eleven':11,'twelve':12,'fifteen':15,'twenty':20}
    for m in re.finditer(r'\b('+'|'.join(words)+r')[ -]+(?:(?:concurrent|free)\s+)?(requests?|calls?|credits?|tasks?|days?|weeks?|months?|hours?|dollars?|tokens?)\b',text,re.I):
        values.add(words[m[1].lower()])
    return values


class UsageQuota(BaseModel):
    model_config = ConfigDict(extra='forbid')
    amount: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    unit: Literal['requests','tokens','neurons','credits','USD','tasks','one-hour sessions','list-price value','usage',
                  'messages','completions','edit predictions','points','CUH','input tokens','output tokens',
                  'Hypercredits','weighted units','interactions','INR']
    period: Literal['second','minute','hour','day','week','month','one-time','concurrent'] | None = None
    window: int = Field(default=1, gt=0, exclude_if=lambda v: v == 1)
    rolling: bool = Field(default=False, exclude_if=lambda v: not v)
    scope: Literal['account','ip','account-model','project','key','unspecified','ip-model',
                   'organization','organization-model','project-model','key-model','plan','team','endpoint','disputed']
    state: Literal['variable','unmetered','account-specific','disputed'] | None = None
    label: str = Field(default='', max_length=120, exclude_if=lambda v: not v)
    condition: str = Field(default='', max_length=200, exclude_if=lambda v: not v)
    condition_quote: str = Field(default='', exclude_if=lambda v: not v)
    reset: str = Field(default='', max_length=200, exclude_if=lambda v: not v)
    source: str
    quote: str = Field(min_length=3)
    value_phrase: str = Field(default='', exclude_if=lambda v: not v)
    period_quote: str = Field(default='', exclude_if=lambda v: not v)
    read: Literal['page','catalog','constant','table','catalog-field'] = Field(default='page', exclude_if=lambda v: v == 'page')
    constant: str | None = None
    table: QuotaTable | None = None
    catalog_field: QuotaCatalogField | None = None
    follow: dict[str,str] | None = None
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
        if not valid_source_url(value, schemes=('http','https')):
            raise ValueError('quota.source needs a public HTTP source without credentials')
        return value

    @field_validator('follow')
    @classmethod
    def _source_index(cls, value):
        if value is None:return value
        from .models import Follow
        if set(value) - {'field','suffix'}:
            raise ValueError('quota source index accepts only field and suffix')
        return Follow.model_validate(value).model_dump()

    @model_validator(mode='after')
    def _evidence(self):
        if '…' in self.quote or '...' in self.quote:
            raise ValueError('quota.quote needs one complete source fragment')
        if self.amount is not None and self.read not in ('table','catalog-field') and self.amount not in _numbers(self.quote):
            raise ValueError('quota.amount is not a number in its source quote')
        if self.window > 1 and self.window not in _numbers(self.quote):
            raise ValueError('quota.window is not a number in its source quote')
        if bool(self.condition) != bool(self.condition_quote):
            raise ValueError('quota.condition needs its condition_quote')
        if not _numbers(self.condition).issubset(_numbers(self.quote + ' ' + self.condition_quote)):
            raise ValueError('quota condition numbers need source evidence')
        if self.amount is not None and self.read not in ('constant','table','catalog-field'):
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
            units = {'requests':r'\b(?:requests?|(?:api )?calls?)\b|(?<![a-z])(?:rpm|rpd|rps|req)(?![a-z])|请求|调用',
                     'USD':r'\$|\b(?:USD|dollars?)\b', 'INR':r'₹|\bINR\b',
                     'credits':r'\b(?:credits?|Hypercredits?)\b|积分|魔粒',
                     'Hypercredits':r'\bhypercredits?\b',
                     'completions':r'\b(?:completions?|autocompletion)\b',
                     'tokens':r'\btokens?\b|(?<![a-z])(?:tpm|tpd)(?![a-z])',
                     'tasks':r'\btasks?\b','messages':r'\bmessages?\b', 'points':r'\bpoints?\b|积分',
                     'one-hour sessions':r'\bone.hour sessions?\b',
                     'list-price value':r'\b(?:list.price|value.based)\b'}.get(self.unit, r'\b' + self.unit + r'\b')
            periods = {'second':r'\b(?:seconds?|secs?|rps)\b',
                       'minute':r'\b(?:minutes?|min|rpm|tpm)\b', 'hour':r'\b(?:hours?|rph)\b|小时',
                       'day':r'\b(?:days?|daily|rpd)\b|每天|每日|24小时', 'week':r'\b(?:weeks?|weekly)\b|周',
                       'month':r'\b(?:months?|monthly|mo)\b|每月|月',
                       'one-time':r'\b(?:one.time|sign.?up|welcome|initial|new accounts?|new users?|registration|trials?|preview|once|first time)\b|注册|首次|试用|仅可领取一次',
                       'concurrent':r'\b(?:concurrent|simultaneous|simultaneously|in flight|at a time)\b|并发',
                       None:''}[self.period]
            period_evidence = self.period_quote or phrase
            if not re.search(units, phrase, re.I) or (periods and not re.search(periods, period_evidence, re.I)):
                raise ValueError('quota unit and period need evidence in their source quote')
        if (self.amount is None or self.period is None or self.state or self.scope in ('unspecified','disputed')) and self.reviewed_on is None:
            raise ValueError('an unresolved quota needs a dated review')
        if self.state in ('variable','unmetered','account-specific') and self.amount is not None:
            raise ValueError('a variable, unmetered or account-specific allowance has no fixed amount')
        if self.state == 'unmetered' and not re.search(r'\b(?:unlimited|unmetered)\b|无限|不限量',self.quote,re.I):
            raise ValueError('unmetered usage needs explicit source evidence')
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
        if self.read == 'table':
            if not self.table or self.amount is None:
                raise ValueError('table quotas need an amount and a cell binding')
            units = {'RPM':('requests','minute'),'RPD':('requests','day'),
                     'TPM':('tokens','minute'),'TPD':('tokens','day')}
            if self.table.column in units:
                if units[self.table.column] != (self.unit,self.period) or self.window != 1:
                    raise ValueError('quota unit and period must match the table column')
            else:
                # The fragment includes the table's unit/window heading when
                # the columns are plan names rather than unit abbreviations.
                unit = {'requests':r'requests?|calls?|req|rpm|rpd|rps|chat/completions','tokens':r'tokens?',
                        'credits':r'credits?', 'tasks':r'tasks?'}.get(self.unit,self.unit)
                period = {'day':r'daily|days?|24 hours','concurrent':r'concurrent',
                          'minute':r'minutes?|min|rpm','second':r'seconds?|\d+s\b',
                          'month':r'months?|monthly','hour':r'hours?|hr'}.get(self.period,self.period or '')
                heading = self.quote + ' ' + ' '.join(self.table.rows) + ' ' + self.table.column + ' ' + self.period_quote
                if not re.search(unit,heading,re.I) or not re.search(period,self.period_quote or heading,re.I):
                    raise ValueError('quota table unit and period need a source heading')
        elif self.table is not None:
            raise ValueError('quota.table requires read=table')
        if self.read == 'catalog-field':
            if not self.catalog_field or not self.model_ids or self.amount is None:
                raise ValueError('catalog fields need a numeric cap, exact models and tier selector')
            units = {'rpm':('requests','minute'),'rpd':('requests','day'),'rps':('requests','second'),
                     'tpm':('tokens','minute'),'tpd':('tokens','day')}
            if units[self.catalog_field.field] != (self.unit,self.period) or self.window != 1:
                raise ValueError('quota unit and period must match the catalog field')
        elif self.catalog_field is not None:
            raise ValueError('quota.catalog_field requires read=catalog-field')
        if self.period in ('one-time','concurrent',None) and (self.window != 1 or self.rolling):
            raise ValueError('a grant, concurrent ceiling or unknown period has no recurring or rolling window')
        return self


def quota_changes(body: str, quota: UsageQuota) -> list[str]:
    from .quotes import flatten, page_texts
    from .prober import _catalog_items, _model_id
    import httpx
    if quota.follow is not None:
        return ['quota source index could not be resolved to its current document']
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
                    and (not quota.period_quote or flatten(quota.period_quote) in flatten(text))
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
    if quota.period_quote and not any(flatten(quota.period_quote) in text for text in page_texts(body)):
        notes.append('quota renewal/grant evidence no longer on its source')
    if quota.read == 'constant':
        values = re.findall(r'\bconst\s+' + re.escape(quota.constant) + r'\s*=\s*([0-9]+(?:\.[0-9]+)?(?:e[+-]?[0-9]+)?)\s*[;,]', body, re.I)
        if not values:
            notes.append(f'quota constant {quota.constant} unreadable')
        elif any(float(value) != quota.amount for value in values):
            notes.append(f'quota constant {quota.constant}={", ".join(dict.fromkeys(values))} (recorded {quota.amount:g})')
    if quota.read == 'table':
        notes.extend(_table_changes(body, quota))
    if quota.read == 'catalog-field':
        try:items = _catalog_items(httpx.Response(200,text=body)) or []
        except (ValueError,TypeError):items = []
        binding = quota.catalog_field
        for mid in quota.model_ids:
            models = [m for m in items if _model_id(m) == mid]
            values = []
            for model in models:
                rows = model.get(binding.collection)
                if not isinstance(rows,list):continue
                values.extend(row.get(binding.field) for row in rows if isinstance(row,dict)
                              and all(str(row.get(k)) == v for k,v in binding.where.items()))
            try:equal = len(values) == 1 and not isinstance(values[0],bool) and float(values[0]) == quota.amount
            except (ValueError,TypeError):equal = False
            if len(models) != 1 or not equal:
                notes.append(f'quota catalog {mid} / {binding.field}: changed, ambiguous or unreadable tier value')
    return notes


async def resolved_quota_entry(client, entry: Entry, attempts: int = 3, backoff: float = 1) -> Entry:
    """Resolve the current release before any quote or numeric comparison."""
    from .models import Follow
    from .prober import _fetch_page, followed_url
    indices, quotas = {}, []
    for q in entry.quotas:
        q = active_quota(entry,q)
        if q is None:
            continue
        if q.follow:
            if q.source not in indices:
                response,_ = await _fetch_page(client,q.source,attempts,backoff)
                try:indices[q.source] = response.json() if response is not None else None
                except ValueError:indices[q.source] = None
            url = followed_url(indices[q.source],Follow.model_validate(q.follow))
            if url:
                try:UsageQuota._http_source(url)
                except ValueError:pass
                else:q = q.model_copy(update={'source':url,'follow':None})
        quotas.append(q)
    return entry.model_copy(update={'quotas':quotas})


async def quota_moved(client, entry: Entry, probed, attempts: int, backoff: float, today: date) -> list[str]:
    from .prober import _page_beside
    pages, notes = {}, []
    entry = await resolved_quota_entry(client,entry,attempts,backoff)
    for i, q in enumerate(entry.quotas):
        q = active_quota(entry,q)
        if q is None:continue
        if q.source not in pages:
            pages[q.source] = await _page_beside(client, q.source, entry, probed, attempts, backoff)
        page, failure = pages[q.source]
        if page is None:
            notes.append(f'quotas[{i}] could not be checked against {q.source}: {failure}')
        else:
            notes.extend(f'quotas[{i}]: {n}' for n in quota_changes(page.text, q))
        if q.reviewed_on and (q.amount is None or q.period is None or q.state or q.scope in ('unspecified','disputed')) and (today - q.reviewed_on).days >= UNKNOWN_RECHECK_DAYS:
            notes.append(f'quotas[{i}]: unresolved quota needs a fresh dated review')
    return notes


SCOPE_WORDS = {'account':'per account','ip':'per IP','account-model':'per account per model',
               'project':'per project','key':'per key','unspecified':'scope not published',
               'ip-model':'per IP per model','organization':'per organization',
               'organization-model':'per organization per model','project-model':'per project per model','key-model':'per key per model',
               'plan':'per service plan','team':'per team','endpoint':'shared across the endpoint','disputed':'sharing scope disputed'}
PERIOD_ADJECTIVES = {'second':'Per-second','minute':'Per-minute','hour':'Hourly','day':'Daily','week':'Weekly',
                     'month':'Monthly','one-time':'One-time','concurrent':'Concurrent',None:''}


def quota_value(q: UsageQuota) -> str:
    if q.state == 'unmetered':
        return 'Unmetered ' + q.unit
    periods = q.period if q.window == 1 else f'{q.window} {q.period}s'
    if q.rolling:
        periods = 'rolling ' + periods
    if q.amount is None:
        window = ('Rolling ' if q.rolling else '') + (f'{q.window}-{q.period}' if q.window != 1 else PERIOD_ADJECTIVES[q.period])
        status = {'variable':'amount varies','account-specific':'see your account for values'}.get(q.state,'amount not published')
        text = (window + ' ' + q.unit + ' allowance: ' + status).strip()
        if q.period is None:
            text += ' (period not published)'
        return text[0].upper() + text[1:] if q.period is None else text
    amount = f'{q.amount:,.15g}'
    value = {'USD':'$','INR':'₹'}.get(q.unit,'') + amount if q.unit in ('USD','INR') else amount + ' ' + q.unit
    if q.period == 'concurrent':
        value += ' at once'
    elif q.period == 'one-time':
        value += ' once'
    elif q.period is None:
        value += ' (period not published)'
    elif q.period != 'one-time':
        value += (' per ' if q.unit == 'one-hour sessions' else '/') + periods
    if q.state == 'disputed':
        value += ' (published sources disagree)'
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
    rows = [{**q.model_dump(mode='json', exclude_none=True), 'amount': q.amount, 'period':q.period}
            for old in entry.quotas if (q := active_quota(entry,old)) is not None]
    if entry.page_catalog and entry.page_catalog.limited_allowance:
        quote = entry.page_catalog.limited_allowance
        m = re.fullmatch(r'(\d+) one-hour sessions per (day|week|month)', quote)
        if m:
            rows.append({'amount':int(m[1]),'unit':'one-hour sessions','period':m[2],
                         'scope':'account','label':'Session-based limited mode',
                         'source':entry.page_catalog.source,'quote':quote})
    return rows


def active_quota(entry: Entry, quota: UsageQuota) -> UsageQuota | None:
    lane = entry.api or entry.client_lane
    if not quota.model_ids or not lane:return quota
    ended = {mid for mid in lane.ignored_ids if mid in lane.model_access and lane.model_access[mid].until}
    ids = [mid for mid in quota.model_ids if mid not in ended]
    return quota.model_copy(update={'model_ids':ids}) if ids else None


def quota_summary(entry: Entry) -> str:
    groups = {}
    for row in structured_quotas(entry):
        q = UsageQuota.model_validate(row)
        key = (q.label, q.scope, q.condition, q.reset, () if q.label else tuple(q.model_ids))
        groups.setdefault(key, []).append(q)
    partitions = []
    for key, quotas in groups.items():
        general = [q for q in quotas if not q.model_ids]
        if general:
            partitions.append((key, general))
        ids = list(dict.fromkeys(mid for q in quotas for mid in q.model_ids))
        profiles = {}
        for mid in ids:
            profile = tuple(sorted({quota_value(q) for q in quotas if mid in q.model_ids}))
            profiles.setdefault(profile, []).append(mid)
        for ids in profiles.values():
            bound = [q.model_copy(update={'model_ids':[mid for mid in q.model_ids if mid in ids]})
                     for q in quotas if set(q.model_ids) & set(ids)]
            partitions.append((key, bound))
    paragraphs = []
    for (label, scope, condition, reset, _), quotas in partitions:
        words = []
        for q in quotas:
            value = quota_value(q)
            if value not in words:words.append(value)
        scoped = SCOPE_WORDS[scope]
        text = (label + ': ' if label else '') + '; '.join(words) + ('; ' if scope == 'unspecified' else ' ') + scoped
        if condition:
            text += ' (' + condition + ')'
        if reset:
            text += '. ' + reset
        ids = list(dict.fromkeys(mid for q in quotas for mid in q.model_ids))
        if ids:
            text += '; for ' + ', '.join('`' + mid + '`' for mid in ids)
        paragraphs.append(text)
    return '\n\n'.join(paragraphs)
