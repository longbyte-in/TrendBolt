from __future__ import annotations

import base64
import hashlib
import os
import secrets
import time
from dataclasses import dataclass
from typing import Optional

import httpx


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


@dataclass
class OAuthTokens:
    access_token: str
    refresh_token: str
    expires_at: int  # epoch seconds


class CanvaConnectOAuth:
    AUTH_URL = "https://www.canva.com/api/oauth/authorize"
    TOKEN_URL = "https://api.canva.com/rest/v1/oauth/token"

    def __init__(self) -> None:
        # Env vars per user instruction / Canva doc
        # https://www.canva.dev/docs/connect/authentication/
        self.client_id = os.getenv("CANVA_API_CLIENT_ID", os.getenv("CANVA_CLIENT_ID", ""))
        self.client_secret = os.getenv("CANVA_API_CLIENT_SECRET", os.getenv("CANVA_CLIENT_SECRET", ""))
        self.redirect_uri = os.getenv("CANVA_REDIRECT_URI", "https://d0ec209c3d1c.ngrok-free.app")
        scopes_env = os.getenv(
            "CANVA_SCOPES",
            "design:content:read",
        )
        self.scopes = [s for s in scopes_env.split() if s]

    def generate_pkce(self) -> tuple[str, str]:
        verifier = _b64url(secrets.token_bytes(48))  # ~64 chars
        digest = hashlib.sha256(verifier.encode("utf-8")).digest()
        challenge = _b64url(digest)
        return verifier, challenge
    
    def build_authorize_url(self, code_challenge: str, state: Optional[str] = None) -> str:
        import urllib.parse as up

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        if state:
            params["state"] = state
        return f"{self.AUTH_URL}?{up.urlencode(params)}"

    def _basic_auth_header(self) -> str:
        # Basic base64(client_id:client_secret)
        raw = f"{self.client_id}:{self.client_secret}".encode("utf-8")
        return f"Basic {base64.b64encode(raw).decode('utf-8')}"

    def exchange_code(self, code: str, code_verifier: str) -> OAuthTokens:
        # As per docs, recommend Basic Auth header, grant_type=authorization_code
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "code_verifier": code_verifier,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
        }
        headers = {
            "Authorization": self._basic_auth_header(),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(self.TOKEN_URL, data=data, headers=headers)
            resp.raise_for_status()
            js = resp.json()
        return OAuthTokens(
            access_token=js["access_token"],
            refresh_token=js.get("refresh_token", ""),
            expires_at=int(time.time()) + int(js.get("expires_in", 3600)),
        )

    def refresh(self, refresh_token: str) -> OAuthTokens:
        # Basic Auth header, grant_type=refresh_token
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
        }
        headers = {
            "Authorization": self._basic_auth_header(),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(self.TOKEN_URL, data=data, headers=headers)
            resp.raise_for_status()
            js = resp.json()
        return OAuthTokens(
            access_token=js["access_token"],
            refresh_token=js.get("refresh_token", refresh_token),
            expires_at=int(time.time()) + int(js.get("expires_in", 3600)),
        )


