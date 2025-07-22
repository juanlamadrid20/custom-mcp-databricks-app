"""FastAPI application for Databricks App Template."""

import glob as glob_module
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastmcp import FastMCP

from server.routers import router


# Load environment variables from .env.local if it exists
def load_env_file(filepath: str) -> None:
  """Load environment variables from a file."""
  if Path(filepath).exists():
    with open(filepath) as f:
      for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
          key, _, value = line.partition('=')
          if key and value:
            os.environ[key] = value


# Load .env files
load_env_file('.env')
load_env_file('.env.local')

# Create MCP server with tools first (before creating FastAPI app)
# Note: FastMCP internally serves at /mcp, so when we mount at /mcp it becomes /mcp/mcp
mcp_server = FastMCP(name='Databricks MCP Server')

# Add MCP prompts from the prompts directory


def load_prompts():
  """Dynamically load prompts from the prompts directory."""
  prompt_files = glob_module.glob('prompts/*.md')

  for prompt_file in prompt_files:
    prompt_name = os.path.splitext(os.path.basename(prompt_file))[0]

    # Read the prompt file
    with open(prompt_file, 'r') as f:
      content = f.read()
      lines = content.strip().split('\n')

      # First line is the title (skip the # prefix)
      title = lines[0].strip().lstrip('#').strip() if lines else prompt_name
      # Full content is what gets returned

    # Create a closure to capture the current values
    def make_prompt_handler(prompt_content, prompt_name, prompt_title):
      @mcp_server.prompt(name=prompt_name, description=prompt_title)
      async def handle_prompt():
        return prompt_content

      return handle_prompt

    # Register the prompt
    make_prompt_handler(content, prompt_name, title)


# Load all prompts
load_prompts()


# Add MCP tools from the original mcp_server
@mcp_server.tool
def health() -> dict:
  """Health check endpoint."""
  print('🔥 health tool called!')
  return {'status': 'healthy'}


@mcp_server.tool
def execute_dbsql(query: str, warehouse_id=None, catalog=None, schema=None, limit=100):
  """Execute SQL query using Databricks SDK with PAT authentication."""
  from databricks.sdk import WorkspaceClient

  try:
    # Initialize Databricks SDK with PAT from environment
    w = WorkspaceClient(
      host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
    )

    # Get warehouse ID from parameter or environment
    warehouse_id = warehouse_id or os.environ.get('DATABRICKS_SQL_WAREHOUSE_ID')
    if not warehouse_id:
      return {
        'success': False,
        'error': (
          'No SQL warehouse ID provided. '
          'Set DATABRICKS_SQL_WAREHOUSE_ID or pass warehouse_id.'
        ),
      }

    # Build the full query with catalog/schema if provided
    full_query = query
    if catalog and schema:
      full_query = f'USE CATALOG {catalog}; USE SCHEMA {schema}; {query}'

    print(f'🔧 Executing SQL on warehouse {warehouse_id}: {query[:100]}...')

    # Execute the query
    result = w.statement_execution.execute_statement(
      warehouse_id=warehouse_id, statement=full_query, wait_timeout='30s'
    )

    # Process results
    if result.result and result.result.data_array:
      columns = [col.name for col in result.manifest.schema.columns]
      data = []

      for row in result.result.data_array[:limit]:
        row_dict = {}
        for i, col in enumerate(columns):
          row_dict[col] = row[i]
        data.append(row_dict)

      return {'success': True, 'data': {'columns': columns, 'rows': data}, 'row_count': len(data)}
    else:
      return {
        'success': True,
        'data': {'message': 'Query executed successfully with no results'},
        'row_count': 0,
      }

  except Exception as e:
    print(f'❌ Error executing SQL: {str(e)}')
    return {'success': False, 'error': f'Error: {str(e)}'}


# Create ASGI app from MCP server
# Note: Setting path='/' here to avoid /mcp/mcp double path
mcp_asgi_app = mcp_server.http_app(path='/')

# Pass the MCP app's lifespan to FastAPI
app = FastAPI(
  title='Databricks App API',
  description='Modern FastAPI application template for Databricks Apps with React frontend',
  version='0.1.0',
  lifespan=mcp_asgi_app.lifespan,
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=[
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
  ],
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*'],
)

app.include_router(router, prefix='/api', tags=['api'])




# Mount the MCP server
app.mount('/mcp', mcp_asgi_app)

# ============================================================================
# SERVE STATIC FILES FROM CLIENT BUILD DIRECTORY (MUST BE LAST!)
# ============================================================================
# This static file mount MUST be the last route registered!
# It catches all unmatched requests and serves the React app.
# Any routes added after this will be unreachable!
if os.path.exists('client/build'):
  app.mount('/', StaticFiles(directory='client/build', html=True), name='static')

if __name__ == '__main__':
  import uvicorn

  port = int(os.environ.get('DATABRICKS_APP_PORT', 8000))
  uvicorn.run(app, host='0.0.0.0', port=port)
