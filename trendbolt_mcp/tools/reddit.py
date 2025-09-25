"""Reddit trending tool implementation using asyncpraw.

The public entry `get_trending` is designed to be testable by allowing a
dependency-injected client. Production uses `AsyncPrawFetcher` which reads
credentials from app settings.
"""

from __future__ import annotations

from typing import Any, AsyncIterable, Protocol
import logging

from ..config import get_settings

logger = logging.getLogger(__name__)


class RedditFetcher(Protocol):
    async def fetch(
        self,
        subreddit: str,
        strategy: str,
        limit: int,
        time_filter: str,
    ) -> AsyncIterable[Any]:
        ...


class AsyncPrawFetcher:
    def __init__(self) -> None:
        import asyncpraw  # local import to keep import-time deps light

        settings = get_settings()
        self._asyncpraw = asyncpraw
        self._client = asyncpraw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent,
        )

    async def fetch(
        self, subreddit: str, strategy: str, limit: int, time_filter: str
    ) -> AsyncIterable[Any]:
        sr = await self._client.subreddit(subreddit, fetch=True)
        if strategy == "top":
            return sr.top(limit=limit, time_filter=time_filter)
        if strategy == "new":
            return sr.new(limit=limit)
        # default: hot
        return sr.hot(limit=limit)

    async def close(self) -> None:
        await self._client.close()


def _shape_post(p: Any) -> dict:
    return {
        "id": getattr(p, "id", None) and f"t3_{getattr(p, 'id')}",
        "title": getattr(p, "title", None),
        "url": getattr(p, "url", None),
        "subreddit": str(getattr(getattr(p, "subreddit", None), "display_name", None) or ""),
        "score": int(getattr(p, "score", 0) or 0),
        "num_comments": int(getattr(p, "num_comments", 0) or 0),
        "created_utc": float(getattr(p, "created_utc", 0.0) or 0.0),
    }


async def get_post_by_id(post_id: str, timeout_seconds: float = 30.0) -> dict | None:
    """Fetch a single Reddit post by its ID (e.g., t3_1ndjq1c)."""
    import asyncpraw  # local import to keep import-time deps light
    
    s = get_settings()
    if not s.reddit_client_id or not s.reddit_client_secret:
        raise ValueError("Reddit credentials required. Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET.")
    
    reddit = asyncpraw.Reddit(
        client_id=s.reddit_client_id,
        client_secret=s.reddit_client_secret,
        user_agent=s.reddit_user_agent,
    )
    
    try:
        submission = await reddit.submission(id=post_id.replace('t3_', ''))
        return {
            "id": f"t3_{submission.id}",
            "title": submission.title,
            "url": submission.url,
            "score": submission.score,
            "subreddit": str(submission.subreddit),
            "created_utc": submission.created_utc,
            "selftext": submission.selftext[:500] if submission.selftext else "",
        }
    except Exception as e:
        logger.error(f"Failed to fetch post {post_id}: {e}")
        return None
    finally:
        await reddit.close()


async def get_trending(
    subreddits: list[str],
    strategy: str = "hot",
    limit: int = 20,
    time_filter: str = "day",
    min_score: int = 0,
    client: RedditFetcher | None = None,
) -> list[dict]:
    """Fetch trending posts from given subreddits and return shaped results.

    - strategy: "hot" | "top" | "new"
    - time_filter: for "top" (hour, day, week, month, year, all)
    - min_score: filter low-quality posts
    """
    close_client = False
    if client is None:
        client = AsyncPrawFetcher()
        close_client = True

    results: list[dict] = []
    for sub in subreddits:
        try:
            posts = client.fetch(sub, strategy, limit, time_filter)
            async for post in posts:
                shaped = _shape_post(post)
                if shaped["score"] >= min_score:
                    results.append(shaped)
        except Exception:
            # Skip failing subreddits in this minimal implementation; higher layers log properly
            continue

    # Rank by score desc and trim
    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    if close_client and isinstance(client, AsyncPrawFetcher):  # type: ignore[arg-type]
        await client.close()
    return results



