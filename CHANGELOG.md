# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `@tool`, `@resource` and `@prompt` marker decorators for component methods (sync and async).
- `McpServerFactory`: provides the mcp SDK's `MCPServer` as a singleton with every marked method registered; each call resolves the component through the container.
- Duplicate tool or prompt names and resource URIs fail at startup.
- `mcp.name` and `mcp.instructions` settings (zero-config).
- Auto-discovery via the `pico_boot.modules` entry point.
