#!/usr/bin/env python3
"""
Comprehensive system health check for Graphiti MCP Server with Ollama integration
"""

import subprocess
import time
import sys
import os

def run_command(cmd, timeout=30):
    """Helper to run commands with timeout"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_docker_container():
    """Check if MCP server container is running"""
    print("🐳 DOCKER CONTAINER STATUS")
    print("-" * 50)
    
    success, stdout, stderr = run_command([
        'docker', 'ps', '--filter', 'name=mcp_server-graphiti-mcp-1', 
        '--format', 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
    ])
    
    if success and "mcp_server-graphiti-mcp-1" in stdout:
        print("✅ Container running:")
        for line in stdout.strip().split('\n'):
            if line and not line.startswith('NAMES'):
                print(f"   {line}")
        return True
    else:
        print("❌ Container not running")
        return False

def check_ollama_connectivity():
    """Check Ollama server and models"""
    print("\n🤖 OLLAMA SERVER STATUS")
    print("-" * 50)
    
    # Test Ollama server connectivity
    success, stdout, stderr = run_command([
        'curl', '-s', '-m', '5', 'http://192.168.31.134:11434/api/tags'
    ], timeout=10)
    
    if success:
        print("✅ Ollama server accessible")
        
        # Test LLM model
        success, stdout, stderr = run_command([
            'curl', '-s', '-X', 'POST', 'http://192.168.31.134:11434/api/generate',
            '-H', 'Content-Type: application/json',
            '-d', '{"model": "deepseek-r1:latest", "prompt": "test", "stream": false}'
        ], timeout=15)
        
        if success and '"response"' in stdout:
            print("✅ LLM Model (deepseek-r1:latest) responding")
        else:
            print("❌ LLM Model not responding")
            return False
        
        # Test embedding model
        success, stdout, stderr = run_command([
            'curl', '-s', '-X', 'POST', 'http://192.168.31.134:11434/api/embeddings',
            '-H', 'Content-Type: application/json', 
            '-d', '{"model": "mxbai-embed-large:latest", "prompt": "test"}'
        ], timeout=15)
        
        if success and '"embedding"' in stdout:
            print("✅ Embedding Model (mxbai-embed-large:latest) responding")
            return True
        else:
            print("❌ Embedding Model not responding")
            return False
    else:
        print("❌ Ollama server not accessible")
        return False

def check_mcp_server_initialization():
    """Check MCP server logs for proper initialization"""
    print("\n🔧 MCP SERVER INITIALIZATION")
    print("-" * 50)
    
    success, stdout, stderr = run_command([
        'docker', 'logs', '--tail', '20', 'mcp_server-graphiti-mcp-1'
    ], timeout=10)
    
    if not success:
        print("❌ Unable to read server logs")
        return False
    
    logs = stdout
    checks = [
        ("Graphiti client initialized successfully", "Graphiti client"),
        ("Using OpenAI model: deepseek-r1:latest", "LLM model configured"),
        ("Running MCP server with SSE transport", "MCP transport active"),
        ("Uvicorn running on", "HTTP server running")
    ]
    
    passed = 0
    for check_text, description in checks:
        if check_text in logs:
            print(f"✅ {description}")
            passed += 1
        else:
            print(f"❌ {description} - not found in logs")
    
    return passed >= 3

def check_neo4j_database():
    """Check Neo4j database connectivity and data"""
    print("\n📊 NEO4J DATABASE STATUS")
    print("-" * 50)
    
    script = '''
import sys
sys.path.insert(0, '/app/.venv/lib/python3.12/site-packages')

try:
    from neo4j import GraphDatabase
    import os
    
    uri = os.getenv('NEO4J_URI')
    user = os.getenv('NEO4J_USER')
    password = os.getenv('NEO4J_PASSWORD')
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        # Test connectivity
        result = session.run("RETURN 1 as test")
        test_result = result.single()
        print("✅ Neo4j connectivity successful")
        
        # Check data counts
        result = session.run("MATCH (n) WHERE n.group_id = 'default' RETURN count(n) as total")
        total = result.single()["total"]
        
        result = session.run("MATCH (e:Episodic) WHERE e.group_id = 'default' RETURN count(e) as episodes")
        episodes = result.single()["episodes"]
        
        result = session.run("MATCH (e:Entity) WHERE e.group_id = 'default' RETURN count(e) as entities")
        entities = result.single()["entities"]
        
        result = session.run("MATCH ()-[r:RELATES_TO]->() WHERE r.group_id = 'default' RETURN count(r) as relationships")
        relationships = result.single()["relationships"]
        
        print(f"✅ Knowledge graph data:")
        print(f"   Total nodes: {total}")
        print(f"   Episodes: {episodes}")
        print(f"   Entities: {entities}")
        print(f"   Relationships: {relationships}")
        
        # Test write capability
        import time, uuid
        test_id = str(uuid.uuid4())
        now = int(time.time() * 1000)
        
        session.run(f"""
            CREATE (t:Test {{
                uuid: '{test_id}',
                content: 'Health check test',
                created_at: {now},
                group_id: 'default'
            }})
        """)
        
        # Clean up test node
        session.run(f"MATCH (t:Test {{uuid: '{test_id}'}}) DELETE t")
        print("✅ Database write/delete operations working")
        
    driver.close()
    
except Exception as e:
    print(f"❌ Neo4j database error: {e}")
'''
    
    return run_test_script(script)

def check_mcp_endpoints():
    """Check MCP server endpoints"""
    print("\n🔗 MCP SERVER ENDPOINTS")
    print("-" * 50)
    
    # Test SSE endpoint
    success, stdout, stderr = run_command([
        'curl', '-s', '-m', '3', 'http://localhost:8000/sse'
    ], timeout=5)
    
    # For SSE, timeout is expected behavior
    if success or "28" in str(success):
        print("✅ SSE endpoint accessible (http://localhost:8000/sse)")
        return True
    else:
        print("❌ SSE endpoint not accessible")
        return False

def run_test_script(script_content):
    """Helper to run a script inside the container"""
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script_content)
        temp_file = f.name
    
    try:
        # Copy script to container
        success, stdout, stderr = run_command([
            'docker', 'cp', temp_file, 
            'mcp_server-graphiti-mcp-1:/tmp/health_check.py'
        ])
        
        if not success:
            return False
        
        # Run script in container
        success, stdout, stderr = run_command([
            'docker', 'exec', '--user', 'root', 'mcp_server-graphiti-mcp-1',
            'python3', '/tmp/health_check.py'
        ], timeout=30)
        
        print(stdout)
        if stderr and "warning" not in stderr.lower():
            print(f"Error: {stderr}")
        
        return success and "✅" in stdout
        
    finally:
        try:
            os.unlink(temp_file)
        except:
            pass

def main():
    print("🏥 GRAPHITI MCP SERVER SYSTEM HEALTH CHECK")
    print("=" * 70)
    print(f"Health check started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"System: Ollama + Neo4j + MCP Server Integration")
    
    # Run all health checks
    checks = [
        ("Docker Container", check_docker_container),
        ("Ollama Connectivity", check_ollama_connectivity),
        ("MCP Server Init", check_mcp_server_initialization),
        ("Neo4j Database", check_neo4j_database),
        ("MCP Endpoints", check_mcp_endpoints)
    ]
    
    results = {}
    for check_name, check_function in checks:
        try:
            results[check_name] = check_function()
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {e}")
            results[check_name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 HEALTH CHECK SUMMARY")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ HEALTHY" if result else "❌ FAILED"
        print(f"{check_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall Health: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 SYSTEM IS FULLY HEALTHY!")
        print("✅ All components operational")
        print("✅ MCP server ready for AI assistant integration")
        print("✅ Ollama integration working perfectly")
        print("✅ Knowledge graph functional")
        
        print("\n🔗 Integration Ready:")
        print("   • SSE Endpoint: http://localhost:8000/sse")
        print("   • Neo4j Browser: http://192.168.31.150:7474")
        print("   • Ollama API: http://192.168.31.134:11434")
        
        return 0
    
    elif passed >= 3:
        print("\n⚠️ SYSTEM MOSTLY HEALTHY")
        print(f"✅ {passed} out of {total} checks passed")
        print("🔧 Some components may need attention")
        
        return 1
    
    else:
        print("\n❌ SYSTEM NEEDS ATTENTION")
        print(f"Only {passed} out of {total} checks passed")
        print("🚨 Multiple components require fixing")
        
        return 2

if __name__ == "__main__":
    sys.exit(main())