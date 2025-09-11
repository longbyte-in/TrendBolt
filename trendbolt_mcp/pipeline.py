from __future__ import annotations

from typing import Sequence

from .config import get_settings
from .tools.reddit import get_trending
from .tools.llm import generate_canvas_post
from .tools.canva_connect import create_autofill_job, get_autofill_job
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
    # Map content to autofill data; adjust keys per your brand template dataset
    autofill_data = {
        "title": {"type": "text", "text": content.get("title", "")},
        "headline": {"type": "text", "text": content.get("headline", "")},
        "description": {"type": "text", "text": content.get("description", "")},
    }
    job = create_autofill_job(data=autofill_data, brand_template_id=template_id or s.canva_brand_template_id)
    job_id = job.get("job", {}).get("id")
    design_result: dict | None = None
    if job_id:
        # Simple poll loop (caller may implement smarter polling externally)
        for _ in range(10):
            j = get_autofill_job(job_id)
            status = j.get("job", {}).get("status")
            if status == "success":
                design_result = j["job"]["result"]["design"]
                break
            if status == "failed":
                break
        else:
            status = "timeout"
    else:
        status = "no_job"

    # Post to Facebook if thumbnail URL available
    post = None
    if design_result and design_result.get("thumbnail", {}).get("url"):
        post = publish_photo(
            caption=content.get("description", ""),
            image_url=design_result["thumbnail"]["url"],
        )
    return {"status": status, "topic": topic, "content": content, "design": design_result, "post": post}


