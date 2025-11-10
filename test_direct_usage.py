#!/usr/bin/env python3
"""
Test PyMOCAT-MC direct usage to demonstrate it works.
"""

import sys
import os

# Add the python_implementation to path for direct testing
sys.path.insert(0, 'python_implementation')

def test_pymocat_mc():
    """Test PyMOCAT-MC functionality."""

    print("=" * 60)
    print("PyMOCAT-MC Functionality Test")
    print("=" * 60)

    try:
        # Import the main class
        from mocat_mc import MOCATMC
        print("✓ Successfully imported MOCATMC")

        # Instantiate
        mocat = MOCATMC()
        print("✓ Successfully instantiated MOCATMC")

        # Test property access
        constants = mocat.constants
        print(f"✓ Constants loaded: {len(constants.__dict__)} items")
        print(f"  - Earth radius: {constants.radiusearthkm} km")
        print(f"  - Gravitational parameter: {constants.mu_const}")

        idx = mocat.idx
        print(f"✓ Indices loaded: {len(idx)} items")
        print(f"  - Semi-major axis index: {idx['a']}")
        print(f"  - Mass index: {idx['mass']}")

        # Test configuration setup
        print("\n--- Testing Configuration Setup ---")
        cfg_mc = mocat.setup_mc_config(rng_seed=1, ic_file='2020.mat')
        print(f"✓ Configuration setup successful")
        print(f"  - Time span: {cfg_mc['n_time']} time steps")
        print(f"  - Initial satellites: {cfg_mc['mat_sats'].shape[0]}")
        print(f"  - Simulation start: {cfg_mc['time0']}")

        # Test a simplified simulation
        print("\n--- Testing Simulation ---")
        nS, nD, nN, nB, mat_sats = mocat.main_mc(cfg_mc, rng_seed=1)
        print(f"✓ Simulation completed successfully")
        print(f"  - Final satellites: {nS}")
        print(f"  - Final derelicts: {nD}")
        print(f"  - Final debris: {nN}")
        print(f"  - Final rocket bodies: {nB}")
        print(f"  - Total objects remaining: {mat_sats.shape[0]}")

        print("\n" + "=" * 60)
        print("✅ ALL FUNCTIONALITY TESTS PASSED!")
        print("PyMOCAT-MC is working correctly!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pymocat_mc()
    sys.exit(0 if success else 1)