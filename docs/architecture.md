# Architecture

```
@tool / @resource / @prompt          McpServerFactory (@factory)
        |                                    |
   marks method meta        @provides(MCPServer): container.keys() -> marked methods
        |                                    |
   component class  <---- container.get(cls) on every call ----+
                                             |
                                  MCPServer (official mcp SDK)
                                  stdio / streamable HTTP
```

## Design decisions

- **Marker decorator + factory** (same idiom as pico-celery's `@task` and
  pico-scheduling's `@scheduled`): the decorator only stores metadata on the
  function; discovery happens once, when the container builds `MCPServer`.
- **Public discovery seam**: components are enumerated with
  `container.keys()`, never by reading pico-ioc internals.
- **The SDK object is the product**: the container provides the SDK's own
  `MCPServer`, not a wrapper. Transports, protocol versions and auth stay the
  SDK's job; this module only translates components into registrations.
- **Container resolution per call**: each call does `container.get(cls)` and
  calls the method on what comes back, so scopes and interceptors are the
  container's, not the protocol's.
- **Signature without `self`**: each method is registered as a plain function
  carrying the method's signature minus `self`, with string annotations
  resolved against the method's own module, so the SDK builds the schema as it
  would for a module-level function.
- **Duplicates fail fast**: the SDK only warns on a duplicate name and keeps
  the first registration; here two components claiming the same name stop the
  container from starting.
- **HTTP inside a pico-fastapi app is not wired yet**: the SDK's streamable
  HTTP app needs its session manager running in the host's lifespan, and
  pico-fastapi owns that lifespan. It will land together with a lifespan seam
  in pico-fastapi.

## Stability and versioning

This module follows the ecosystem policy in [ADR-014: API Stability and Deprecation](https://github.com/dperezcabrera/pico-ioc/blob/main/docs/adr/adr-0014-api-stability-and-deprecation.md). The public API is exactly what `__all__` exports plus the `mcp.*` settings keys and their defaults, pinned by `tests/test_exports.py`. Before 1.0 a breaking change ships as a minor release; a deprecated name keeps working, with a `DeprecationWarning` naming its replacement, for at least one minor release and 90 days before removal.
