# 🤖 Databricks MCP Server Template

Host Model Context Protocol (MCP) prompts and tools on Databricks Apps, enabling AI assistants like Claude to interact with your Databricks workspace through a secure, authenticated interface.

## What is this?

This template lets you create an MCP server that runs on Databricks Apps. You can:
- 📝 **Add prompts** as simple markdown files in the `prompts/` folder
- 🛠️ **Create tools** as Python functions that leverage Databricks SDK
- 🔐 **Authenticate securely** with OAuth through Databricks Apps
- 🚀 **Deploy instantly** to make your MCP server accessible to Claude

Think of it as a bridge between Claude and your Databricks workspace - you define what Claude can see and do, and this server handles the rest.

## How it Works

### Architecture Overview

```
┌─────────────┐       MCP Protocol      ┌──────────────────┐        OAuth         ┌─────────────────┐
│   Claude    │ ◄─────────────────────► │  dba-mcp-proxy   │ ◄──────────────────► │ Databricks App  │
│    CLI      │     (stdio/JSON-RPC)    │ (local process)  │    (HTTPS/SSE)      │  (MCP Server)   │
└─────────────┘                         └──────────────────┘                      └─────────────────┘
                                                ▲                                           │
                                                │                                           ▼
                                                └────────── Databricks OAuth ──────► Workspace APIs
```

### Components

1. **MCP Server** (`server/app.py`): A FastAPI app with integrated MCP server that:
   - Dynamically loads prompts from `prompts/*.md` files
   - Exposes Python functions as MCP tools via `@mcp_server.tool` decorator
   - Handles both HTTP requests and MCP protocol over Server-Sent Events

2. **Prompts** (`prompts/`): Simple markdown files where:
   - Filename = prompt name (e.g., `check_system.md` → `check_system` prompt)
   - First line with `#` = description
   - File content = what gets returned to Claude

3. **Local Proxy** (`dba_mcp_proxy/`): Authenticates and proxies MCP requests:
   - Handles Databricks OAuth authentication automatically
   - Translates between Claude's stdio protocol and HTTP/SSE
   - Works with both local development and deployed apps

## Quick Start

### Add to Claude

Since this repo is public, you can use it directly:

```bash
# Add this MCP server to Claude
claude mcp add databricks-mcp \
  uvx \
  --from git+ssh://git@github.com/databricks-solutions/custom-mcp-databricks-app.git \
  dba-mcp-proxy \
  --databricks-host https://your-workspace.cloud.databricks.com \
  --databricks-app-url https://your-app.databricksapps.com
```

### Or Use Your Own Fork

1. Fork this repository
2. Customize prompts and tools
3. Deploy to Databricks Apps
4. Use your own proxy:

```bash
# Using your fork
claude mcp add my-databricks-mcp \
  uvx \
  --from git+ssh://git@github.com/YOUR-ORG/YOUR-REPO.git \
  dba-mcp-proxy \
  --databricks-host https://your-workspace.cloud.databricks.com \
  --databricks-app-url https://your-app.databricksapps.com
```

### Local Development

```bash
# Clone and setup
git clone <your-repo>
cd <your-repo>
./setup.sh

# Start dev server
./watch.sh

# Add to Claude for local testing
claude mcp add databricks-mcp-local \
  uvx \
  --from git+ssh://git@github.com/YOUR-ORG/YOUR-REPO.git \
  dba-mcp-proxy \
  --databricks-host https://your-workspace.cloud.databricks.com \
  --databricks-app-url http://localhost:8000
```

## Customization Guide

