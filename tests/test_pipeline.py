import pytest


@pytest.mark.asyncio
async def test_pipeline_module_imports():
    import trendbolt_mcp.pipeline as pipeline

    assert hasattr(pipeline, "run_once")

