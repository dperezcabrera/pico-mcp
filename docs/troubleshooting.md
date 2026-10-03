# Troubleshooting

## My tool does not show up in `tools/list`

- Is the component's module listed in `init(modules=[...])` (or discoverable
  by pico-boot)? Only registered components are scanned.
- The decorator must be on a method of a `@component` class; plain functions
  are not discovered.
- Decorators need parentheses: `@tool()`. A bare `@tool` raises
  `TypeError: tool() takes 0 positional arguments` at import time.

## `duplicate MCP tool 'x': A.a and B.b`

Two components declare the same name. Rename one with `@tool(name="...")`.
Resources clash on the URI, prompts on the name.

## `NameError: name 'X' is not defined` at startup

An annotation in a marked method names a type that the method's module does
not import (common with `from __future__ import annotations`, where nothing
fails until the signature is read). Import it there.

## The client says `Error executing tool x`

The method raised. The SDK reports any exception as an error result and logs
the traceback on the server side. Raise `mcp.server.mcpserver.exceptions.ToolError`
to put a message of your own in the result (after the SDK's `Error executing
tool x:` prefix) so the model can act on it.

## Nothing prints when I run the server

With the stdio transport the server talks through stdin/stdout and waits for a
client. Launch it from an MCP client, or use the streamable HTTP transport to
test it by hand.
