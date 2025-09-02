#!/usr/bin/env python3
"""
Test runner for PyMOCAT-MC
This script runs all tests without requiring pytest
"""

import sys
import os
import subprocess
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def run_test(name, script_path):
    """Run a single test script and return the result"""
    print(f"\n{BLUE}{BOLD}{name}{RESET}")
    print("-" * 50)
    
    # Check if test file exists
    if not script_path.exists():
        print(f"{RED}X Test file not found: {script_path}{RESET}")
        return "missing"
    
    try:
        # Check Python and basic imports first
        if name == "Basic Functionality Tests":
            check_cmd = [sys.executable, "-c", "import numpy, scipy; print('Dependencies OK')"]
            dep_result = subprocess.run(
                check_cmd,
                capture_output=True,
                text=True,
                timeout=10)
            if dep_result.returncode != 0:
                print(f"{RED}X Missing dependencies: {dep_result.stderr.strip()}{RESET}")
                print(f"{YELLOW}Run: pip install -r requirements.txt{RESET}")
                return "deps_missing"
        
        # Ensure we run from the repository root (parent of tests directory)
        repo_root = Path(__file__).parent.parent.resolve()
        
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=120,  # Increased timeout
            cwd=str(repo_root)  # Always run from where run_tests.py is located
        )
        
        # Print output
        if result.stdout:
            stdout = result.stdout.strip()
            # Truncate very long output but keep important parts
            if len(stdout) > 2000:
                lines = stdout.split('\n')
                if len(lines) > 50:
                    # Show first 20 and last 20 lines
                    truncated = '\n'.join(lines[:20]) \
                        + "\n\n... [output truncated] ...\n\n" + '\n'.join(lines[-20:])
                    print(truncated)
                else:
                    print(stdout[:2000] + "... [truncated]")
            else:
                print(stdout)
        
        # Check for errors
        if result.returncode == 0:
            if "ERROR" in result.stdout or "X " in result.stdout:
                # Count errors vs successes
                error_count = result.stdout.count("X ") \
                    + result.stdout.count("ERROR")
                success_count = result.stdout.count("OK") \
                    + result.stdout.count("SUCCESS")
                
                if success_count > error_count:
                    print(f"{YELLOW}! Test completed with warnings{RESET}")
                    return "warning"
                else:
                    print(f"{RED}X Test failed with errors{RESET}")
                    return "failed"
            else:
                print(f"{GREEN}+ Test passed{RESET}")
                return "passed"
        else:
            if result.stderr:
                stderr = result.stderr.strip()
                print(f"{RED}Error output:{RESET}")
                print(stderr[:500])  # Limit error output
                
                # Check for common issues
                if "ModuleNotFoundError" in stderr:
                    print(f"{YELLOW}Hint: Try 'pip install -r requirements.txt'{RESET}")
                elif "Permission denied" in stderr:
                    print(f"{YELLOW}Hint: Check file permissions{RESET}")
                elif "No such file" in stderr:
                    print(f"{YELLOW}Hint: Run from repository root directory{RESET}")
            
            print(f"{RED}X Test failed (exit code: {result.returncode}){RESET}")
            return "failed"
            
    except subprocess.TimeoutExpired:
        print(f"{RED}X Test timed out (>120 seconds){RESET}")
        print(f"{YELLOW}Hint: Test may be hanging on import or computation{RESET}")
        return "timeout"
    except FileNotFoundError:
        print(f"{RED}X Python interpreter not found{RESET}")
        print(f"{YELLOW}Hint: Make sure Python is installed and in PATH{RESET}")
        return "error"
    except Exception as e:
        print(f"{RED}X Test error: {e}{RESET}")
        return "error"


def main():
    """Run all tests"""
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}PyMOCAT-MC Test Suite{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    
    # Get paths
    test_dir = Path(__file__).parent  # tests/ directory 
    repo_root = test_dir.parent       # repository root
    examples_dir = repo_root / "python_implementation" / "examples"
    
    # Define tests to run
    tests = [
        (
            "Basic Functionality Tests",
            test_dir / "test_basic_functionality_simple.py"),
        ("Import Test", test_dir / "test_import.py"),
        ("Minimal Simulation Test", test_dir / "minimal_test.py"),
        ("Simple Run Test", test_dir / "test_simple_run.py"),
        (
            "Quick Start Example",
            examples_dir / "Quick_Start" / "quick_start.py"),
    ]
    
    # Run tests
    results = {}
    for test_name, test_path in tests:
        if test_path.exists():
            results[test_name] = run_test(test_name, test_path)
        else:
            print(f"\n{YELLOW}! Skipping {test_name}: File not found at {test_path}{RESET}")
            results[test_name] = "skipped"
    
    # Print summary
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}TEST SUMMARY{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    
    passed = sum(1 for r in results.values() if r == "passed")
    failed = sum(1 for r in results.values() if r == "failed")
    warnings = sum(1 for r in results.values() if r == "warning")
    skipped = sum(1 for r in results.values() if r == "skipped")
    missing = sum(1 for r in results.values() if r == "missing")
    deps_missing = sum(1 for r in results.values() if r == "deps_missing")
    errors = sum(1 for r in results.values() if r in ["error", "timeout"])
    
    for test_name, result in results.items():
        if result == "passed":
            symbol = f"{GREEN}+{RESET}"
        elif result == "failed":
            symbol = f"{RED}X{RESET}"
        elif result == "warning":
            symbol = f"{YELLOW}!{RESET}"
        elif result == "skipped":
            symbol = f"{YELLOW}S{RESET}"
        elif result == "missing":
            symbol = f"{RED}M{RESET}"
        elif result == "deps_missing":
            symbol = f"{RED}D{RESET}"
        else:
            symbol = f"{RED}E{RESET}"
        
        print(f"{symbol} {test_name}: {result.upper().replace('_', ' ')}")
    
    print(f"\n{BOLD}Results:{RESET}")
    print(f"  {GREEN}Passed: {passed}{RESET}")
    if warnings > 0:
        print(f"  {YELLOW}Warnings: {warnings}{RESET}")
    if failed > 0:
        print(f"  {RED}Failed: {failed}{RESET}")
    if errors > 0:
        print(f"  {RED}Errors: {errors}{RESET}")
    if missing > 0:
        print(f"  {RED}Missing files: {missing}{RESET}")
    if deps_missing > 0:
        print(f"  {RED}Missing dependencies: {deps_missing}{RESET}")
    if skipped > 0:
        print(f"  {YELLOW}Skipped: {skipped}{RESET}")
    
    # Overall result
    total_issues = failed + errors + missing + deps_missing
    if total_issues == 0:
        if warnings > 0:
            print(f"\n{YELLOW}{BOLD}All tests passed with warnings!{RESET}")
        else:
            print(f"\n{GREEN}{BOLD}All tests passed!{RESET}")
        return 0
    else:
        print(f"\n{RED}{BOLD}{total_issues} test(s) failed{RESET}")
        if deps_missing > 0:
            print(f"{YELLOW}Try running: python setup_environment.py{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())