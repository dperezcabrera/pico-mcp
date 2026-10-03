"""Marker decorators: store the MCP registration on the method; the server
factory picks them up when the container builds ``MCPServer``."""

MCP_META = "_pico_mcp_meta"


def _marker(kind: str, **options):
    def dec(fn):
        setattr(fn, MCP_META, (kind, options))
        return fn

    return dec


def tool(**options):
    """Expose a component method as an MCP tool.

    ``options`` go to ``MCPServer.add_tool`` (``name``, ``description``, ``annotations``...).
    """
    return _marker("tool", **options)


def resource(uri: str, **options):
    """Expose a component method as an MCP resource; ``{param}`` in ``uri`` makes a template."""
    return _marker("resource", uri=uri, **options)


def prompt(**options):
    """Expose a component method as an MCP prompt."""
    return _marker("prompt", **options)
