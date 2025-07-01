# Graphiti MCP Server with Ollama Integration

A Model Context Protocol (MCP) server that exposes Graphiti's temporally-aware knowledge graph functionality with full Ollama support for local AI processing.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Ollama server with required models
- Neo4j database (can be provided via Docker)

### 1. Clone and Setup
```bash
git clone <repository>
cd mcp_server/
cp .env.optimized .env  # Copy and customize environment
```

### 2. Start Services
```bash
# Start MCP server (includes Neo4j if needed)
docker compose up -d

# Verify everything is running
python3 run_tests.py --health-check
```

### 3. Verify Integration
```bash
# Run all tests
python3 run_tests.py

# Generate status report
python3 tests/reports/ollama_status_report.py
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Neo4j Database
NEO4J_URI=neo4j://192.168.31.150:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Ollama Configuration
OPENAI_API_KEY=abc  # Dummy key for Ollama
OPENAI_BASE_URL=http://192.168.31.134:11434/v1/
MODEL_NAME=deepseek-r1:latest
EMBEDDER_MODEL_NAME=mxbai-embed-large:latest
EMBEDDING_DIM=1024
```

### Required Ollama Models
```bash
# Install required models on Ollama server
ollama pull deepseek-r1:latest
ollama pull mxbai-embed-large:latest
```

## 🧪 Testing

### Test Organization
```
tests/
├── integration/     # External service integration tests
├── unit/           # Component unit tests  
├── validation/     # Data verification tests
├── reports/        # Status and health reports
└── legacy/         # Historical test files
```

### Running Tests
```bash
# Complete system health check
python3 run_tests.py --health-check

# Run specific test suites
python3 run_tests.py --suite unit
python3 run_tests.py --suite integration
python3 run_tests.py --suite validation

# Run all tests with reports
python3 run_tests.py --reports

# Individual test files
python3 tests/integration/test_ollama_integration.py
python3 tests/validation/test_mcp_tools.py
```

## 🔌 MCP Tools Available

### Core Tools
- **add_episode**: Store conversations in knowledge graph
- **search_nodes**: Find entities and relationships
- **search_facts**: Search for specific relationship facts
- **get_episodes**: Retrieve recent episodes
- **get_status**: Check server health
- **clear_graph**: Reset knowledge graph

### Entity Types
- **Preference**: User likes/dislikes
- **Procedure**: Step-by-step instructions
- **Requirement**: Project needs and specifications

## 🌐 Integration

### Claude Desktop
Use the generated `mcp_config_stdio.json`:
```json
{
  "mcpServers": {
    "graphiti": {
      "command": "uv",
      "args": ["run", "graphiti_mcp_server.py", "--transport", "stdio"],
      "cwd": "/path/to/mcp_server"
    }
  }
}
```

### SSE Transport (Web Applications)
Connect to: `http://localhost:8000/sse`

### Neo4j Browser
Access knowledge graph: `http://192.168.31.150:7474`

## 📊 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Assistant  │◄──►│  MCP Server     │◄──►│  Neo4j Database │
│   (Claude, etc) │    │  (Port 8000)    │    │  (Port 7474)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Ollama Server  │
                       │  (Port 11434)   │
                       │  - LLM Model    │
                       │  - Embeddings   │
                       └─────────────────┘
```

## 🎯 Key Features

### ✅ Local AI Processing
- **Zero external API calls** - Complete privacy
- **No API usage costs** - Unlimited usage
- **Offline capable** - No internet dependency
- **Custom models** - Use any Ollama-compatible model

### ✅ Persistent Memory
- **Temporal knowledge graph** - Time-aware relationships
- **Hybrid search** - Semantic + keyword + graph traversal
- **Entity extraction** - Automatic relationship discovery
- **Conversation context** - Long-term memory across sessions

### ✅ Production Ready
- **Docker deployment** - Containerized and scalable
- **Health monitoring** - Comprehensive status reporting
- **Test coverage** - Full test suite included
- **Documentation** - Complete setup and usage guides

## 🔍 Monitoring and Debugging

### Health Checks
```bash
# Comprehensive system check
python3 tests/reports/system_health_check.py

# Ollama status report
python3 tests/reports/ollama_status_report.py

