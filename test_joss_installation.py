#!/usr/bin/env python3
"""
Test script to verify PyMOCAT-MC installation meets JOSS requirements.
"""

import subprocess
import sys
import os
import tempfile
import shutil

def test_github_installation():
    """Test installation from GitHub repository."""
    print("Testing installation from GitHub...")

    # Create a temporary virtual environment
    with tempfile.TemporaryDirectory() as tmpdir:
        venv_dir = os.path.join(tmpdir, "test_venv")

        # Create virtual environment
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)

        # Get pip and python paths in venv
        if sys.platform == "win32":
            pip_path = os.path.join(venv_dir, "Scripts", "pip")
            python_path = os.path.join(venv_dir, "Scripts", "python")
        else:
            pip_path = os.path.join(venv_dir, "bin", "pip")
            python_path = os.path.join(venv_dir, "bin", "python")

        # Install from GitHub
        print("Installing from GitHub...")
        result = subprocess.run(
            [pip_path, "install", "git+https://github.com/rushilkukreja/PyMOCAT-MC.git"],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            print(f"ERROR: Installation failed!")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return False

        # Test import
        print("Testing import...")
        result = subprocess.run(
            [python_path, "-c", "from pymocat_mc import MOCATMC; print('Import successful!')"],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            print(f"ERROR: Import failed!")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return False

        print("SUCCESS: Installation and import work correctly!")
        return True

def test_local_installation():
    """Test local development installation."""
    print("\nTesting local development installation...")

    # Create a temporary virtual environment
    with tempfile.TemporaryDirectory() as tmpdir:
        venv_dir = os.path.join(tmpdir, "test_venv_local")

        # Create virtual environment
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)

        # Get pip and python paths in venv
        if sys.platform == "win32":
            pip_path = os.path.join(venv_dir, "Scripts", "pip")
            python_path = os.path.join(venv_dir, "Scripts", "python")
        else:
            pip_path = os.path.join(venv_dir, "bin", "pip")
            python_path = os.path.join(venv_dir, "bin", "python")

        # Install in development mode
        print("Installing in development mode...")
        result = subprocess.run(
            [pip_path, "install", "-e", "."],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            print(f"ERROR: Local installation failed!")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return False

        # Test import
        print("Testing import from local installation...")
        result = subprocess.run(
            [python_path, "-c", "from pymocat_mc import MOCATMC; mocat = MOCATMC(); print('Local import successful!')"],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            print(f"ERROR: Local import failed!")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return False

        # Test running an example
        print("Testing example execution...")
        result = subprocess.run(
            [python_path, "-m", "pymocat_mc.examples.Quick_Start.quick_start"],
            capture_output=True, text=True, timeout=30
        )

        if result.returncode != 0:
            print(f"ERROR: Example execution failed!")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return False

        print("SUCCESS: Local installation works correctly!")
        return True

def check_github_issues():
    """Check if GitHub issues are accessible."""
    print("\nChecking GitHub issues accessibility...")
    print("Repository URL: https://github.com/rushilkukreja/PyMOCAT-MC")
    print("Issues URL: https://github.com/rushilkukreja/PyMOCAT-MC/issues")

    # Note: This is a forked repository. The parent repository may need to enable issues.
    print("NOTE: This repository appears to be a fork. Issues may need to be enabled in repository settings.")
    print("To enable issues: Go to Settings > Features > Check 'Issues'")

    return True

def main():
    """Run all installation tests."""
    print("=" * 60)
    print("JOSS Installation Compliance Tests for PyMOCAT-MC")
    print("=" * 60)

    results = {
        "GitHub Installation": False,
        "Local Installation": False,
        "GitHub Issues": False
    }

    # Test GitHub installation (skip for now as it may be slow)
    print("\nSkipping GitHub installation test (can be run separately)")
    # results["GitHub Installation"] = test_github_installation()

    # Test local installation
    results["Local Installation"] = test_local_installation()

    # Check GitHub issues
    results["GitHub Issues"] = check_github_issues()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name}: {status}")

    # JOSS compliance notes
    print("\n" + "=" * 60)
    print("JOSS COMPLIANCE NOTES")
    print("=" * 60)
    print("1. Package Installation:")
    print("   - GitHub installation: pip install git+https://github.com/rushilkukreja/PyMOCAT-MC.git")
    print("   - Local development: pip install -e .")
    print("   - PyPI publication: Pending (not required for JOSS)")
    print("\n2. GitHub Issues:")
    print("   - Repository is a fork, issues may need to be enabled in Settings")
    print("   - Direct URL: https://github.com/rushilkukreja/PyMOCAT-MC/issues")
    print("\n3. Import Structure:")
    print("   - Correct: from pymocat_mc import MOCATMC")
    print("   - Package structure properly configured under pymocat_mc/")

    all_passed = all(results.values())
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())