"""Builds the ``MCPServer`` from the ``@tool``/``@resource``/``@prompt`` methods
of every registered component.

Each call resolves the component through the container, so scopes and
interceptors apply exactly as for any other caller.
"""

import functools
import inspect
from collections.abc import Callable
from typing import Any

from mcp.server.mcpserver import MCPServer
from pico_ioc import PicoContainer, factory, provides

from .config import McpSettings
from .decorators import MCP_META


@factory
class McpServerFactory:
    """Provides the SDK's ``MCPServer`` with every marked component method registered."""

    @provides(MCPServer, scope="singleton")
    def create_mcp_server(self, container: PicoContainer, settings: McpSettings) -> MCPServer:
        server = MCPServer(settings.name, instructions=settings.instructions)
        seen: dict[tuple[str, str], str] = {}
        for cls, fn, (kind, options) in _discover(container):
            handler = _bind(container, cls, fn)
            key = (kind, options.get("uri") or options.get("name") or fn.__name__)
            origin = f"{cls.__qualname__}.{fn.__name__}"
            if key in seen:
                # The SDK only warns and keeps the first one: a silently shadowed tool is a bug.
                raise ValueError(f"duplicate MCP {kind} {key[1]!r}: {seen[key]} and {origin}")
            seen[key] = origin
            getattr(server, kind)(**options)(handler)
        return server


def _discover(container: PicoContainer):
    for key in container.keys():
        for _, fn in inspect.getmembers(key, inspect.isfunction):
            meta = getattr(fn, MCP_META, None)
            if meta is not None:
                yield key, fn, meta


def _bind(container: PicoContainer, cls: type, fn: Callable[..., Any]) -> Callable[..., Any]:
    """A plain function with ``fn``'s signature minus ``self``, as the SDK expects."""
    # eval_str resolves string annotations against fn's module, not this one.
    sig = inspect.signature(fn, eval_str=True)
    sig = sig.replace(parameters=list(sig.parameters.values())[1:])
    name = fn.__name__

    if inspect.iscoroutinefunction(fn):

        async def handler(*args, **kwargs):
            return await getattr(container.get(cls), name)(*args, **kwargs)
    else:

        def handler(*args, **kwargs):
            return getattr(container.get(cls), name)(*args, **kwargs)

    functools.update_wrapper(handler, fn)
    del handler.__wrapped__
    handler.__signature__ = sig
    handler.__annotations__ = {p.name: p.annotation for p in sig.parameters.values() if p.annotation is not p.empty}
    if sig.return_annotation is not sig.empty:
        handler.__annotations__["return"] = sig.return_annotation
    return handler
