"""Marker decorators: store the MCP registration on the method; the server
factory picks them up when the container builds ``MCPServer``."""

from mcp.types import ToolAnnotations

MCP_META = "_pico_mcp_meta"


def _marker(kind: str, **options):
    def dec(fn):
        setattr(fn, MCP_META, (kind, options))
        return fn

    return dec


def tool(
    *,
    read_only: bool | None = None,
    destructive: bool | None = None,
    idempotent: bool | None = None,
    open_world: bool | None = None,
    **options,
):
    """Expose a component method as an MCP tool.

    The flags become the standard MCP tool annotations (``readOnlyHint``...),
    which clients and approval gateways read to decide how much to trust a call.
    ``options`` go to ``MCPServer.add_tool`` (``name``, ``description``, ``title``...).
    """
    hints = {
        "read_only_hint": read_only,
        "destructive_hint": destructive,
        "idempotent_hint": idempotent,
        "open_world_hint": open_world,
    }
    hints = {k: v for k, v in hints.items() if v is not None}
    if hints:
        if "annotations" in options:
            raise TypeError("@tool: pass the semantic flags or annotations=, not both")
        if read_only and destructive:
            raise ValueError("@tool: a read-only tool cannot be destructive")
        if read_only:
            # destructiveHint defaults to true; say it explicitly for consumers that skip readOnlyHint.
            hints.setdefault("destructive_hint", False)
        options["annotations"] = ToolAnnotations(**hints)
    return _marker("tool", **options)


def resource(uri: str, **options):
    """Expose a component method as an MCP resource; ``{param}`` in ``uri`` makes a template."""
    return _marker("resource", uri=uri, **options)


def prompt(**options):
    """Expose a component method as an MCP prompt."""
    return _marker("prompt", **options)
