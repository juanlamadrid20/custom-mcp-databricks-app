#!/usr/bin/env -S uv run python
"""Test the MCP proxy prompts with remote Databricks app."""

import json
import subprocess
import sys


def test_prompts(url):
  """Test the MCP proxy with prompts/list command."""
  # Run the proxy with a test command
  cmd = [
    sys.executable,
    '/Users/nikhil.thorat/emu/mcp-commands-databricks-app/mcp_databricks_client.py',
    url,
  ]

  # Send a prompts/list request
  request = {'jsonrpc': '2.0', 'id': 1, 'method': 'prompts/list', 'params': {}}

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
      if 'result' in response and 'prompts' in response['result']:
        print(f'\nFound {len(response["result"]["prompts"])} prompts!')
        for prompt in response['result']['prompts']:
          print(f'  - {prompt["name"]}: {prompt["description"]}')
      else:
        print(f'\nResponse: {json.dumps(response, indent=2)}')
    except json.JSONDecodeError as e:
      print(f'\nFailed to parse response: {e}')


if __name__ == '__main__':
  remote_url = 'https://mcp-commands-5722066275360235.aws.databricksapps.com'
  print(f'Testing MCP proxy prompts with remote URL: {remote_url}')
  test_prompts(remote_url)
