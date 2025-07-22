#!/usr/bin/env python3
"""Test script to explore FastMCP's dynamic discovery capabilities."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from server.mcp_server import mcp


async def test_fastmcp_discovery():
  """Test if we can dynamically discover prompts and tools from FastMCP."""
  print('Testing FastMCP Discovery...\n')

  # Check if FastMCP instance has the managers
  print(f'FastMCP instance type: {type(mcp)}')
  print(f'Has _prompt_manager: {hasattr(mcp, "_prompt_manager")}')
  print(f'Has _tool_manager: {hasattr(mcp, "_tool_manager")}')

  if hasattr(mcp, '_prompt_manager'):
    print('\n--- Prompts ---')
    # Get list of prompts
    prompts = await mcp._prompt_manager.list_prompts()
    print(f'Number of prompts: {len(prompts)}')
    for prompt in prompts:
      print(f'  - {prompt.key}: {prompt.description or "No description"}')

  if hasattr(mcp, '_tool_manager'):
    print('\n--- Tools ---')
    # Get list of tools
    tools = await mcp._tool_manager.list_tools()
    print(f'Number of tools: {len(tools)}')
    for tool in tools:
      print(f'  - {tool.key}: {tool.description or "No description"}')
      # Show tool parameters
      if hasattr(tool, 'parameters') and tool.parameters:
        print(f'    Parameters: {tool.parameters}')

  # Also check what other attributes are available
  print('\n--- FastMCP Attributes ---')
  public_attrs = [attr for attr in dir(mcp) if not attr.startswith('_')]
  print(f'Public attributes: {public_attrs[:10]}...')  # Show first 10


if __name__ == '__main__':
  asyncio.run(test_fastmcp_discovery())
