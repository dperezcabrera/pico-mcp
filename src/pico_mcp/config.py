"""Settings for pico-mcp (prefix ``mcp``, zero-config)."""

from dataclasses import dataclass

from pico_ioc import configured


@configured(target="self", prefix="mcp", mapping="tree")
@dataclass
class McpSettings:
    """Identity the server announces to MCP clients."""

    name: str = "pico-mcp"
    instructions: str | None = None
