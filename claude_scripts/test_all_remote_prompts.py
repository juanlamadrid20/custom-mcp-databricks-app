#!/usr/bin/env -S uv run python
"""Test getting all prompts from the remote Databricks app."""

import json
import subprocess
import sys
import time


def get_prompt(url, prompt_name):
  """Get a specific prompt from the MCP server."""
  cmd = [
    sys.executable,
    '/Users/nikhil.thorat/emu/mcp-commands-databricks-app/mcp_databricks_client.py',
    url,
  ]

  request = {'jsonrpc': '2.0', 'id': 1, 'method': 'prompts/get', 'params': {'name': prompt_name}}

  proc = subprocess.Popen(
    cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
  )

  stdout, stderr = proc.communicate(input=json.dumps(request) + '\n', timeout=10)

  if stdout:
    try:
      response = json.loads(stdout.strip())
      return response.get('result', {})
    except json.JSONDecodeError:
      return None
  return None


def list_prompts(url):
  """List all prompts from the MCP server."""
  cmd = [
    sys.executable,
    '/Users/nikhil.thorat/emu/mcp-commands-databricks-app/mcp_databricks_client.py',
    url,
  ]

  request = {'jsonrpc': '2.0', 'id': 1, 'method': 'prompts/list', 'params': {}}

  proc = subprocess.Popen(
    cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
  )

  stdout, stderr = proc.communicate(input=json.dumps(request) + '\n', timeout=10)

  if stdout:
    try:
      response = json.loads(stdout.strip())
      return response.get('result', {}).get('prompts', [])
    except json.JSONDecodeError:
      return []
  return []


if __name__ == '__main__':
  remote_url = 'https://mcp-commands-5722066275360235.aws.databricksapps.com'
  print(f'Testing all prompts from: {remote_url}\n')

  # First list all prompts
  prompts = list_prompts(remote_url)
  print(f'Found {len(prompts)} prompts:\n')

  # Then get each prompt
  for prompt in prompts:
    print(f'{"=" * 60}')
    print(f'Prompt: {prompt["name"]}')
    print(f'Description: {prompt["description"]}')

    # Get the full prompt content
    full_prompt = get_prompt(remote_url, prompt['name'])
    if full_prompt and 'messages' in full_prompt:
      for msg in full_prompt['messages']:
        content = msg.get('content', {})
        if isinstance(content, dict) and content.get('type') == 'text':
          text = content.get('text', '')
          # Show first 200 characters
          preview = text[:200] + '...' if len(text) > 200 else text
          print(f'Content preview: {preview}')
    print('')
    time.sleep(0.5)  # Small delay between requests
