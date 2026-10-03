# FAQ

## Does this replace the mcp SDK?

No. The container provides the SDK's own `MCPServer`; this module only turns
component methods into registrations on it. Everything in the SDK
documentation applies to the object you get.

## Why mcp 2.x and not 1.x?

mcp 2 renamed `FastMCP` to `MCPServer` and changed several APIs. Supporting
both lines would double the surface for a module that starts on 2.x; the pin
is `>= 2.0, < 3`.

## Can a tool use other components?

Yes: inject them in the component's constructor, as with any pico component.
The tool's parameters are what the model sends; the constructor's are what the
container provides.

## How do I expose the server over HTTP inside my FastAPI app?

Not yet: run it standalone with `server.run(transport="streamable-http")` or
over stdio. Mounting it inside a pico-fastapi app needs a lifespan seam in
pico-fastapi (see [Architecture](architecture.md)).

## Can I add tools without decorators?

Yes. Get `MCPServer` from the container and call the SDK's `add_tool`,
`resource` or `prompt` on it, before running it.
