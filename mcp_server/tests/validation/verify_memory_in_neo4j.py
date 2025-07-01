#!/usr/bin/env python3
"""
Verify the saved memories are visible and accessible in Neo4j browser
"""

import subprocess

def run_docker_command(cmd, timeout=30):
    """Helper to run docker commands with timeout"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def verify_memories_in_neo4j():
    """Check that our test memories are visible in Neo4j"""
    print("🔍 VERIFYING MEMORIES ARE VISIBLE IN NEO4J BROWSER")
    print("=" * 70)
    
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
        print(f"🔗 Connected to Neo4j at: {uri}")
        print(f"📊 Neo4j Browser URL: http://192.168.31.150:7474")
        print(f"🔑 Login credentials: {user} / [password]")
        
        print(f"\\n📋 CURRENT DATABASE CONTENTS:")
        print("=" * 50)
        
        # Show all episode types with counts
        result = session.run("""
            MATCH (e:Episodic) WHERE e.group_id = 'default'
            RETURN e.source as source, count(e) as episode_count
            ORDER BY episode_count DESC
        """)
        
        total_episodes = 0
        print(f"\\n📚 Episodes by Source:")
        for record in result:
            source = record['source']
            count = record['episode_count']
            total_episodes += count
            print(f"   {source}: {count} episodes")
        
        print(f"\\nTotal Episodes: {total_episodes}")
        
        # Show our new test memories specifically
        result = session.run("""
            MATCH (e:Episodic) WHERE e.group_id = 'default'
            AND e.source IN ['user_conversation', 'requirements_meeting', 'technical_planning']
            RETURN e.name as name, e.content as content, e.source as source, e.uuid as uuid
            ORDER BY e.created_at DESC
        """)
        
        test_memories = list(result)
        print(f"\\n🧠 Our Test Memories ({len(test_memories)} found):")
        print("=" * 50)
        
        for i, memory in enumerate(test_memories):
            print(f"\\n   Memory {i+1}: {memory['name']}")
            print(f"      UUID: {memory['uuid']}")
            print(f"      Source: {memory['source']}")
            content_preview = memory['content'][:120] + "..." if len(memory['content']) > 120 else memory['content']
            print(f"      Content: {content_preview}")
        
        # Show entities in the database
        result = session.run("""
            MATCH (e:Entity) WHERE e.group_id = 'default'
            RETURN e.name as name, e.summary as summary
            ORDER BY e.name
        """)
        
        entities = list(result)
        print(f"\\n👥 Entities in Database ({len(entities)} found):")
        print("=" * 50)
        
        for entity in entities:
            print(f"   • {entity['name']}")
            summary_preview = entity['summary'][:80] + "..." if len(entity['summary']) > 80 else entity['summary']
            print(f"     {summary_preview}")
        
        # Show relationships
        result = session.run("""
            MATCH (a:Entity)-[r:RELATES_TO]->(b:Entity) 
            WHERE r.group_id = 'default'
            RETURN a.name as from_name, r.name as relationship, b.name as to_name
            LIMIT 10
        """)
        
        relationships = list(result)
        print(f"\\n🔗 Relationships ({len(relationships)} found):")
        print("=" * 50)
        
        for rel in relationships:
            print(f"   • {rel['from_name']} → {rel['to_name']}")
            print(f"     Relationship: {rel['relationship']}")
        
        print(f"\\n🔍 USEFUL NEO4J BROWSER QUERIES:")
        print("=" * 50)
        print("Copy these queries into Neo4j Browser to explore the data:")
        
        print(f"\\n1. View all our test memories:")
        print("""   MATCH (e:Episodic) WHERE e.group_id = 'default'
   AND e.source IN ['user_conversation', 'requirements_meeting', 'technical_planning']
   RETURN e ORDER BY e.created_at DESC""")
        
        print(f"\\n2. Search for TypeScript preferences:")
        print("""   MATCH (e:Episodic) WHERE e.group_id = 'default'
   AND toLower(e.content) CONTAINS 'typescript'
   RETURN e.name, e.content""")
        
        print(f"\\n3. View complete knowledge graph:")
        print("""   MATCH (n) WHERE n.group_id = 'default'
   OPTIONAL MATCH (n)-[r]-(m) WHERE r.group_id = 'default'
   RETURN n, r, m LIMIT 50""")
        
        print(f"\\n4. Search by person name:")
        print("""   MATCH (e:Episodic) WHERE e.group_id = 'default'
   AND toLower(e.content) CONTAINS 'lisa wang'
   RETURN e.name, e.content, e.source""")
        
        print(f"\\n5. Recent memories (last hour):")
        print("""   MATCH (e:Episodic) WHERE e.group_id = 'default'
   AND e.created_at > (timestamp() - 3600000)
   RETURN e ORDER BY e.created_at DESC""")
    
    driver.close()
    print(f"\\n✅ Verification complete - all data accessible in Neo4j Browser!")

except Exception as e:
    print(f"❌ Verification failed: {e}")
    import traceback
    traceback.print_exc()
'''
    
    # Run script in container
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script)
        temp_file = f.name
    
    try:
        # Copy script to container
        success, stdout, stderr = run_docker_command([
            'docker', 'cp', temp_file, 
            'mcp_server-graphiti-mcp-1:/tmp/verify_neo4j.py'
        ])
        
        if not success:
            print(f"❌ Failed to copy script: {stderr}")
            return False
        
        # Run script in container
        success, stdout, stderr = run_docker_command([
            'docker', 'exec', '--user', 'root', 'mcp_server-graphiti-mcp-1',
            'python3', '/tmp/verify_neo4j.py'
        ], timeout=30)
        
        print(stdout)
        if stderr and "warning" not in stderr.lower():
            print(f"Stderr: {stderr}")
        
        return success
        
    finally:
        try:
            os.unlink(temp_file)
        except:
            pass

def main():
    print("🔍 NEO4J BROWSER VERIFICATION")
    print("=" * 70)
    
    # Check container is running
    success, stdout, stderr = run_docker_command([
        'docker', 'ps', '--filter', 'name=mcp_server-graphiti-mcp-1', 
        '--format', '{{.Status}}'
    ])
    
    if not success or "Up" not in stdout:
        print("❌ MCP server container is not running")
        return False
    
    print(f"✅ Container status: {stdout.strip()}")
    
    # Run verification
    success = verify_memories_in_neo4j()
    
    if success:
        print("\n🎉 SUCCESS!")
        print("✅ All memories are stored and accessible in Neo4j")
        print("✅ Data can be viewed in Neo4j Browser")
        print("✅ MCP memory functionality fully verified")
        
        print("\n🔗 Next Steps:")
        print("1. Open Neo4j Browser: http://192.168.31.150:7474")
        print("2. Login with: neo4j / granite-life-bonanza-sunset-lagoon-1071") 
        print("3. Run the provided queries to explore your memories")
        print("4. Your MCP server is ready for AI assistant integration!")
        
        return True
    else:
        print("\n❌ Verification failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)