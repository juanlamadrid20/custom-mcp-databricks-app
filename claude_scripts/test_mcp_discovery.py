#!/usr/bin/env python3
"""Test MCP discovery against localhost."""

import json
import subprocess
import sys


def test_mcp_discovery():
  """Test MCP discovery by sending requests to the client."""
  # Start the MCP client process
  proc = subprocess.Popen(
    [sys.executable, 'mcp_databricks_client.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    env={**subprocess.os.environ},
  )

  # Test prompts/list
  prompts_request = {'jsonrpc': '2.0', 'id': 'test-prompts', 'method': 'prompts/list'}

  proc.stdin.write(json.dumps(prompts_request) + '\n')
  proc.stdin.flush()

  # Read response
  response = proc.stdout.readline()
  if response:
    print('Prompts discovered:')
    result = json.loads(response)
    if 'result' in result and 'prompts' in result['result']:
      for prompt in result['result']['prompts']:
        print(f'  - {prompt["name"]}: {prompt.get("description", "No description")}')
    else:
      print(f'  Response: {result}')

  # Test tools/list
  tools_request = {'jsonrpc': '2.0', 'id': 'test-tools', 'method': 'tools/list'}

  proc.stdin.write(json.dumps(tools_request) + '\n')
  proc.stdin.flush()

  # Read response
  response = proc.stdout.readline()
  if response:
    print('\nTools discovered:')
    result = json.loads(response)
    if 'result' in result and 'tools' in result['result']:
      for tool in result['result']['tools']:
        print(f'  - {tool["name"]}: {tool.get("description", "No description")}')
    else:
      print(f'  Response: {result}')

  # Clean up
  proc.terminate()


if __name__ == '__main__':
  test_mcp_discovery()
