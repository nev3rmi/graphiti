#!/usr/bin/env python3
"""
Save comprehensive development knowledge to MCP memory - Fixed Version
"""

import subprocess
import time
import json

def run_docker_command(cmd, timeout=30):
    """Helper to run docker commands with timeout"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def save_development_knowledge():
    """Save comprehensive development knowledge to MCP memory"""
    print("🧠 SAVING DEVELOPMENT KNOWLEDGE TO MCP MEMORY")
    print("=" * 70)
    
    # Development knowledge entries to save
    knowledge_entries = [
        {
            "name": "ollama_integration_best_practices",
            "content": """
OLLAMA INTEGRATION BEST PRACTICES FOR MCP SERVERS

Key Configuration Patterns:
• Always use OPENAI_BASE_URL=http://[ollama-host]:11434/v1/ for Ollama endpoint
• Set dummy OPENAI_API_KEY=abc for Ollama (required by OpenAI client but unused)
• Use MODEL_NAME=deepseek-r1:latest for robust local LLM inference
• Set EMBEDDER_MODEL_NAME=mxbai-embed-large:latest for quality embeddings
• Configure EMBEDDING_DIM=1024 to match mxbai-embed-large dimensions

Critical Issues & Solutions:
• Embedder model mismatch: Default OpenAI configs override Ollama settings in Graphiti
• Solution: Explicitly configure OpenAIEmbedderConfig with base_url and model params
• Permission issues in Docker: Use --user root for script execution in containers
• Memory allocation: Increase semaphore limits for better concurrency with local models

Environment Variable Patterns:
• NEO4J_URI=neo4j://[host]:7687 for database connection
• SEMAPHORE_LIMIT=10 for balanced performance vs resource usage
• GROUP_ID=default for consistent data organization
• MCP_SERVER_HOST=0.0.0.0 for Docker networking

Performance Optimizations:
• Use deepseek-r1:latest for fast, capable local inference
• mxbai-embed-large provides good quality/speed balance for embeddings
• Configure proper timeouts (30-90 seconds) for LLM operations
• Monitor Docker resource usage and adjust container limits accordingly
            """,
            "source": "development_knowledge",
            "description": "Best practices for integrating Ollama with MCP servers and Graphiti"
        },
        {
            "name": "graphiti_mcp_development_patterns",
            "content": """
GRAPHITI MCP SERVER DEVELOPMENT PATTERNS & INSIGHTS

Architecture Patterns:
• FastMCP + Graphiti Core + Neo4j provides robust knowledge graph foundation
• SSE transport enables real-time AI assistant integration
• Docker containerization essential for consistent deployment
• Environment-driven configuration allows flexible model switching

Code Organization Best Practices:
• Separate tests by category: integration/, unit/, validation/, reports/
• Use run_tests.py for unified test execution and health monitoring
• Implement comprehensive health checks for all system components
• Create status reports for easy system monitoring and debugging

Database Design Insights:
• Use group_id='default' for consistent data namespacing
• Episode nodes store conversation content with temporal metadata
• Entity nodes represent extracted people, organizations, concepts
• RELATES_TO edges capture relationships between entities
• Full-text indices enable efficient content search

Error Handling Patterns:
• Always validate Ollama connectivity before operations
• Use timeouts for all async operations (30-90 seconds)
• Implement graceful fallbacks when models are unavailable
• Log configuration details for easier debugging

Testing Strategies:
• Direct Neo4j tests avoid complex LLM dependencies
• Health checks validate all system components independently
• Memory flow tests verify end-to-end functionality
• Status reports provide comprehensive system monitoring

Integration Considerations:
• MCP protocol requires specific tool definitions and schemas
• SSE transport needs proper CORS and connection handling
• Neo4j browser provides valuable debugging and data exploration
• Docker networking requires careful port and host configuration
            """,
            "source": "development_knowledge", 
            "description": "Development patterns and architectural insights for Graphiti MCP servers"
        },
        {
            "name": "troubleshooting_knowledge_base",
            "content": """
GRAPHITI MCP SERVER TROUBLESHOOTING KNOWLEDGE BASE

Common Issues & Solutions:

1. EMBEDDER MODEL MISMATCH
   Problem: "model text-embedding-3-small not found" with Ollama
   Cause: Graphiti defaults to OpenAI models, ignoring custom embedder config
   Solution: Explicitly configure OpenAIEmbedderConfig with base_url and model
   Code Pattern: embedder_config = OpenAIEmbedderConfig(base_url=ollama_url, model="mxbai-embed-large:latest")

