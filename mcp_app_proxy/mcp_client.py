#!/usr/bin/env -S uv run python
"""Pure MCP Protocol Proxy for Databricks App.

This implements the MCP protocol directly to create a true transparent proxy
that forwards all requests to the remote Databricks App MCP server.

Usage:
    mcp_databricks_client.py <URL>

    URL must be provided:
    - Full URL like http://localhost:8000/mcp/sse/
    - Or base URL like https://app.databricksapps.com (will append /mcp/sse/)
"""

import json
import os
import subprocess
import sys

import requests
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv('.env.local')

# Databricks configuration
DATABRICKS_HOST = os.environ.get(
  'DATABRICKS_HOST', 'https://eng-ml-inference-team-us-west-2.cloud.databricks.com'
)


def get_workspace_client():
  """Get Databricks WorkspaceClient using environment variables."""
  return WorkspaceClient()


def get_databricks_app_url():
  """Get the Databricks App URL from environment or SDK."""
  try:
    # First check environment variable
    app_url = os.environ.get('DATABRICKS_APP_URL')
    if app_url:
      return app_url

    # Otherwise get from SDK
    w = get_workspace_client()
    apps = list(w.apps.list())

    for app in apps:
      if app.name == 'mcp-commands':
        return app.url + '/mcp/sse/'  # Add MCP SSE endpoint path

    raise Exception("App 'mcp-commands' not found in apps list")
  except Exception as e:
    raise Exception(f'Failed to get Databricks App URL: {e}')


def get_oauth_token():
  """Get OAuth token from Databricks CLI."""
  try:
    # Use SDK to get current user's token
    get_workspace_client()
    # The SDK handles authentication internally
    # For OAuth, we need to get the token from the underlying client
    result = subprocess.run(
      ['databricks', 'auth', 'token', '--host', DATABRICKS_HOST],
      capture_output=True,
      text=True,
      check=True,
    )
    return json.loads(result.stdout).get('access_token')
  except Exception as e:
    raise Exception(f'Failed to get OAuth token: {e}')


class MCPProxy:
  """Pure MCP Protocol Proxy."""

  def __init__(self, url):
    if not url:
      raise ValueError('URL argument is required')

    # Ensure URL ends with /mcp/ for the MCP endpoint
    if not url.endswith('/mcp/'):
      if url.endswith('/'):
        url = url + 'mcp/'
      else:
        url = url + '/mcp/'
    self.app_url = url

    self.session_id = None
    self.initialized = False
    self.session = requests.Session()
    self.is_local = self.app_url.startswith('http://localhost')

  def _initialize_session(self):
    """Initialize MCP session with proper handshake."""
    if self.initialized:
      return

    # Get appropriate token based on environment
    if self.is_local:
      oauth_token = 'local-test-token'
    else:
      oauth_token = get_oauth_token()

    headers = {
      'Authorization': f'Bearer {oauth_token}',
      'Content-Type': 'application/json',
      'Accept': 'application/json, text/event-stream',
    }

    # Get session ID
    response = self.session.get(self.app_url, headers=headers)
    self.session_id = response.headers.get('mcp-session-id')

    if self.session_id:
      headers['mcp-session-id'] = self.session_id

    # Initialize MCP session
    init_request = {
      'jsonrpc': '2.0',
      'id': 'initialize',
      'method': 'initialize',
      'params': {
        'protocolVersion': '2024-11-05',
        'capabilities': {'roots': {'listChanged': True}, 'sampling': {}},
        'clientInfo': {'name': 'databricks-mcp-proxy', 'version': '1.0.0'},
      },
    }

    self.session.post(self.app_url, headers=headers, json=init_request)

    # Send initialized notification
    initialized_request = {'jsonrpc': '2.0', 'method': 'notifications/initialized'}

    self.session.post(self.app_url, headers=headers, json=initialized_request)
    self.initialized = True

  def proxy_request(self, request_data):
    """Proxy an MCP request to the remote server."""
    try:
      # Initialize session if needed
      self._initialize_session()

      # Get appropriate token based on environment
      if self.is_local:
        oauth_token = 'local-test-token'
      else:
        oauth_token = get_oauth_token()

      headers = {
        'Authorization': f'Bearer {oauth_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
      }

      if self.session_id:
        headers['mcp-session-id'] = self.session_id

      response = self.session.post(self.app_url, headers=headers, json=request_data)

      if response.status_code == 200:
        # Handle SSE response
        if 'event: message' in response.text:
          for line in response.text.split('\n'):
            if line.startswith('data: '):
              try:
                return json.loads(line[6:])
              except json.JSONDecodeError:
                continue
        else:
          return response.json()

      return {
        'jsonrpc': '2.0',
        'id': request_data.get('id'),
        'error': {
          'code': response.status_code,
          'message': f'HTTP {response.status_code}: {response.text[:100]}',
        },
      }

    except Exception as e:
      return {
        'jsonrpc': '2.0',
        'id': request_data.get('id'),
        'error': {'code': -32000, 'message': str(e)},
      }

  def run(self):
    """Run the MCP proxy server using stdio transport."""
    # Main loop - read from stdin, proxy to remote, write to stdout
    try:
      for line in sys.stdin:
        line = line.strip()
        if not line:
          continue

        try:
          request = json.loads(line)
          response = self.proxy_request(request)
          print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
          error_response = {
            'jsonrpc': '2.0',
            'id': None,
            'error': {'code': -32700, 'message': 'Parse error'},
          }
          print(json.dumps(error_response), flush=True)

    except KeyboardInterrupt:
      pass
    except Exception as e:
      error_response = {
        'jsonrpc': '2.0',
        'id': None,
        'error': {'code': -32000, 'message': f'Proxy error: {e}'},
      }
      print(json.dumps(error_response), flush=True)


def main():
  """Main entry point for the MCP proxy."""
  try:
    # Get URL from command line argument
    if len(sys.argv) < 2:
      print(f'Usage: {sys.argv[0]} <URL>', file=sys.stderr)
      print('URL examples:', file=sys.stderr)
      print('  - http://localhost:8000/mcp/sse/', file=sys.stderr)
      print('  - http://localhost:8000', file=sys.stderr)
      print('  - https://myapp.databricksapps.com', file=sys.stderr)
      sys.exit(1)

    url = sys.argv[1]
    proxy = MCPProxy(url)
    print(f'Connected to MCP server at: {proxy.app_url}', file=sys.stderr)
    proxy.run()
  except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)


if __name__ == '__main__':
  main()
