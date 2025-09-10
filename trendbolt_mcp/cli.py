from __future__ import annotations

import asyncio
import json
from typing import Optional

import click

from .pipeline import run_once


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


if __name__ == "__main__":
    trendbolt()


