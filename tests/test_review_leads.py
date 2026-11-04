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
    '''}, {'known.example'})
    assert [r['url'] for r in result] == [
        'https://unknown.example/free/', 'https://vendor.example/haimaker-ai-alternative']
    assert [r['kind'] for r in result] == ['link', 'comparison']
    assert all(r['sources'] == [source] for r in result)


def test_source_verdict_does_not_cover_every_repository_on_the_same_host():
    source = 'https://directory.example/list'
    result = collect_leads({source: '''
        [Read](https://github.com/owner/read-list)
        [New](https://github.com/owner/new-list)
    '''}, {'https://github.com/owner/read-list'})
    assert [r['url'] for r in result] == ['https://github.com/owner/new-list']


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
        ('https://vendor.example/tool-a-vs-tool-b', [pricing, terms], 'comparison')]


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
