#!/usr/bin/env python3
"""Test script to verify package installation and functionality."""

import sys
import os

def test_import():
    """Test that the package can be imported."""
    try:
        from pymocat_mc import MOCATMC
        print("✓ Package import successful")
        return True
    except ImportError as e:
        print(f"✗ Package import failed: {e}")
        return False

def test_module_run():
    """Test that examples can be run as modules."""
    import subprocess

    # Test if the quick_start module can be found
    result = subprocess.run(
        [sys.executable, "-c",
         "import pymocat_mc.examples.Quick_Start.quick_start; print('✓ Example module found')"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(result.stdout.strip())
        return True
    else:
        print(f"✗ Example module not found: {result.stderr}")
        return False

def test_data_files():
    """Test that data files are accessible."""
    try:
        import pymocat_mc
        import os

        package_dir = os.path.dirname(pymocat_mc.__file__)
        data_dir = os.path.join(package_dir, 'supporting_data')

        if os.path.exists(data_dir):
            print(f"✓ Data directory found at {data_dir}")

            # Check for key data files
            key_files = [
                'dens_jb2008_032020_022224.mat',
                'megaconstellationLaunches.xlsx',
                'TLEhistoric/2020.mat'
            ]

            for file in key_files:
                file_path = os.path.join(data_dir, file)
                if os.path.exists(file_path):
                    print(f"  ✓ {file} found")
                else:
                    print(f"  ✗ {file} missing")

            return True
        else:
            print(f"✗ Data directory not found at {data_dir}")
            return False

    except Exception as e:
        print(f"✗ Error checking data files: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("PyMOCAT-MC Installation Test")
    print("=" * 50)

    tests = [
        ("Import Test", test_import),
        ("Module Test", test_module_run),
        ("Data Files Test", test_data_files),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        results.append(test_func())

    print("\n" + "=" * 50)
    if all(results):
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())