2. CONTAINER PERMISSION ISSUES
   Problem: "Permission denied" when running scripts in Docker
   Cause: Non-root user cannot execute copied files
   Solution: Use --user root flag or chmod 755 before execution
   Command: docker exec --user root container_name python3 script.py

3. SERVER INITIALIZATION FAILURES
   Problem: MCP server starts but Graphiti client not initialized
   Cause: Missing environment variables or model unavailability
   Solution: Check logs for specific errors, verify model accessibility
   Debug: docker logs container_name | grep -E "(ERROR|Graphiti|initialized)"

4. NEO4J CONNECTION ISSUES
   Problem: "Connection refused" to Neo4j database
   Cause: Incorrect URI, credentials, or network configuration
   Solution: Test direct connection with curl http://neo4j-host:7474
   Verify: Check NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD environment variables

5. MEMORY OPERATIONS FAILING
   Problem: Episodes not saving or retrieving properly
   Cause: Group ID mismatch, database connectivity, or LLM errors
   Solution: Use group_id='default' consistently, verify database health
   Test: Direct Neo4j queries to verify data storage and retrieval

6. SEARCH FUNCTIONALITY ISSUES
   Problem: Search returns no results despite stored data
   Cause: Embedding model mismatch, index issues, or query problems
   Solution: Verify embedder configuration, rebuild indices if needed
   Fallback: Use keyword-based search with CONTAINS queries

7. DOCKER NETWORKING PROBLEMS
   Problem: Services cannot reach each other
   Cause: Incorrect host names, port mappings, or network configuration
   Solution: Use service names in docker-compose, verify port exposure
   Test: docker exec container_name curl http://service_name:port

8. PERFORMANCE ISSUES
   Problem: Slow response times or timeouts
   Cause: Resource constraints, high concurrency, or model limitations
   Solution: Adjust SEMAPHORE_LIMIT, increase timeouts, monitor resources
   Monitor: docker stats to check CPU/memory usage

Debugging Commands:
• docker logs --tail 50 mcp_server-graphiti-mcp-1
• docker exec container_name printenv | grep -E "MODEL|NEO4J|OLLAMA"
• curl -s http://ollama-host:11434/api/tags
• python3 tests/reports/system_health_check.py
• Neo4j browser queries for data verification
            """,
            "source": "development_knowledge",
            "description": "Comprehensive troubleshooting guide for Graphiti MCP server development"
        },
        {
            "name": "deployment_and_scaling_insights",
            "content": """
DEPLOYMENT AND SCALING INSIGHTS FOR GRAPHITI MCP SERVERS

Production Deployment Patterns:

Docker Compose Configuration:
• Use secrets for sensitive environment variables (API keys, passwords)
• Configure resource limits: memory, CPU constraints for containers
• Implement health checks for all services (MCP server, Neo4j, Ollama)
• Use named volumes for persistent Neo4j data storage
• Set up log rotation and monitoring for container logs

Environment Management:
• Create environment-specific .env files (.env.dev, .env.prod, .env.test)
• Use strong passwords for Neo4j in production environments
• Implement proper secrets management (Docker secrets, K8s secrets)
• Configure backup strategies for Neo4j database
• Monitor disk usage for graph database growth

Performance Optimization:
• Tune SEMAPHORE_LIMIT based on available resources and model speed
• Configure Neo4j memory settings: heap size, page cache size
• Use SSD storage for Neo4j data directory for better I/O performance
• Monitor Ollama GPU utilization and adjust concurrent requests
• Implement connection pooling for database connections

Scaling Considerations:
• Neo4j clustering for high availability and read scaling
• Multiple Ollama instances behind load balancer for LLM scaling
• Horizontal scaling of MCP server instances with shared Neo4j backend
• Content delivery networks for static assets and documentation
• Message queuing for async processing of large episode batches

Security Best Practices:
• Network isolation between services using Docker networks
• Firewall rules restricting access to internal services
• Regular security updates for base images and dependencies
• Audit logging for all database and API operations
• Rate limiting for MCP endpoint access

Monitoring and Observability:
• Prometheus metrics for system performance monitoring
• Grafana dashboards for visualizing system health
• Log aggregation with ELK stack or similar
• Application performance monitoring (APM) for request tracing
• Custom health checks for business logic validation

Backup and Recovery:
• Automated Neo4j database backups with retention policies
• Configuration backup for environment variables and settings
• Container image versioning and rollback strategies
• Data migration scripts for schema updates
• Disaster recovery procedures and testing

