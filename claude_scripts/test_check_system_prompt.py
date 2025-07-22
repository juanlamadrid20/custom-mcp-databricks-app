#!/usr/bin/env python
"""Test the check_system prompt to see exactly what Claude receives."""

import json

import httpx
import httpx_sse

# Test MCP server
url = 'http://localhost:8000/mcp/'

print('🔧 Testing MCP server check_system prompt')
print('=' * 60)

# Use a client with SSE support
with httpx.Client() as client:
  # Initialize first
  print('\n1️⃣ Initializing MCP session...')
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
        print('✅ Initialized successfully')
        break

  # List prompts to confirm check_system exists
  print('\n2️⃣ Listing available prompts...')
  with httpx_sse.connect_sse(
    client,
    'POST',
    url,
    json={'jsonrpc': '2.0', 'method': 'prompts/list', 'id': 2},
    headers={'Accept': 'text/event-stream, application/json'},
  ) as event_source:
    for event in event_source.iter_sse():
      if event.data:
        data = json.loads(event.data)
        if 'result' in data:
          print('✅ Available prompts:')
          for prompt in data['result']['prompts']:
            print(f'  - {prompt["name"]}: {prompt.get("description", "No description")}')
        break

  # Get the check_system prompt
  print('\n3️⃣ Getting check_system prompt...')
  with httpx_sse.connect_sse(
    client,
    'POST',
    url,
    json={'jsonrpc': '2.0', 'method': 'prompts/get', 'params': {'name': 'check_system'}, 'id': 3},
    headers={'Accept': 'text/event-stream, application/json'},
  ) as event_source:
    for event in event_source.iter_sse():
      if event.data:
        data = json.loads(event.data)
        print('\n✅ Raw response:')
        print(json.dumps(data, indent=2))

        # Extract and display the actual content
        if 'result' in data and 'messages' in data['result']:
          messages = data['result']['messages']
          print('\n📝 ACTUAL PROMPT CONTENT CLAUDE RECEIVES:')
          print('=' * 60)
          for i, msg in enumerate(messages):
            print(f'\nMessage {i + 1}:')
            print(f'  Role: {msg["role"]}')
            print(f'  Content Type: {msg["content"].get("type", "unknown")}')
            print(f'  Text Content:\n{msg["content"]["text"]}')
            print('-' * 60)
        break

print('\n✨ Test complete!')
