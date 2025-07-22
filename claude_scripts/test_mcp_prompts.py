"""Test script for MCP prompts functionality."""

import json

import httpx
import httpx_sse

# Test MCP server with prompts
url = 'http://localhost:8000/mcp/mcp/'

# Send initialize request
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
prompts_request = {'jsonrpc': '2.0', 'method': 'prompts/list', 'id': 2}

# First init, then list prompts
with httpx.Client() as client:
  with httpx_sse.connect_sse(
    client,
    'POST',
    url,
    json=[init_request, prompts_request],
    headers={'Accept': 'text/event-stream'},
  ) as event_source:
    for event in event_source.iter_sse():
      if event.data:
        data = json.loads(event.data)
        print(json.dumps(data, indent=2))

        # If this is the prompts list response, display the prompts
        if data.get('id') == 2 and 'result' in data:
          prompts = data['result'].get('prompts', [])
          print(f'\n🎯 Found {len(prompts)} prompts:')
          for prompt in prompts:
            print(f'  - {prompt["name"]}: {prompt.get("description", "No description")}')
