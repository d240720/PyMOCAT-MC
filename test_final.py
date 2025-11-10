#!/usr/bin/env python3
"""
Final test to verify PyMOCAT-MC installation works correctly.
"""

import subprocess
import sys
import tempfile
import os

def test_installation():
    """Test that PyMOCAT-MC can be installed and imported."""

    print("=" * 60)
    print("Testing PyMOCAT-MC Installation")
    print("=" * 60)

    # Create a temporary virtual environment
    with tempfile.TemporaryDirectory() as tmpdir:
        venv_dir = os.path.join(tmpdir, 'test_venv')

        # Create virtual environment
        print("\n1. Creating virtual environment...")
        result = subprocess.run([sys.executable, '-m', 'venv', venv_dir],
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"✗ Failed to create venv: {result.stderr}")
            return False
        print("✓ Virtual environment created")

        # Get paths
        if sys.platform == 'win32':
            pip_path = os.path.join(venv_dir, 'Scripts', 'pip')
            python_path = os.path.join(venv_dir, 'Scripts', 'python')
        else:
            pip_path = os.path.join(venv_dir, 'bin', 'pip')
            python_path = os.path.join(venv_dir, 'bin', 'python')

        # Install from current directory
        print("\n2. Installing PyMOCAT-MC...")
        result = subprocess.run([pip_path, 'install', '-e', '.', '--quiet'],
                              capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"✗ Installation failed: {result.stderr}")
            return False
        print("✓ PyMOCAT-MC installed")

        # Test import
        print("\n3. Testing import...")
        test_script = '''
import sys
try:
    from pymocat_mc import MOCATMC
    print("✓ Successfully imported MOCATMC")
    mocat = MOCATMC()
    print("✓ Successfully instantiated MOCATMC")
    print(f"✓ Constants loaded: {len(mocat.constants.__dict__)} items")
    print(f"✓ Indices loaded: {len(mocat.idx)} items")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)
'''
        result = subprocess.run([python_path, '-c', test_script],
                              capture_output=True, text=True, timeout=30)
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            return False

        # Test that examples can be imported
        print("\n4. Testing example imports...")
        example_test = '''
try:
    from pymocat_mc.examples.Quick_Start import quick_start
    print("✓ Quick Start example importable")
except Exception as e:
    print(f"✗ Example import failed: {e}")
    import sys
    sys.exit(1)
'''
        result = subprocess.run([python_path, '-c', example_test],
                              capture_output=True, text=True, timeout=30)
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            return False

    return True


def test_direct_import():
    """Test import in current Python environment."""

    print("\n5. Testing in current environment...")
    try:
        # Try to import directly (if installed)
        from pymocat_mc import MOCATMC
        print("✓ Direct import works in current environment")
        return True
    except ImportError:
        print("✗ Not installed in current environment (expected)")
        return False


if __name__ == "__main__":
    print("Running PyMOCAT-MC installation tests...\n")

    # Test in clean virtual environment
    success = test_installation()

    if success:
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("PyMOCAT-MC is properly installable with pip")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✗ TESTS FAILED")
        print("Installation issues need to be resolved")
        print("=" * 60)
        sys.exit(1)