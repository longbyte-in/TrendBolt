def test_cli_module_import():
    import trendbolt_mcp.cli as cli

    assert hasattr(cli, "trendbolt")

