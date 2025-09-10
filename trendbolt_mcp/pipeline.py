from __future__ import annotations

from typing import Sequence

from .config import get_settings
from .tools.reddit import get_trending
from .tools.llm import generate_canvas_post
from .tools.canva import create_design
from .tools.facebook import publish_photo


async def run_once(
    subreddits: Sequence[str] | None = None,
    min_score: int | None = None,
    template_id: str | None = None,
    strategy: str | None = None,
    limit: int | None = None,
    time_filter: str | None = None,
) -> dict:
    s = get_settings()
    subs = list(subreddits or s.subreddits)
    min_s = int(min_score if min_score is not None else s.min_score)
    topics = await get_trending(
        subs,
        strategy=strategy or "hot",
        limit=limit or 20,
        time_filter=time_filter or "day",
        min_score=min_s,
    )
    if not topics:
        return {"status": "no_topics"}
    topic = topics[0]
    content = generate_canvas_post(topic=topic, brand={"cta": "Follow TrendBolt"})
    design = create_design(
        template_id=template_id or s.template_id,
        design_brief=content["design_brief"],
    )
    post = publish_photo(caption=content["caption"], image_url=design["asset_url"])  # type: ignore[arg-type]
    return {"status": "ok", "topic": topic, "content": content, "design": design, "post": post}


