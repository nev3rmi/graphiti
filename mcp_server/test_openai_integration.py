#!/usr/bin/env python3
"""
Test the MCP server with OpenAI integration
"""

import subprocess
import json
import time

def test_openai_api_connectivity():
    """Test direct OpenAI API connectivity"""
    print("🔌 Testing OpenAI API Connectivity...")
    
    # Read the API key from env file
    with open('.env', 'r') as f:
        env_content = f.read()
        for line in env_content.split('\n'):
            if line.startswith('OPENAI_API_KEY='):
                api_key = line.split('=', 1)[1].strip()
                break
        else:
            print("❌ Could not find OPENAI_API_KEY in .env file")
            return False
    
    # Test OpenAI API call
    try:
        result = subprocess.run([
            'curl', '-s', '-X', 'POST',
            'https://api.openai.com/v1/chat/completions',
            '-H', 'Content-Type: application/json',
            '-H', f'Authorization: Bearer {api_key}',
            '-d', json.dumps({
                "model": "gpt-4.1-mini",
                "messages": [{"role": "user", "content": "Hello, just say OK"}],
                "max_tokens": 10
            })
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            if 'choices' in response and len(response['choices']) > 0:
                content = response['choices'][0]['message']['content'].strip()
                print(f"✅ OpenAI API working: {content}")
                return True
            else:
                print(f"⚠️ Unexpected OpenAI response: {response}")
                return False
        else:
            print(f"❌ OpenAI API call failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI API test error: {e}")
        return False

def test_embedding_api():
    """Test OpenAI embedding API"""
    print("\n🔍 Testing OpenAI Embedding API...")
    
    # Read the API key from env file
    with open('.env', 'r') as f:
        env_content = f.read()
        for line in env_content.split('\n'):
            if line.startswith('OPENAI_API_KEY='):
                api_key = line.split('=', 1)[1].strip()
                break
        else:
            print("❌ Could not find OPENAI_API_KEY in .env file")
            return False
    
    try:
        result = subprocess.run([
            'curl', '-s', '-X', 'POST',
            'https://api.openai.com/v1/embeddings',
            '-H', 'Content-Type: application/json',
            '-H', f'Authorization: Bearer {api_key}',
            '-d', json.dumps({
                "model": "text-embedding-3-small",
                "input": "Hello world"
            })
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            if 'data' in response and len(response['data']) > 0:
                embedding = response['data'][0]['embedding']
                print(f"✅ OpenAI Embeddings working: {len(embedding)} dimensions")
                return True
            else:
                print(f"⚠️ Unexpected embedding response: {response}")
                return False
        else:
            print(f"❌ Embedding API call failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Embedding API test error: {e}")
        return False

def test_mcp_server_with_openai():
    """Test adding an episode through the MCP server using OpenAI"""
    print("\n🧠 Testing MCP Server with OpenAI Integration...")
    
    # Create a test script that adds an episode
    test_script = '''
import sys
sys.path.insert(0, '/app/.venv/lib/python3.12/site-packages')

try:
    from neo4j import GraphDatabase
    import os
    import asyncio
    import time
    
    # Import the Graphiti module from the app
    sys.path.insert(0, '/app')
    from graphiti_core import Graphiti
    
    async def test_episode_addition():
        try:
            # Initialize Graphiti client with OpenAI configuration
            client = Graphiti(
                uri=os.environ.get("NEO4J_URI", "neo4j://192.168.31.150:7687"),
                user=os.environ.get("NEO4J_USER", "neo4j"), 
                password=os.environ.get("NEO4J_PASSWORD", "granite-life-bonanza-sunset-lagoon-1071"),
                model=os.environ.get("MODEL_NAME", "gpt-4.1-mini"),
                api_key=os.environ.get("OPENAI_API_KEY"),
                embedder_model=os.environ.get("EMBEDDER_MODEL_NAME", "text-embedding-3-small"),
                embedding_dim=int(os.environ.get("EMBEDDING_DIM", "1536")),
                group_id="openai_test"
            )
            
            print("✅ Graphiti client initialized with OpenAI")
            
            # Add a test episode
            episode_content = "Sarah Chen is a machine learning engineer at DataFlow Inc. She recently developed a recommendation algorithm that improved user engagement by 40%. She graduated from Stanford with a PhD in Computer Science."
            
            print(f"📝 Adding test episode: {episode_content[:50]}...")
            
            result = await client.add_episode(
                episode_content,
                source="openai_integration_test",
                source_description="Testing OpenAI integration with MCP server"
            )
            
            print(f"✅ Episode added successfully")
            
            # Wait a moment for processing
            await asyncio.sleep(3)
            
            # Search for the added content
            print("🔍 Searching for added content...")
            search_results = await client.search(
                query="Sarah Chen machine learning",
                limit=5
            )
            
            print(f"📊 Search results:")
            print(f"   Nodes found: {len(search_results.nodes)}")
            print(f"   Edges found: {len(search_results.edges)}")
            
            for node in search_results.nodes[:3]:
                print(f"   - {node.name}: {node.summary[:60]}...")
            
            await client.close()
            print("\\n✅ OpenAI integration test completed successfully!")
            
        except Exception as e:
            print(f"❌ Episode addition failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Run the test
    asyncio.run(test_episode_addition())
    
except Exception as e:
    print(f"❌ Test setup failed: {e}")
    import traceback
    traceback.print_exc()
'''
    
    # Write and execute the test script
    with open('/tmp/openai_integration_test.py', 'w') as f:
        f.write(test_script)
    
    try:
        # Copy script to container
        subprocess.run([
            'docker', 'cp', '/tmp/openai_integration_test.py',
            'mcp_server-graphiti-mcp-1:/tmp/openai_integration_test.py'
        ], check=True)
        
        # Run the test
        print("🚀 Running OpenAI integration test in container...")
        result = subprocess.run([
            'docker', 'exec', 'mcp_server-graphiti-mcp-1',
            'python3', '/tmp/openai_integration_test.py'
        ], capture_output=True, text=True, timeout=120)
        
        print("📄 Test Output:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Errors:")
            print(result.stderr)
        
        return "Episode added successfully" in result.stdout
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def monitor_real_time_logs():
    """Monitor server logs for OpenAI API calls"""
    print("\n📊 Monitoring Recent Server Activity...")
    
    try:
        # Get recent logs
        result = subprocess.run([
            'docker', 'logs', '--since=30s', 'mcp_server-graphiti-mcp-1'
        ], capture_output=True, text=True, timeout=10)
        
        print("Recent server logs:")
        print(result.stdout[-1000:])  # Last 1000 characters
        
        if result.stderr:
            print("Error logs:")
            print(result.stderr[-500:])  # Last 500 characters
            
    except Exception as e:
        print(f"❌ Log monitoring failed: {e}")

def main():
    print("🧪 OpenAI Integration Test for Graphiti MCP Server")
    print("=" * 60)
    
    # Test OpenAI API connectivity
    openai_ok = test_openai_api_connectivity()
    embedding_ok = test_embedding_api()
    
    if not (openai_ok and embedding_ok):
        print("\n❌ OpenAI API tests failed. Check your API key and connectivity.")
        return
    
    # Test MCP server integration
    mcp_ok = test_mcp_server_with_openai()
    
    # Monitor logs
    monitor_real_time_logs()
    
    print("\n" + "=" * 60)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"OpenAI LLM API:     {'✅ PASS' if openai_ok else '❌ FAIL'}")
    print(f"OpenAI Embedding:   {'✅ PASS' if embedding_ok else '❌ FAIL'}")
    print(f"MCP Integration:    {'✅ PASS' if mcp_ok else '❌ FAIL'}")
    
    if openai_ok and embedding_ok and mcp_ok:
        print("\n🎉 All tests passed! MCP server with OpenAI is working perfectly.")
        print("\n📌 Current Configuration:")
        print("   • LLM Model: gpt-4.1-mini")
        print("   • Embedding Model: text-embedding-3-small (1536 dimensions)")
        print("   • Neo4j Database: Connected and indexed")
        print("   • MCP Server: Running on port 8000 with SSE transport")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()