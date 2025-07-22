#!/usr/bin/env -S uv run python
"""Test direct local MCP access."""

import asyncio

from server.app import execute_dbsql, health, mcp_server


async def test_mcp_tools():
  """Test MCP tools directly."""
  print('Testing local MCP server tools...')

  # List available tools
  tools = await mcp_server._tool_manager.list_tools()
  print(f'\nAvailable MCP tools ({len(tools)}):')
  for tool in tools:
    print(f'  - {tool.name}: {tool.description}')

  # Test the health tool directly
  print('\nTesting health tool directly:')
  health_result = health()
  print(f'  Result: {health_result}')

  # Test execute_dbsql with a simple query
  print('\nTesting execute_dbsql tool (will fail without warehouse):')
  sql_result = execute_dbsql(query='SELECT 1 as test', limit=1)
  print(f'  Result: {sql_result}')


if __name__ == '__main__':
  asyncio.run(test_mcp_tools())
