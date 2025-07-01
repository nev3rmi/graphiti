#!/usr/bin/env python3
"""
Add memory episodes to the MCP server and verify in Neo4j
"""

import json
import subprocess
import time
import uuid
from datetime import datetime

class MemoryTester:
    def __init__(self):
        self.container_name = "mcp_server-graphiti-mcp-1"
    
    def add_episode_via_docker(self, episode_data):
        """Add an episode using the running Docker container"""
        try:
            # Create the MCP request
            mcp_request = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/call",
                "params": {
                    "name": "add_episode",
                    "arguments": episode_data
                }
            }
            
            # Create a Python script to run inside the container
            script_content = f'''
import json
import asyncio
import sys
import os

# Set up environment
sys.path.insert(0, '/app')
os.environ["PYTHONPATH"] = "/app"

async def add_episode():
    try:
        from graphiti_core import Graphiti
        
        # Initialize Graphiti client with the same config as the server
        client = Graphiti(
            uri=os.environ.get("NEO4J_URI", "neo4j://192.168.31.150:7687"),
            user=os.environ.get("NEO4J_USER", "neo4j"), 
            password=os.environ.get("NEO4J_PASSWORD", "granite-life-bonanza-sunset-lagoon-1071"),
            model=os.environ.get("MODEL_NAME", "deepseek-r1:latest"),
            api_key=os.environ.get("OPENAI_API_KEY", "abc"),
            base_url=os.environ.get("OPENAI_BASE_URL", "http://192.168.31.134:11434/v1/"),
            embedder_model=os.environ.get("EMBEDDER_MODEL_NAME", "mxbai-embed-large:latest"),
            embedding_dim=int(os.environ.get("EMBEDDING_DIM", "1024")),
            group_id="default"
        )
        
        # Add the episode
        episode_data = {json.dumps(episode_data)}
        
        result = await client.add_episode(
            episode_data["data"],
            **episode_data["metadata"]
        )
        
        print(f"Episode added successfully: {{result}}")
        await client.close()
        
    except Exception as e:
        print(f"Error adding episode: {{e}}")
        import traceback
        traceback.print_exc()

# Run the async function
asyncio.run(add_episode())
'''
            
            # Write the script to a temporary file
            with open('/tmp/add_episode_script.py', 'w') as f:
                f.write(script_content)
            
            # Copy script to container
            subprocess.run([
                'docker', 'cp', '/tmp/add_episode_script.py', 
                f'{self.container_name}:/tmp/add_episode_script.py'
            ], check=True)
            
            # Run the script in the container
            result = subprocess.run([
                'docker', 'exec', self.container_name,
                'python3', '/tmp/add_episode_script.py'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"✅ Episode added: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ Failed to add episode: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error in add_episode_via_docker: {e}")
            return False
    
    def check_neo4j_data(self):
        """Check what data exists in Neo4j"""
        try:
            # Create a script to query Neo4j
            query_script = '''
import os
from neo4j import GraphDatabase

uri = os.environ.get("NEO4J_URI", "neo4j://192.168.31.150:7687")
user = os.environ.get("NEO4J_USER", "neo4j")
password = os.environ.get("NEO4J_PASSWORD", "granite-life-bonanza-sunset-lagoon-1071")

try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        # Count nodes
        result = session.run("MATCH (n) RETURN count(n) as node_count")
        node_count = result.single()["node_count"]
        print(f"Total nodes: {node_count}")
        
        # Count episodes
        result = session.run("MATCH (e:Episodic) RETURN count(e) as episode_count")
        episode_count = result.single()["episode_count"]
        print(f"Episodes: {episode_count}")
        
        # Count entities
        result = session.run("MATCH (e:Entity) RETURN count(e) as entity_count")
        entity_count = result.single()["entity_count"]
        print(f"Entities: {entity_count}")
        
        # Count relationships
        result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
        rel_count = result.single()["rel_count"]
        print(f"Relationships: {rel_count}")
        
        # Show some recent episodes
        print("\\nRecent episodes:")
        result = session.run("""
            MATCH (e:Episodic) 
            RETURN e.content, e.created_at, e.source 
            ORDER BY e.created_at DESC 
            LIMIT 5
        """)
        
        for record in result:
            content = record["e.content"][:100] + "..." if len(record["e.content"]) > 100 else record["e.content"]
            print(f"  - {content}")
            print(f"    Created: {record['e.created_at']}, Source: {record['e.source']}")
        
        # Show some entities
        print("\\nRecent entities:")
        result = session.run("""
            MATCH (e:Entity) 
            RETURN e.name, e.summary 
            ORDER BY e.created_at DESC 
            LIMIT 5
        """)
        
        for record in result:
            print(f"  - {record['e.name']}: {record['e.summary'][:80]}...")
    
    driver.close()
    print("\\n✅ Neo4j query completed successfully")
    
except Exception as e:
    print(f"❌ Neo4j query failed: {e}")
    import traceback
    traceback.print_exc()
'''
            
            # Write and run the query script
            with open('/tmp/query_neo4j.py', 'w') as f:
                f.write(query_script)
            
            subprocess.run([
                'docker', 'cp', '/tmp/query_neo4j.py',
                f'{self.container_name}:/tmp/query_neo4j.py'
            ], check=True)
            
            result = subprocess.run([
                'docker', 'exec', self.container_name,
                'python3', '/tmp/query_neo4j.py'
            ], capture_output=True, text=True, timeout=30)
            
            print("📊 Neo4j Database Status:")
            print(result.stdout)
            
            if result.stderr:
                print(f"Errors: {result.stderr}")
            
        except Exception as e:
            print(f"❌ Error checking Neo4j: {e}")

def main():
    print("💾 Adding Memory Episodes to Graphiti MCP Server")
    print("=" * 60)
    
    tester = MemoryTester()
    
    # Sample episodes to add
    episodes = [
        {
            "data": "Alice Johnson is a senior software engineer at TechCorp. She has 8 years of experience in Python development and specializes in machine learning applications. She recently led the development of a recommendation system that increased user engagement by 25%.",
            "metadata": {
                "source": "employee_profile",
                "timestamp": int(time.time()),
                "type": "profile_data"
            }
        },
        {
            "data": "Bob Wilson joined the AI research team last month. He has a PhD in Computer Science from MIT and previously worked at Google DeepMind. His expertise is in natural language processing and transformer architectures.",
            "metadata": {
                "source": "new_hire_info", 
                "timestamp": int(time.time()) + 1,
                "type": "profile_data"
            }
        },
        {
            "data": "Alice and Bob are collaborating on Project Phoenix, a new conversational AI system. The project aims to integrate advanced reasoning capabilities with real-time knowledge updates. The deadline is set for Q2 2024.",
            "metadata": {
                "source": "project_meeting",
                "timestamp": int(time.time()) + 2,
                "type": "project_info"
            }
        },
        {
            "data": "TechCorp has three main departments: Engineering (led by Sarah Kim), Research (led by Dr. Martinez), and Product (led by Mike Chen). The company focuses on AI-powered solutions for enterprise customers.",
            "metadata": {
                "source": "org_chart",
                "timestamp": int(time.time()) + 3,
                "type": "organizational_data"
            }
        },
        {
            "data": "The quarterly review meeting is scheduled for next Friday. Alice will present the recommendation system results, Bob will discuss the NLP research progress, and the team will plan the next phase of Project Phoenix.",
            "metadata": {
                "source": "meeting_schedule",
                "timestamp": int(time.time()) + 4,
                "type": "event_data"
            }
        }
    ]
    
    print("📝 Adding sample episodes...")
    
    for i, episode in enumerate(episodes, 1):
        print(f"\n--- Episode {i} ---")
        print(f"Content: {episode['data'][:80]}...")
        
        success = tester.add_episode_via_docker(episode)
        if success:
            print(f"✅ Episode {i} added successfully")
        else:
            print(f"❌ Episode {i} failed")
        
        # Wait between episodes to avoid overwhelming the system
        time.sleep(2)
    
    print("\n" + "=" * 60)
    print("🔍 Checking Neo4j Database...")
    
    # Wait a bit for processing
    time.sleep(5)
    
    # Check what's in Neo4j
    tester.check_neo4j_data()
    
    print("\n" + "=" * 60)
    print("🌐 Neo4j Browser Access:")
    print("URL: http://192.168.31.150:7474")
    print("Username: neo4j")
    print("Password: granite-life-bonanza-sunset-lagoon-1071")
    print()
    print("🔍 Useful Queries to run in Neo4j Browser:")
    print("1. View all nodes: MATCH (n) RETURN n LIMIT 25")
    print("2. View episodes: MATCH (e:Episodic) RETURN e")
    print("3. View entities: MATCH (e:Entity) RETURN e")
    print("4. View relationships: MATCH (a)-[r]->(b) RETURN a, r, b LIMIT 25")
    print("5. Search for Alice: MATCH (e) WHERE e.name CONTAINS 'Alice' RETURN e")

if __name__ == "__main__":
    main()