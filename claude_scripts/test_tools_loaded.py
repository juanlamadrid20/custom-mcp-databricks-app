#!/usr/bin/env python3
"""Test that MCP tools are properly loaded."""

import requests

# Test if tools are available via API docs
response = requests.get('http://localhost:8000/docs')
if response.status_code == 200:
    print("✅ API docs available")
else:
    print(f"❌ API docs not available: {response.status_code}")

# Test the health check endpoint to verify server is running
response = requests.get('http://localhost:8000/api/user/me')
print(f"User endpoint status: {response.status_code}")

# Check MCP info endpoint
response = requests.get('http://localhost:8000/api/mcp_info/prompts')
if response.status_code == 200:
    prompts = response.json()
    print(f"\n✅ Found {len(prompts)} prompts:")
    for prompt in prompts:
        print(f"  - {prompt['name']}: {prompt['description']}")
else:
    print(f"❌ Could not get prompts: {response.status_code}")

# Simple MCP test with initialization
print("\n🔧 Testing MCP initialization...")
init_payload = {
    "jsonrpc": "2.0",
    "id": "initialize",
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test-client", "version": "1.0.0"}
    }
}

# First get session ID
response = requests.get(
    'http://localhost:8000/mcp/',
    headers={'Accept': 'application/json, text/event-stream'}
)
session_id = response.headers.get('mcp-session-id')
print(f"Session ID: {session_id}")

# Then initialize
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json, text/event-stream'
}
if session_id:
    headers['mcp-session-id'] = session_id

response = requests.post('http://localhost:8000/mcp/', json=init_payload, headers=headers)
print(f"Init response status: {response.status_code}")
if response.status_code == 200:
    # Send initialized notification
    initialized_payload = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }
    requests.post('http://localhost:8000/mcp/', json=initialized_payload, headers=headers)
    
    # List tools
    tools_payload = {
        "jsonrpc": "2.0",
        "id": "tools-list",
        "method": "tools/list"
    }
    
    response = requests.post('http://localhost:8000/mcp/', json=tools_payload, headers=headers)
    if response.status_code == 200:
        # Handle SSE response
        if 'text/event-stream' in response.headers.get('content-type', ''):
            print("Got SSE response, parsing events...")
            for line in response.text.split('\n'):
                if line.startswith('data: '):
                    import json
                    try:
                        data = json.loads(line[6:])
                        if 'result' in data and 'tools' in data['result']:
                            tools = data['result']['tools']
                            print(f"\n✅ Found {len(tools)} tools:")
                            for tool in tools:
                                print(f"  - {tool['name']}: {tool['description']}")
                    except:
                        pass
        else:
            result = response.json()
            if 'result' in result and 'tools' in result['result']:
                tools = result['result']['tools']
                print(f"\n✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"  - {tool['name']}: {tool['description']}")