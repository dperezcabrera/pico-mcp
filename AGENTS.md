# pico-mcp

Expose pico-ioc components as MCP servers: @tool, @resource and @prompt on component methods, served by the official mcp SDK (2.x).

## Commands

```bash
pip install -e ".[dev]"
pytest tests/ -v
pytest --cov=pico_mcp --cov-report=term-missing tests/
mkdocs serve -f mkdocs.yml
```

## Project Structure

```
src/pico_mcp/
  __init__.py       # Public API
  decorators.py     # @tool / @resource / @prompt markers (options passed to the SDK)
  server.py         # McpServerFactory: provides MCPServer, discovery via container.keys()
  config.py         # McpSettings (prefix "mcp")
```

## Key Concepts

- Marker + factory idiom (like pico-celery @task): decorator stores meta, the MCPServer provider scans components.
- Each call resolves the component via container.get(cls) and calls the method on it: scopes and interceptors apply.
- Methods are registered as plain functions with the signature minus self (annotations resolved in the method's module).
- Duplicate tool/prompt names or resource URIs raise at startup (the SDK would only warn).
- Tests use the SDK's in-process `Client(server)`; no transport.

## Boundaries

- The container provides the SDK's `MCPServer` itself; do not wrap it
- mcp pinned `< 3`: a new major is a deliberate migration
- Do not modify `_version.py`
