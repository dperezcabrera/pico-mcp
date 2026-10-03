"""The public API is exactly what ``__all__`` declares (stability contract)."""

import pico_mcp


def test_public_api_is_declared_and_importable():
    assert set(pico_mcp.__all__) == {"McpServerFactory", "McpSettings", "prompt", "resource", "tool"}
    for name in pico_mcp.__all__:
        assert getattr(pico_mcp, name) is not None
