from trendbolt_mcp.tools import llm as llm_tool


class FakeLLM:
    def __init__(self, payload: str) -> None:
        self._payload = payload

    def generate(self, prompt: str) -> str:
        return self._payload


def test_generate_canvas_post_parses_json():
    payload = (
        '{"caption":"Hello","alt_text":"Alt","hashtags":["#x"],'
        '"design_brief":{"headline":"H","subtext":"S","cta":"C",'
        '"color_theme":"dark_on_light","layout":"headline_top_subtext_center_cta_bottom",'
        '"image_guidance":"g"}}'
    )
    out = llm_tool.generate_canvas_post(
        topic={"title": "T", "url": "u"}, brand={"cta": "C"}, client=FakeLLM(payload)
    )
    assert out["caption"] == "Hello"
    assert out["design_brief"]["headline"] == "H"


def test_generate_canvas_post_fallback_on_non_json():
    out = llm_tool.generate_canvas_post(
        topic={"title": "T", "url": "u"}, brand={"cta": "C"}, client=FakeLLM("Not JSON")
    )
    assert "caption" in out and "design_brief" in out

