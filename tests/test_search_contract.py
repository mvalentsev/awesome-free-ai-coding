"""Search the same complete provider facts on both published surfaces."""
import json
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess

import pytest

from freetier_radar.render import build_index, render_site, _site_client_configs
from freetier_radar.models import save_registry
from test_render import TODAY, make
from test_site import SEARCH_ASSETS, TEMPLATES


def records(html):
    class Rows(HTMLParser):
        def __init__(self):
            super().__init__()
            self.rows = {}
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == "tr" and "data-search" in attrs:
                self.rows[attrs["data-id"]] = json.loads(attrs["data-search"])
    parser = Rows()
    parser.feed(html)
    return parser.rows


@pytest.mark.skipif(shutil.which("node") is None, reason="needs browser JavaScript runtime")
def test_full_folded_lead_cross_field_terms_and_callable_ids_match_on_both_surfaces(tmp_path):
    entries = [make(id="groq", name="Groq", limits="1,160 tokens/minute\n\n" + "Details. " * 50,
                    api={"base_url":"https://example.com/v1", "model_ids":["vendor/preview:free"]}),
               make(id="other", name="Other", limits="10 tokens/minute"),
               make(id="version", name="Version", models=[{"family":"qwen3-8b"}])]
    registry = tmp_path / "registry.yaml"
    save_registry(registry, entries)
    html = render_site(registry, TEMPLATES, tmp_path / "index.html", today=TODAY)
    index = build_index(entries, TODAY)
    sources = [records(html), {e["id"]:e["search"] for e in index["entries"]}]
    assert sources[0] == sources[1]
    assert sources[0]["groq"]["limits"].startswith("1,160 tokens/minute")
    queries = ["groq tokens", "1,160", "vendor/preview:free", "no card groq tokens", "qwen3 8b", "qwen 3.8", "missing", "api-free-tier"]
    script = SEARCH_ASSETS + "\nconst sources=" + json.dumps(sources) + ";\nconst config=" + json.dumps(index["search_config"]) + ";\n" + """
    const queries = QUERIES;
    console.log(JSON.stringify(sources.map(rows => queries.map(text => {
      const q = FreeTierSearch.parse(text, config);
      return Object.keys(rows).filter(id => {
        const row = rows[id]; FreeTierSearch.prepareOffer(row);
        return FreeTierSearch.wanted(row,q.picked.section,q.picked.filters) &&
          (!q.terms.length || FreeTierSearch.scoreOffer(row,q.terms)>0);
      }).sort();
    }))));""".replace("QUERIES", json.dumps(queries))
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    expected = [["groq"], ["groq"], ["groq"], ["groq"], ["version"], [], [], ["groq", "other", "version"]]
    assert json.loads(result.stdout) == [expected, expected]


def test_every_client_model_comes_from_its_generated_route_and_keeps_its_conditions():
    e = make(id="provider", api={"base_url":"https://x.ai/v1", "model_ids":["funded", "plain"],
        "anthropic_base_url":"https://x.ai", "model_access":{"funded":{"source":"https://x.ai/free", "initial_payment_usd":5}},
        "codex":{"base_url":"https://x.ai/v1", "source":"https://x.ai/codex", "quote":"Use Codex CLI with this provider"}},
        quotas=[{"amount":10,"unit":"requests","period":"day","scope":"account","source":"https://x.ai/free","quote":"10 requests per day"}])
    configs = _site_client_configs([e], TODAY)
    for client, rows in configs.items():
        row, = rows
        assert row["id"] == "provider"
        assert [m["id"] for m in row["models"]] == ["plain", "funded"]
        plain, funded = row["models"]
        assert not plain["access"] and "$5" in funded["access"]
        assert "10 requests/day" in row["limits"]
        assert not any("10 requests/day" in m["access"] for m in row["models"])
        assert "funded" in funded["model"]
        if client != "litellm":
            assert "funded" in funded["command"]
        if client in ("opencode", "litellm"):
            assert funded["model"] == "provider/funded"
    assert configs["codex"][0]["models"][1]["command"] == "codex -p provider -m funded"
    assert configs["claude"][0]["models"][1]["command"] == "claude-provider --model funded"


@pytest.mark.skipif(shutil.which("node") is None, reason="needs browser JavaScript runtime")
def test_an_exact_callable_id_wins_over_ambiguous_search_spellings():
    script = SEARCH_ASSETS + """
    const ids = ['vendor/ab', 'vendor/a-b'];
    console.log(JSON.stringify([
      FreeTierSearch.matchingIds('vendor/a-b',ids),
      FreeTierSearch.matchingIds('VENDOR/A_B',ids),
      FreeTierSearch.matchingIds('VENDOR/A_B',['vendor/a-b']),
      FreeTierSearch.matchingIds('vendor/ended',ids)
    ]));"""
    result = subprocess.run(["node", "-e", script],capture_output=True,text=True,timeout=30)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == [["vendor/a-b"], ["vendor/ab", "vendor/a-b"], ["vendor/a-b"], []]


@pytest.mark.skipif(shutil.which("node") is None, reason="needs browser JavaScript runtime")
def test_archived_reason_lead_is_shared_and_the_table_link_keeps_the_archive(tmp_path):
    from test_site import _js_function
    e = make(id="ended", name="Ended", delisted={"on":TODAY,
             "reason":"The free allowance was withdrawn.\n\n" + "Further details. " * 30})
    registry = tmp_path / "registry.yaml"
    save_registry(registry, [e])
    html = render_site(registry, TEMPLATES, tmp_path / "index.html", today=TODAY)
    index = build_index([e], TODAY)
    row, = index["entries"]
    assert row["archived"]
    assert records(html)["ended"] == row["search"]
    script = SEARCH_ASSETS + "\nvar row=" + json.dumps(row["search"]) + ";\nvar CONFIG=" + json.dumps(index["search_config"]) + ";\n" + """
    var location={search:'?q=withdrawn',pathname:'/'}, input={value:'withdrawn'}, toTable={};
    var history={replaceState:function(){}};
    """ + "\n".join(_js_function(html,n) for n in ("parse","withoutSearch","sync")) + """
    FreeTierSearch.prepareOffer(row);
    sync('',{},true);
    console.log(JSON.stringify({matches:FreeTierSearch.scoreOffer(row,['withdrawn'])>0,href:toTable.href}));"""
    result = subprocess.run(["node", "-e", script],capture_output=True,text=True,timeout=30)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"matches":True,"href":"browse.html?q=withdrawn&archived=1"}
