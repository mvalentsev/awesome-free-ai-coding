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
