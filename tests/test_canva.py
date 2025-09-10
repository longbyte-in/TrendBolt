import json

import httpx

from trendbolt_mcp.tools.canva import create_design, _sign_payload


def test_sign_payload_hex():
    sig = _sign_payload("secret", b"{}")
    assert len(sig) == 64


class FakeClient:
    def __init__(self, response_json):
        self._response_json = response_json
        self.closed = False

    def post(self, url, content=None, headers=None):
        class R:
            def __init__(self, payload):
                self._payload = payload

            def raise_for_status(self):
                return None

            def json(self):
                return self._payload

        return R(self._response_json)

    def close(self):
        self.closed = True


def test_create_design_happy_path(monkeypatch):
    monkeypatch.setenv("REDDIT_CLIENT_ID", "x")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "y")
    monkeypatch.setenv("CANVA_BRIDGE_BASE_URL", "https://bridge")
    monkeypatch.setenv("CANVA_BRIDGE_SIGNING_SECRET", "s")
    monkeypatch.setenv("FACEBOOK_APP_ID", "a")
    monkeypatch.setenv("FACEBOOK_APP_SECRET", "b")
    monkeypatch.setenv("FACEBOOK_PAGE_ID", "c")
    monkeypatch.setenv("FACEBOOK_PAGE_ACCESS_TOKEN", "d")

    out = create_design(
        template_id="t",
        design_brief={"headline": "H"},
        client=FakeClient({
            "asset_url": "https://storage/asset.png",
            "preview_url": "https://storage/prev.png",
            "design_id": "id",
        }),
    )
    assert out["asset_url"].endswith("asset.png")

