#!/usr/bin/env python3
"""Simple test for MCP server functionality"""

import json
import requests
import time

def test_sse_endpoint():
    """Test SSE endpoint"""
    print("Testing SSE endpoint...")
    try:
        response = requests.get("http://localhost:8000/sse", timeout=5)
        print(f"SSE endpoint status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"SSE test failed: {e}")
        return False

def test_mcp_via_stdio():
    """Test MCP server via stdio using docker exec"""
    print("Testing MCP server functionality...")
    
    import subprocess
    
    # Test commands to run
    test_commands = [
        '{"jsonrpc": "2.0", "id": "1", "method": "tools/list"}',
        '{"jsonrpc": "2.0", "id": "2", "method": "tools/call", "params": {"name": "get_status", "arguments": {}}}'
    ]
    
    for i, cmd in enumerate(test_commands):
        print(f"\nTest {i+1}: {cmd[:50]}...")
        try:
            # Run command inside docker container
            result = subprocess.run([
                "docker", "exec", "-i", "mcp_server-graphiti-mcp-1",
                "sh", "-c", f'echo \'{cmd}\' | uv run graphiti_mcp_server.py --transport stdio'
            ], capture_output=True, text=True, timeout=30)
            
            print(f"Exit code: {result.returncode}")
            if result.stdout:
                print(f"Output: {result.stdout[:200]}...")
            if result.stderr:
                print(f"Error: {result.stderr[:200]}...")
                
        except subprocess.TimeoutExpired:
            print("Command timed out")
        except Exception as e:
            print(f"Command failed: {e}")

def main():
    print("🧪 Simple MCP Server Test")
    print("=" * 40)
    
    # Test HTTP endpoint
    sse_ok = test_sse_endpoint()
    
    # Test MCP functionality
    if sse_ok:
        test_mcp_via_stdio()
    else:
        print("SSE endpoint not working, skipping MCP tests")

if __name__ == "__main__":
    main()