This template uses [FastMCP](https://github.com/jlowin/fastmcp), a framework that makes it easy to build MCP servers. FastMCP provides two main decorators for extending functionality:

- **`@mcp_server.prompt`** - For registering prompts that return text
- **`@mcp_server.tool`** - For registering tools that execute functions

### Adding Prompts

The easiest way is to create a markdown file in the `prompts/` directory:

```markdown
# Get cluster information

List all available clusters in the workspace with their current status
```

The prompt will be automatically loaded with:
- **Name**: filename without extension (e.g., `get_clusters.md` → `get_clusters`)
- **Description**: first line after `#` 
- **Content**: entire file content

Alternatively, you can register prompts as functions in `server/app.py`:

```python
@mcp_server.prompt(name="dynamic_status", description="Get dynamic system status")
async def get_dynamic_status():
    # This can include dynamic logic, API calls, etc.
    w = get_workspace_client()
    current_user = w.current_user.me()
    return f"Current user: {current_user.display_name}\nWorkspace: {DATABRICKS_HOST}"
```

We auto-load `prompts/` for convenience, but function-based prompts are useful when you need dynamic content.

### Adding Tools

Add a function in `server/app.py` using the `@mcp_server.tool` decorator:

```python
@mcp_server.tool
def list_clusters(status: str = "RUNNING") -> dict:
    """List Databricks clusters by status."""
    w = get_workspace_client()
    clusters = []
    for cluster in w.clusters.list():
        if cluster.state.name == status:
            clusters.append({
                "id": cluster.cluster_id,
                "name": cluster.cluster_name,
                "state": cluster.state.name
            })
    return {"clusters": clusters}
```

Tools must:
- Use the `@mcp_server.tool` decorator
- Have a docstring (becomes the tool description)
- Return JSON-serializable data (dict, list, str, etc.)
- Accept only JSON-serializable parameters


## Deployment

```bash
# Deploy to Databricks Apps
./deploy.sh

# Check status
./app_status.sh
```

Your MCP server will be available at `https://your-app.databricksapps.com/mcp/`

## Authentication

- **Local Development**: No authentication required
- **Production**: OAuth is handled automatically by the proxy using your Databricks CLI credentials

## Examples

### Using with Claude

Once added, you can interact with your MCP server in Claude:

```
Human: What prompts are available?

Claude: I can see the following prompts from your Databricks MCP server:
- check_system: Get system information
- list_files: List files in the current directory
- ping_google: Check network connectivity
```

### Sample Tool Usage

```
Human: Can you execute a SQL query to show databases?

Claude: I'll execute that SQL query for you using the execute_dbsql tool.

[Executes SQL and returns results]
```

## Project Structure

```
├── server/                    # FastAPI backend with MCP server
│   ├── app.py                # Main application + MCP tools
│   └── routers/              # API endpoints
├── prompts/                  # MCP prompts (markdown files)
│   ├── check_system.md      
│   ├── list_files.md        
│   └── ping_google.md       
├── dba_mcp_proxy/           # MCP proxy for Claude CLI
│   └── mcp_client.py        # OAuth + proxy implementation
├── client/                  # React frontend (optional)
├── scripts/                 # Development tools
└── pyproject.toml          # Python package configuration
```

## Advanced Usage

### Environment Variables

Configure in `.env.local`:
```bash
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-token  # For local development
DATABRICKS_SQL_WAREHOUSE_ID=your-warehouse-id  # For SQL tools
```

### Creating Complex Tools

Tools can access the full Databricks SDK:

```python
@mcp_server.tool
def create_job(name: str, notebook_path: str, cluster_id: str) -> dict:
    """Create a Databricks job."""
    w = get_workspace_client()
    job = w.jobs.create(
        name=name,
        tasks=[{
            "task_key": "main",
            "notebook_task": {"notebook_path": notebook_path},
            "existing_cluster_id": cluster_id
        }]
    )
    return {"job_id": job.job_id, "run_now_url": f"{DATABRICKS_HOST}/#job/{job.job_id}"}
```

## Troubleshooting

- **Authentication errors**: Run `databricks auth login` to refresh credentials
- **MCP not found**: Ensure the app is deployed and accessible
- **Tool errors**: Check logs at `https://your-app.databricksapps.com/logz`

## Contributing

1. Fork the repository
2. Add your prompts and tools
3. Test locally with `./watch.sh`
4. Submit a pull request

## License

See [LICENSE.md](LICENSE.md)