#!/usr/bin/env python3
"""
Add sample data directly to Neo4j to demonstrate the graph structure
"""

import subprocess
import time
import uuid
from datetime import datetime

def add_sample_data_to_neo4j():
    """Add sample data directly to Neo4j using Cypher queries"""
    
    print("💾 Adding Sample Data Directly to Neo4j")
    print("=" * 50)
    
    # Generate UUIDs and timestamps
    now = int(time.time() * 1000)  # milliseconds
    
    # Sample data as Cypher queries
    cypher_queries = [
        # Create episodes
        f"""
        CREATE (e1:Episodic {{
            uuid: '{uuid.uuid4()}',
            content: 'Alice Johnson is a senior software engineer at TechCorp. She has 8 years of experience in Python development and specializes in machine learning applications.',
            source: 'employee_profile',
            source_description: 'Employee profile data',
            created_at: {now},
            valid_at: {now},
            group_id: 'default'
        }})
        """,
        
        f"""
        CREATE (e2:Episodic {{
            uuid: '{uuid.uuid4()}',
            content: 'Bob Wilson joined the AI research team last month. He has a PhD in Computer Science from MIT and previously worked at Google DeepMind.',
            source: 'new_hire_info',
            source_description: 'New hire information',
            created_at: {now + 1000},
            valid_at: {now + 1000},
            group_id: 'default'
        }})
        """,
        
        f"""
        CREATE (e3:Episodic {{
            uuid: '{uuid.uuid4()}',
            content: 'Alice and Bob are collaborating on Project Phoenix, a new conversational AI system. The project deadline is Q2 2024.',
            source: 'project_meeting',
            source_description: 'Project meeting notes',
            created_at: {now + 2000},
            valid_at: {now + 2000},
            group_id: 'default'
        }})
        """,
        
        # Create entities
        f"""
        CREATE (alice:Entity {{
            uuid: '{uuid.uuid4()}',
            name: 'Alice Johnson',
            summary: 'Senior software engineer at TechCorp with 8 years of Python experience, specializing in machine learning applications.',
            entity_type: 'Person',
            created_at: {now},
            group_id: 'default'
        }})
        """,
        
        f"""
        CREATE (bob:Entity {{
            uuid: '{uuid.uuid4()}',
            name: 'Bob Wilson', 
            summary: 'AI researcher with PhD from MIT, previously at Google DeepMind, joined TechCorp AI research team.',
            entity_type: 'Person',
            created_at: {now + 1000},
            group_id: 'default'
        }})
        """,
        
        f"""
        CREATE (techcorp:Entity {{
            uuid: '{uuid.uuid4()}',
            name: 'TechCorp',
            summary: 'Technology company with Engineering, Research, and Product departments.',
            entity_type: 'Organization',
            created_at: {now},
            group_id: 'default'
        }})
        """,
        
        f"""
        CREATE (phoenix:Entity {{
            uuid: '{uuid.uuid4()}',
            name: 'Project Phoenix',
            summary: 'Conversational AI system project with Q2 2024 deadline.',
            entity_type: 'Project',
            created_at: {now + 2000},
            group_id: 'default'
        }})
        """,
        
        # Create relationships
        f"""
        MATCH (alice:Entity {{name: 'Alice Johnson'}}), (techcorp:Entity {{name: 'TechCorp'}})
        CREATE (alice)-[:RELATES_TO {{
            uuid: '{uuid.uuid4()}',
            name: 'works_at',
            fact: 'Alice Johnson works at TechCorp as a senior software engineer',
            created_at: {now},
            valid_at: {now},
            group_id: 'default'
        }}]->(techcorp)
        """,
        
        f"""
        MATCH (bob:Entity {{name: 'Bob Wilson'}}), (techcorp:Entity {{name: 'TechCorp'}})
        CREATE (bob)-[:RELATES_TO {{
            uuid: '{uuid.uuid4()}',
            name: 'works_at',
            fact: 'Bob Wilson works at TechCorp in the AI research team',
            created_at: {now + 1000},
            valid_at: {now + 1000},
            group_id: 'default'
        }}]->(techcorp)
        """,
        
        f"""
        MATCH (alice:Entity {{name: 'Alice Johnson'}}), (phoenix:Entity {{name: 'Project Phoenix'}})
        CREATE (alice)-[:RELATES_TO {{
            uuid: '{uuid.uuid4()}',
            name: 'works_on',
            fact: 'Alice Johnson is collaborating on Project Phoenix',
            created_at: {now + 2000},
            valid_at: {now + 2000},
            group_id: 'default'
        }}]->(phoenix)
        """,
        
        f"""
        MATCH (bob:Entity {{name: 'Bob Wilson'}}), (phoenix:Entity {{name: 'Project Phoenix'}})
        CREATE (bob)-[:RELATES_TO {{
            uuid: '{uuid.uuid4()}',
            name: 'works_on',
            fact: 'Bob Wilson is collaborating on Project Phoenix',
            created_at: {now + 2000},
            valid_at: {now + 2000},
            group_id: 'default'
        }}]->(phoenix)
        """,
        
        f"""
        MATCH (alice:Entity {{name: 'Alice Johnson'}}), (bob:Entity {{name: 'Bob Wilson'}})
        CREATE (alice)-[:RELATES_TO {{
            uuid: '{uuid.uuid4()}',
            name: 'collaborates_with',
            fact: 'Alice Johnson collaborates with Bob Wilson on Project Phoenix',
            created_at: {now + 2000},
            valid_at: {now + 2000},
            group_id: 'default'
        }}]->(bob)
        """
    ]
    
    # Create a Python script to execute the queries
    script_content = f'''
import sys
sys.path.insert(0, '/app/.venv/lib/python3.12/site-packages')

try:
    from neo4j import GraphDatabase
    import os
    
    uri = os.environ.get("NEO4J_URI", "neo4j://192.168.31.150:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "granite-life-bonanza-sunset-lagoon-1071")
    
    print(f"Connecting to Neo4j at: {{uri}}")
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    queries = {cypher_queries}
    
    with driver.session() as session:
        for i, query in enumerate(queries):
            try:
                print(f"Executing query {{i+1}}/{{len(queries)}}...")
                session.run(query)
                print(f"✅ Query {{i+1}} completed")
            except Exception as e:
                print(f"❌ Query {{i+1}} failed: {{e}}")
    
    # Verify the data
    print("\\n🔍 Verifying created data...")
    
    with driver.session() as session:
        # Count nodes
        result = session.run("MATCH (n) WHERE n.group_id = 'default' RETURN count(n) as count")
        total_nodes = result.single()["count"]
        print(f"Total nodes: {{total_nodes}}")
        
        # Count by type
        result = session.run("MATCH (e:Episodic) WHERE e.group_id = 'default' RETURN count(e) as count")
        episodes = result.single()["count"]
        print(f"Episodes: {{episodes}}")
        
        result = session.run("MATCH (e:Entity) WHERE e.group_id = 'default' RETURN count(e) as count")
        entities = result.single()["count"]
        print(f"Entities: {{entities}}")
        
        result = session.run("MATCH ()-[r:RELATES_TO]->() WHERE r.group_id = 'default' RETURN count(r) as count")
        relationships = result.single()["count"]
        print(f"Relationships: {{relationships}}")
        
        # Show entities
        print("\\n👥 Created Entities:")
        result = session.run("MATCH (e:Entity) WHERE e.group_id = 'default' RETURN e.name, e.summary ORDER BY e.name")
        for record in result:
            print(f"  - {{record['e.name']}}: {{record['e.summary'][:60]}}...")
    
    driver.close()
    print("\\n✅ Sample data added successfully!")
    
except Exception as e:
    print(f"❌ Failed to add sample data: {{e}}")
    import traceback
    traceback.print_exc()
'''
    
    # Write and execute the script
    with open('/tmp/add_sample_data.py', 'w') as f:
        f.write(script_content)
    
    try:
        # Copy to container
        subprocess.run([
            'docker', 'cp', '/tmp/add_sample_data.py',
            'mcp_server-graphiti-mcp-1:/tmp/add_sample_data.py'
        ], check=True)
        
        # Execute
        print("🚀 Executing data insertion...")
        result = subprocess.run([
            'docker', 'exec', 'mcp_server-graphiti-mcp-1',
            'python3', '/tmp/add_sample_data.py'
        ], capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Errors:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Failed to execute script: {e}")

def show_neo4j_browser_guide():
    """Show how to use Neo4j Browser"""
    
    print("\n" + "=" * 60)
    print("🌐 NEO4J BROWSER GUIDE")
    print("=" * 60)
    
    print("📍 Access Information:")
    print("URL: http://192.168.31.150:7474")
    print("Username: neo4j")
    print("Password: granite-life-bonanza-sunset-lagoon-1071")
    
    print("\n🔍 Useful Queries to Try:")
    
    queries = [
        ("View all nodes", "MATCH (n) RETURN n LIMIT 50"),
        ("View all episodes", "MATCH (e:Episodic) RETURN e"),
        ("View all entities", "MATCH (e:Entity) RETURN e"),
        ("View all relationships", "MATCH (a)-[r]->(b) RETURN a, r, b LIMIT 25"),
        ("Find Alice Johnson", "MATCH (p:Entity {name: 'Alice Johnson'}) RETURN p"),
        ("Find Alice's relationships", "MATCH (alice:Entity {name: 'Alice Johnson'})-[r]->(other) RETURN alice, r, other"),
        ("View the collaboration network", "MATCH (a:Entity)-[r:RELATES_TO]->(b:Entity) WHERE r.name = 'collaborates_with' RETURN a, r, b"),
        ("Search for TechCorp connections", "MATCH (tc:Entity {name: 'TechCorp'})<-[r]-(person) RETURN tc, r, person"),
        ("View Project Phoenix team", "MATCH (project:Entity {name: 'Project Phoenix'})<-[r]-(person) RETURN project, r, person")
    ]
    
    for i, (description, query) in enumerate(queries, 1):
        print(f"\n{i}. {description}:")
        print(f"   {query}")
    
    print("\n💡 Tips for Neo4j Browser:")
    print("• Click on nodes to see their properties")
    print("• Use the graph visualization to explore connections")
    print("• Try different layout options in the settings")
    print("• Use CTRL+Enter to execute queries")
    print("• The graph will show relationships as arrows between nodes")

def main():
    print("🎯 Creating Sample Memory Data for Neo4j Visualization")
    print("=" * 60)
    
    # Add sample data
    add_sample_data_to_neo4j()
    
    # Show how to use Neo4j Browser
    show_neo4j_browser_guide()

if __name__ == "__main__":
    main()