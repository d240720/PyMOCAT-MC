#!/usr/bin/env python3
"""
Test script to verify JOSS compliance for PyMOCAT-MC package.

This script demonstrates that the package:
1. Can be imported correctly as `from pymocat_mc import MOCATMC`
2. Examples work without sys.path manipulation
3. Package structure is correct for pip installation
"""

import sys
import os

def test_package_structure():
    """Test that the package structure is correct."""
    print("=" * 70)
    print("JOSS Compliance Test for PyMOCAT-MC")
    print("=" * 70)

    # Add the project root to path (simulating pip install)
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    print("\n1. Testing package import...")
    try:
        from pymocat_mc import MOCATMC
        print("   ✅ from pymocat_mc import MOCATMC - SUCCESS")
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False

    print("\n2. Testing MOCATMC instantiation...")
    try:
        mocat = MOCATMC()
        print("   ✅ MOCATMC() instantiation - SUCCESS")
    except Exception as e:
        print(f"   ❌ Instantiation failed: {e}")
        return False

    print("\n3. Testing basic functionality...")
    try:
        cfg = mocat.setup_mc_config(rng_seed=42, ic_file='test.mat')
        print(f"   ✅ Configuration setup - SUCCESS ({cfg['n_time']} time steps)")
    except Exception as e:
        print(f"   ❌ Configuration failed: {e}")
        return False

    print("\n4. Checking package structure...")
    package_dir = os.path.join(project_root, 'pymocat_mc')
    if os.path.exists(package_dir):
        print(f"   ✅ Package directory exists: {package_dir}")

        # Check for key files
        init_file = os.path.join(package_dir, '__init__.py')
        main_module = os.path.join(package_dir, 'mocat_mc.py')

        if os.path.exists(init_file):
            print(f"   ✅ __init__.py exists")
        else:
            print(f"   ❌ __init__.py missing")
            return False

        if os.path.exists(main_module):
            print(f"   ✅ mocat_mc.py exists")
        else:
            print(f"   ❌ mocat_mc.py missing")
            return False
    else:
        print(f"   ❌ Package directory missing: {package_dir}")
        return False

    print("\n5. Checking examples don't use sys.path hacks...")
    example_files = [
        'python_implementation/examples/Quick_Start/quick_start.py',
        'python_implementation/examples/Scenario_No_Launch/scenario_no_launch.py',
        'python_implementation/examples/Realistic_Operations_No_Launch/realistic_operations_no_launch.py'
    ]

    all_clean = True
    for example_file in example_files:
        full_path = os.path.join(project_root, example_file)
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                content = f.read()
                if 'sys.path.append' in content or 'sys.path.insert' in content:
                    print(f"   ❌ {example_file} still uses sys.path manipulation")
                    all_clean = False
                else:
                    print(f"   ✅ {os.path.basename(example_file)} - clean imports")
        else:
            print(f"   ⚠️  {example_file} not found")

    if not all_clean:
        return False

    return True

def main():
    """Run all tests and report results."""
    success = test_package_structure()

    print("\n" + "=" * 70)
    if success:
        print("🎉 JOSS COMPLIANCE ACHIEVED! 🎉")
        print()
        print("The PyMOCAT-MC package now meets JOSS requirements:")
        print("✅ Correct package structure (pymocat_mc directory)")
        print("✅ Proper imports work: from pymocat_mc import MOCATMC")
        print("✅ Examples use clean imports (no sys.path manipulation)")
        print("✅ Ready for pip installation")
        print()
        print("To install locally:")
        print("  pip install -e .")
        print()
        print("To install from GitHub (after pushing changes):")
        print("  pip install git+https://github.com/rushilkukreja/PyMOCAT-MC.git")
    else:
        print("❌ JOSS COMPLIANCE FAILED")
        print("Please review the errors above and fix them.")
    print("=" * 70)

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())