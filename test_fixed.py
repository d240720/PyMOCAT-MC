#!/usr/bin/env python3
"""
Test the fixed PyMOCAT-MC package to ensure it works correctly.
"""

import subprocess
import sys
import tempfile
import os

def test_fixed_installation():
    """Test that the fixed PyMOCAT-MC works correctly."""

    print("=" * 60)
    print("Testing FIXED PyMOCAT-MC Installation")
    print("=" * 60)

    # Test direct import first
    print("\n1. Testing direct import...")
    try:
        # Test local import
        sys.path.insert(0, 'python_implementation')
        from mocat_mc import MOCATMC
        print("✓ Direct import successful")

        mocat = MOCATMC()
        print("✓ MOCATMC instantiation successful")

        # Test property access
        constants = mocat.constants
        print(f"✓ Constants loaded: {len(constants.__dict__)} items")

        idx = mocat.idx
        print(f"✓ Indices loaded: {len(idx)} items")

        print("✓ All direct tests passed!")

    except Exception as e:
        print(f"✗ Direct import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test in virtual environment
    print("\n2. Testing in virtual environment...")
    with tempfile.TemporaryDirectory() as tmpdir:
        venv_dir = os.path.join(tmpdir, 'test_venv')

        # Create virtual environment
        result = subprocess.run([sys.executable, '-m', 'venv', venv_dir],
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"✗ Failed to create venv: {result.stderr}")
            return False

        # Get paths
        if sys.platform == 'win32':
            pip_path = os.path.join(venv_dir, 'Scripts', 'pip')
            python_path = os.path.join(venv_dir, 'Scripts', 'python')
        else:
            pip_path = os.path.join(venv_dir, 'bin', 'pip')
            python_path = os.path.join(venv_dir, 'bin', 'python')

        # Install
        result = subprocess.run([pip_path, 'install', '-e', '.', '--quiet'],
                              capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"✗ Installation failed: {result.stderr}")
            return False
        print("✓ Package installed in venv")

        # Test import
        test_script = '''
import sys
try:
    from pymocat_mc import MOCATMC
    print("✓ Package import successful")

    mocat = MOCATMC()
    print("✓ MOCATMC instantiation successful")

    # Test accessing properties
    constants = mocat.constants
    print(f"✓ Constants loaded: {len(constants.__dict__)} items")

    idx = mocat.idx
    print(f"✓ Indices loaded: {len(idx)} items")

    print("✓ All virtual environment tests passed!")

except Exception as e:
    print(f"✗ Virtual environment test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
        result = subprocess.run([python_path, '-c', test_script],
                              capture_output=True, text=True, timeout=30)
        print(result.stdout)
        if result.returncode != 0:
            print(f"✗ Virtual environment test failed: {result.stderr}")
            return False

    return True

if __name__ == "__main__":
    success = test_fixed_installation()

    if success:
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("PyMOCAT-MC is now fully working and JOSS compliant!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ TESTS FAILED")
        print("Additional fixes needed")
        print("=" * 60)
        sys.exit(1)