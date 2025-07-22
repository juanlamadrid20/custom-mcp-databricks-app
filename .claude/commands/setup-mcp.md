---
description: "Set up and deploy a Databricks MCP server from this template"
---

# 🚀 Databricks MCP Server Setup

I'll help you set up your own Databricks MCP (Model Context Protocol) server so Claude can interact with your Databricks workspace!

## 📋 What We'll Do

⏺ **Step 1: Environment Setup** - Configure Databricks authentication
⏺ **Step 2: Deploy MCP Server** - Deploy to Databricks Apps  
⏺ **Step 3: Add to Claude** - Configure Claude to use your MCP server
⏺ **Step 4: Test Connection** - Verify everything works
⏺ **Step 5: Customize** - Add your own prompts and tools (optional)

---

## Step 1: Environment Setup

**Let me check if your environment is already configured:**

[I'll check for .env.local and test Databricks authentication]

**If setup is needed, I'll run the interactive setup script:**

```bash
# I'll open a new terminal for interactive setup
./setup.sh --auto-close
```

This will guide you through:
- Databricks authentication (PAT or OAuth)
- Workspace configuration
- Dependency installation

---

## Step 2: Deploy MCP Server

**Once setup is complete, I'll deploy your MCP server:**

**a) Check if app exists:**
[I'll run `./app_status.sh` to check current status]

**b) Create and deploy app:**
```bash
# Deploy (creates app if needed)
nohup ./deploy.sh --create --verbose > /tmp/mcp-deploy.log 2>&1 &
```

**c) Monitor deployment:**
[I'll tail the log file and wait for completion]

**d) Get your app URL:**
[I'll run `./app_status.sh` to get the deployed URL]

**Your MCP Server Details:**
- **Workspace:** [DATABRICKS_HOST from .env.local]
- **App Name:** [DATABRICKS_APP_NAME from .env.local]
- **App URL:** [URL from app_status.sh]

---

## Step 3: Add MCP Server to Claude

**Now let's add your MCP server to Claude!**

Based on your deployment, here's your personalized command:

```bash
# Set your configuration
export DATABRICKS_HOST="[your-workspace-from-env]"
export DATABRICKS_APP_URL="[your-app-url-from-status]"

# Add MCP server to Claude
claude mcp add databricks-mcp --scope user -- \
  uvx --from git+ssh://git@github.com/databricks-solutions/custom-mcp-databricks-app.git \
  dba-mcp-proxy \
  --databricks-host $DATABRICKS_HOST \
  --databricks-app-url $DATABRICKS_APP_URL
```

**Would you like me to run this command for you?** 

I have all the information needed:
- Databricks Host: [from .env.local]
- App URL: [from app_status.sh]

[If yes, I'll execute the claude mcp add command with the actual values]

---

## Step 4: Test Connection

**Let's verify your MCP server is working:**

```bash
# Test with echo trick
echo "What MCP prompts are available from databricks-mcp?" | claude
```

[I'll run this and show you the results]

**Expected output:**
- Should list available prompts (check_system, list_files, ping_google)
- Should show available tools (execute_parameterized_sql, etc.)

**Note:** You'll need to restart this Claude session to see the MCP server in the `/mcp` command. The echo test confirms it's working for new sessions.

---

## Step 5: Customize (Optional)

**Your MCP server is now live! Want to add custom functionality?**

### Add Custom Prompts

Create markdown files in the `prompts/` directory:

```markdown
# prompts/my_custom_prompt.md
# Description of what this prompt does

Content that will be returned to Claude
```

### Add Custom Tools

Add functions in `server/app.py`:

```python
@mcp_server.tool
def my_custom_tool(param: str) -> dict:
    """Tool description for Claude."""
    # Your implementation
    return {"result": "data"}
```

**Would you like me to:**
1. ✨ Add a custom prompt for your use case?
2. 🛠️ Create a custom tool for specific Databricks operations?
3. 📚 Show you more examples of what's possible?
4. ✅ Leave it as is - you're all set!

---

## 🎉 Success!

Your Databricks MCP server is deployed and connected to Claude. You can now:
- Use prompts like `check_system` to verify connectivity
- Execute SQL queries with proper parameterization
- Browse DBFS files
- Add your own custom prompts and tools

**Remember:** Restart Claude or open a new session to see your MCP server in the `/mcp` list!