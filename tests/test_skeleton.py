def test_skeleton_imports():
    import trendbolt_mcp
    import trendbolt_mcp.server
    import trendbolt_mcp.tools

    assert hasattr(trendbolt_mcp, "__version__")

