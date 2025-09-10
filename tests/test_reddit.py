import types
import asyncio
import pytest

from trendbolt_mcp.tools import reddit as reddit_tool


class FakePost:
    def __init__(self, id, title, url, subreddit, score, num_comments, created_utc):
        self.id = id
        self.title = title
        self.url = url
        self.subreddit = types.SimpleNamespace(display_name=subreddit)
        self.score = score
        self.num_comments = num_comments
        self.created_utc = created_utc


class FakeFetcher:
    async def fetch(self, subreddit: str, strategy: str, limit: int, time_filter: str):
        for i in range(3):
            yield FakePost(
                id=f"abc{i}",
                title=f"Title {i}",
                url=f"https://example.com/{i}",
                subreddit=subreddit,
                score=100 - i,
                num_comments=10 * i,
                created_utc=1234567890 + i,
            )


@pytest.mark.asyncio
async def test_get_trending_shapes_and_sorts():
    results = await reddit_tool.get_trending(
        subreddits=["technology"],
        client=FakeFetcher(),
    )
    assert len(results) == 3
    assert results[0]["score"] >= results[1]["score"] >= results[2]["score"]

