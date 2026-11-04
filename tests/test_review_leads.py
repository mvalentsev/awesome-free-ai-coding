import pytest

from freetier_radar.review_leads import collect_leads


def test_lead_collection_preserves_competitor_paths_without_inventing_domains():
    source = 'https://vendor.example/models'
    result = collect_leads({source: '''
        <a href="/haimaker-ai-alternative">Haimaker</a>
        <a href="https://unknown.example/free/?utm_source=vendor">Unknown API</a>
        <a href="https://unknown.example/free/#models">Same API</a>
        <a href="https://known.example/free/">Already reviewed</a>
        <a href="/privacy">Privacy</a><a href="https://x.com/vendor">Social</a>
        <a href="https://cdn.example/logo.svg">Logo</a>
        <a href="https://[broken">Malformed</a>
    '''}, {'known.example'}, content_types={source: 'text/html'})
    assert [r['url'] for r in result] == [
        'https://unknown.example/free/', 'https://unknown.example/free/?utm_source=vendor',
        'https://vendor.example/haimaker-ai-alternative']
    assert [r['kind'] for r in result] == ['link', 'link', 'comparison']
    assert all(r['sources'] == [source] for r in result)


def test_source_verdict_does_not_cover_every_repository_on_the_same_host():
    source = 'https://directory.example/list'
    result = collect_leads({source: '''
        [Read](https://github.com/owner/read-list)
        [New](https://github.com/owner/new-list)
    '''}, {'https://github.com/owner/read-list'})
    assert [r['url'] for r in result] == ['https://github.com/owner/new-list']


def test_exact_decisions_normalize_url_aliases_without_covering_another_path():
    result = collect_leads({'https://directory.example/list': '''
        <a href="https://known.example/models/?ref=new#current">Known</a>
        <a href="https://known.example/models/?ref=old#current">Exact known resource</a>
        <a href="https://known.example/Models/">Different path</a>
        <a href="https://unknown.example/free">Unknown</a>
    '''}, {'https://www.known.example/models/?ref=old#previous', 'https://[broken'},
        content_types={'https://directory.example/list': 'text/html'})
    assert [r['url'] for r in result] == [
        'https://known.example/Models/', 'https://known.example/models/?ref=new',
        'https://unknown.example/free']


def test_invalid_source_does_not_hide_valid_source_provenance():
    body = '<a href="https://unknown.example/free">Unknown</a>'
    result = collect_leads({'https://[broken': body, 'https://directory.example/list': body}, set())
    assert [(r['url'], r['sources']) for r in result] == [
        ('https://unknown.example/free', ['https://directory.example/list'])]


@pytest.mark.parametrize('literal', [
    '```html\n<a href="/fake">Model comparisons directory</a>\n```',
    '`<a href="/fake">Model comparisons directory</a>`',
    'Text <script>a.href.replace(/([?&](continue|followup)=)/g, "");</script>',
    'Text <style>[Model comparisons directory](/fake)</style>',
])
def test_markdown_code_and_inline_hidden_html_are_not_link_sources(literal):
    source = 'https://vendor.example/list.md'
    result = collect_leads({source: literal+'\n\n[Model comparisons directory](/real-directory)'}, set())
    assert [(r['url'], r['kind']) for r in result] == [
        ('https://vendor.example/real-directory', 'comparison')]


def test_reference_links_remain_leads_beside_html_badges_and_pdf_sources():
    source = 'https://directory.example/list'
    result = collect_leads({source: '''
        <a href="https://known.example/">An existing provider</a>
        [New provider][provider]
        [provider]: https://unknown.example/free
        [Offer terms](https://new.example/free-tier.pdf)
    '''}, {'known.example'})
    assert [r['url'] for r in result] == [
        'https://new.example/free-tier.pdf', 'https://unknown.example/free']


def test_comparison_routes_preserve_sources_and_do_not_invent_vendor_domains():
    pricing = 'https://vendor.example/pricing'
    terms = 'https://vendor.example/terms'
    result = collect_leads({
        terms: '[Other tool](https://vendor.example/tool-a-vs-tool-b#terms)',
        pricing: '''<a href="/tool-a-vs-tool-b?ref=pricing">Vs another tool</a>
                    <a href="/tool-a-vs-tool-b#features">Same comparison</a>''',
    }, {'vendor.example'})
    assert [(r['url'], r['sources'], r['kind']) for r in result] == [
        ('https://vendor.example/tool-a-vs-tool-b', [pricing, terms], 'comparison'),
        ('https://vendor.example/tool-a-vs-tool-b?ref=pricing', [pricing], 'comparison')]


def test_ordinary_known_paths_and_editor_names_do_not_become_comparison_leads():
    source = 'https://vendor.example/pricing'
    result = collect_leads({source: '''
        <a href="/privacy">Privacy</a><a href="/plans">Compare plans</a>
        <a href="/integrations/vscode">VS Code</a>
        <a href="/comparison-settings">Settings</a>
        <a href="/docs/comparison-guide">Guide</a>
        <a href="/compare/main...release">Compare revisions</a>
        <a href="/v1/models">Models</a>
    '''}, {'vendor.example'})
    assert result == []


