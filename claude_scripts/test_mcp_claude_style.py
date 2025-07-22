#!/usr/bin/env python3
"""Test MCP server prompts to see exactly what Claude receives."""

import json

import httpx

# Test MCP server directly
base_url = 'http://localhost:8000/mcp/mcp/'

# First, initialize the MCP session
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

# Make requests with proper headers
headers = {'Accept': 'application/json, text/event-stream'}

with httpx.Client() as client:
  # Initialize
  print('1. Initializing MCP session...')
  response = client.post(base_url, json=init_request, headers=headers)
  print(f'Status: {response.status_code}')
  print(f'Response: {json.dumps(response.json(), indent=2)}\n')

  # List prompts
  print('2. Listing prompts...')
  list_request = {'jsonrpc': '2.0', 'method': 'prompts/list', 'id': 2}
  response = client.post(base_url, json=list_request, headers=headers)
  print(f'Status: {response.status_code}')
  result = response.json()
  print(f'Response: {json.dumps(result, indent=2)}\n')

  # Get the check_system prompt
  print('3. Getting check_system prompt...')
  get_prompt_request = {
    'jsonrpc': '2.0',
    'method': 'prompts/get',
    'params': {'name': 'check_system'},
    'id': 3,
  }
  response = client.post(base_url, json=get_prompt_request, headers=headers)
  print(f'Status: {response.status_code}')
  result = response.json()
  print(f'Response: {json.dumps(result, indent=2)}\n')

  # Extract and display the actual prompt content
  if 'result' in result and 'messages' in result['result']:
    messages = result['result']['messages']
    print('4. Actual prompt content Claude receives:')
    print('=' * 60)
    for msg in messages:
      print(f'Role: {msg["role"]}')
      print(f'Content: {msg["content"]["text"]}')
      print('-' * 60)
