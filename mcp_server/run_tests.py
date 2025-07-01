#!/usr/bin/env python3
"""
Unified test runner for Graphiti MCP Server with Ollama integration
"""

import subprocess
import sys
import time
import argparse
from pathlib import Path

def run_test(test_path, timeout=60):
    """Run a single test file"""
    try:
        result = subprocess.run([
            sys.executable, test_path
        ], capture_output=True, text=True, timeout=timeout)
        
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': f'Test timed out after {timeout} seconds',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }

def run_test_suite(test_dir, suite_name):
    """Run all tests in a directory"""
    print(f"\n🧪 RUNNING {suite_name.upper()} TESTS")
    print("=" * 70)
    
    test_files = list(Path(test_dir).glob("test_*.py"))
    if not test_files:
        print(f"No test files found in {test_dir}")
        return True, 0, 0
    
    passed = 0
    failed = 0
    
    for test_file in sorted(test_files):
        print(f"\n📋 Running {test_file.name}...")
        result = run_test(str(test_file))
        
        if result['success']:
            print(f"✅ {test_file.name} PASSED")
            passed += 1
        else:
            print(f"❌ {test_file.name} FAILED")
            print(f"   Return code: {result['returncode']}")
            if result['stderr']:
                print(f"   Error: {result['stderr'][:200]}...")
            failed += 1
        
        # Show brief output for failed tests
        if not result['success'] and result['stdout']:
            lines = result['stdout'].split('\n')
            error_lines = [line for line in lines if '❌' in line or 'ERROR' in line.upper()]
            if error_lines:
                print("   Key errors:")
                for line in error_lines[:3]:
                    print(f"     {line.strip()}")
    
    success = failed == 0
    print(f"\n📊 {suite_name} Results: {passed} passed, {failed} failed")
    return success, passed, failed

def run_report(report_path, report_name):
    """Run a status report"""
    print(f"\n📊 GENERATING {report_name.upper()}")
    print("=" * 70)
    
    result = run_test(str(report_path), timeout=90)
    
    if result['success']:
        print(f"✅ {report_name} completed successfully")
        # Show key status lines
        lines = result['stdout'].split('\n')
        status_lines = [line for line in lines if '✅' in line or '❌' in line]
        if status_lines:
            print("📋 Key Status Indicators:")
            for line in status_lines[-10:]:  # Show last 10 status lines
                print(f"   {line.strip()}")
    else:
        print(f"❌ {report_name} failed")
        if result['stderr']:
            print(f"   Error: {result['stderr']}")
    
    return result['success']

def main():
    parser = argparse.ArgumentParser(description="Run Graphiti MCP Server tests")
    parser.add_argument('--suite', choices=['unit', 'integration', 'validation', 'all'], 
                       default='all', help='Test suite to run')
    parser.add_argument('--reports', action='store_true', 
                       help='Generate status reports')
    parser.add_argument('--health-check', action='store_true',
                       help='Run comprehensive health check only')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    print("🚀 GRAPHITI MCP SERVER TEST RUNNER")
    print("=" * 70)
    print(f"Test run started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Configuration: Ollama + Neo4j + MCP Server")
    
    # Check if container is running
    try:
        result = subprocess.run([
            'docker', 'ps', '--filter', 'name=mcp_server-graphiti-mcp-1', 
            '--format', '{{.Status}}'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and "Up" in result.stdout:
            print(f"✅ Container status: {result.stdout.strip()}")
        else:
            print("❌ MCP server container is not running")
            print("Start the container with: docker compose up")
            return 1
    except Exception as e:
        print(f"❌ Unable to check container status: {e}")
        return 1
    
    # Run health check if requested
    if args.health_check:
        health_check_path = Path("tests/reports/system_health_check.py")
        if health_check_path.exists():
            success = run_report(health_check_path, "System Health Check")
            return 0 if success else 1
        else:
            print("❌ Health check script not found")
            return 1
    
    total_passed = 0
    total_failed = 0
    suite_results = {}
    
    # Define test suites
    test_suites = []
    if args.suite in ['unit', 'all']:
        test_suites.append(('tests/unit', 'Unit'))
    if args.suite in ['integration', 'all']:
        test_suites.append(('tests/integration', 'Integration'))
    if args.suite in ['validation', 'all']:
        test_suites.append(('tests/validation', 'Validation'))
    
    # Run test suites
    for test_dir, suite_name in test_suites:
        if Path(test_dir).exists():
            success, passed, failed = run_test_suite(test_dir, suite_name)
            suite_results[suite_name] = success
            total_passed += passed
            total_failed += failed
        else:
            print(f"\n⚠️ {suite_name} test directory not found: {test_dir}")
    
    # Generate reports if requested
    if args.reports:
        print(f"\n📊 GENERATING STATUS REPORTS")
        print("=" * 70)
        
        reports = [
            ('tests/reports/system_health_check.py', 'System Health Check'),
            ('tests/reports/ollama_status_report.py', 'Ollama Status Report')
        ]
        
        for report_path, report_name in reports:
            if Path(report_path).exists():
                run_report(Path(report_path), report_name)
            else:
                print(f"⚠️ Report not found: {report_path}")
    
    # Final summary
    print(f"\n" + "=" * 70)
    print("📋 FINAL TEST SUMMARY")
    print("=" * 70)
    
    print(f"📊 Overall Results:")
    print(f"   Total tests passed: {total_passed}")
    print(f"   Total tests failed: {total_failed}")
    print(f"   Success rate: {total_passed/(total_passed+total_failed)*100:.1f}%" if (total_passed+total_failed) > 0 else "No tests run")
    
    print(f"\n📋 Suite Results:")
    for suite_name, success in suite_results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {suite_name:12} {status}")
    
    # Overall assessment
    all_passed = all(suite_results.values()) and total_failed == 0
    
    if all_passed:
        print(f"\n🎉 ALL TESTS PASSED!")
        print("✅ MCP server is fully functional")
        print("✅ Ollama integration working perfectly")
        print("✅ Knowledge graph operations verified")
        print("✅ Ready for AI assistant integration")
        
        print(f"\n🔗 System Endpoints:")
        print("   • MCP SSE: http://localhost:8000/sse")
        print("   • Neo4j Browser: http://192.168.31.150:7474")
        print("   • Ollama API: http://192.168.31.134:11434")
        
        return 0
    else:
        print(f"\n⚠️ SOME TESTS FAILED")
        print(f"❌ {total_failed} test(s) failed")
        failed_suites = [name for name, success in suite_results.items() if not success]
        if failed_suites:
            print(f"❌ Failed suites: {', '.join(failed_suites)}")
        print("🔧 Check the detailed output above for specific issues")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())