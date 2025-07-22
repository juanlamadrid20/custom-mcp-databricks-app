#!/usr/bin/env python3
"""Test MCP server prompts with SSE to see exactly what Claude receives."""

import json

import httpx
import httpx_sse

# Test MCP server directly
base_url = 'http://localhost:8000/mcp/mcp/'

# Initialize request
init_request = {
  'jsonrpc': '2.0',
  'method': 'initialize',
  'params': {
    'protocolVersion': '2024-11-05',
    'capabilities': {'prompts': {}, 'tools': {}},
    'clientInfo': {'name': 'test-client', 'version': '1.0.0'},
  },
  'id': 1,
}

# List prompts request
list_request = {'jsonrpc': '2.0', 'method': 'prompts/list', 'id': 2}

# Get check_system prompt request
get_prompt_request = {
  'jsonrpc': '2.0',
  'method': 'prompts/get',
  'params': {'name': 'check_system'},
  'id': 3,
}


def process_sse_responses(requests):
  """Send requests and process SSE responses."""
  responses = {}

  with httpx.Client() as client:
    with httpx_sse.connect_sse(
      client, 'POST', base_url, json=requests, headers={'Accept': 'text/event-stream'}
    ) as event_source:
      for event in event_source.iter_sse():
        if event.data:
          data = json.loads(event.data)
          request_id = data.get('id')
          if request_id:
            responses[request_id] = data

  return responses


# Test sequence
print('Testing MCP server prompts...')
print('=' * 60)

# Send all requests in one batch
responses = process_sse_responses([init_request, list_request, get_prompt_request])

# Process responses
print('\n1. Initialize response:')
if 1 in responses:
  print(json.dumps(responses[1], indent=2))

print('\n2. List prompts response:')
if 2 in responses:
  print(json.dumps(responses[2], indent=2))
  if 'result' in responses[2]:
    prompts = responses[2]['result'].get('prompts', [])
    print(f'\nFound {len(prompts)} prompts:')
    for prompt in prompts:
      print(f'  - {prompt["name"]}: {prompt.get("description", "No description")}')

print('\n3. Get check_system prompt response:')
if 3 in responses:
  print(json.dumps(responses[3], indent=2))

  # Extract the actual prompt content
  if 'result' in responses[3] and 'messages' in responses[3]['result']:
    messages = responses[3]['result']['messages']
    print('\n4. Actual prompt content Claude receives:')
    print('=' * 60)
    for i, msg in enumerate(messages):
      print(f'Message {i + 1}:')
      print(f'  Role: {msg["role"]}')
      print(f'  Content: {msg["content"]["text"]}')
      print('-' * 60)
