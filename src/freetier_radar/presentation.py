"""Public navigation invariants; visual and usefulness review remains separate."""
from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


class Links(HTMLParser):
    def __init__(self, text: str):
        super().__init__()
        self.targets: list[str] = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.targets.extend(value for name, value in attrs if name == 'href' and value)


def is_setup(target: str) -> bool:
    url = urlsplit(target)
    return url.fragment in {'plug', 'connections', '-plug-it-into-your-agent'} or \
        url.path.rstrip('/').endswith('configs/README.md')


def check_presentation(root: Path) -> list[str]:
    from .render import README_BUDGET

    readme_bytes = (root / 'README.md').read_bytes()
    readme = readme_bytes.decode('utf-8')
    centered = re.search(r'<div\s+align="center">(.*?)</div>', readme, re.S)
    top = centered.group(1) if centered else ''
    readme_links = re.findall(r'\[[^\]]+\]\(([^)]+)\)', top) + Links(top).targets
    site = (root / 'index.html').read_text(encoding='utf-8')
    site_top = re.split(r'<main\b', site, maxsplit=1)[0]
    problems = []
    size = len(readme_bytes)
    if size > README_BUDGET:
        problems.append(f'README.md is {size} bytes, over {README_BUDGET} — '
                        'keep the full reference on the site.')
    for name, links in (('README.md', readme_links), ('index.html', Links(site_top).targets)):
        count = sum(is_setup(link) for link in links)
        if count != 1:
            problems.append(f'{name}: primary navigation needs one setup action; found {count}. '
                            'Reuse Plug it in instead of adding an alias for its configs.')
    return problems