def test_named_comparisons_merge_html_and_markdown_provenance():
    pricing = 'https://vendor.example/pricing'
    terms = 'https://vendor.example/terms'
    result = collect_leads({
        pricing: '''<a href="/library/models?ref=nav" title="Model comparisons directory">Read</a>
            [Models](/library/models#models "Alternatives")
            <a href="/library/providers" aria-label="European AI alternatives directory"></a>
            <a href="/library/review"><img alt="Tool A vs Tool B"></a>''',
        terms: ('[Model comparisons directory][models]\n\n'
                '[models]: https://vendor.example/library/models#overview\n\n'
                '[European AI alternatives directory](/library/providers)'),
    }, {'vendor.example'})
    assert [(r['url'], r['kind'], r['sources']) for r in result] == [
        ('https://vendor.example/library/models', 'comparison', [terms]),
        ('https://vendor.example/library/models?ref=nav', 'comparison', [pricing]),
        ('https://vendor.example/library/providers', 'comparison', [pricing, terms]),
        ('https://vendor.example/library/review', 'comparison', [pricing])]


def test_navigation_hidden_code_and_boolean_attributes_do_not_create_comparisons():
    result = collect_leads({'https://vendor.example/pricing': '''
        <a href="/client" aria-label title><img alt>Client
            <script>"Alternatives to Other tool"</script>
            <style>/* Model comparisons directory */</style></a>
        <a href="/auth">Alternative authentication</a>
        <a href="/plans">Compare free plans</a>
        <a href="/compare/main...release" title="Main vs Release">Diff</a>
        <a href="/assets/roundup.svg">Model comparisons directory</a>
    '''}, {'vendor.example'})
    assert result == []


def test_later_comparison_label_does_not_lose_earlier_source():
    pricing = 'https://vendor.example/pricing'
    terms = 'https://vendor.example/terms'
    result = collect_leads({
        pricing: '<a href="https://unknown.example/library">Read more</a>',
        terms: '[Alternatives to Other tool](https://unknown.example/library)',
    }, set())
    assert [(r['url'], r['kind'], r['sources']) for r in result] == [
        ('https://unknown.example/library', 'comparison', [pricing, terms])]


@pytest.mark.parametrize('link,definition', [
    ('[Model comparisons directory][  MODEL   LIST ]', '[model list]: /library'),
    ('[Model comparisons directory][]', '[Model comparisons directory]: /library'),
    ('[Model comparisons directory]', '[Model comparisons directory]: /library'),
])
def test_reference_comparison_labels_survive_reference_forms_and_whitespace(link, definition):
    source = 'https://vendor.example/pricing'
    result = collect_leads({source: '<a href="/privacy">Privacy</a>\n\n'+link+'\n\n'+definition},
                           {'vendor.example'})
    assert [(r['url'], r['kind'], r['sources']) for r in result] == [
        ('https://vendor.example/library', 'comparison', [source])]


@pytest.mark.parametrize('markdown', [
    '[Model **comparisons** directory](<https://vendor.example/library>)',
    '[Alternatives to `Other tool`][models]\n\n[models]: <https://vendor.example/library>',
    '[![Model **comparisons** directory](/badge.svg)](/library)',
])
def test_markdown_link_names_use_visible_formatting_and_angle_destinations(markdown):
    source = 'https://vendor.example/pricing'
    result = collect_leads({source: '<a href="/privacy">Privacy</a>\n\n'+markdown}, {'vendor.example'})
    assert [(r['url'], r['kind']) for r in result] == [
        ('https://vendor.example/library', 'comparison')]


@pytest.mark.parametrize('code', [
    '```javascript\n[CAT_NECESSARY]: {\n[Model comparisons directory](/fake)\n```',
    '~~~markdown\n[Model comparisons directory](/fake)\n~~~',
    '    [Model comparisons directory](/fake)',
    '`[Model comparisons directory](/fake)`',
])
def test_markdown_code_is_not_a_relative_link_or_reference(code):
    source = 'https://vendor.example/tool-a-vs-tool-b/'
    result = collect_leads({source: code+'\n\n[Model comparisons directory](/library)'}, {'vendor.example'})
    assert [(r['url'], r['kind']) for r in result] == [
        ('https://vendor.example/library', 'comparison')]


def test_existing_literal_absolute_source_urls_survive_code_examples():
    source = 'https://vendor.example/pricing'
    result = collect_leads({source: '<a href="/privacy">Privacy</a>\n<pre><code>\n'
        '[Model comparisons directory]: https://unknown.example/free\n</code></pre>'}, {'vendor.example'})
    assert [(r['url'], r['kind']) for r in result] == [('https://unknown.example/free', 'link')]
