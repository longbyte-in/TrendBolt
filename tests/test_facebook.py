from trendbolt_mcp.tools.facebook import publish_photo


class FakeClient:
    def __init__(self, payload):
        self._payload = payload

    def post(self, url, data=None):
        class R:
            def __init__(self, p):
                self._p = p

            def raise_for_status(self):
                return None

            def json(self):
                return self._p

        return R(self._payload)


def test_publish_photo_returns_id(monkeypatch):
    monkeypatch.setenv("REDDIT_CLIENT_ID", "x")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "y")
    monkeypatch.setenv("CANVA_BRIDGE_BASE_URL", "https://x")
    monkeypatch.setenv("CANVA_BRIDGE_SIGNING_SECRET", "s")
    monkeypatch.setenv("FACEBOOK_APP_ID", "a")
    monkeypatch.setenv("FACEBOOK_APP_SECRET", "b")
    monkeypatch.setenv("FACEBOOK_PAGE_ID", "c")
    monkeypatch.setenv("FACEBOOK_PAGE_ACCESS_TOKEN", "d")

    out = publish_photo(
        caption="hello",
        image_url="https://example/1.png",
        client=FakeClient({"id": "123"}),
    )
    assert out["post_id"] == "123"

