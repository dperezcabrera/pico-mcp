# Getting Started

## Prerequisites

- Python >= 3.11 (tested on 3.11, 3.12, 3.13 and 3.14)
- pico-ioc >= 2.5.2 (pico-boot recommended for auto-discovery)
- mcp >= 2.0, < 3 (installed automatically)

## Install

```bash
pip install pico-mcp
```

## Key concepts

| Piece | What it does |
|---|---|
| `@tool(read_only=, destructive=, idempotent=, open_world=, **options)` | Exposes the method as an MCP tool; the flags become the standard tool annotations, `options` go to `MCPServer.add_tool` (`name`, `description`, `title`...) |
| `@resource(uri, **options)` | Exposes the method as a resource; `{param}` placeholders in `uri` make it a template |
| `@prompt(**options)` | Exposes the method as a prompt |
| `MCPServer` | Provided by the container as a singleton, with every marked method registered |
| `McpSettings` | `mcp.name` and `mcp.instructions`, announced to clients |

## Semantics

- The method signature minus `self` is the input schema; the return annotation drives structured output, exactly as for a plain function given to the SDK.
- A parameter annotated `mcp.server.mcpserver.Context` receives the request context and is left out of the schema.
- Each call resolves the component through the container: singletons share state, prototype scope gets a fresh instance per call, and interceptors run.
- Sync and async methods are both supported.
- An exception inside a tool reaches the client as an error result (`is_error`), as the SDK does for any tool.
- Two marked methods with the same tool or prompt name, or the same resource URI, fail at startup.

## Tool annotations

The four flags map one to one to the MCP tool annotations:

| Flag | Annotation | Meaning |
|---|---|---|
| `read_only=True` | `readOnlyHint` | Does not change its environment (also sets `destructiveHint: false`) |
| `destructive=True` | `destructiveHint` | May destroy or overwrite data |
| `idempotent=True` | `idempotentHint` | Repeating the call with the same arguments has no extra effect |
| `open_world=True` | `openWorldHint` | Talks to external systems (web, email, payments) |

Only the flags you pass are set. The spec reads a missing hint conservatively
(`destructiveHint` and `openWorldHint` default to true), so an unannotated tool
is treated as possibly destructive. `read_only=True` with `destructive=True`
raises at import; the flags and a raw `annotations=` cannot be combined.

```python
@component
class Payments:
    @tool(read_only=True)
    def balance(self, account: str) -> int: ...

    @tool(destructive=True, open_world=True)
    def refund(self, charge_id: str) -> str: ...
```

Annotations are hints from the server: a client or gateway trusts them only as
far as it trusts the server that declares them.

## Running the server

```python
from mcp.server.mcpserver import MCPServer
from pico_boot import init

server = init(modules=["myapp"]).get(MCPServer)
server.run()                               # stdio
server.run(transport="streamable-http")    # HTTP on 127.0.0.1:8000/mcp
```

`MCPServer` is the SDK object itself: anything the SDK offers (custom routes, `streamable_http_app()`, more tools added by hand) works on it.

## Configuration

```yaml
mcp:
  name: orders                       # default "pico-mcp"
  instructions: Use get_order first. # optional
```

## Testing

The SDK's `Client` connects to a server in-process, with no transport:

```python
from mcp import Client
from mcp.server.mcpserver import MCPServer


async def test_get_order(make_container):
    server = make_container(orders_module).get(MCPServer)
    async with Client(server) as client:
        result = await client.call_tool("get_order", {"order_id": "1"})
    assert not result.is_error
```
