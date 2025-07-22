#!/usr/bin/env python3
"""Test the MCP endpoint locally."""

import json

import requests

# Test local endpoint
url = 'http://localhost:8000/mcp'

# Test initialize request
init_request = {
  'jsonrpc': '2.0',
  'method': 'initialize',
  'params': {'protocolVersion': '0.1.0', 'capabilities': {'tools': {}}},
  'id': 1,
}

print(f'Testing MCP endpoint at {url}')
print(f'Request: {json.dumps(init_request, indent=2)}')

try:
  response = requests.post(url, json=init_request)
  print(f'Status: {response.status_code}')
  print(f'Headers: {dict(response.headers)}')
  print(f'Response: {response.text}')
except Exception as e:
  print(f'Error: {e}')
