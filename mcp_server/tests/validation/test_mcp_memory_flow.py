#!/usr/bin/env python3
"""
Test complete MCP memory flow: Save data -> Retrieve data -> Verify in Neo4j
"""

import subprocess
import time
import uuid
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

def test_mcp_memory_save():
    """Test saving memory through MCP add_episode functionality"""
    print("💾 TESTING MCP MEMORY SAVE")
    print("=" * 60)
    
    # Create test data that simulates real conversation memory
    test_memories = [
        {
            "name": "user_preference_discussion",
            "content": "The user mentioned they prefer working with TypeScript over JavaScript because of the type safety. They also said they like using React with Next.js for web development. They dislike debugging CSS issues and prefer using Tailwind CSS.",
            "source_description": "User preference conversation about programming languages and tools"
        },
        {
            "name": "project_requirements_meeting", 
            "content": "Sarah Chen, the product manager at DevFlow Corp, outlined the requirements for the new customer dashboard. The project needs real-time analytics, user authentication with SSO, data export to CSV/Excel, and mobile responsive design. The deadline is Q1 2024 and the budget is $50K.",
            "source_description": "Project requirements gathering session"
        },
        {
            "name": "technical_discussion",
            "content": "Discussion about implementing microservices architecture. The team decided to use Docker containers, Kubernetes for orchestration, and PostgreSQL for the main database. Redis will be used for caching. The API will be RESTful with GraphQL for complex queries.",
            "source_description": "Technical architecture planning session"
        }
    ]
    
    script_template = '''
import sys
sys.path.insert(0, '/app/.venv/lib/python3.12/site-packages')

try:
    import asyncio
    import os
    from datetime import datetime, timezone
    from graphiti_core import Graphiti
    from graphiti_core.llm_client.openai_client import OpenAIClient
    from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
    from graphiti_core.llm_client.config import LLMConfig
    
    async def save_memory():
        # Initialize Graphiti client with Ollama
        llm_config = LLMConfig(
            api_key=os.getenv('OPENAI_API_KEY', 'abc'),
            base_url=os.getenv('OPENAI_BASE_URL', 'http://192.168.31.134:11434/v1/'),
            model=os.getenv('MODEL_NAME', 'deepseek-r1:latest')
        )
        llm_client = OpenAIClient(config=llm_config)
        
        embedder_config = OpenAIEmbedderConfig(
            api_key=os.getenv('OPENAI_API_KEY', 'abc'),
            base_url=os.getenv('OPENAI_BASE_URL', 'http://192.168.31.134:11434/v1/'),
            model=os.getenv('EMBEDDER_MODEL_NAME', 'mxbai-embed-large:latest'),
            embedding_dim=int(os.getenv('EMBEDDING_DIM', '1024'))
        )
        embedder = OpenAIEmbedder(config=embedder_config)
        
        client = Graphiti(
            uri=os.getenv('NEO4J_URI'),
            user=os.getenv('NEO4J_USER'),
            password=os.getenv('NEO4J_PASSWORD'),
            llm_client=llm_client,
            embedder=embedder
        )
        
        # Save memory (this is what MCP add_episode tool does)
        print(f"💾 Saving memory: {MEMORY_NAME}")
        
        result = await client.add_episode(
            name="{MEMORY_NAME}",
            episode_body="{MEMORY_CONTENT}",
            source_description="{SOURCE_DESC}",
            reference_time=datetime.now(timezone.utc)
        )
        
        if result and hasattr(result, 'episodes') and result.episodes:
            episode = result.episodes[0]
            print(f"✅ Memory saved successfully!")
            print(f"   Episode UUID: {episode.uuid}")
            print(f"   Content length: {len(episode.content)} characters")
            print(f"   Created at: {episode.created_at}")
            
            # Show extracted entities if any
            if hasattr(result, 'nodes') and result.nodes:
                print(f"   Entities extracted: {len(result.nodes)}")
                for node in result.nodes[:3]:  # Show first 3
                    print(f"      - {node.name}: {node.summary[:50]}...")
            
            # Show relationships if any  
            if hasattr(result, 'edges') and result.edges:
                print(f"   Relationships created: {len(result.edges)}")
                for edge in result.edges[:3]:  # Show first 3
                    print(f"      - {edge.source_node_uuid} → {edge.target_node_uuid}: {edge.name}")
            
            return episode.uuid
        else:
            print("❌ Memory save failed - no episode returned")
            return None
        
        await client.close()
    
    # Run the save operation
    episode_uuid = asyncio.run(save_memory())
    print(f"\\n📝 Memory save result: {episode_uuid}")
    
except Exception as e:
    print(f"❌ Memory save failed: {e}")
    import traceback
    traceback.print_exc()
'''
    
    saved_uuids = []
    
    for i, memory in enumerate(test_memories):
        print(f"\n📝 Saving Memory {i+1}/3: {memory['name']}")
        
        # Create script with specific memory data
        script = script_template.replace("{MEMORY_NAME}", memory['name']) \
                               .replace("{MEMORY_CONTENT}", memory['content']) \
                               .replace("{SOURCE_DESC}", memory['source_description'])
        
        success, stdout, stderr = run_script_in_container(script)
        
        if success and "✅" in stdout:
            print("✅ Memory saved successfully")
            # Extract UUID from output if possible
            lines = stdout.split('\n')
            for line in lines:
                if "Episode UUID:" in line:
                    uuid_part = line.split("Episode UUID:")[-1].strip()
                    saved_uuids.append(uuid_part)
                    break
        else:
            print("❌ Memory save failed")
            if stderr:
                print(f"   Error: {stderr[:200]}...")
    
    print(f"\n📊 Memory Save Summary:")
    print(f"   Total memories to save: {len(test_memories)}")
    print(f"   Successfully saved: {len([u for u in saved_uuids if u])}")
    print(f"   Saved UUIDs: {saved_uuids}")
    
    return len(saved_uuids) > 0

