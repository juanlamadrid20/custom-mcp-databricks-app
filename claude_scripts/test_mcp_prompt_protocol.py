#!/usr/bin/env python
"""Test MCP prompt protocol to see exactly what Claude receives."""

import json
import time
from subprocess import PIPE, STDOUT, Popen

# Start the MCP client process
process = Popen(
  ['uv', 'run', 'python', 'mcp_databricks_client.py', 'http://localhost:8000'],
  stdin=PIPE,
  stdout=PIPE,
  stderr=STDOUT,
  text=True,
  bufsize=0,
)


def send_request(request):
  """Send a request and get response."""
  json_str = json.dumps(request)
  print(f'\n📤 Sending: {json_str}')
  process.stdin.write(json_str + '\n')
  process.stdin.flush()

  # Read response
  response_line = process.stdout.readline()
  if response_line:
    print(f'📥 Response: {response_line.strip()}')
    return json.loads(response_line)
  return None


# Wait for connection message
time.sleep(0.5)
connection_msg = process.stdout.readline()
print(f'🔗 {connection_msg.strip()}')

# 1. Initialize
print('\n1️⃣ Initializing MCP session...')
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
init_response = send_request(init_request)

# 2. List prompts
print('\n2️⃣ Listing prompts...')
list_request = {'jsonrpc': '2.0', 'method': 'prompts/list', 'params': {}, 'id': 2}
list_response = send_request(list_request)

if list_response and 'result' in list_response:
  prompts = list_response['result'].get('prompts', [])
  print(f'\n✅ Found {len(prompts)} prompts:')
  for prompt in prompts:
    print(f'  - {prompt["name"]}: {prompt.get("description", "No description")}')

# 3. Get check_system prompt
print('\n3️⃣ Getting check_system prompt...')
get_prompt_request = {
  'jsonrpc': '2.0',
  'method': 'prompts/get',
  'params': {'name': 'check_system'},
  'id': 3,
}
prompt_response = send_request(get_prompt_request)

if prompt_response and 'result' in prompt_response:
  result = prompt_response['result']
  print('\n📝 ACTUAL MCP PROMPT RESPONSE:')
  print('=' * 60)
  print(json.dumps(result, indent=2))

  if 'messages' in result:
    print('\n🎯 PROMPT MESSAGES CLAUDE RECEIVES:')
    print('=' * 60)
    for i, msg in enumerate(result['messages']):
      print(f'\nMessage {i + 1}:')
      print(f'  Role: {msg.get("role", "unknown")}')
      content = msg.get('content', {})
      if isinstance(content, dict):
        print(f'  Content Type: {content.get("type", "unknown")}')
        print(f'  Text: {content.get("text", "NO TEXT")}')
      else:
        print(f'  Content: {content}')
      print('-' * 60)

# Terminate the process
process.terminate()
print('\n✨ Test complete!')
