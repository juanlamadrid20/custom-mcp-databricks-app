#!/usr/bin/env -S uv run python
"""Test the MCP proxy with remote Databricks app."""

import json
import subprocess
import sys


def test_proxy(url):
  """Test the MCP proxy with list_tools command."""
  # Run the proxy with a test command
  cmd = [
    sys.executable,
    '/Users/nikhil.thorat/emu/mcp-commands-databricks-app/mcp_databricks_client.py',
    url,
  ]

  # Send a tools/list request
  request = {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list', 'params': {}}

  proc = subprocess.Popen(
    cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
  )

  # Send request and get response
  stdout, stderr = proc.communicate(input=json.dumps(request) + '\n', timeout=10)

  print(f'STDERR:\n{stderr}')
  print(f'\nSTDOUT:\n{stdout}')

  if stdout:
    try:
      response = json.loads(stdout.strip())
      if 'result' in response and 'tools' in response['result']:
        print(f'\nFound {len(response["result"]["tools"])} tools!')
        for tool in response['result']['tools'][:3]:  # Show first 3
          print(f'  - {tool["name"]}: {tool["description"][:60]}...')
      else:
        print(f'\nResponse: {json.dumps(response, indent=2)}')
    except json.JSONDecodeError as e:
      print(f'\nFailed to parse response: {e}')


if __name__ == '__main__':
  remote_url = 'https://mcp-commands-5722066275360235.aws.databricksapps.com'
  print(f'Testing MCP proxy with remote URL: {remote_url}')
  test_proxy(remote_url)