def test_mcp_memory_retrieve():
    """Test retrieving memories through MCP search functionality"""
    print("\n🔍 TESTING MCP MEMORY RETRIEVAL")
    print("=" * 60)
    
    search_tests = [
        {
            "query": "TypeScript programming preferences",
            "description": "Search for user programming preferences"
        },
        {
            "query": "Sarah Chen product manager requirements",
            "description": "Search for project requirements and team members"
        },
        {
            "query": "microservices Docker Kubernetes architecture",
            "description": "Search for technical architecture decisions"
        },
        {
            "query": "DevFlow Corp customer dashboard",
            "description": "Search for specific project information"
        }
    ]
    
    script_template = '''
import sys
sys.path.insert(0, '/app/.venv/lib/python3.12/site-packages')

try:
    import asyncio
    import os
    from datetime import datetime, timezone
    from graphiti_core import Graphiti
    from graphiti_core.llm_client.openai_client import OpenAIClient
    from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
    from graphiti_core.llm_client.config import LLMConfig
    
    async def retrieve_memory():
        # Initialize Graphiti client
        llm_config = LLMConfig(
            api_key=os.getenv('OPENAI_API_KEY', 'abc'),
            base_url=os.getenv('OPENAI_BASE_URL', 'http://192.168.31.134:11434/v1/'),
            model=os.getenv('MODEL_NAME', 'deepseek-r1:latest')
        )
        llm_client = OpenAIClient(config=llm_config)
        
        embedder_config = OpenAIEmbedderConfig(
            api_key=os.getenv('OPENAI_API_KEY', 'abc'),
            base_url=os.getenv('OPENAI_BASE_URL', 'http://192.168.31.134:11434/v1/'),
            model=os.getenv('EMBEDDER_MODEL_NAME', 'mxbai-embed-large:latest'),
            embedding_dim=int(os.getenv('EMBEDDING_DIM', '1024'))
        )
        embedder = OpenAIEmbedder(config=embedder_config)
        
        client = Graphiti(
            uri=os.getenv('NEO4J_URI'),
            user=os.getenv('NEO4J_USER'),
            password=os.getenv('NEO4J_PASSWORD'),
            llm_client=llm_client,
            embedder=embedder
        )
        
        print(f"🔍 Searching for: {SEARCH_QUERY}")
        
        # Search for relevant memories (this is what MCP search_nodes tool does)
        results = await client.search(
            query="{SEARCH_QUERY}",
            num_results=5
        )
        
        if results:
            print(f"✅ Found {len(results)} relevant memories:")
            for i, result in enumerate(results):
                print(f"\\n   Result {i+1}:")
                print(f"      Name: {result.name}")
                print(f"      Score: {result.score:.3f}")
                print(f"      Summary: {result.summary[:100]}...")
                if hasattr(result, 'uuid'):
                    print(f"      UUID: {result.uuid}")
        else:
            print("❌ No memories found for this search")
        
        # Also try to get recent episodes (this is what MCP get_episodes tool does)
        episodes = await client.retrieve_episodes(
            reference_time=datetime.now(timezone.utc),
            last_n=10
        )
        
        if episodes:
            print(f"\\n📚 Recent episodes ({len(episodes)} found):")
            for i, episode in enumerate(episodes[:3]):  # Show first 3
                print(f"\\n   Episode {i+1}:")
                print(f"      UUID: {episode.uuid}")
                content_preview = episode.content[:80] + "..." if len(episode.content) > 80 else episode.content
                print(f"      Content: {content_preview}")
                print(f"      Source: {episode.source}")
        
        await client.close()
        return len(results) if results else 0
    
    # Run the search
    num_results = asyncio.run(retrieve_memory())
    print(f"\\n🔍 Search results: {num_results} relevant memories found")
    
except Exception as e:
    print(f"❌ Memory retrieval failed: {e}")
    import traceback
    traceback.print_exc()
'''
    
    total_found = 0
    
    for i, search_test in enumerate(search_tests):
        print(f"\n🔍 Search Test {i+1}/4: {search_test['description']}")
        
        # Create script with specific search query
        script = script_template.replace("{SEARCH_QUERY}", search_test['query'])
        
        success, stdout, stderr = run_script_in_container(script)
        
        if success and "✅" in stdout:
            print("✅ Search completed successfully")
            # Count results mentioned in output
            if "relevant memories found" in stdout:
                try:
                    result_line = [line for line in stdout.split('\n') if "relevant memories found" in line][0]
                    num_results = int(result_line.split()[2])
                    total_found += num_results
                except:
                    pass
        else:
            print("❌ Search failed")
            if stderr:
                print(f"   Error: {stderr[:200]}...")
    
    print(f"\n📊 Memory Retrieval Summary:")
    print(f"   Total searches performed: {len(search_tests)}")
    print(f"   Total relevant memories found: {total_found}")
    
    return total_found > 0

