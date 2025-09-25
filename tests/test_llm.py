from trendbolt_mcp.tools import llm as llm_tool


class FakeLLM:
    def __init__(self, payload: str) -> None:
        self._payload = payload

    def generate(self, prompt: str) -> str:
        return self._payload


def test_generate_canvas_post_parses_json():
    payload = (
        '{"title":"Hello","headline":"H","description":"D","image_available":true}'
    )
    out = llm_tool.generate_canvas_post(
        topic={"title": "T", "url": "u"}, brand={"cta": "C"}, client=FakeLLM(payload)
    )
    assert out["title"] == "Hello"
    assert out["headline"] == "H"


def test_generate_canvas_post_fallback_on_non_json():
    out = llm_tool.generate_canvas_post(
        topic={"title": "T", "url": "u"}, brand={"cta": "C"}, client=FakeLLM("Not JSON")
    )
    assert "title" in out and "description" in out

