Read and follow ./AGENTS.md for project conventions.

## Pico Ecosystem Context

pico-mcp — Expose pico-ioc components as MCP servers: `@tool`, `@resource` and `@prompt` on component methods, registered on the official `mcp` SDK's `MCPServer`, which the container provides. Auto-discovered via the `pico_boot.modules` entry point.

## Key Reminders

- pico-ioc dependency: `>= 2.5.2`; mcp `>= 2.0.0, < 3`
- **NEVER change `version_scheme`** in pyproject.toml. It MUST remain `"post-release"`.
- requires-python >= 3.11
- Commit messages: one line only
