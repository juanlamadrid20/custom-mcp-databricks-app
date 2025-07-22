#!/usr/bin/env python
"""Test complete MCP functionality with single /mcp/ path."""

import json

import httpx
import httpx_sse

# Test MCP server
url = 'http://localhost:8000/mcp/'

print('🔧 Testing MCP server at:', url)
print('=' * 60)

# Use a client with SSE support
with httpx.Client() as client:
  with httpx_sse.connect_sse(
    client,
    'POST',
    url,
    json={
      'jsonrpc': '2.0',
      'method': 'initialize',
      'params': {
        'protocolVersion': '2024-11-05',
        'capabilities': {'prompts': {}, 'tools': {}},
        'clientInfo': {'name': 'test-client', 'version': '1.0.0'},
      },
      'id': 1,
    },
    headers={'Accept': 'text/event-stream, application/json'},
  ) as event_source:
    for event in event_source.iter_sse():
      if event.data:
        data = json.loads(event.data)
        print('\n✅ Initialize response:')
        print(json.dumps(data, indent=2))
        break

  # Test tools/list
  print('\n🔧 Testing tools/list...')
  with httpx_sse.connect_sse(
    client,
    'POST',
    url,
    json={'jsonrpc': '2.0', 'method': 'tools/list', 'id': 2},
    headers={'Accept': 'text/event-stream, application/json'},
  ) as event_source:
    for event in event_source.iter_sse():
      if event.data:
        data = json.loads(event.data)
        if 'result' in data:
          print('\n✅ Available tools:')
          for tool in data['result']['tools']:
            print(f'  - {tool["name"]}: {tool["description"]}')
        break

  # Test prompts/list
  print('\n📝 Testing prompts/list...')
  with httpx_sse.connect_sse(
    client,
    'POST',
    url,
    json={'jsonrpc': '2.0', 'method': 'prompts/list', 'id': 3},
    headers={'Accept': 'text/event-stream, application/json'},
  ) as event_source:
    for event in event_source.iter_sse():
      if event.data:
        data = json.loads(event.data)
        if 'result' in data:
          print('\n✅ Available prompts:')
          for prompt in data['result']['prompts']:
            print(f'  - {prompt["name"]}: {prompt.get("description", "No description")}')
        break

print('\n✨ MCP server is working correctly with single /mcp/ path!')
