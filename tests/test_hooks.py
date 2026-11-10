import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).parents[1]


def run_hook_env(tmp_path, *, cache=None):
    env = os.environ.copy()
    env.pop('UV_CACHE_DIR', None)
    env['TMPDIR'] = str(tmp_path)
    if cache is not None:
        env['UV_CACHE_DIR'] = cache
    return subprocess.run(
        ['sh', '-c', '. "$1"; printf "%s" "$UV_CACHE_DIR"', 'sh',
         str(ROOT / '.githooks/uv-env')],
        env=env, check=True, capture_output=True, text=True,
    ).stdout


def test_hooks_choose_a_writable_cache_when_none_is_set(tmp_path):
    assert run_hook_env(tmp_path) == str(tmp_path / 'freetier-uv-cache')


def test_hooks_preserve_an_explicit_cache(tmp_path):
    explicit = str(tmp_path / 'chosen-cache')
    assert run_hook_env(tmp_path, cache=explicit) == explicit
