import pytest

from freetier_radar.validate import check_repository


def repository(tmp_path, monkeypatch, readme, site):
    # Isolate presentation at the real repository-check boundary.
    monkeypatch.setattr('freetier_radar.layout.check_layout', lambda root: [])
    monkeypatch.setattr('freetier_radar.validate.load_registry', lambda path: [])
    monkeypatch.setattr('freetier_radar.claims.check_claims', lambda root, *, entries: [])
    monkeypatch.setattr('freetier_radar.validate.registry_form_problems', lambda root, *, entries: [])
    from freetier_radar.render import MAP_BEGIN, MAP_END
    (tmp_path / 'CONTRIBUTING.md').write_text(MAP_BEGIN + '\n' + MAP_END)
    (tmp_path / 'README.md').write_text('<div align="center">\n' + readme + '\n</div>')
    (tmp_path / 'index.html').write_text(site + '<main></main>')
    return tmp_path


@pytest.mark.parametrize('readme,site,surface', [
    ('[Plug it in](#-plug-it-into-your-agent) · [Client configs](configs/README.md)',
     '<nav><a href="#plug">Plug it in</a></nav>', 'README.md'),
    ('[Plug it in](#-plug-it-into-your-agent)',
     '<header><a href="#plug">Client configs</a></header><nav><a href="#plug">Plug it in</a></nav>',
     'index.html'),
])
def test_repository_check_rejects_two_names_for_the_same_setup_action(tmp_path, monkeypatch,
                                                                    readme, site, surface):
    root = repository(tmp_path, monkeypatch, readme, site)
    assert any(surface in p and 'setup' in p for p in check_repository(root))


def test_contextual_setup_links_and_separate_start_links_remain_allowed(tmp_path, monkeypatch):
    root = repository(tmp_path, monkeypatch, '[Plug it in](#-plug-it-into-your-agent)',
                      '<header><a href="#start">Start here</a></header>'
                      '<nav><a href="#start">Start here</a><a href="#plug">Plug it in</a></nav>')
    with (root / 'README.md').open('a') as stream:
        stream.write('\n[Ready to connect](configs/README.md)\n')
    with (root / 'index.html').open('a') as stream:
        stream.write('<a href="#plug">Connection details</a>')
    assert check_repository(root) == []


@pytest.mark.parametrize('surface', ['README.md', 'index.html'])
def test_removing_the_existing_setup_action_is_also_rejected(tmp_path, monkeypatch, surface):
    root = repository(tmp_path, monkeypatch, '[Plug it in](#-plug-it-into-your-agent)',
                      '<nav><a href="#plug">Plug it in</a></nav>')
    (root / surface).write_text('<div align="center"></div><main></main>')
    assert any(surface in p and 'setup' in p for p in check_repository(root))


@pytest.mark.parametrize('extra', [0, 1])
@pytest.mark.parametrize('newline', ['\n', '\r\n'])
def test_repository_check_enforces_the_readme_byte_budget(tmp_path, monkeypatch, extra, newline):
    from freetier_radar.render import README_BUDGET

    root = repository(tmp_path, monkeypatch, '[Plug it in](#-plug-it-into-your-agent)',
                      '<nav><a href="#plug">Plug it in</a></nav>')
    readme = root / 'README.md'
    text = readme.read_text().replace('\n', newline)
    room = README_BUDGET - len(text.encode('utf-8')) + extra
    readme.write_bytes((text + 'é' * (room // 2) + 'x' * (room % 2)).encode('utf-8'))
    problems = check_repository(root)
    assert problems == ([f'presentation: README.md is {README_BUDGET + extra} bytes, '
                         f'over {README_BUDGET} — keep the full reference on the site.']
                        if extra else [])
