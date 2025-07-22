#!/usr/bin/env python3
"""Test deployed MCP server directly."""

import json
import os
import subprocess

import requests


# Get app URL
def get_databricks_app_url():
  """Get Databricks App URL from apps list."""
  try:
    cmd = ['databricks', 'apps', 'list', '--output', 'json']
    result = subprocess.run(cmd, capture_output=True, text=True, check=True, env={**os.environ})
    apps = json.loads(result.stdout)

    for app in apps:
      if app.get('name') == 'mcp-commands':
        return app.get('url') + '/mcp/'

    raise Exception("App 'mcp-commands' not found")
  except Exception as e:
    raise Exception(f'Failed to get app URL: {e}')


# Get OAuth token
def get_oauth_token():
  """Get OAuth token from Databricks CLI."""
  try:
    host = os.environ.get('DATABRICKS_HOST')
    cmd = ['databricks', 'auth', 'token', '--host', host]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(result.stdout).get('access_token')
  except Exception as e:
    raise Exception(f'Failed to get OAuth token: {e}')


try:
  app_url = get_databricks_app_url()
  print(f'App URL: {app_url}')

  oauth_token = get_oauth_token()
  print(f'Got OAuth token: {oauth_token[:10]}...')

  # Test direct HTTP request
  headers = {
    'Authorization': f'Bearer {oauth_token}',
    'Content-Type': 'application/json',
  }

  # Test health endpoint
  print('\nTesting health endpoint...')
  response = requests.get(app_url.replace('/mcp/', '/health'), headers=headers)
  print(f'Health response: {response.status_code}')
  if response.status_code == 200:
    print(f'Response: {response.text}')
  else:
    print(f'Error: {response.text[:200]}')

except Exception as e:
  print(f'Error: {e}')
