export const PROJECT_TITLE =
  "AI-Powered Workforce and Technology Recommendation Assistant";

export const PROJECT_DESCRIPTION =
  "A session-aware AI assistant that connects internal workforce capabilities with current public technology information.";

export const PROJECT_CAPABILITIES: readonly string[] = [
  "General knowledge through a local Ollama model",
  "Internal workforce search using PostgreSQL-backed LangChain tools",
  "Current GitHub repository discovery using MCP tools",
  "Multi-source workforce and repository recommendations",
  "Redis-backed conversation history",
  "Session-scoped semantic response caching",
];

export const TECHNOLOGY_BADGES: readonly string[] = [
  "Next.js",
  "FastAPI",
  "LangChain",
  "Ollama",
  "PostgreSQL",
  "Redis",
  "MCP",
  "GitHub REST API",
  "Docker Compose",
];

export const ARCHITECTURE_FLOW: readonly string[] = [
  "User",
  "Next.js",
  "FastAPI",
  "Semantic Cache",
  "LangChain Agent",
];

export const ARCHITECTURE_BRANCHES: ReadonlyArray<{
  label: string;
  flow: string;
}> = [
  { label: "Internal data", flow: "LangChain tools → PostgreSQL" },
  { label: "External data", flow: "MCP tools → GitHub REST API" },
];
