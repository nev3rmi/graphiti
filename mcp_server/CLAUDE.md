# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Graphiti MCP Server - a Model Context Protocol implementation that exposes Graphiti's temporally-aware knowledge graph functionality to AI assistants like Claude, Cursor, and other MCP-compatible clients. It enables AI agents to maintain persistent memory through structured knowledge graphs.

## Development Commands

### Environment Setup

```bash
# Install dependencies
uv sync

# Run the MCP server directly with stdio transport (for development/testing)
uv run graphiti_mcp_server.py --transport stdio

# Run with SSE transport for web-based connections
uv run graphiti_mcp_server.py --transport sse

# Run with custom options
uv run graphiti_mcp_server.py --model gpt-4.1-mini --temperature 0.7 --group-id my_project
```

### Docker Development

```bash
# Run with Docker Compose (includes Neo4j)
docker compose up

# Run in detached mode
docker compose up -d

# View logs
docker compose logs -f graphiti-mcp
```

### Configuration

Environment variables are configured via `.env` file (copy from `.env.example`):
- `OPENAI_API_KEY` - Required for LLM operations
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` - Neo4j connection settings
- `MODEL_NAME` - OpenAI model for primary operations (default: gpt-4.1-mini)
- `SEMAPHORE_LIMIT` - Concurrent operation limit to prevent rate limiting (default: 10)

## Code Architecture

### Core Components

- **Main Server**: `graphiti_mcp_server.py` - FastMCP server implementation that orchestrates all MCP functionality
- **Transport Layer**: Supports both stdio (for direct CLI integration) and SSE (for web-based connections)
- **Memory Integration**: Uses Graphiti core library for knowledge graph operations

### Key MCP Tools Exposed

1. **Episode Management**: 
   - `add_episode` - Ingest text, JSON, or message data into knowledge graph
   - `get_episodes` - Retrieve recent episodes for a group
   - `delete_episode` - Remove episodes from the graph

2. **Entity & Relationship Search**:
   - `search_nodes` - Find relevant entity summaries with hybrid search
   - `search_facts` - Search for relationships (edges) between entities
   - `get_entity_edge` - Retrieve specific entity relationships by UUID

3. **Graph Maintenance**:
   - `clear_graph` - Reset knowledge graph and rebuild indices
   - `get_status` - Check server and database connection status

### Client Integration Patterns

The server supports two primary integration modes:

1. **Stdio Transport**: Direct process communication for CLI tools
   ```json
   {
     "transport": "stdio",
     "command": "uv",
     "args": ["run", "graphiti_mcp_server.py", "--transport", "stdio"]
   }
   ```

2. **SSE Transport**: HTTP-based for web applications and remote clients
   ```json
   {
     "transport": "sse",
     "url": "http://localhost:8000/sse"
   }
   ```

### Memory Usage Guidelines

When working with the MCP server, follow patterns from `cursor_rules.md`:
- Always search existing knowledge before adding new information
- Use entity type filters (`Preference`, `Procedure`, `Requirement`) for targeted searches
- Store new information immediately using `add_episode`
- Respect discovered preferences and follow established procedures

## Dependencies and Requirements

- Python 3.10+ required
- Neo4j 5.26+ for graph storage
- OpenAI API key for LLM operations and embeddings
- `uv` package manager for dependency management
- Docker optional for containerized deployment