Load Testing Insights:
• Test concurrent episode ingestion with realistic data volumes
• Validate search performance with large knowledge graphs
• Stress test Ollama model serving under high concurrency
• Monitor memory usage during large batch operations
• Test recovery behavior after service failures

Cost Optimization:
• Local processing eliminates external API costs completely
• Resource right-sizing based on actual usage patterns
• Scheduled scaling for predictable load patterns
• Storage optimization with data compression and archival
• GPU resource sharing for multiple Ollama model serving
            """,
            "source": "development_knowledge",
            "description": "Production deployment and scaling strategies for Graphiti MCP servers"
        },
        {
            "name": "advanced_development_techniques",
            "content": """
ADVANCED DEVELOPMENT TECHNIQUES FOR GRAPHITI MCP SYSTEMS

Custom Entity Type Development:
• Define domain-specific entity types extending BaseModel with Pydantic
• Implement custom validation rules for entity extraction
• Create specialized relationship types for domain knowledge
• Use entity type filtering for targeted search and retrieval
• Build entity hierarchies for complex domain modeling

Knowledge Graph Optimization:
• Design efficient graph schemas for specific use cases
• Implement graph algorithms for relationship discovery
• Use graph traversal patterns for contextual search
• Optimize index strategies for query performance
• Create materialized views for common query patterns

Advanced Search Implementations:
• Hybrid search combining semantic similarity and keyword matching
• Implement relevance scoring with custom algorithms
• Use graph-based ranking for relationship-aware search
• Create faceted search with multiple filter dimensions
• Build auto-complete and suggestion systems

Custom MCP Tool Development:
• Extend base MCP tools with domain-specific functionality
• Implement batch operations for bulk data processing
• Create specialized query tools for complex information retrieval
• Build analytics tools for knowledge graph insights
• Design workflow tools for multi-step AI assistant tasks

Integration Architecture Patterns:
• Multi-tenant systems with group-based data isolation
• Event-driven architectures with message streaming
• Microservices patterns for component separation
• API gateway patterns for unified access control
• Webhook systems for real-time data synchronization

Data Pipeline Development:
• ETL pipelines for importing external data sources
• Data validation and cleaning pipelines
• Incremental update systems for large datasets
• Conflict resolution algorithms for concurrent updates
• Data lineage tracking for audit and debugging

AI Model Integration:
• Custom embedding models for domain-specific content
• Fine-tuned LLMs for specialized entity extraction
• Multi-model systems with model routing and fallbacks
• Model versioning and A/B testing frameworks
• Performance monitoring for model drift detection

Testing and Quality Assurance:
• Property-based testing for graph operations
• Contract testing for MCP protocol compliance
• Performance testing with realistic data volumes
• Chaos engineering for system resilience testing
• Data quality monitoring and validation

Development Workflow Optimization:
• Local development environments with Docker Compose
• CI/CD pipelines with automated testing and deployment
• Code generation for MCP tool definitions
• Configuration management with environment templating
• Documentation generation from code annotations

