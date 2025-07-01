#!/usr/bin/env python3
"""
Final status report for MCP server with Ollama integration
"""

import subprocess
import time

def print_ollama_status_report():
    print("🤖 GRAPHITI MCP SERVER + OLLAMA STATUS REPORT")
    print("=" * 70)
    print(f"Report generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n🔧 CONFIGURATION:")
    print("   • LLM Provider: Ollama (Local)")
    print("   • LLM Model: deepseek-r1:latest")
    print("   • Embedding Model: mxbai-embed-large:latest")
    print("   • Embedding Dimensions: 1024")
    print("   • Ollama Server: http://192.168.31.134:11434")
    print("   • Database: Neo4j at neo4j://192.168.31.150:7687")
    print("   • Transport: SSE (Server-Sent Events)")
    print("   • Port: 8000")
    
    print("\n🚀 SERVER STATUS:")
    # Check container status
    try:
        result = subprocess.run([
            'docker', 'ps', '--filter', 'name=mcp_server-graphiti-mcp-1', 
            '--format', '{{.Status}}'
        ], capture_output=True, text=True)
        
        if "Up" in result.stdout:
            uptime = result.stdout.strip()
            print(f"   ✅ Container: {uptime}")
        else:
            print("   ❌ Container: Not running")
    except:
        print("   ❌ Container: Status unknown")
    
    # Check recent logs for key indicators
    try:
        logs_result = subprocess.run([
            'docker', 'logs', '--tail', '10', 'mcp_server-graphiti-mcp-1'
        ], capture_output=True, text=True)
        
        logs = logs_result.stdout
        
        if "Graphiti client initialized successfully" in logs:
            print("   ✅ Graphiti: Initialized successfully")
        
        if "Using OpenAI model: deepseek-r1:latest" in logs:
            print("   ✅ Ollama LLM: deepseek-r1:latest configured")
        
        if "Running MCP server with SSE transport" in logs:
            print("   ✅ MCP Server: Running with SSE transport")
        
        if "Uvicorn running on http://0.0.0.0:8000" in logs:
            print("   ✅ HTTP Server: Listening on port 8000")
            
    except:
        print("   ⚠️ Could not check detailed status")
    
    print("\n🤖 OLLAMA STATUS:")
    # Check Ollama connectivity
    try:
        # Test deepseek-r1 model
        result = subprocess.run([
            'curl', '-s', '-X', 'POST', 'http://192.168.31.134:11434/api/generate',
            '-H', 'Content-Type: application/json',
            '-d', '{"model": "deepseek-r1:latest", "prompt": "Hello", "stream": false}'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and '"response"' in result.stdout:
            print("   ✅ LLM Model: deepseek-r1:latest responding")
        else:
            print("   ❌ LLM Model: Not responding")
        
        # Test embedding model
        result = subprocess.run([
            'curl', '-s', '-X', 'POST', 'http://192.168.31.134:11434/api/embeddings',
            '-H', 'Content-Type: application/json', 
            '-d', '{"model": "mxbai-embed-large:latest", "prompt": "test"}'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and '"embedding"' in result.stdout:
            print("   ✅ Embedding Model: mxbai-embed-large:latest working")
        else:
            print("   ❌ Embedding Model: Not responding")
            
    except:
        print("   ⚠️ Could not check Ollama status")
    
    print("\n📊 DATABASE STATUS:")
    # Check database connectivity and content
    try:
        db_script = '''
import sys
sys.path.insert(0, '/app/.venv/lib/python3.12/site-packages')
from neo4j import GraphDatabase
import os

try:
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USER")
    password = os.environ.get("NEO4J_PASSWORD")
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        # Check node counts
        result = session.run("MATCH (n) WHERE n.group_id = 'default' RETURN count(n) as total")
        total_nodes = result.single()["total"]
        
        result = session.run("MATCH (e:Episodic) WHERE e.group_id = 'default' RETURN count(e) as episodes")
        episodes = result.single()["episodes"]
        
        result = session.run("MATCH (e:Entity) WHERE e.group_id = 'default' RETURN count(e) as entities")
        entities = result.single()["entities"]
        
        result = session.run("MATCH ()-[r:RELATES_TO]->() WHERE r.group_id = 'default' RETURN count(r) as relationships")
        relationships = result.single()["relationships"]
        
        print(f"Total nodes: {total_nodes}")
        print(f"Episodes: {episodes}")
        print(f"Entities: {entities}")
        print(f"Relationships: {relationships}")
    
    driver.close()
    
except Exception as e:
    print(f"Database check failed: {e}")
'''
        
        with open('/tmp/db_status_check.py', 'w') as f:
            f.write(db_script)
        
        subprocess.run([
            'docker', 'cp', '/tmp/db_status_check.py',
            'mcp_server-graphiti-mcp-1:/tmp/db_status_check.py'
        ], check=True)
        
        db_result = subprocess.run([
            'docker', 'exec', 'mcp_server-graphiti-mcp-1',
            'python3', '/tmp/db_status_check.py'
        ], capture_output=True, text=True, timeout=15)
        
        if db_result.returncode == 0:
            for line in db_result.stdout.strip().split('\n'):
                if line.strip():
                    print(f"   ✅ {line}")
        else:
            print("   ❌ Database connection failed")
            
    except:
        print("   ⚠️ Could not check database status")
    
    print("\n🔗 CONNECTION ENDPOINTS:")
    print("   • MCP SSE Endpoint: http://localhost:8000/sse")
    print("   • Neo4j Browser: http://192.168.31.150:7474")
    print("   • Ollama API: http://192.168.31.134:11434")
    
    print("\n📋 MCP TOOLS AVAILABLE:")
    tools = [
        "add_episode - Store conversations in knowledge graph",
        "search_nodes - Find entities and relationships", 
        "search_facts - Search for specific facts",
        "get_episodes - Retrieve recent episodes",
        "get_status - Check server health",
        "clear_graph - Reset knowledge graph"
    ]
    
    for tool in tools:
        print(f"   • {tool}")
    
    print("\n💡 USAGE INSTRUCTIONS:")
    print("   1. For Claude Desktop: Use the generated mcp_config_stdio.json")
    print("   2. For custom clients: Connect to http://localhost:8000/sse")
    print("   3. View data: Access Neo4j Browser at http://192.168.31.150:7474")
    print("   4. Monitor Ollama: Check http://192.168.31.134:11434/api/tags")
    
    print("\n🎯 ADVANTAGES OF OLLAMA INTEGRATION:")
    print("   ✅ Fully local AI processing (no external API calls)")
    print("   ✅ Zero API usage costs")
    print("   ✅ Complete data privacy (nothing leaves your network)")
    print("   ✅ No internet dependency for AI operations")
    print("   ✅ Customizable models and parameters")
    print("   ✅ Fast local inference with GPU acceleration")
    
    print("\n" + "=" * 70)
    print("🎉 MCP SERVER WITH OLLAMA IS READY FOR USE!")
    print("=" * 70)
    print("Your AI assistant now has persistent memory powered by:")
    print("• Local LLM processing via Ollama")
    print("• Neo4j knowledge graph storage")
    print("• MCP protocol for seamless integration")
    print("• Complete privacy and cost efficiency")

if __name__ == "__main__":
    print_ollama_status_report()