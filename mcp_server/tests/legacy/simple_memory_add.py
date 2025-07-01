#!/usr/bin/env python3
"""
Simple approach to add memory via the running MCP server
"""

import json
import subprocess
import time

def add_memory_via_logs():
    """Add memory by monitoring what the server does"""
    
    print("💾 Adding Memory to Graphiti MCP Server")
    print("=" * 50)
    
    # Sample data to add
    episodes = [
        "Alice Johnson works as a senior software engineer at TechCorp. She specializes in Python and machine learning.",
        "Bob Wilson is a new AI researcher who joined from Google DeepMind. He has expertise in NLP and transformers.",
        "Alice and Bob are working together on Project Phoenix, an advanced conversational AI system.",
        "TechCorp has three main departments: Engineering, Research, and Product.",
        "The quarterly review meeting is next Friday where Alice will present the recommendation system results."
    ]
    
    # Create a script that uses the MCP server's internal functionality
    script_content = '''
import asyncio
import sys
import os
import json

# Add the app directory to Python path
sys.path.insert(0, '/app')

async def test_memory():
    try:
        # Use the same approach as the MCP server
        import importlib.util
        spec = importlib.util.spec_from_file_location("mcp_server", "/app/graphiti_mcp_server.py")
        mcp_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mcp_module)
        
        # Get the graphiti client instance
        graphiti_client = mcp_module.graphiti_client
        
        if graphiti_client is None:
            print("❌ Graphiti client not initialized")
            return
        
        episodes = [
            "Alice Johnson works as a senior software engineer at TechCorp. She specializes in Python and machine learning.",
            "Bob Wilson is a new AI researcher who joined from Google DeepMind. He has expertise in NLP and transformers.", 
            "Alice and Bob are working together on Project Phoenix, an advanced conversational AI system.",
            "TechCorp has three main departments: Engineering, Research, and Product.",
            "The quarterly review meeting is next Friday where Alice will present the recommendation system results."
        ]
        
        for i, episode in enumerate(episodes):
            print(f"Adding episode {i+1}: {episode[:50]}...")
            
            try:
                result = await graphiti_client.add_episode(
                    episode,
                    source=f"memory_test_{i+1}",
                    source_description="Test memory addition"
                )
                print(f"✅ Episode {i+1} added successfully")
                await asyncio.sleep(1)  # Brief pause
                
            except Exception as e:
                print(f"❌ Episode {i+1} failed: {e}")
        
        print("\\n🔍 Checking what was added...")
        
        # Search for some of the added content
        try:
            results = await graphiti_client.search(
                query="Alice Johnson TechCorp",
                limit=5
            )
            
            print(f"Found {len(results.nodes)} nodes and {len(results.edges)} edges")
            
            for node in results.nodes[:3]:
                print(f"  Node: {node.name} - {node.summary[:60]}...")
                
        except Exception as e:
            print(f"Search failed: {e}")
            
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        import traceback
        traceback.print_exc()

# Run the test
asyncio.run(test_memory())
'''
    
    print("📝 Creating memory addition script...")
    
    # Write script to temp file
    with open('/tmp/memory_script.py', 'w') as f:
        f.write(script_content)
    
    # Copy to container
    try:
        subprocess.run([
            'docker', 'cp', '/tmp/memory_script.py',
            'mcp_server-graphiti-mcp-1:/tmp/memory_script.py'
        ], check=True)
        
        print("✅ Script copied to container")
        
        # Run the script
        print("🚀 Running memory addition...")
        result = subprocess.run([
            'docker', 'exec', 'mcp_server-graphiti-mcp-1',
            'python3', '/tmp/memory_script.py'
        ], capture_output=True, text=True, timeout=120)
        
        print("📄 Output:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Errors:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Failed to run memory script: {e}")

def check_neo4j_directly():
    """Check Neo4j using the native driver inside container"""
    
    print("\n🔍 Checking Neo4j Database...")
    
    query_script = '''
import sys
sys.path.insert(0, '/app/.venv/lib/python3.12/site-packages')

try:
    from neo4j import GraphDatabase
    import os
    
    uri = os.environ.get("NEO4J_URI", "neo4j://192.168.31.150:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "granite-life-bonanza-sunset-lagoon-1071")
    
    print(f"Connecting to: {uri}")
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        # Basic counts
        print("\\n📊 Database Statistics:")
        
        result = session.run("MATCH (n) RETURN count(n) as total")
        total = result.single()["total"]
        print(f"Total nodes: {total}")
        
        result = session.run("MATCH (e:Episodic) RETURN count(e) as episodes")
        episodes = result.single()["episodes"]
        print(f"Episodes: {episodes}")
        
        result = session.run("MATCH (e:Entity) RETURN count(e) as entities")
        entities = result.single()["entities"]
        print(f"Entities: {entities}")
        
        result = session.run("MATCH ()-[r]->() RETURN count(r) as relationships")
        relationships = result.single()["relationships"]
        print(f"Relationships: {relationships}")
        
        # Show recent data
        print("\\n📝 Recent Episodes:")
        result = session.run("""
            MATCH (e:Episodic) 
            WHERE e.group_id = 'default'
            RETURN e.content, e.created_at, e.source
            ORDER BY e.created_at DESC 
            LIMIT 5
        """)
        
        for record in result:
            content = record["e.content"][:80] + "..." if len(record["e.content"]) > 80 else record["e.content"]
            print(f"  - {content}")
            print(f"    Source: {record['e.source']}")
        
        print("\\n👥 Recent Entities:")
        result = session.run("""
            MATCH (e:Entity) 
            WHERE e.group_id = 'default'
            RETURN e.name, e.summary
            ORDER BY e.created_at DESC 
            LIMIT 5
        """)
        
        for record in result:
            summary = record["e.summary"][:60] + "..." if record["e.summary"] and len(record["e.summary"]) > 60 else record["e.summary"]
            print(f"  - {record['e.name']}: {summary}")
    
    driver.close()
    print("\\n✅ Neo4j check completed")
    
except Exception as e:
    print(f"❌ Neo4j check failed: {e}")
    import traceback
    traceback.print_exc()
'''
    
    with open('/tmp/neo4j_check.py', 'w') as f:
        f.write(query_script)
    
    try:
        subprocess.run([
            'docker', 'cp', '/tmp/neo4j_check.py',
            'mcp_server-graphiti-mcp-1:/tmp/neo4j_check.py'
        ], check=True)
        
        result = subprocess.run([
            'docker', 'exec', 'mcp_server-graphiti-mcp-1',
            'python3', '/tmp/neo4j_check.py'
        ], capture_output=True, text=True, timeout=30)
        
        print(result.stdout)
        
        if result.stderr:
            print("Errors:", result.stderr)
            
    except Exception as e:
        print(f"❌ Neo4j check failed: {e}")

def main():
    # First add some memory
    add_memory_via_logs()
    
    # Wait for processing
    print("\n⏳ Waiting for processing...")
    time.sleep(10)
    
    # Then check what's in Neo4j
    check_neo4j_directly()
    
    print("\n" + "=" * 50)
    print("🌐 Access Neo4j Browser:")
    print("URL: http://192.168.31.150:7474")
    print("Username: neo4j") 
    print("Password: granite-life-bonanza-sunset-lagoon-1071")
    print()
    print("🔍 Try these queries in Neo4j Browser:")
    print("MATCH (n) RETURN n LIMIT 25")
    print("MATCH (e:Episodic) RETURN e")
    print("MATCH (p:Entity {name: 'Alice Johnson'}) RETURN p")

if __name__ == "__main__":
    main()