# Check container logs
docker logs mcp_server-graphiti-mcp-1
```

### Neo4j Queries
See `tests/reports/neo4j_browser_queries.md` for useful queries to explore your knowledge graph.

### Performance Tuning
- Adjust `SEMAPHORE_LIMIT` for concurrency control
- Monitor resource usage with `docker stats`
- Use faster models for better performance
- Scale Neo4j resources as needed

## 🛠️ Development

### Project Structure
```
mcp_server/
├── graphiti_mcp_server.py      # Main MCP server
├── docker-compose.yml          # Docker services
├── Dockerfile                  # Container definition
├── .env                        # Environment config
├── run_tests.py               # Test runner
├── tests/                     # Test suite
│   ├── integration/           # Integration tests
│   ├── unit/                  # Unit tests
│   ├── validation/            # Validation tests
│   └── reports/               # Status reports
└── README.md                  # This file
```

### Adding New Features
1. Implement in `graphiti_mcp_server.py`
2. Add tests in appropriate `tests/` subdirectory
3. Update documentation
4. Run full test suite: `python3 run_tests.py`

## 📋 Troubleshooting

### Common Issues

**Container won't start:**
```bash
docker compose down
docker compose up --build
```

**Ollama not responding:**
```bash
curl http://192.168.31.134:11434/api/tags
ollama list  # Check installed models
```

**Neo4j connection failed:**
```bash
# Check Neo4j is accessible
curl http://192.168.31.150:7474
# Verify credentials in .env
```

**Tests failing:**
```bash
# Run health check first
python3 run_tests.py --health-check

# Check individual components
python3 tests/unit/test_configuration.py
```

## 📞 Support

- **Documentation**: See `/tests/README.md` for detailed test information
- **Configuration**: Use `.env.optimized` as template for different setups
- **Monitoring**: Regular health checks ensure system reliability
- **Logs**: Container logs provide detailed debugging information

## 🏆 Production Deployment

For production use:
1. Use strong passwords for Neo4j
2. Consider resource limits in Docker Compose
3. Set up log rotation and monitoring
4. Regular backups of Neo4j database
5. Monitor Ollama server resources
6. Use environment-specific `.env` files

---

## 📚 Legacy Documentation

The sections below contain the original documentation for reference.

### Original Features

The Graphiti MCP server exposes the following key high-level functions of Graphiti:

- **Episode Management**: Add, retrieve, and delete episodes (text, messages, or JSON data)
- **Entity Management**: Search and manage entity nodes and relationships in the knowledge graph
- **Search Capabilities**: Search for facts (edges) and node summaries using semantic and hybrid search
- **Group Management**: Organize and manage groups of related data with group_id filtering
- **Graph Maintenance**: Clear the graph and rebuild indices

### Available Tools (Complete List)

The Graphiti MCP server exposes the following tools:

- `add_episode`: Add an episode to the knowledge graph (supports text, JSON, and message formats)
- `search_nodes`: Search the knowledge graph for relevant node summaries
- `search_facts`: Search the knowledge graph for relevant facts (edges between entities)
- `delete_entity_edge`: Delete an entity edge from the knowledge graph
- `delete_episode`: Delete an episode from the knowledge graph
- `get_entity_edge`: Get an entity edge by its UUID
- `get_episodes`: Get the most recent episodes for a specific group
- `clear_graph`: Clear all data from the knowledge graph and rebuild indices
- `get_status`: Get the status of the Graphiti MCP server and Neo4j connection

### Working with JSON Data

The Graphiti MCP server can process structured JSON data through the `add_episode` tool with `source="json"`. This
allows you to automatically extract entities and relationships from structured data:

```
add_episode(
name="Customer Profile",
episode_body="{\"company\": {\"name\": \"Acme Technologies\"}, \"products\": [{\"id\": \"P001\", \"name\": \"CloudSync\"}, {\"id\": \"P002\", \"name\": \"DataMiner\"}]}",
source="json",
source_description="CRM data"
)
```

### Alternative Installation (Without Docker)

1. Ensure you have Python 3.10 or higher installed.
2. A running Neo4j database (version 5.26 or later required)
3. OpenAI API key for LLM operations (or Ollama setup)

#### Setup
```bash
# Install uv if you don't have it already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create a virtual environment and install dependencies in one step
uv sync
```

#### Running Directly
```bash
uv run graphiti_mcp_server.py
```

With options:
```bash
uv run graphiti_mcp_server.py --model gpt-4.1-mini --transport sse
```

### Legacy Environment Variables

- `OPENAI_BASE_URL`: Optional base URL for OpenAI API
- `MODEL_NAME`: OpenAI model name to use for LLM operations.
- `SMALL_MODEL_NAME`: OpenAI model name to use for smaller LLM operations.
- `LLM_TEMPERATURE`: Temperature for LLM responses (0.0-2.0).
- `AZURE_OPENAI_*`: Various Azure OpenAI configuration options
- `SEMAPHORE_LIMIT`: Episode processing concurrency

### Telemetry

The Graphiti MCP server uses the Graphiti core library, which includes anonymous telemetry collection. To disable:

```bash
export GRAPHITI_TELEMETRY_ENABLED=false
```

---

**Ready for AI assistant integration with complete local processing and persistent memory capabilities!**