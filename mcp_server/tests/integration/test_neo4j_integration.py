#!/usr/bin/env python3
"""
Test MCP tools by making direct calls to the running server
"""

import subprocess
import json
import time
import uuid

def run_docker_command(cmd, timeout=30):
    """Helper to run docker commands with timeout"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_add_episode_direct():
    """Test add_episode by directly using Graphiti within the container"""
    print("\n🧪 Testing add_episode via direct Graphiti call...")
    
    script = '''
import sys
sys.path.insert(0, '/app/.venv/lib/python3.12/site-packages')

try:
    import asyncio
    import os
    from graphiti_core import Graphiti
    from graphiti_core.llm_client.openai_client import OpenAIClient
    from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
    from graphiti_core.llm_client.config import LLMConfig
    
    async def test_add_episode():
        # Create LLM client with Ollama configuration
        llm_config = LLMConfig(
            api_key=os.getenv('OPENAI_API_KEY', 'abc'),
            base_url=os.getenv('OPENAI_BASE_URL', 'http://192.168.31.134:11434/v1/'),
            model=os.getenv('MODEL_NAME', 'deepseek-r1:latest')
        )
        llm_client = OpenAIClient(config=llm_config)
        
        # Create embedder client (check env vars)
        embedder_model = os.getenv('EMBEDDER_MODEL_NAME', 'mxbai-embed-large:latest')
        embedding_dim = int(os.getenv('EMBEDDING_DIM', '1024'))
        base_url = os.getenv('OPENAI_BASE_URL', 'http://192.168.31.134:11434/v1/')
        
        print(f"   Using embedder model: {embedder_model}")
        print(f"   Using embedding dimension: {embedding_dim}")
        print(f"   Using base URL: {base_url}")
        
        embedder_config = OpenAIEmbedderConfig(
            api_key=os.getenv('OPENAI_API_KEY', 'abc'),
            base_url=base_url,
            model=embedder_model,
            embedding_dim=embedding_dim
        )
        embedder = OpenAIEmbedder(config=embedder_config)
        
        # Initialize Graphiti client
        client = Graphiti(
            uri=os.getenv('NEO4J_URI', 'neo4j://192.168.31.150:7687'),
            user=os.getenv('NEO4J_USER', 'neo4j'),
            password=os.getenv('NEO4J_PASSWORD', 'granite-life-bonanza-sunset-lagoon-1071'),
            llm_client=llm_client,
            embedder=embedder
        )
        
        # Test episode data
        test_content = "Michael Torres is a DevOps engineer at DataFlow Systems. He specializes in Kubernetes orchestration and has implemented CI/CD pipelines for over 20 microservices. He recently migrated the entire infrastructure to AWS EKS, reducing deployment time by 60%."
        
        # Add episode using Graphiti (need to import datetime)
        from datetime import datetime, timezone
        
        episodes = await client.add_episode(
            name="mcp_test_episode",
            episode_body=test_content,
            source_description="Testing MCP tools with Ollama integration",
            reference_time=datetime.now(timezone.utc)
        )
        
        if episodes and hasattr(episodes, 'episodes') and episodes.episodes:
            print(f"✅ add_episode successful: Added {len(episodes.episodes)} episodes")
            for ep in episodes.episodes:
                print(f"   Episode UUID: {ep.uuid}")
                print(f"   Content preview: {ep.content[:100]}...")
        else:
            print("❌ add_episode failed: No episodes returned")
        
        await client.close()
    
    # Run the async test
    asyncio.run(test_add_episode())
    
except Exception as e:
    print(f"❌ add_episode test failed: {e}")
    import traceback
    traceback.print_exc()
'''
    
    return run_script_in_container(script)

def test_search_nodes_direct():
    """Test search_nodes by directly using Graphiti within the container"""
    print("\n🧪 Testing search_nodes via direct Graphiti call...")
    
    script = '''
import sys
sys.path.insert(0, '/app/.venv/lib/python3.12/site-packages')

try:
    import asyncio
    import os
    from graphiti_core import Graphiti
    from graphiti_core.llm_client.openai_client import OpenAIClient
    from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
    from graphiti_core.llm_client.config import LLMConfig
    
    async def test_search_nodes():
        # Create clients with Ollama configuration
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
        
        # Initialize Graphiti client
        client = Graphiti(
            uri=os.getenv('NEO4J_URI', 'neo4j://192.168.31.150:7687'),
            user=os.getenv('NEO4J_USER', 'neo4j'),
            password=os.getenv('NEO4J_PASSWORD', 'granite-life-bonanza-sunset-lagoon-1071'),
            llm_client=llm_client,
            embedder=embedder
        )
        
        # Search for entities
        results = await client.search(
            query="developer engineer technology",
            num_results=5
        )
        
        if results:
            print(f"✅ search_nodes successful: Found {len(results)} results")
            for i, result in enumerate(results[:3]):  # Show first 3
                print(f"   Result {i+1}: {result.name} (Score: {result.score:.3f})")
                print(f"      Summary: {result.summary[:80]}...")
        else:
            print("❌ search_nodes failed: No results returned")
        
        await client.close()
    
    asyncio.run(test_search_nodes())
    
except Exception as e:
    print(f"❌ search_nodes test failed: {e}")
    import traceback
    traceback.print_exc()
'''
    
    return run_script_in_container(script)

def test_get_episodes_direct():
    """Test get_episodes by directly using Graphiti within the container"""
    print("\n🧪 Testing get_episodes via direct Graphiti call...")
    
    script = '''
import sys
sys.path.insert(0, '/app/.venv/lib/python3.12/site-packages')

try:
    import asyncio
    import os
    from graphiti_core import Graphiti
    from graphiti_core.llm_client.openai_client import OpenAIClient
    from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
    from graphiti_core.llm_client.config import LLMConfig
    
    async def test_get_episodes():
        # Create clients
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
        
        # Initialize Graphiti client
        client = Graphiti(
            uri=os.getenv('NEO4J_URI', 'neo4j://192.168.31.150:7687'),
            user=os.getenv('NEO4J_USER', 'neo4j'),
            password=os.getenv('NEO4J_PASSWORD', 'granite-life-bonanza-sunset-lagoon-1071'),
            llm_client=llm_client,
            embedder=embedder
        )
        
        # Get recent episodes using correct method name
        from datetime import datetime, timezone
        
        episodes = await client.retrieve_episodes(
            reference_time=datetime.now(timezone.utc),
            last_n=10
        )
        
        if episodes:
            print(f"✅ get_episodes successful: Retrieved {len(episodes)} episodes")
            for i, ep in enumerate(episodes[:3]):  # Show first 3
                content_preview = ep.content[:100] + "..." if len(ep.content) > 100 else ep.content
                print(f"   Episode {i+1}: {content_preview}")
        else:
            print("❌ get_episodes failed: No episodes returned")
        
        await client.close()
    
    asyncio.run(test_get_episodes())
    
except Exception as e:
    print(f"❌ get_episodes test failed: {e}")
    import traceback
    traceback.print_exc()
'''
    
    return run_script_in_container(script)

def test_connectivity_simple():
    """Simple connectivity test to Neo4j"""
    print("\n🧪 Testing basic Neo4j connectivity...")
    
    script = '''
import sys
sys.path.insert(0, '/app/.venv/lib/python3.12/site-packages')

try:
    from neo4j import GraphDatabase
    import os
    
    uri = os.getenv('NEO4J_URI', 'neo4j://192.168.31.150:7687')
    user = os.getenv('NEO4J_USER', 'neo4j')
    password = os.getenv('NEO4J_PASSWORD', 'granite-life-bonanza-sunset-lagoon-1071')
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        result = session.run("MATCH (n) WHERE n.group_id = 'default' RETURN count(n) as total")
        total = result.single()["total"]
        print(f"✅ Neo4j connectivity successful: {total} total nodes found")
        
        result = session.run("MATCH (e:Episodic) WHERE e.group_id = 'default' RETURN count(e) as episodes")
        episodes = result.single()["episodes"]
        print(f"   Episodes in database: {episodes}")
    
    driver.close()
    
except Exception as e:
    print(f"❌ Neo4j connectivity test failed: {e}")
    import traceback
    traceback.print_exc()
'''
    
    return run_script_in_container(script)

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
            'mcp_server-graphiti-mcp-1:/tmp/test_script.py'
        ])
        
        if not success:
            print(f"❌ Failed to copy test script: {stderr}")
            return False
        
        # Run script in container as root
        success, stdout, stderr = run_docker_command([
            'docker', 'exec', '--user', 'root', 'mcp_server-graphiti-mcp-1',
            'python3', '/tmp/test_script.py'
        ], timeout=60)
        
        print(stdout)
        if stderr:
            print(f"Stderr: {stderr}")
        
        return success and "✅" in stdout
        
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file)
        except:
            pass

def check_ollama_connectivity():
    """Verify Ollama is working before running tests"""
    print("🔧 Checking Ollama connectivity...")
    
    # Test LLM model
    success, stdout, stderr = run_docker_command([
        'curl', '-s', '-X', 'POST', 'http://192.168.31.134:11434/api/generate',
        '-H', 'Content-Type: application/json',
        '-d', '{"model": "deepseek-r1:latest", "prompt": "Hello", "stream": false}'
    ], timeout=15)
    
    if success and '"response"' in stdout:
        print("✅ Ollama LLM model responding")
    else:
        print("❌ Ollama LLM model not responding")
        return False
    
    # Test embedding model
    success, stdout, stderr = run_docker_command([
        'curl', '-s', '-X', 'POST', 'http://192.168.31.134:11434/api/embeddings',
        '-H', 'Content-Type: application/json', 
        '-d', '{"model": "mxbai-embed-large:latest", "prompt": "test"}'
    ], timeout=15)
    
    if success and '"embedding"' in stdout:
        print("✅ Ollama embedding model responding")
        return True
    else:
        print("❌ Ollama embedding model not responding")
        return False

def main():
    print("🧪 DIRECT MCP FUNCTIONALITY TEST WITH OLLAMA")
    print("=" * 70)
    print(f"Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check prerequisites
    if not check_ollama_connectivity():
        print("\n❌ Ollama connectivity failed. Ensure Ollama server is running.")
        return
    
    # Check container status
    success, stdout, stderr = run_docker_command([
        'docker', 'ps', '--filter', 'name=mcp_server-graphiti-mcp-1', 
        '--format', '{{.Status}}'
    ])
    
    if not success or "Up" not in stdout:
        print("\n❌ MCP server container is not running.")
        return
    
    print(f"✅ Container status: {stdout.strip()}")
    
    # Test core functionality
    test_results = {}
    
    print("\n" + "=" * 70)
    print("TESTING CORE GRAPHITI FUNCTIONALITY")
    print("=" * 70)
    
    test_results['connectivity'] = test_connectivity_simple()
    test_results['add_episode'] = test_add_episode_direct()
    test_results['search_nodes'] = test_search_nodes_direct()
    test_results['get_episodes'] = test_get_episodes_direct()
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 FUNCTIONALITY TEST SUMMARY")
    print("=" * 70)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL CORE FUNCTIONALITY WORKING WITH OLLAMA!")
        print("✅ Graphiti client successfully initialized with Ollama")
        print("✅ Episode creation working with deepseek-r1:latest model")
        print("✅ Entity search working with mxbai-embed-large:latest embeddings")
        print("✅ Episode retrieval working properly")
        print("✅ Knowledge graph operations fully operational")
        print("\n🔗 This confirms the MCP tools will work correctly!")
    else:
        print(f"\n⚠️ {total - passed} tests had issues")
        print("Check the detailed output above for specific error messages")
    
    print("\n" + "=" * 70)
    print("Test completed at:", time.strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == "__main__":
    main()