#!/usr/bin/env python
"""Simple test to get check_system prompt from MCP server."""

import json
import subprocess
import time


def test_mcp_prompt():
  """Test getting the check_system prompt."""
  # Start MCP client
  process = subprocess.Popen(
    ['uv', 'run', 'python', 'mcp_databricks_client.py', 'http://localhost:8000'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
  )

  # Wait for connection
  time.sleep(1)

  # Send all requests at once (batch mode)
  requests = [
    {
      'jsonrpc': '2.0',
      'method': 'initialize',
      'params': {
        'protocolVersion': '2024-11-05',
        'capabilities': {'prompts': {}, 'tools': {}},
        'clientInfo': {'name': 'test-client', 'version': '1.0.0'},
      },
      'id': 1,
    },
    {'jsonrpc': '2.0', 'method': 'prompts/list', 'params': {}, 'id': 2},
    {'jsonrpc': '2.0', 'method': 'prompts/get', 'params': {'name': 'check_system'}, 'id': 3},
  ]

  # Send all requests
  for req in requests:
    process.stdin.write(json.dumps(req) + '\n')
  process.stdin.flush()

  # Read all responses
  responses = []
  for _ in range(3):
    line = process.stdout.readline()
    if line:
      try:
        responses.append(json.loads(line.strip()))
      except json.JSONDecodeError:
        pass

  # Process responses
  for resp in responses:
    if resp.get('id') == 3 and 'result' in resp:
      # This is the check_system prompt response
      result = resp['result']
      print('📝 CHECK_SYSTEM PROMPT RESPONSE:')
      print('=' * 60)
      print(json.dumps(result, indent=2))

      if 'messages' in result:
        print('\n🎯 MESSAGES CLAUDE RECEIVES:')
        print('=' * 60)
        for msg in result['messages']:
          content = msg.get('content', {})
          if isinstance(content, dict):
            text = content.get('text', '')
            print(f'\nRole: {msg.get("role", "unknown")}')
            print(f'Text:\n{text}')
            print('-' * 60)

  process.terminate()


if __name__ == '__main__':
  test_mcp_prompt()
