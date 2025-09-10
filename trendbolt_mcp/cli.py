from __future__ import annotations

import asyncio
import json
from typing import Optional

import click

from .pipeline import run_once
from .integrations.canva_connect import CanvaConnectOAuth


@click.group()
def trendbolt() -> None:
    """TrendBolt command line."""


@trendbolt.command("run")
@click.option("--subreddit", "subreddits", multiple=True, help="Subreddit(s) to scan")
@click.option("--min-score", type=int, default=None, help="Minimum score filter")
@click.option("--template-id", type=str, default=None, help="Canva template id")
@click.option("--strategy", type=click.Choice(["hot", "top", "new"]), default=None)
@click.option("--limit", type=int, default=None)
@click.option("--time-filter", type=str, default=None, help="top: hour/day/week/month/year/all")
def run_cmd(
    subreddits: tuple[str, ...],
    min_score: Optional[int],
    template_id: Optional[str],
    strategy: Optional[str],
    limit: Optional[int],
    time_filter: Optional[str],
) -> None:
    """Run the end-to-end pipeline once and print a JSON summary."""
    result = asyncio.run(
        run_once(
            subreddits=subreddits or None,
            min_score=min_score,
            template_id=template_id,
            strategy=strategy,
            limit=limit,
            time_filter=time_filter,
        )
    )
    click.echo(json.dumps(result, indent=2))


@trendbolt.group()
def canva() -> None:
    """Canva Connect OAuth helpers."""


@canva.command("auth-url")
@click.option("--state", type=str, default=None)
def canva_auth_url(state: Optional[str]) -> None:
    oauth = CanvaConnectOAuth()
    verifier, challenge = oauth.generate_pkce()
    url = oauth.build_authorize_url(challenge, state=state)
    out = {"authorize_url": url, "code_verifier": verifier}
    click.echo(json.dumps(out, indent=2))


@canva.command("exchange")
@click.option("--code", required=True, type=str)
@click.option("--verifier", required=True, type=str)
def canva_exchange(code: str, verifier: str) -> None:
    oauth = CanvaConnectOAuth()
    tokens = oauth.exchange_code(code, verifier)
    click.echo(json.dumps(tokens.__dict__, indent=2))


@canva.command("refresh")
@click.option("--refresh-token", required=True, type=str)
def canva_refresh(refresh_token: str) -> None:
    oauth = CanvaConnectOAuth()
    tokens = oauth.refresh(refresh_token)
    click.echo(json.dumps(tokens.__dict__, indent=2))


@trendbolt.command("mcp")
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--port", default=8765, help="Port to bind to")
def mcp_serve(host: str, port: int) -> None:
    """Start the TrendBolt MCP server."""
    import asyncio
    from .server import main
    
    click.echo(f"Starting TrendBolt MCP server on {host}:{port}")
    asyncio.run(main())


if __name__ == "__main__":
    trendbolt()


