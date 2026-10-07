from __future__ import annotations

import sys
import types

import pytest
from mcp import Client
from mcp.server.mcpserver import Context, MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pico_ioc import MethodCtx, MethodInterceptor, component, intercepted_by

from pico_mcp import prompt, resource, tool


@component
class Orders:
    def __init__(self):
        self.db = {"1": "book"}

    @tool(description="Look up an order by id")
    def get_order(self, order_id: str) -> str:
        return self.db[order_id]

    @tool()
    async def count_orders(self, ctx: Context) -> int:
        """Count the stored orders."""
        assert ctx.request_id
        return len(self.db)

    @resource("orders://{order_id}")
    def order_resource(self, order_id: str) -> str:
        return f"order {order_id}: {self.db.get(order_id, 'missing')}"

    @prompt()
    def summarize(self, order_id: str) -> str:
        """Ask the model to summarize an order."""
        return f"Summarize order {order_id}"

    @tool()
    def cancel(self, order_id: str) -> str:
        raise ToolError(f"order {order_id} already shipped")

    @tool()
    def ping(self):
        return "pong"

    def not_exposed(self) -> None:
        pass


@component
class Upper(MethodInterceptor):
    def invoke(self, ctx: MethodCtx, call_next):
        return call_next(ctx).upper()


@component(scope="prototype")
class Greeter:
    instances = 0

    def __init__(self):
        Greeter.instances += 1

    @tool()
    @intercepted_by(Upper)
    def greet(self, name: str) -> str:
        return f"hello {name}"


@pytest.fixture
def server(make_container) -> MCPServer:
    return make_container(sys.modules[__name__]).get(MCPServer)


async def test_tools_carry_schema_from_the_signature(server):
    async with Client(server) as client:
        tools = {t.name: t for t in (await client.list_tools()).tools}
    assert set(tools) == {"get_order", "count_orders", "cancel", "ping", "greet"}
    assert tools["get_order"].description == "Look up an order by id"
    assert tools["get_order"].input_schema["required"] == ["order_id"]
    assert tools["count_orders"].description == "Count the stored orders."
    assert "ctx" not in tools["count_orders"].input_schema["properties"]


async def test_sync_and_async_tools_run_on_the_component(server):
    async with Client(server) as client:
        sync = await client.call_tool("get_order", {"order_id": "1"})
        async_ = await client.call_tool("count_orders", {})
        untyped = await client.call_tool("ping", {})
    assert sync.structured_content == {"result": "book"}
    assert async_.structured_content == {"result": 1}
    assert untyped.content[0].text == "pong"


async def test_tool_errors_reach_the_client_as_errors(server):
    async with Client(server) as client:
        result = await client.call_tool("get_order", {"order_id": "missing"})
        custom = await client.call_tool("cancel", {"order_id": "7"})
    assert result.is_error
    assert custom.is_error and "order 7 already shipped" in custom.content[0].text


def test_bare_decorator_fails_at_import():
    with pytest.raises(TypeError):
        tool(lambda self: None)


def test_unresolvable_annotation_fails_at_startup(make_container):
    bad = types.ModuleType("bad_tools")

    @component
    class Bad:
        @tool()
        def lookup(self, key: Missing) -> str:  # noqa: F821
            return key

    bad.Bad = Bad
    with pytest.raises(Exception, match="Missing"):
        make_container(bad).get(MCPServer)


async def test_calls_go_through_the_container_scopes_and_interceptors(server):
    Greeter.instances = 0
    async with Client(server) as client:
        first = await client.call_tool("greet", {"name": "ana"})
        await client.call_tool("greet", {"name": "bob"})
    assert first.structured_content == {"result": "HELLO ANA"}
    assert Greeter.instances == 2


async def test_resources_and_prompts_are_exposed(server):
    async with Client(server) as client:
        templates = (await client.list_resource_templates()).resource_templates
        read = await client.read_resource("orders://1")
        prompt_result = await client.get_prompt("summarize", {"order_id": "7"})
    assert [t.uri_template for t in templates] == ["orders://{order_id}"]
    assert read.contents[0].text == "order 1: book"
    assert prompt_result.messages[0].content.text == "Summarize order 7"


def test_settings_set_the_server_identity(make_container):
    container = make_container(
        sys.modules[__name__], config={"mcp": {"name": "orders", "instructions": "Use get_order first."}}
    )
    server = container.get(MCPServer)
    assert server.name == "orders"
    assert server.instructions == "Use get_order first."


def test_server_is_empty_without_decorated_methods(make_container):
    assert make_container().get(MCPServer).name == "pico-mcp"


def test_duplicate_names_fail_fast(make_container):
    dup = types.ModuleType("dup_tools")

    @component
    class A:
        @tool(name="lookup")
        def a(self) -> str:
            return "a"

    @component
    class B:
        @tool(name="lookup")
        def b(self) -> str:
            return "b"

    dup.A, dup.B = A, B
    with pytest.raises(Exception, match="duplicate MCP tool 'lookup'"):
        make_container(dup).get(MCPServer)


async def test_semantic_flags_become_standard_annotations(make_container):
    @component
    class Ledger:
        @tool(read_only=True)
        def balance(self, account: str) -> int:
            return 0

        @tool(destructive=True, idempotent=False, open_world=True)
        def wire(self, account: str, cents: int) -> str:
            return "sent"

        @tool(destructive=False, idempotent=True)
        def tag(self, account: str, label: str) -> str:
            return label

    ledger = types.ModuleType("ledger_tools")
    ledger.Ledger = Ledger
    server = make_container(ledger).get(MCPServer)
    async with Client(server) as client:
        tools = {t.name: t.annotations for t in (await client.list_tools()).tools}
    assert tools["balance"].read_only_hint is True
    assert tools["balance"].destructive_hint is False
    assert tools["wire"].read_only_hint is None
    assert (tools["wire"].destructive_hint, tools["wire"].idempotent_hint, tools["wire"].open_world_hint) == (
        True,
        False,
        True,
    )
    assert (tools["tag"].destructive_hint, tools["tag"].idempotent_hint) == (False, True)


async def test_tools_without_flags_carry_no_annotations(server):
    async with Client(server) as client:
        tools = {t.name: t for t in (await client.list_tools()).tools}
    assert tools["get_order"].annotations is None


def test_read_only_and_destructive_conflict():
    with pytest.raises(ValueError, match="read-only tool cannot be destructive"):
        tool(read_only=True, destructive=True)


def test_flags_and_raw_annotations_are_exclusive():
    from mcp.types import ToolAnnotations

    with pytest.raises(TypeError, match="not both"):
        tool(read_only=True, annotations=ToolAnnotations())
