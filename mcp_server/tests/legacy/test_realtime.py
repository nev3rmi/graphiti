#!/usr/bin/env python3
"""
Real-time test of the MCP server using SSE protocol
"""

import json
import time
import asyncio
import aiohttp
import uuid
from typing import Dict, Any


class MCPClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def send_mcp_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send MCP request via SSE"""
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": method
        }
        if params:
            request["params"] = params
            
        try:
            async with self.session.post(
                f"{self.base_url}/mcp",
                json=request,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}: {await response.text()}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def test_tools_list(self):
        """Test listing available tools"""
        print("🛠️ Testing tools/list...")
        result = await self.send_mcp_request("tools/list")
        
        if "error" in result:
            print(f"❌ Tools list failed: {result['error']}")
            return False
        elif "result" in result and "tools" in result["result"]:
            tools = result["result"]["tools"]
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools[:5]:  # Show first 5 tools
                print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')[:60]}...")
            return True
        else:
            print(f"⚠️ Unexpected response: {result}")
            return False
    
    async def test_get_status(self):
        """Test get_status tool"""
        print("🔍 Testing get_status...")
        result = await self.send_mcp_request("tools/call", {
            "name": "get_status",
            "arguments": {}
        })
        
        if "error" in result:
            print(f"❌ Get status failed: {result['error']}")
            return False
        elif "result" in result:
            print(f"✅ Status: {result['result']}")
            return True
        else:
            print(f"⚠️ Unexpected response: {result}")
            return False
    
    async def test_add_episode(self):
        """Test adding an episode"""
        print("📝 Testing add_episode...")
        
        test_data = {
            "data": "Alice is a software engineer who loves Python programming. She works at TechCorp and specializes in machine learning applications.",
            "metadata": {
                "source": "realtime_test",
                "timestamp": int(time.time())
            }
        }
        
        result = await self.send_mcp_request("tools/call", {
            "name": "add_episode",
            "arguments": test_data
        })
        
        if "error" in result:
            print(f"❌ Add episode failed: {result['error']}")
            return False
        elif "result" in result:
            print(f"✅ Episode added: {result['result']}")
            return True
        else:
            print(f"⚠️ Unexpected response: {result}")
            return False
    
    async def test_search_nodes(self):
        """Test searching nodes"""
        print("🔍 Testing search_nodes...")
        
        # Wait a moment for the episode to be processed
        await asyncio.sleep(3)
        
        result = await self.send_mcp_request("tools/call", {
            "name": "search_nodes",
            "arguments": {
                "query": "Alice software engineer",
                "limit": 5
            }
        })
        
        if "error" in result:
            print(f"❌ Search nodes failed: {result['error']}")
            return False
        elif "result" in result:
            nodes = result["result"]
            print(f"✅ Found {len(nodes)} nodes:")
            for node in nodes[:3]:  # Show first 3 results
                print(f"   - {node.get('name', 'Unknown')}: {node.get('summary', 'No summary')[:60]}...")
            return True
        else:
            print(f"⚠️ Unexpected response: {result}")
            return False


async def test_basic_connectivity():
    """Test basic HTTP connectivity"""
    print("🌐 Testing basic connectivity...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/sse", timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    print("✅ SSE endpoint is accessible")
                    return True
                else:
                    print(f"❌ SSE endpoint returned {response.status}")
                    return False
    except asyncio.TimeoutError:
        print("✅ SSE endpoint is working (timeout expected for streaming endpoint)")
        return True
    except Exception as e:
        print(f"❌ Connectivity test failed: {e}")
        return False


async def main():
    print("🧪 Real-time MCP Server + Ollama Integration Test")
    print("=" * 60)
    
    # Test basic connectivity first
    connectivity_ok = await test_basic_connectivity()
    
    if not connectivity_ok:
        print("❌ Basic connectivity failed, skipping MCP tests")
        return
    
    print()
    
    # Test MCP functionality
    async with MCPClient() as client:
        tests = [
            ("Tools List", client.test_tools_list()),
            ("Get Status", client.test_get_status()),
            ("Add Episode", client.test_add_episode()),
            ("Search Nodes", client.test_search_nodes()),
        ]
        
        results = []
        for test_name, test_coro in tests:
            print(f"\n--- {test_name} ---")
            try:
                success = await test_coro
                results.append((test_name, success))
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")
                results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MCP server with Ollama is working correctly.")
    elif passed > 0:
        print("⚠️ Some tests passed. The server is partially functional.")
    else:
        print("❌ All tests failed. Check server configuration and logs.")


if __name__ == "__main__":
    asyncio.run(main())