#!/bin/bash
# Test local MCP server with direct curl commands

echo "🧪 Testing Local MCP Server with curl"
echo "=====================================\n"

BASE_URL="http://localhost:8000"

# Check if server is running
echo "Checking if local server is running..."
if ! curl -s --connect-timeout 3 "${BASE_URL}/mcp/" > /dev/null 2>&1; then
  echo "❌ ERROR: No local server running on ${BASE_URL}"
  echo "   Please start the server with: ./watch.sh"
  exit 1
fi

echo "✅ Local server is running\n"

echo "1. Test MCP endpoint availability:"
curl -s "${BASE_URL}/mcp/" | head -3
echo "\n"

echo "2. Test tools/list via curl:"
curl -s -X POST "${BASE_URL}/mcp/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer local-test-token" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | jq '.'
echo "\n"

echo "3. Test health tool:"
curl -s -X POST "${BASE_URL}/mcp/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer local-test-token" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "health", "arguments": {}}}' | jq '.'
echo "\n"

echo "✅ Local MCP curl tests complete"