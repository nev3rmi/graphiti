#!/usr/bin/env python3

import json
import subprocess
import sys

def test_mcp_server():
    """Test the MCP server functionality"""
    
    # First, initialize MCP
    init_request = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {
                    "listChanged": False
                },
                "sampling": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    # Test add_memory
    add_memory_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "add_memory",
            "arguments": {
                "name": "Test Memory",
                "episode_body": "This is a test memory entry to verify Ollama integration works correctly.",
                "source": "text",
                "source_description": "test data"
            }
        }
    }
    
    try:
        # Start MCP server process
        proc = subprocess.Popen(
            ["uv", "run", "graphiti_mcp_server.py", "--transport", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send initialization
        init_str = json.dumps(init_request) + "\n"
        print(f"Initializing: {init_str.strip()}")
        proc.stdin.write(init_str)
        proc.stdin.flush()
        
        # Read init response
        response = proc.stdout.readline()
        print(f"Init Response: {response.strip()}")
        
        # Send add_memory request
        request_str = json.dumps(add_memory_request) + "\n"
        print(f"Sending: {request_str.strip()}")
        proc.stdin.write(request_str)
        proc.stdin.flush()
        
        # Read response with timeout
        import time
        time.sleep(5)  # Give some time for processing
        
        while True:
            try:
                response = proc.stdout.readline()
                if not response:
                    break
                print(f"Response: {response.strip()}")
                try:
                    resp_data = json.loads(response)
                    if "error" in resp_data:
                        print(f"Error: {resp_data['error']}")
                    elif "result" in resp_data:
                        print("Success!")
                        break
                except json.JSONDecodeError:
                    print(f"Non-JSON response: {response}")
            except:
                break
        
        proc.terminate()
        proc.wait()
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing MCP server with Ollama...")
    success = test_mcp_server()
    sys.exit(0 if success else 1)