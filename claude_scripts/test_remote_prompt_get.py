#!/usr/bin/env -S uv run python
"""Test getting a specific prompt from the remote Databricks app."""

import json
import subprocess
import sys


def test_get_prompt(url, prompt_name):
  """Test the MCP proxy with prompts/get command."""
  # Run the proxy with a test command
  cmd = [
    sys.executable,
    '/Users/nikhil.thorat/emu/mcp-commands-databricks-app/mcp_databricks_client.py',
    url,
  ]

  # Send a prompts/get request
  request = {'jsonrpc': '2.0', 'id': 1, 'method': 'prompts/get', 'params': {'name': prompt_name}}

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
      if 'result' in response:
        print(f"\nPrompt '{prompt_name}' response:")
        print(json.dumps(response['result'], indent=2))
      else:
        print(f'\nFull response: {json.dumps(response, indent=2)}')
    except json.JSONDecodeError as e:
      print(f'\nFailed to parse response: {e}')


if __name__ == '__main__':
  remote_url = 'https://mcp-commands-5722066275360235.aws.databricksapps.com'
  prompt_name = 'check_system'
  print(f"Testing MCP proxy to get prompt '{prompt_name}' from: {remote_url}\n")
  test_get_prompt(remote_url, prompt_name)
