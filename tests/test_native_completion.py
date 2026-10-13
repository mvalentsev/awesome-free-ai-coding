"""Native completion evidence must belong to the launched isolated session."""
import json

import pytest

from freetier_radar import review


def test_live_client_recovers_a_missing_final_event_from_the_same_completed_session(tmp_path, monkeypatch):
    entry = {'id': 'vendor', 'name': 'Vendor', 'category': 'api-free-tier',
             'url': 'https://vendor.example', 'offering': 'Public chat lane',
             'free_part': 'models', 'models': [{'family': 'alpha'}],
             'api': {'base_url': 'https://vendor.example/v1', 'auth': 'none',
                     'openai_compatible': True, 'model_ids': ['alpha']},
             'probe': {'type': 'api-models', 'endpoint': 'https://vendor.example/v1/models'},
             'first_seen': '2026-09-01', 'last_verified': '2026-10-13'}
    registry = json.dumps({'entries': [entry]}).encode()
    monkeypatch.setattr(review, 'scoped', lambda bundle: {'sha': 'a' * 40})
    monkeypatch.setattr(review, 'blob', lambda repo, sha, path:
                        registry if path == 'registry.yaml' else b'{"provider":{}}')
    binary = tmp_path / 'opencode'
    binary.write_text('''#!/usr/bin/env python3
import json, sys
from pathlib import Path
args = sys.argv[1:]
if '--help' in args:
    print('--standalone --auto')
    sys.exit(0)
marker = Path('audit-marker.txt').read_text().strip()
if args[:2] == ['session', 'export']:
    assert args[2:] == ['--standalone', 'ses_current']
    print(json.dumps({
        'info': {'id': 'ses_current', 'outcome': 'succeeded',
                 'model': {'providerID': 'vendor', 'id': 'alpha'},
                 'location': {'directory': str(Path.cwd())}},
        'messages': [
            {'id': 'msg-tool', 'type': 'assistant', 'finish': 'tool-calls',
             'model': {'providerID': 'vendor', 'id': 'alpha'},
             'time': {'created': 1, 'completed': 2},
             'content': [{'type': 'tool', 'name': 'read',
                          'state': {'status': 'completed',
                                    'content': [{'type': 'text', 'text': marker}]}}]},
            {'id': 'msg-answer', 'type': 'assistant', 'finish': 'stop',
             'model': {'providerID': 'vendor', 'id': 'alpha'},
             'time': {'created': 3, 'completed': 4},
             'content': [{'type': 'text', 'text': marker}]},
            {'type': 'idle', 'outcome': 'succeeded', 'time': {'created': 5}},
        ]
    }))
    sys.exit(0)
assert args[0] == 'run' and '--standalone' in args
for event in [
    {'type': 'tool_use', 'sessionID': 'ses_current',
     'part': {'type': 'tool', 'messageID': 'msg-tool',
              'state': {'status': 'completed', 'output': marker}}},
    {'type': 'text', 'sessionID': 'ses_current',
     'part': {'type': 'text', 'messageID': 'msg-answer', 'text': marker}},
]:
    print(json.dumps(event))
''')
    binary.chmod(0o755)
    bundle = review.Bundle(tmp_path / 'evidence', tmp_path)
    result = review.live_client(bundle, 'opencode', str(binary), 'vendor', 'alpha')
    assert result['passed'], result
    assert result['completed_turn']
    assert result['stdout_completed_turn'] is False
    assert result['completion_source'] == 'session-export'
    assert json.loads((bundle.out / result['evidence'] / 'session-export.json').read_text())['info']['id'] == 'ses_current'


@pytest.mark.parametrize('defect', [None, 'other-session', 'other-directory', 'other-provider',
                                   'other-model', 'running', 'failed', 'length', 'no-idle',
                                   'early-idle', 'missing-completion', 'other-answer',
                                   'error', 'no-tool', 'tool-failed', 'missing-read',
                                   'wrong-answer', 'bad-content', 'bad-messages', 'not-object'])
def test_export_requires_bound_terminal_completion_and_a_real_read(tmp_path, defect):
    from freetier_radar.conformance import check_opencode_session_export
    model = {'providerID': 'vendor', 'id': 'alpha'}
    info = {'id': 'ses_current', 'outcome': 'succeeded', 'model': dict(model),
            'location': {'directory': str(tmp_path.resolve())}}
    assistant = {'id': 'msg-answer', 'type': 'assistant', 'finish': 'stop', 'model': dict(model),
                 'time': {'completed': 4}, 'content': [
                     {'type': 'tool', 'state': {'status': 'completed', 'content': [
                         {'type': 'text', 'text': 'fresh marker'}]}},
                     {'type': 'text', 'text': 'fresh marker'}]}
    idle = {'type': 'idle', 'outcome': 'succeeded', 'time': {'created': 5}}
    data = {'info': info, 'messages': [assistant, idle]}
    if defect == 'other-session': info['id'] = 'ses_other'
    if defect == 'other-directory': info['location']['directory'] = str(tmp_path / 'other')
    if defect == 'other-provider': assistant['model']['providerID'] = 'other'
    if defect == 'other-model': info['model']['id'] = 'beta'
    if defect == 'running': info['outcome'] = 'running'
    if defect == 'failed': idle['outcome'] = 'failed'
    if defect == 'length': assistant['finish'] = 'length'
    if defect == 'no-idle': data['messages'].pop()
    if defect == 'early-idle': idle['time']['created'] = 3
    if defect == 'missing-completion': assistant['time'] = {}
    if defect == 'other-answer': assistant['id'] = 'msg-other'
    if defect == 'error': assistant['error'] = {'message': 'provider failed'}
    if defect == 'no-tool': assistant['content'].pop(0)
    if defect == 'tool-failed': assistant['content'][0]['state']['status'] = 'error'
    if defect == 'missing-read': assistant['content'][0]['state']['content'][0]['text'] = 'another file'
    if defect == 'wrong-answer': assistant['content'][1]['text'] = 'another answer'
    if defect == 'bad-content': assistant['content'] = None
    if defect == 'bad-messages': data['messages'] = [None]
    if defect == 'not-object': data = None
    result = check_opencode_session_export(data, 'ses_current', 'vendor', 'alpha',
                                          tmp_path, 'fresh marker', 'msg-answer')
    assert result['passed'] is (defect is None)
