import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChevronLeft, FileCode, Wrench } from "lucide-react";
import { PromptsService, McpService } from "@/fastapi_client";

interface Prompt {
  name: string;
  description: string;
  filename: string;
}

interface PromptDetail {
  name: string;
  content: string;
}

interface MCPItem {
  name: string;
  description: string;
}

export function PromptsPage() {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [mcpPrompts, setMcpPrompts] = useState<MCPItem[]>([]);
  const [mcpTools, setMcpTools] = useState<MCPItem[]>([]);
  const [selectedPrompt, setSelectedPrompt] = useState<PromptDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      // Fetch prompts from prompts directory
      const promptsResponse = await PromptsService.listPromptsApiPromptsGet();
      setPrompts(promptsResponse);
      
      // Fetch MCP discovery info
      const mcpResponse = await McpService.getMcpDiscoveryApiMcpInfoDiscoveryGet();
      if (mcpResponse.prompts) {
        setMcpPrompts(mcpResponse.prompts);
      }
      if (mcpResponse.tools) {
        setMcpTools(mcpResponse.tools);
      }
    } catch (err) {
      setError("Failed to load data");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchPromptDetail = async (promptName: string) => {
    try {
      const response = await PromptsService.getPromptApiPromptsPromptNameGet(promptName);
      setSelectedPrompt(response);
    } catch (err) {
      setError("Failed to load prompt detail");
      console.error(err);
    }
  };

  const handleBack = () => {
    setSelectedPrompt(null);
    setError(null);
  };

  if (loading) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">Loading prompts...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center text-red-500">{error}</div>
      </div>
    );
  }

  if (selectedPrompt) {
    return (
      <div className="container mx-auto py-8 max-w-4xl">
        <Button
          variant="ghost"
          onClick={handleBack}
          className="mb-6"
        >
          <ChevronLeft className="mr-2 h-4 w-4" />
          Back to prompts
        </Button>
        
        <Card>
          <CardHeader>
            <CardTitle>{selectedPrompt.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="whitespace-pre-wrap font-mono text-sm bg-muted p-4 rounded-lg">
              {selectedPrompt.content}
            </pre>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8">MCP Discovery</h1>
      
      {/* MCP Prompts Section */}
      <div className="mb-12">
        <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
          <FileCode className="h-6 w-6" />
          MCP Prompts (Slash Commands)
        </h2>
        
        {mcpPrompts.length === 0 ? (
          <div className="text-center text-muted-foreground mb-8">
            No MCP prompts found.
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 mb-8">
            {mcpPrompts.map((prompt) => (
              <Card key={prompt.name}>
                <CardHeader>
                  <CardTitle className="text-lg">
                    /{prompt.name}
                  </CardTitle>
                  <CardDescription>{prompt.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Available as slash command in Claude Code
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* MCP Tools Section */}
      <div className="mb-12">
        <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
          <Wrench className="h-6 w-6" />
          MCP Tools
        </h2>
        
        {mcpTools.length === 0 ? (
          <div className="text-center text-muted-foreground mb-8">
            No MCP tools found.
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 mb-8">
            {mcpTools.map((tool) => (
              <Card key={tool.name}>
                <CardHeader>
                  <CardTitle className="text-lg">
                    {tool.name}
                  </CardTitle>
                  <CardDescription className="whitespace-pre-line">{tool.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Available as MCP tool
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Prompt Files Section */}
      <div>
        <h2 className="text-2xl font-semibold mb-4">Prompt Files</h2>
        
        {prompts.length === 0 ? (
          <div className="text-center text-muted-foreground">
            No prompt files found. Add markdown files to the prompts directory.
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {prompts.map((prompt) => (
              <Card
                key={prompt.name}
                className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => fetchPromptDetail(prompt.name)}
              >
                <CardHeader>
                  <CardTitle className="text-lg">
                    {prompt.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </CardTitle>
                  <CardDescription>{prompt.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Click to view full prompt
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}