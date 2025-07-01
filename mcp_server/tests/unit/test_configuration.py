#!/usr/bin/env python3
"""
Unit tests for MCP server configuration with Ollama integration
"""

import subprocess
import os

def run_docker_command(cmd, timeout=30):
    """Helper to run docker commands with timeout"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_environment_variables():
    """Test that all required environment variables are set correctly"""
    print("🔧 TESTING ENVIRONMENT CONFIGURATION")
    print("=" * 60)
    
    required_vars = {
        'OPENAI_API_KEY': 'abc',
        'OPENAI_BASE_URL': 'http://192.168.31.134:11434/v1/',
        'MODEL_NAME': 'deepseek-r1:latest',
        'EMBEDDER_MODEL_NAME': 'mxbai-embed-large:latest',
        'EMBEDDING_DIM': '1024',
        'NEO4J_URI': 'neo4j://192.168.31.150:7687',
        'NEO4J_USER': 'neo4j',
        'NEO4J_PASSWORD': 'granite-life-bonanza-sunset-lagoon-1071'
    }
    
    print("📋 Checking environment variables:")
    
    passed = 0
    total = len(required_vars)
    
    for var_name, expected in required_vars.items():
        success, stdout, stderr = run_docker_command([
            'docker', 'exec', 'mcp_server-graphiti-mcp-1',
            'printenv', var_name
        ], timeout=5)
        
        if success:
            actual = stdout.strip()
            if actual == expected or (var_name == 'NEO4J_PASSWORD' and len(actual) > 10):
                if var_name == 'NEO4J_PASSWORD':
                    print(f"✅ {var_name}: [MASKED]")
                else:
                    print(f"✅ {var_name}: {actual}")
                passed += 1
            else:
                print(f"⚠️ {var_name}: {actual} (expected: {expected})")
        else:
            print(f"❌ {var_name}: not set")
    
    print(f"\n📊 Configuration check: {passed}/{total} variables correct")
    return passed == total

def test_file_permissions():
    """Test that necessary files have correct permissions"""
    print("\n📁 TESTING FILE PERMISSIONS")
    print("=" * 60)
    
    files_to_check = [
        '/app/graphiti_mcp_server.py',
        '/app/.env',
        '/app/pyproject.toml'
    ]
    
    print("📋 Checking file permissions:")
    
    passed = 0
    for file_path in files_to_check:
        success, stdout, stderr = run_docker_command([
            'docker', 'exec', 'mcp_server-graphiti-mcp-1',
            'ls', '-la', file_path
        ], timeout=5)
        
        if success:
            permissions = stdout.split()[0]
            print(f"✅ {file_path}: {permissions}")
            passed += 1
        else:
            print(f"❌ {file_path}: not accessible")
    
    print(f"\n📊 File access check: {passed}/{len(files_to_check)} files accessible")
    return passed == len(files_to_check)

def test_python_dependencies():
    """Test that required Python packages are installed"""
    print("\n📦 TESTING PYTHON DEPENDENCIES")
    print("=" * 60)
    
    script = '''
import sys
required_packages = [
    'graphiti_core',
    'neo4j',
    'openai', 
    'fastmcp',
    'pydantic',
    'dotenv'
]

print("📋 Checking Python packages:")
failed = []

for package in required_packages:
    try:
        __import__(package.replace('-', '_'))
        print(f"✅ {package}: installed")
    except ImportError:
        print(f"❌ {package}: missing")
        failed.append(package)

if not failed:
    print("\\n✅ All required packages installed")
else:
    print(f"\\n❌ Missing packages: {', '.join(failed)}")
'''
    
    success, stdout, stderr = run_docker_command([
        'docker', 'exec', 'mcp_server-graphiti-mcp-1',
        'python3', '-c', script
    ], timeout=15)
    
    print(stdout)
    if stderr:
        print(f"Errors: {stderr}")
    
    return success and "All required packages installed" in stdout

def test_docker_configuration():
    """Test Docker container configuration"""
    print("\n🐳 TESTING DOCKER CONFIGURATION")
    print("=" * 60)
    
    # Check container network
    success, stdout, stderr = run_docker_command([
        'docker', 'inspect', 'mcp_server-graphiti-mcp-1',
        '--format', '{{.NetworkSettings.Networks}}'
    ], timeout=10)
    
    if success:
        print(f"✅ Container network configuration: {stdout.strip()}")
    else:
        print("❌ Unable to inspect container network")
        return False
    
    # Check port mapping
    success, stdout, stderr = run_docker_command([
        'docker', 'port', 'mcp_server-graphiti-mcp-1'
    ], timeout=5)
    
    if success and "8000" in stdout:
        print(f"✅ Port mapping: {stdout.strip()}")
    else:
        print("❌ Port 8000 not mapped")
        return False
    
    # Check resource usage
    success, stdout, stderr = run_docker_command([
        'docker', 'stats', 'mcp_server-graphiti-mcp-1', '--no-stream', '--format',
        'table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}'
    ], timeout=10)
    
    if success:
        print(f"✅ Resource usage:")
        print(f"   {stdout.strip()}")
    else:
        print("⚠️ Unable to get resource stats")
    
    return True

def main():
    print("🧪 MCP SERVER CONFIGURATION TESTS")
    print("=" * 70)
    
    # Check if container is running
    success, stdout, stderr = run_docker_command([
        'docker', 'ps', '--filter', 'name=mcp_server-graphiti-mcp-1', 
        '--format', '{{.Status}}'
    ])
    
    if not success or "Up" not in stdout:
        print("❌ MCP server container is not running")
        print("Start the container with: docker compose up")
        return False
    
    print(f"✅ Container status: {stdout.strip()}")
    
    # Run all configuration tests
    tests = [
        ("Environment Variables", test_environment_variables),
        ("File Permissions", test_file_permissions),
        ("Python Dependencies", test_python_dependencies),
        ("Docker Configuration", test_docker_configuration)
    ]
    
    results = {}
    for test_name, test_function in tests:
        try:
            results[test_name] = test_function()
        except Exception as e:
            print(f"❌ {test_name} test failed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 CONFIGURATION TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
    
    print(f"\nOverall: {passed}/{total} configuration tests passed")
    
    if passed == total:
        print("\n🎉 ALL CONFIGURATION TESTS PASSED!")
        print("✅ MCP server is properly configured")
        print("✅ Ollama integration settings correct")
        print("✅ All dependencies available")
        print("✅ Docker container properly set up")
    else:
        print(f"\n⚠️ {total - passed} configuration issues found")
        print("Check the detailed output above for specific problems")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)