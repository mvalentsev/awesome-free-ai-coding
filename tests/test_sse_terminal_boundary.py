"""A terminal SSE header does not establish that its JSON payload arrived."""
import httpx
import pytest
import respx
from freetier_radar.prober import _codex_call,_codex_completed,_codex_ended

class Chunks(httpx.AsyncByteStream):
    def __init__(self,*chunks):self.chunks=chunks
    async def __aiter__(self):
        for chunk in self.chunks:yield chunk

@respx.mock
async def test_reader_waits_for_terminal_data_after_separate_event_header():
    respx.post('https://vendor.example/v1/responses').mock(return_value=httpx.Response(200,
        stream=Chunks(b'data: {"type":"response.output_item.done"}\n\n',
                      b'event: response.completed\n',
                      b'data: {"type":"response.completed","response":{"status":"completed"}}\n\n')))
    async with httpx.AsyncClient() as client:
        answer=await _codex_call(client,'https://vendor.example/v1/responses','model',{},1,0)
    assert _codex_completed(answer)
    assert '"status":"completed"' in answer[1]

@pytest.mark.parametrize('text',[
    'event: response.completed\n',
    'data: {"type":"response.completed","response":',
    'data: {"type":"response.output_text.delta","delta":"response.completed"}\n\n',
])
def test_header_partial_json_and_assistant_words_do_not_end_stream(text):
    assert not _codex_ended(text)

@pytest.mark.parametrize('kind',['response.completed','response.failed','response.incomplete'])
def test_complete_terminal_data_event_ends_stream(kind):
    assert _codex_ended('event: '+kind+'\ndata: {"type":"'+kind+'"}\n\n')
