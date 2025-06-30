#!/usr/bin/env python3
"""
Test MCP server via stdio transport
"""

import json
import subprocess
import tempfile
import os

def test_mcp_stdio():
    """Test MCP server using stdio transport"""
    print("🔧 Testing MCP server via stdio transport...")
    
    # Test commands
    test_commands = [
        {"jsonrpc": "2.0", "id": "1", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}},
        {"jsonrpc": "2.0", "id": "2", "method": "tools/list"},
        {"jsonrpc": "2.0", "id": "3", "method": "tools/call", "params": {"name": "get_status", "arguments": {}}},
    ]
    
    for i, command in enumerate(test_commands):
        print(f"\n--- Test {i+1}: {command['method']} ---")
        
        try:
            # Write command to temporary file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                json.dump(command, f)
                temp_file = f.name
            
            # Copy file to container
            subprocess.run(['docker', 'cp', temp_file, f'mcp_server-graphiti-mcp-1:/tmp/test_input.json'], check=True)
            
            # Run MCP server with stdio transport
            result = subprocess.run([
                'docker', 'exec', '-i', 'mcp_server-graphiti-mcp-1',
                'sh', '-c', 'cat /tmp/test_input.json | uv run graphiti_mcp_server.py --transport stdio'
            ], capture_output=True, text=True, timeout=30)
            
            # Clean up temp file
            os.unlink(temp_file)
            
            print(f"Exit code: {result.returncode}")
            if result.stdout:
                try:
                    response = json.loads(result.stdout.strip())
                    print(f"✅ Success: {json.dumps(response, indent=2)}")
                except json.JSONDecodeError:
                    print(f"📄 Raw output: {result.stdout[:500]}...")
            
            if result.stderr:
                print(f"⚠️ Stderr: {result.stderr[:200]}...")
                
        except subprocess.TimeoutExpired:
            print("⏰ Command timed out")
        except Exception as e:
            print(f"❌ Command failed: {e}")

def test_functional_workflow():
    """Test a functional workflow: add episode -> search"""
    print("\n🎯 Testing functional workflow...")
    
    workflow_commands = [
        # Initialize
        {"jsonrpc": "2.0", "id": "1", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}},
        
        # Add episode
        {"jsonrpc": "2.0", "id": "2", "method": "tools/call", "params": {
            "name": "add_episode", 
            "arguments": {
                "data": "Sarah is a data scientist at AI Research Labs. She specializes in natural language processing and has published several papers on transformer models.",
                "metadata": {"source": "test_workflow", "timestamp": 1672531200}
            }
        }},
        
        # Search for the added content
        {"jsonrpc": "2.0", "id": "3", "method": "tools/call", "params": {
            "name": "search_nodes",
            "arguments": {"query": "Sarah data scientist", "limit": 5}
        }}
    ]
    
    for i, command in enumerate(workflow_commands):
        print(f"\nWorkflow step {i+1}: {command['method']}")
        
        try:
            # Create input script that handles the workflow
            script_content = f'''
import json
import sys
import os

# Send the command
command = {json.dumps(command)}
print(json.dumps(command))
sys.stdout.flush()

# For stdio, we need to handle the response properly
# In a real scenario, this would be more complex
'''
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
                f.write(script_content)
                script_file = f.name
            
            # Copy script to container
            subprocess.run(['docker', 'cp', script_file, f'mcp_server-graphiti-mcp-1:/tmp/workflow_step.py'], check=True)
            
            # Run the workflow step
            result = subprocess.run([
                'docker', 'exec', 'mcp_server-graphiti-mcp-1',
                'sh', '-c', 'python3 /tmp/workflow_step.py | uv run graphiti_mcp_server.py --transport stdio'
            ], capture_output=True, text=True, timeout=45)
            
            # Clean up
            os.unlink(script_file)
            
            if result.returncode == 0:
                print(f"✅ Step completed successfully")
                if result.stdout:
                    print(f"Response: {result.stdout[:300]}...")
            else:
                print(f"❌ Step failed with code {result.returncode}")
                if result.stderr:
                    print(f"Error: {result.stderr[:200]}...")
            
        except Exception as e:
            print(f"❌ Workflow step failed: {e}")

def main():
    print("🧪 Graphiti MCP Server Stdio Test")
    print("=" * 50)
    
    # Test basic MCP functionality
    test_mcp_stdio()
    
    # Test functional workflow
    test_functional_workflow()
    
    print("\n" + "=" * 50)
    print("📋 Test completed!")
    print("Check the output above for test results.")

if __name__ == "__main__":
    main()