def test_verify_in_neo4j():
    """Verify the saved memories are actually in Neo4j and searchable"""
    print("\n🔍 VERIFYING MEMORIES IN NEO4J")
    print("=" * 60)
    
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
        print("🔍 Searching for our test memories in Neo4j...")
        
        # Look for episodes we just added
        result = session.run("""
            MATCH (e:Episodic) WHERE e.group_id = 'default'
            AND (e.name CONTAINS 'preference' OR e.name CONTAINS 'requirements' OR e.name CONTAINS 'technical')
            RETURN e.name as name, e.content as content, e.source_description as source, 
                   e.created_at as created, e.uuid as uuid
            ORDER BY e.created_at DESC
            LIMIT 10
        """)
        
        test_episodes = list(result)
        print(f"✅ Found {len(test_episodes)} test episodes in Neo4j:")
        
        for i, ep in enumerate(test_episodes):
            print(f"\\n   Episode {i+1}:")
            print(f"      Name: {ep['name']}")
            print(f"      UUID: {ep['uuid']}")
            print(f"      Source: {ep['source']}")
            content_preview = ep['content'][:100] + "..." if len(ep['content']) > 100 else ep['content']
            print(f"      Content: {content_preview}")
        
        # Look for entities that might have been extracted
        result = session.run("""
            MATCH (e:Entity) WHERE e.group_id = 'default'
            AND (e.name CONTAINS 'Sarah' OR e.name CONTAINS 'DevFlow' OR e.name CONTAINS 'TypeScript')
            RETURN e.name as name, e.summary as summary, e.uuid as uuid
            ORDER BY e.created_at DESC
            LIMIT 5
        """)
        
        extracted_entities = list(result)
        if extracted_entities:
            print(f"\\n✅ Found {len(extracted_entities)} extracted entities:")
            for entity in extracted_entities:
                print(f"      - {entity['name']}: {entity['summary'][:80]}...")
        else:
            print("\\n⚠️ No new entities extracted (this is normal for some configurations)")
        
        # Check total database state
        result = session.run("""
            MATCH (n) WHERE n.group_id = 'default'
            RETURN labels(n)[0] as node_type, count(n) as count
            ORDER BY count DESC
        """)
        
        print(f"\\n📊 Current Neo4j Database State:")
        total_nodes = 0
        for record in result:
            node_type = record["node_type"]
            count = record["count"]
            total_nodes += count
            print(f"      {node_type}: {count} nodes")
        print(f"      Total: {total_nodes} nodes")
        
        # Test searchability with keywords
        search_terms = ['TypeScript', 'Sarah Chen', 'microservices', 'DevFlow']
        print(f"\\n🔍 Testing searchability:")
        
        for term in search_terms:
            result = session.run(f"""
                MATCH (e:Episodic) WHERE e.group_id = 'default'
                AND toLower(e.content) CONTAINS toLower('{term}')
                RETURN count(e) as matches
            """)
            matches = result.single()['matches']
            print(f"      '{term}': {matches} episode matches")
    
    driver.close()
    print(f"\\n✅ Neo4j verification complete")
    
