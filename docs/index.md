# pico-mcp

`@tool`, `@resource` and `@prompt` on pico components: an MCP server built from your container, served by the official `mcp` SDK.

## Install

```bash
pip install pico-mcp
```

## 30-second example

```python
from mcp.server.mcpserver import MCPServer
from pico_boot import init
from pico_ioc import component
from pico_mcp import tool


@component
class Weather:
    @tool(description="Current temperature in Celsius for a city")
    def temperature(self, city: str) -> float:
        return 21.5


init(modules=[__name__]).get(MCPServer).run()
```

No wiring: pico-boot discovers the module, the factory discovers the marked methods and the SDK derives each tool's input schema from the signature. Point any MCP client (Claude Code, Claude Desktop, Cursor) at the script and the tool is there.
