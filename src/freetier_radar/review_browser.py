"""One parameterized browser suite; its result is bound to a commit and coverage plan."""
import json
from pathlib import Path

from jinja2 import Environment

from .indexnow import index_at
from .render import PAGES_URL, REPO_URL
from .review import Bundle, blob, scoped


def browser_plan(bundle: Bundle) -> dict:
    scope = scoped(bundle)
    index = index_at(scope['sha'], repo=bundle.repo)
    before = index_at(scope['base'], repo=bundle.repo)
    current = {m['family']: m for m in index['models']}
    models = [current.get(m['family'], {**m, 'rows': [], 'tier': None})
              for m in {m['family']: m for m in [*before['models'], *index['models']]}.values()
              if m.get('page') and m['family'] in scope['families']]
    if not models:
        models = [m for m in index['models'] if m.get('page') and m.get('tier') == 'strong'][:2]
    rows = [e for e in index['entries'] if e['id'] in scope['rows']]
    folded_ids = {e['duplicate_of'] for e in rows if e.get('duplicate_of')}
    folded_targets = {e['id']: {'name': e['name'], 'page': e['page']}
                      for e in index['entries'] if e['id'] in folded_ids}
    old = {e['id']: {m['family'] for m in e.get('models', [])} for e in before['entries']}
    links = [[e['id'], m['family']] for e in rows for m in e.get('models', [])
             if m['family'] not in old.get(e['id'], set())]
    widths, schemes = [1440, 375, 320], ['light', 'dark']
    cases = []
    for width in widths:
        for scheme in schemes:
            prefix = f'{width}/{scheme}/'
            cases += [prefix + kind + '/' + m['family'] for kind in ('search', 'browse', 'model') for m in models]
            cases += [prefix + 'provider/' + e['id'] for e in rows]
            if width != 320:
                cases.append(prefix + 'readme')
    return {'sha': scope['sha'], 'site': PAGES_URL + '/', 'repository': REPO_URL,
            'chart_date': json.loads(blob(bundle.repo, scope['sha'], 'src/freetier_radar/intelligence-index.json'))['read_on']
                          if 'src/freetier_radar/intelligence-index.json' in scope['paths'] else None,
            'models': models, 'rows': rows, 'folded_targets': folded_targets,
            'links': links, 'widths': widths, 'schemes': schemes, 'cases': cases,
            'output': str(bundle.out / 'browser-execution.json')}


def browser_script(bundle: Bundle, *, cases: list[str] | None = None) -> str:
    plan = browser_plan(bundle)
    bundle.save('browser-plan', plan)
    if cases is not None:
        if len(cases) != len(set(cases)) or not set(cases) <= set(plan['cases']):
            raise ValueError('selected browser cases must be a unique subset of the full plan')
        plan = {**plan, 'selected_cases': cases}
    template = Path(__file__).resolve().parents[2] / 'templates/review-browser.js.j2'
    return Environment(autoescape=False).from_string(template.read_text()).render(plan=json.dumps(plan))


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
