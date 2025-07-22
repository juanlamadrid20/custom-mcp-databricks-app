#!/bin/bash

# Test remote MCP functionality
REMOTE_URL="https://mcp-commands-5722066275360235.aws.databricksapps.com"

echo "Testing remote MCP functionality at $REMOTE_URL"
echo "============================================"

# Test 1: Initialize
echo -e "\n1. Testing MCP initialize:"
curl -s -X POST "$REMOTE_URL/mcp/initialize" \
  -H "Content-Type: application/json" \
  -d '{"protocolVersion": "2024-11-05", "capabilities": {"prompts": {"listChanged": true}, "tools": {}}, "clientInfo": {"name": "curl-test", "version": "1.0.0"}}' | jq .

# Test 2: List tools
echo -e "\n2. Testing MCP tools list:"
curl -s -X POST "$REMOTE_URL/mcp/tools/list" \
  -H "Content-Type: application/json" | jq .

# Test 3: List prompts
echo -e "\n3. Testing MCP prompts list:"
curl -s -X POST "$REMOTE_URL/mcp/prompts/list" \
  -H "Content-Type: application/json" | jq .

# Test 4: Get a specific prompt
echo -e "\n4. Testing MCP prompts get for 'sql-explain':"
curl -s -X POST "$REMOTE_URL/mcp/prompts/get" \
  -H "Content-Type: application/json" \
  -d '{"name": "sql-explain"}' | jq .

# Test 5: Check MCP SSE endpoint
echo -e "\n5. Testing MCP SSE endpoint (should return connection info):"
curl -s -I "$REMOTE_URL/mcp" | head -20

echo -e "\nRemote MCP tests complete!"