Debugging and Profiling:
• Graph visualization tools for knowledge exploration
• Query profiling and optimization techniques
• Memory profiling for large graph operations
• Distributed tracing for multi-service debugging
• Custom logging strategies for complex workflows
            """,
            "source": "development_knowledge",
            "description": "Advanced development techniques and patterns for sophisticated Graphiti MCP systems"
        }
    ]
    
    # Create script content without template formatting issues
    script_content = '''
import sys
sys.path.insert(0, '/app/.venv/lib/python3.12/site-packages')

try:
    from neo4j import GraphDatabase
    import os
    import time
    import uuid
    import json
    
    uri = os.getenv('NEO4J_URI')
    user = os.getenv('NEO4J_USER')
    password = os.getenv('NEO4J_PASSWORD')
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    # Knowledge entries data
    knowledge_entries = ''' + json.dumps(knowledge_entries, indent=2) + '''
    
    saved_count = 0
    
    with driver.session() as session:
        print("🧠 Saving development knowledge entries...")
        
        for entry in knowledge_entries:
            now = int(time.time() * 1000)
            entry_uuid = str(uuid.uuid4())
            
            query = """
            CREATE (e:Episodic {
                uuid: $uuid,
                name: $name,
                content: $content,
                source: $source,
                source_description: $description,
                created_at: $created_at,
                valid_at: $valid_at,
                group_id: 'default'
            })
            RETURN e.uuid as episode_id
            """
            
            result = session.run(query, {
                'uuid': entry_uuid,
                'name': entry['name'],
                'content': entry['content'].strip(),
                'source': entry['source'],
                'description': entry['description'],
                'created_at': now,
                'valid_at': now
            })
            
            record = result.single()
            if record:
                saved_count += 1
                print(f"✅ Saved: {entry['name']}")
                print(f"   UUID: {entry_uuid}")
                print(f"   Content length: {len(entry['content'])} characters")
            else:
                print(f"❌ Failed to save: {entry['name']}")
        
        print(f"\\n📊 Knowledge Save Summary:")
        print(f"   Total entries: {len(knowledge_entries)}")
        print(f"   Successfully saved: {saved_count}")
        print(f"   Success rate: {saved_count/len(knowledge_entries)*100:.1f}%")
        
        # Verify searchability
        search_terms = ['Ollama', 'development', 'troubleshooting', 'deployment', 'best practices']
        print(f"\\n🔍 Verifying searchability:")
        
        for term in search_terms:
            result = session.run("""
                MATCH (e:Episodic) WHERE e.group_id = 'default'
                AND e.source = 'development_knowledge'
                AND toLower(e.content) CONTAINS toLower($term)
                RETURN count(e) as matches
            """, {'term': term})
            
            matches = result.single()['matches']
            print(f"   {term}: {matches} matches")
        
        # Get total count
        result = session.run("""
            MATCH (e:Episodic) WHERE e.group_id = 'default'
            RETURN count(e) as total
        """)
        total = result.single()['total']
        print(f"\\n📈 Total episodes in database: {total}")
    
    driver.close()
    print(f"\\n✅ Development knowledge successfully saved to MCP memory!")

except Exception as e:
    print(f"❌ Failed to save development knowledge: {e}")
    import traceback
    traceback.print_exc()
'''
    
    # Run script in container
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script_content)
        temp_file = f.name
    
    try:
        # Copy script to container
        success, stdout, stderr = run_docker_command([
            'docker', 'cp', temp_file, 
            'mcp_server-graphiti-mcp-1:/tmp/save_knowledge_fixed.py'
        ])
        
        if not success:
            print(f"❌ Failed to copy script: {stderr}")
            return False
        
        # Run script in container
        success, stdout, stderr = run_docker_command([
            'docker', 'exec', '--user', 'root', 'mcp_server-graphiti-mcp-1',
            'python3', '/tmp/save_knowledge_fixed.py'
        ], timeout=90)
        
        print(stdout)
        if stderr and "warning" not in stderr.lower():
            print(f"Stderr: {stderr}")
        
        return success and "successfully saved" in stdout
        
    finally:
        try:
            os.unlink(temp_file)
        except:
            pass

def main():
    print("🧠 SAVING DEVELOPMENT KNOWLEDGE TO MCP MEMORY")
    print("=" * 70)
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("Storing comprehensive development insights for future projects")
    
    # Check container
    success, stdout, stderr = run_docker_command([
        'docker', 'ps', '--filter', 'name=mcp_server-graphiti-mcp-1', 
        '--format', '{{.Status}}'
    ])
    
    if not success or "Up" not in stdout:
        print("❌ MCP server container is not running")
        return False
    
    print(f"✅ Container status: {stdout.strip()}")
    
    # Save knowledge
    save_success = save_development_knowledge()
    
    print("\\n" + "=" * 70)
    print("📋 DEVELOPMENT KNOWLEDGE STORAGE RESULTS")
    print("=" * 70)
    
    print(f"Save Knowledge:     {'✅ SUCCESS' if save_success else '❌ FAILED'}")
    
    if save_success:
        print("\\n🎉 DEVELOPMENT KNOWLEDGE SUCCESSFULLY SAVED!")
        print("✅ Ollama integration best practices stored")
        print("✅ Graphiti MCP development patterns documented")  
        print("✅ Comprehensive troubleshooting guide available")
        print("✅ Deployment and scaling insights preserved")
        print("✅ Advanced development techniques catalogued")
        
        print("\\n🔍 Knowledge Access Methods:")
        print("   • MCP search: Query for specific topics like 'Ollama troubleshooting'")
        print("   • Keyword search: 'best practices', 'deployment', 'performance'")
        print("   • Neo4j browser: Filter by source = 'development_knowledge'")
        print("   • AI assistant: Ask about specific development challenges")
        
        return True
    else:
        print("\\n❌ Failed to save development knowledge")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)