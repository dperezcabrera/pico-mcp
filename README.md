# pico-mcp

[![PyPI](https://img.shields.io/pypi/v/pico-mcp.svg)](https://pypi.org/project/pico-mcp/)
[![Ask DeepWiki](https://img.shields.io/badge/Ask-DeepWiki-blue)](https://deepwiki.com/dperezcabrera/pico-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
![CI (tox matrix)](https://github.com/dperezcabrera/pico-mcp/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/dperezcabrera/pico-mcp/branch/main/graph/badge.svg)](https://codecov.io/gh/dperezcabrera/pico-mcp)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=dperezcabrera_pico-mcp&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=dperezcabrera_pico-mcp)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=dperezcabrera_pico-mcp&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=dperezcabrera_pico-mcp)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=dperezcabrera_pico-mcp&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=dperezcabrera_pico-mcp)
[![PyPI Downloads](https://img.shields.io/pypi/dm/pico-mcp)](https://pypi.org/project/pico-mcp/)
[![Docs](https://img.shields.io/badge/Docs-pico--mcp-blue?style=flat&logo=readthedocs&logoColor=white)](https://dperezcabrera.github.io/pico-mcp/)
[![Interactive Lab](https://img.shields.io/badge/Learn-online-green?style=flat&logo=python&logoColor=white)](https://dperezcabrera.github.io/pico-learn/)

Expose [pico-ioc](https://github.com/dperezcabrera/pico-ioc) components as [Model Context Protocol](https://modelcontextprotocol.io) servers: `@tool`, `@resource` and `@prompt` on component methods, served by the official `mcp` SDK.

## Installation

```bash
pip install pico-mcp
```

Auto-discovered by pico-boot; with plain pico-ioc add `"pico_mcp"` to `init(modules=[...])`.

## Quick start

```python
from mcp.server.mcpserver import MCPServer
from pico_boot import init
from pico_ioc import component
from pico_mcp import prompt, resource, tool


@component
class Orders:
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    @tool(description="Look up an order by id", read_only=True)
    def get_order(self, order_id: str) -> Order:
        return self.repo.get(order_id)

    @tool(destructive=True)
    def cancel_order(self, order_id: str) -> None:
        self.repo.cancel(order_id)

    @resource("orders://{order_id}")
    def order_text(self, order_id: str) -> str:
        return self.repo.get(order_id).summary()

    @prompt()
    def review(self, order_id: str) -> str:
        """Ask the model to review an order."""
        return f"Review order {order_id} and flag anything unusual."


server = init(modules=["orders"]).get(MCPServer)
server.run()                              # stdio: Claude Code, Claude Desktop, Cursor
# server.run(transport="streamable-http") # http://127.0.0.1:8000/mcp
```

The input schema comes from the method signature (minus `self`), the description from the docstring or `description=`. Every call resolves the component through the container, so constructor injection, scopes and `@intercepted_by` interceptors apply as for any other caller. Two components declaring the same tool, resource or prompt name fail at startup instead of shadowing each other.

`read_only`, `destructive`, `idempotent` and `open_world` become the standard MCP tool annotations (`readOnlyHint`, `destructiveHint`...). Clients use them to decide what to confirm with the user, and an approval gateway such as [pico-tool-gateway](https://github.com/dperezcabrera/pico-tool-gateway) can route by them: read-only calls pass, destructive ones wait for a human. A tool without flags says nothing, which the MCP spec reads as possibly destructive.

Name the server with config:

```yaml
mcp:
  name: orders
  instructions: Call get_order before answering questions about an order.
```

## Documentation

Full documentation: https://dperezcabrera.github.io/pico-mcp/

## Built for AI-assisted development

pico-mcp is part of an ecosystem designed for humans and coding agents building software together. Every package ships `AGENTS.md` working conventions, an `llms.txt` machine-readable docs index and documented behaviour pinned by regression tests; [pico-testing](https://github.com/dperezcabrera/pico-testing) gives agents a verification loop for their own changes, and releases are gated by the whole ecosystem booting together against real infrastructure. The full story: [Built for AI-assisted development](https://github.com/dperezcabrera/pico-ioc#built-for-ai-assisted-development).

Install the agent skills for [Claude Code](https://code.claude.com) or [OpenAI Codex](https://openai.com/index/introducing-codex/):

```bash
curl -sL https://raw.githubusercontent.com/dperezcabrera/pico-skills/main/install.sh | bash
```

The `pico-conventions` skill teaches the assistant this module's API surface and invariants; `/add-component` and `/add-tests` scaffold components and tests that use it.

## License

MIT
