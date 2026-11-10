"""One parameterized browser suite; its result is bound to a commit and coverage plan."""
import json
import html as html_text
import re
from pathlib import Path

from jinja2 import Environment

from . import git
from .indexnow import index_at
from .layout import Kind, node_for
from .render import MODEL_SORT, PAGES_URL, REPO_URL
from .review import Bundle, blob, scoped

COVERAGE_PURPOSES = ('changed-content', 'shared-layout')


def _representatives(items: list[dict], features) -> list[dict]:
    """Cover shared layout states with the longest suitable content."""
    pending = set().union(*(features(item) for item in items))
    chosen = []
    while pending:
        item = max(items, key=lambda item: (len(features(item) & pending), len(json.dumps(item))))
        chosen.append(item)
        pending -= features(item)
    return chosen


def _row_features(row: dict) -> set[str]:
    if row.get('duplicate_of'):
        return {'folded'}
    state = {'archived' if row.get('archived') else 'live'}
    state.add('models' if row.get('models') else 'no-models')
    for name in ('page_catalog', 'quotas', 'access', 'model_access', 'api', 'data_use', 'border'):
        if row.get(name):
            state.add(name)
    if (row.get('api') or {}).get('notice'):
        state.add('notice')
    return state


def _model_features(model: dict) -> set[str]:
    return {'listed' if model.get('rows') else 'withdrawn',
            'measured' if model.get('tier') else 'unmeasured',
            'multiple-providers' if len(model.get('rows', [])) > 1 else 'single-or-empty'}


def browser_scope(paths: list[str]) -> tuple[bool, bool]:
    """Browser output and shared-layout scope, using the repository map."""
    shared_layout = any(path.startswith('_layouts/') or path == '_config.yml'
                        or (path.startswith('assets/') and Path(path).suffix in ('.js', '.css'))
                        for path in paths)
    browser_changed = shared_layout or any(
        node.kind in (Kind.PAGE, Kind.GENERATED)
        for path in paths if (node := node_for(path)) is not None)
    return browser_changed, shared_layout