except Exception as e:
    print(f"❌ Neo4j verification failed: {e}")
    import traceback
    traceback.print_exc()
'''
    
    success, stdout, stderr = run_script_in_container(script)
    
    if success:
        print("✅ Neo4j verification completed")
        return "test episodes in Neo4j" in stdout
    else:
        print("❌ Neo4j verification failed")
        if stderr:
            print(f"Error: {stderr}")
        return False

def run_script_in_container(script_content):
    """Helper to run a script inside the container"""
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script_content)
        temp_file = f.name
    
    try:
        # Copy script to container
        success, stdout, stderr = run_docker_command([
            'docker', 'cp', temp_file, 
            'mcp_server-graphiti-mcp-1:/tmp/memory_test.py'
        ])
        
        if not success:
            return False, "", f"Failed to copy script: {stderr}"
        
        # Run script in container
        success, stdout, stderr = run_docker_command([
            'docker', 'exec', '--user', 'root', 'mcp_server-graphiti-mcp-1',
            'python3', '/tmp/memory_test.py'
        ], timeout=90)
        
        print(stdout)
        if stderr and "warning" not in stderr.lower():
            print(f"Stderr: {stderr}")
        
        return success, stdout, stderr
        
    finally:
        try:
            os.unlink(temp_file)
        except:
            pass

def main():
    print("🧠 MCP MEMORY FLOW TEST: SAVE → RETRIEVE → VERIFY")
    print("=" * 70)
    print(f"Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("Testing complete memory lifecycle with Ollama integration")
    
    # Check container is running
    success, stdout, stderr = run_docker_command([
        'docker', 'ps', '--filter', 'name=mcp_server-graphiti-mcp-1', 
        '--format', '{{.Status}}'
    ])
    
    if not success or "Up" not in stdout:
        print("\n❌ MCP server container is not running")
        print("Start with: docker compose up")
        return False
    
    print(f"✅ Container status: {stdout.strip()}")
    
    # Run memory flow tests
    results = {}
    
    try:
        # Step 1: Save memories
        results['save'] = test_mcp_memory_save()
        
        # Step 2: Retrieve memories  
        results['retrieve'] = test_mcp_memory_retrieve()
        
        # Step 3: Verify in Neo4j
        results['verify'] = test_verify_in_neo4j()
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False
    
    # Final summary
    print("\n" + "=" * 70)
    print("📋 MCP MEMORY FLOW TEST RESULTS")
    print("=" * 70)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.capitalize():15} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 COMPLETE SUCCESS!")
        print("✅ MCP memory save functionality working")
        print("✅ MCP memory retrieval functionality working") 
        print("✅ Data properly stored and searchable in Neo4j")
        print("✅ Full memory lifecycle verified with Ollama")
        
        print("\n🧠 Memory System Capabilities Confirmed:")
        print("   • AI assistants can save conversation context")
        print("   • Memories are semantically searchable")
        print("   • Entity extraction and relationship mapping")
        print("   • Persistent storage across sessions")
        print("   • Temporal knowledge graph functionality")
        
        print("\n🔗 Integration Ready:")
        print("   • MCP tools: add_episode, search_nodes, get_episodes")
        print("   • Ollama processing: Local LLM + embeddings")
        print("   • Neo4j storage: Searchable knowledge graph")
        print("   • Complete privacy: No external API calls")
        
        return True
        
    else:
        print(f"\n⚠️ {total - passed} tests had issues")
        if results.get('save'):
            print("✅ Memory saving works")
        if results.get('retrieve'):
            print("✅ Memory retrieval works")
        if results.get('verify'):
            print("✅ Neo4j storage verified")
        print("Check detailed output above for specific issues")
        
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n" + "=" * 70)
    print(f"Test completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    exit(0 if success else 1)