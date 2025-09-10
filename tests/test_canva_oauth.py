from trendbolt_mcp.integrations.canva_connect import CanvaConnectOAuth


def test_pkce_and_auth_url(monkeypatch):
    monkeypatch.setenv("CANVA_API_CLIENT_ID", "client")
    monkeypatch.setenv("CANVA_REDIRECT_URI", "https://example/callback")
    oauth = CanvaConnectOAuth()
    verifier, challenge = oauth.generate_pkce()
    assert len(verifier) > 10 and len(challenge) > 10
    url = oauth.build_authorize_url(challenge, state="abc")
    assert "client_id=client" in url and "code_challenge=" in url