def browser_plan(bundle: Bundle) -> dict:
    scope = scoped(bundle)
    browser_changed, shared_layout = browser_scope(scope['paths'])
    index = index_at(scope['sha'], repo=bundle.repo)
    before = index_at(scope['base'], repo=bundle.repo)
    current = {m['family']: m for m in index['models']}
    models = [current.get(m['family'], {**m, 'rows': [], 'tier': None})
              for m in {m['family']: m for m in [*before['models'], *index['models']]}.values()
              if m.get('page') and m['family'] in scope['families']]
    if not models:
        models = [m for m in index['models'] if m.get('page') and m.get('rows')][:2]
    rows = [e for e in index['entries'] if e['id'] in scope['rows']]
    old = {e['id']: {m['family'] for m in e.get('models', [])} for e in before['entries']}
    links = [[e['id'], m['family']] for e in rows for m in e.get('models', [])
             if m['family'] not in old.get(e['id'], set())]
    widths, schemes = [1440, 375, 320], ['light', 'dark']
    html = git.show(bundle.repo, scope['sha'], 'index.html') or ''
    config_block = re.search(r'<script type="application/json" id="client-configs">(.*?)</script>', html, re.S)
    client_configs = json.loads(config_block.group(1)) if config_block else {}
    clients = list(client_configs)
    words = {word for key in ('sections', 'filters')
             for item in index.get('search_config', {}).get(key, []) for word in item.get('words', [])}
    named = sorted((e for e in index['entries'] if not e.get('archived') and not e.get('duplicate_of')
                    and e.get('page') and re.fullmatch(r'[A-Za-z][A-Za-z0-9]+', e.get('name', ''))
                    and e['name'].lower() not in words
                    and e['name'].lower() not in current), key=lambda e: (len(e['name']), e['name']))[:2]
    readme = git.show(bundle.repo, scope['sha'], 'README.md') or ''
    readme_model_list = 'Where each one is free' in readme
    comparison = re.search(r'<summary><b>Where each one is free</b>.*?</details>', readme, re.S)
    comparison_families = re.findall(r'^- (?:\[)?`([^`]+)`', comparison.group() if comparison else '', re.M)
    readme_models = [current[family] for family in comparison_families if family in current]
    readme_images = [html_text.unescape(alt) for alt in re.findall(
        r'<picture>.*?<img\s[^>]*alt="([^"]+)"', readme, re.S)]
    row_controls = _representatives(
        [row for row in index['entries'] if row.get('page')] if shared_layout else rows,
        _row_features)
    model_controls = _representatives(
        [model for model in index['models'] if model.get('page')] if shared_layout else models,
        _model_features)
    execution_rows = list({row['id']: row for row in [*rows, *row_controls]}.values())
    execution_models = list({model['family']: model for model in [*models, *model_controls]}.values())
    folded_ids = {row['duplicate_of'] for row in execution_rows if row.get('duplicate_of')}
    folded_targets = {row['id']: {'name': row['name'], 'page': row['page']}
                      for row in index['entries'] if row['id'] in folded_ids}
    config_control = max(clients, key=lambda client: len(json.dumps(client_configs[client])), default=None)
    coverage = {}

    def add(width, scheme, kind, name='', purpose=COVERAGE_PURPOSES[1]):
        case = f'{width}/{scheme}/{kind}' + ('/' + name if name else '')
        coverage.setdefault(case, purpose)

    # Unique content and associations once. Themes and widths exercise the
    # shared components on representatives, not every provider's same page.
    for model in models:
        for kind in ('search', 'browse', 'model'):
            add(1440, 'light', kind, model['family'], COVERAGE_PURPOSES[0])
    for row in rows:
        add(1440, 'light', 'provider', row['id'], COVERAGE_PURPOSES[0])
    for client in clients:
        add(1440, 'light', 'config', client, 'client-content')
    for width, scheme in ((1440, 'light'), (1440, 'dark'), (375, 'light'), (375, 'dark'), (320, 'light')):
        for row in row_controls:
            add(width, scheme, 'provider', row['id'])
        for model in model_controls:
            for kind in ('search', 'browse', 'model'):
                add(width, scheme, kind, model['family'])
        if config_control:
            add(width, scheme, 'config', config_control)
        if len(named) == 2:
            add(width, scheme, 'search-flow')
        if width != 320:
            add(width, scheme, 'readme')
            for i in range(len(readme_images)):
                add(width, scheme, 'readme-image', str(i))
    cases = list(coverage)
    sortable = [row for row in index['entries'] if not row.get('archived') and not row.get('duplicate_of')
                and len([m for m in row.get('models', []) if not m.get('superseded_by')]) >= index.get('model_sort', MODEL_SORT)['minimum']]
    sort_row = next((row for row in sortable if row['id'] == 'opencode'), sortable[0] if sortable else None)
    if index.get('model_sort'):
        for width, scheme in ((1440, 'light'), (375, 'dark')):
            for kind in ('home', 'index', *(('provider', 'browse') if sort_row else ())):
                add(width, scheme, 'model-sort', kind, 'user-sort')
        cases = list(coverage)
    if not browser_changed and not scope['rows'] and not scope['families']:
        cases, coverage = [], {}
    return {'sha': scope['sha'], 'site': PAGES_URL + '/', 'repository': REPO_URL,
            'chart_date': json.loads(blob(bundle.repo, scope['sha'], 'src/freetier_radar/intelligence-index.json'))['read_on']
                          if 'src/freetier_radar/intelligence-index.json' in scope['paths'] else None,
            'models': execution_models, 'rows': execution_rows, 'folded_targets': folded_targets,
            'links': links, 'widths': widths, 'schemes': schemes, 'cases': cases,
            'coverage': coverage,
            'representative_rows': [row['id'] for row in row_controls],
            'representative_models': [model['family'] for model in model_controls],
            'model_sort': index.get('model_sort'), 'models_catalog': index['models'], 'sort_row': sort_row,
            'clients': clients,
            'readme_model_list': readme_model_list, 'readme_images': readme_images,
            'readme_models': readme_models,
            'readme_providers': {row['id']: row['name'] for row in index['entries'] if row.get('name')},
            'search_rows': [{'name': e['name'], 'page': e['page']} for e in named],
            'output': str(bundle.out / 'browser-execution.json')}


def browser_script(bundle: Bundle, *, cases: list[str] | None = None) -> str:
    plan = browser_plan(bundle)
    bundle.save('browser-plan', plan)
    if cases is not None:
        if len(cases) != len(set(cases)) or not set(cases) <= set(plan['cases']):
            raise ValueError('selected browser cases must be a unique subset of the full plan')
        plan = {**plan, 'selected_cases': cases}
    template = Path(__file__).resolve().parents[2] / 'templates/review-browser.js.j2'
    return Environment(autoescape=False).from_string(template.read_text()).render(
        plan=json.dumps(plan), readme_model_list=plan['readme_model_list'])


def accept_browser(bundle: Bundle, result: dict, plan: dict) -> dict:
    if not plan:
        raise ValueError('generate the browser plan first')
    if not isinstance(result, dict) or not isinstance(result.get('records', []), list) or any(
            not isinstance(record, dict) or not isinstance(record.get('id'), str) or
            ('image_url' in record and any(not isinstance(record.get(key), str)
                                         for key in ('image_url', 'image_path')))
            for record in result.get('records', [])):
        raise ValueError('browser result and each record must be objects')
    records = result.get('records', [])
    ids = [r.get('id') for r in records]
    passed = (result.get('sha') == plan['sha'] == scoped(bundle)['sha'] and result.get('passed') is True and not result.get('error')
              and not result.get('pageErrors') and len(ids) == len(plan['cases'])
              and set(ids) == set(plan['cases']))
    bundle.write('browser-execution.json', (json.dumps(result, indent=2) + '\n').encode())
    return bundle.save('browser', {'sha': plan['sha'], 'passed': passed,
                                   'planned_cases': len(plan['cases']), 'completed_cases': len(ids),
                                   'missing': sorted(set(plan['cases']) - set(ids)),
                                   'pageErrors': result.get('pageErrors', []), 'error': result.get('error')})
