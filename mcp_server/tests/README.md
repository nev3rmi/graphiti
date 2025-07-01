# MCP Server Test Suite

This directory contains all tests for the Graphiti MCP Server with Ollama integration.

## Directory Structure

```
tests/
├── README.md                          # This file
├── integration/                       # Integration tests with external services
│   ├── test_ollama_integration.py    # Test Ollama LLM and embedding models
│   ├── test_neo4j_integration.py     # Test Neo4j database operations
│   └── test_mcp_full_integration.py  # Complete end-to-end MCP functionality
├── unit/                             # Unit tests for individual components
│   ├── test_server_startup.py       # Test server initialization
│   ├── test_configuration.py        # Test environment configuration
│   └── test_data_operations.py      # Test data manipulation functions
├── validation/                       # Validation and verification tests
│   ├── test_data_accessibility.py   # Verify data is accessible in Neo4j
│   ├── test_mcp_tools.py           # Test all MCP tools functionality
│   └── test_search_functionality.py # Test search and retrieval operations
└── reports/                          # Status reports and comprehensive checks
    ├── ollama_status_report.py      # Comprehensive Ollama integration status
    ├── system_health_check.py      # Overall system health verification
    └── neo4j_browser_queries.md    # Useful Neo4j queries for manual testing
```

## Test Categories

### 🔗 Integration Tests (`integration/`)
- Test connections to external services (Ollama, Neo4j)
- Verify full end-to-end workflows
- Test real data processing pipelines

### 🧪 Unit Tests (`unit/`)
- Test individual components in isolation
- Verify configuration handling
- Test core functionality without external dependencies

### ✅ Validation Tests (`validation/`)
- Verify data integrity and accessibility
- Test MCP protocol compliance
- Validate search and retrieval operations

### 📊 Reports (`reports/`)
- Comprehensive status reporting
- System health monitoring
- Documentation and query examples

## Running Tests

### Individual Test Files
```bash
# Run specific integration test
python3 tests/integration/test_ollama_integration.py

# Run MCP tools validation
python3 tests/validation/test_mcp_tools.py

# Generate status report
python3 tests/reports/ollama_status_report.py
```

### Full Test Suite
```bash
# Run all tests in category
python3 -m pytest tests/integration/
python3 -m pytest tests/validation/

# Run comprehensive system check
python3 tests/reports/system_health_check.py
```

## Test Requirements

- **Docker**: MCP server container must be running
- **Ollama**: Local Ollama server with deepseek-r1:latest and mxbai-embed-large:latest
- **Neo4j**: Database accessible at configured URI
- **Environment**: Proper .env configuration for Ollama integration

## Expected Results

All tests should pass when:
- ✅ MCP server container is running
- ✅ Ollama models are available and responding
- ✅ Neo4j database is accessible
- ✅ Environment variables are properly configured
- ✅ Knowledge graph contains test data

## Troubleshooting

If tests fail:
1. Check container status: `docker ps`
2. Verify Ollama connectivity: `curl http://192.168.31.134:11434/api/tags`
3. Check server logs: `docker logs mcp_server-graphiti-mcp-1`
4. Verify environment: `docker exec mcp_server-graphiti-mcp-1 printenv | grep -E "MODEL|OLLAMA|NEO4J"`