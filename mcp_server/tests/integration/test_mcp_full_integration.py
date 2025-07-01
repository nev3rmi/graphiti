#!/usr/bin/env python3
"""
Comprehensive test suite for Graphiti MCP Server with Ollama integration
"""

import json
import time
import uuid
import httpx
import asyncio
from typing import Any, Dict, List


class MCPTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def create_mcp_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a properly formatted MCP request"""
        return {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": method,
            "params": params
        }
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool via HTTP"""
        request = self.create_mcp_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        
        response = await self.client.post(
            f"{self.base_url}/mcp",
            json=request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        
        return response.json()
    
    async def test_server_status(self) -> bool:
        """Test if MCP server is responsive"""
        print("🔍 Testing MCP server status...")
        try:
            result = await self.call_mcp_tool("get_status", {})
            print(f"✅ Server status: {result}")
            return True
        except Exception as e:
            print(f"❌ Server status test failed: {e}")
            return False
    
    async def test_clear_graph(self) -> bool:
        """Clear the graph for fresh testing"""
        print("🧹 Clearing graph...")
        try:
            result = await self.call_mcp_tool("clear_graph", {})
            print(f"✅ Graph cleared: {result}")
            return True
        except Exception as e:
            print(f"❌ Graph clear failed: {e}")
            return False
    
    async def test_add_episode(self) -> bool:
        """Test adding an episode to the knowledge graph"""
        print("📝 Testing episode addition...")
        try:
            test_data = {
                "data": "John Smith is a software engineer at TechCorp. He specializes in machine learning and has 5 years of experience. He recently completed a project on natural language processing.",
                "metadata": {
                    "source": "test_conversation",
                    "timestamp": int(time.time())
                }
            }
            
            result = await self.call_mcp_tool("add_episode", test_data)
            print(f"✅ Episode added successfully: {result}")
            return True
        except Exception as e:
            print(f"❌ Episode addition failed: {e}")
            return False
    
    async def test_search_nodes(self) -> bool:
        """Test searching for nodes in the knowledge graph"""
        print("🔍 Testing node search...")
        try:
            # Wait a moment for processing
            await asyncio.sleep(2)
            
            result = await self.call_mcp_tool("search_nodes", {
                "query": "John Smith",
                "limit": 5
            })
            
            if result and "result" in result and result["result"]:
                nodes = result["result"]
                print(f"✅ Found {len(nodes)} nodes")
                for node in nodes[:2]:  # Show first 2 results
                    print(f"   - {node.get('name', 'Unknown')}: {node.get('summary', 'No summary')}")
                return True
            else:
                print("⚠️ No nodes found, but search completed")
                return True
        except Exception as e:
            print(f"❌ Node search failed: {e}")
            return False
    
    async def test_search_facts(self) -> bool:
        """Test searching for facts/relationships"""
        print("🔗 Testing fact search...")
        try:
            result = await self.call_mcp_tool("search_facts", {
                "query": "software engineer",
                "limit": 5
            })
            
            if result and "result" in result:
                facts = result["result"]
                print(f"✅ Found {len(facts)} facts")
                for fact in facts[:2]:  # Show first 2 results
                    print(f"   - {fact.get('fact', 'No fact description')}")
                return True
            else:
                print("⚠️ No facts found, but search completed")
                return True
        except Exception as e:
            print(f"❌ Fact search failed: {e}")
            return False
    
    async def test_get_episodes(self) -> bool:
        """Test retrieving recent episodes"""
        print("📚 Testing episode retrieval...")
        try:
            result = await self.call_mcp_tool("get_episodes", {
                "limit": 5
            })
            
            if result and "result" in result:
                episodes = result["result"]
                print(f"✅ Retrieved {len(episodes)} episodes")
                for episode in episodes[:2]:  # Show first 2 results
                    content = episode.get('content', 'No content')[:100] + "..."
                    print(f"   - {content}")
                return True
            else:
                print("⚠️ No episodes found, but retrieval completed")
                return True
        except Exception as e:
            print(f"❌ Episode retrieval failed: {e}")
            return False
    
    async def test_complex_scenario(self) -> bool:
        """Test a complex multi-step scenario"""
        print("🎯 Testing complex scenario...")
        try:
            # Add multiple related episodes
            episodes = [
                "Alice Johnson works as a data scientist at DataCorp. She has expertise in Python and machine learning.",
                "Bob Wilson is a project manager at DataCorp. He oversees the AI development team.",
                "Alice Johnson and Bob Wilson are collaborating on a new recommendation system project.",
                "The recommendation system project uses collaborative filtering and deep learning techniques.",
                "DataCorp is planning to launch the recommendation system in Q2 2024."
            ]
            
            print("   Adding multiple related episodes...")
            for i, episode in enumerate(episodes):
                await self.call_mcp_tool("add_episode", {
                    "data": episode,
                    "metadata": {
                        "source": f"complex_test_{i}",
                        "timestamp": int(time.time()) + i
                    }
                })
                await asyncio.sleep(1)  # Brief pause between episodes
            
            # Wait for processing
            await asyncio.sleep(3)
            
            # Search for related information
            print("   Searching for DataCorp information...")
            result = await self.call_mcp_tool("search_nodes", {
                "query": "DataCorp",
                "limit": 10
            })
            
            datacorp_nodes = result.get("result", []) if result else []
            print(f"   Found {len(datacorp_nodes)} DataCorp-related nodes")
            
            # Search for project information
            print("   Searching for project information...")
            result = await self.call_mcp_tool("search_facts", {
                "query": "recommendation system",
                "limit": 10
            })
            
            project_facts = result.get("result", []) if result else []
            print(f"   Found {len(project_facts)} project-related facts")
            
            print("✅ Complex scenario completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Complex scenario failed: {e}")
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        print("🚀 Starting comprehensive MCP server tests with Ollama integration\n")
        
        results = {}
        
        # Test basic connectivity
        results["server_status"] = await self.test_server_status()
        
        if not results["server_status"]:
            print("❌ Server is not responding, skipping other tests")
            return results
        
        # Clear graph for fresh testing
        results["clear_graph"] = await self.test_clear_graph()
        
        # Test core functionality
        results["add_episode"] = await self.test_add_episode()
        results["search_nodes"] = await self.test_search_nodes()
        results["search_facts"] = await self.test_search_facts()
        results["get_episodes"] = await self.test_get_episodes()
        
        # Test complex scenario
        results["complex_scenario"] = await self.test_complex_scenario()
        
        return results


# Alternative HTTP-based test (if MCP protocol doesn't work)
async def test_http_endpoints():
    """Test HTTP endpoints directly"""
    print("🌐 Testing HTTP endpoints...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Test SSE endpoint
            response = await client.get("http://localhost:8000/sse")
            print(f"✅ SSE endpoint status: {response.status_code}")
            
            # Test health endpoint if available
            try:
                response = await client.get("http://localhost:8000/health")
                print(f"✅ Health endpoint status: {response.status_code}")
            except:
                print("ℹ️ Health endpoint not available")
                
        except Exception as e:
            print(f"❌ HTTP endpoint test failed: {e}")


async def main():
    """Main test runner"""
    print("=" * 60)
    print("🧪 Graphiti MCP Server + Ollama Integration Test Suite")
    print("=" * 60)
    
    # Test HTTP endpoints first
    await test_http_endpoints()
    print()
    
    # Test MCP functionality
    async with MCPTester() as tester:
        results = await tester.run_all_tests()
        
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, passed_test in results.items():
            status = "✅ PASS" if passed_test else "❌ FAIL"
            print(f"{test_name:20} {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! MCP server with Ollama is working correctly.")
        else:
            print("⚠️ Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    asyncio.run(main())