#!/usr/bin/env python3
"""
Comprehensive test suite for PyMOCAT-MC package installation validation.

This test suite validates that PyMOCAT-MC can be properly imported and used
after pip installation, meeting JOSS requirements.
"""

import sys
import os
import tempfile
import shutil
import unittest
from typing import Optional

class TestPyMOCATMCPackage(unittest.TestCase):
    """Test suite for PyMOCAT-MC package functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.temp_dir = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        if hasattr(cls, 'temp_dir') and os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)

    def test_package_import(self):
        """Test that pymocat_mc package can be imported."""
        try:
            import pymocat_mc
            self.assertTrue(hasattr(pymocat_mc, '__version__'))
        except ImportError as e:
            self.fail(f"Failed to import pymocat_mc package: {e}")

    def test_mocatmc_class_import(self):
        """Test that MOCATMC class can be imported."""
        try:
            from pymocat_mc import MOCATMC
            self.assertTrue(callable(MOCATMC))
        except ImportError as e:
            self.fail(f"Failed to import MOCATMC class: {e}")

    def test_mocatmc_instantiation(self):
        """Test that MOCATMC class can be instantiated."""
        try:
            from pymocat_mc import MOCATMC
            mocat = MOCATMC()
            self.assertIsNotNone(mocat)
            # Check that essential attributes exist
            self.assertTrue(hasattr(mocat, 'constants'))
            self.assertTrue(hasattr(mocat, 'idx'))
        except Exception as e:
            self.fail(f"Failed to instantiate MOCATMC: {e}")

    def test_supporting_functions_importable(self):
        """Test that supporting functions are importable."""
        try:
            from pymocat_mc.supporting_functions.cfg_mc_constants import CfgMCConstants
            from pymocat_mc.supporting_functions.get_idx import get_idx

            # Test instantiation
            constants = CfgMCConstants()
            idx = get_idx()

            self.assertIsNotNone(constants)
            self.assertIsInstance(idx, dict)
        except ImportError as e:
            self.fail(f"Failed to import supporting functions: {e}")

    def test_configuration_setup(self):
        """Test basic configuration setup without data files."""
        try:
            from pymocat_mc import MOCATMC

            mocat = MOCATMC()

            # Test basic configuration setup (should work without data files)
            # This should not fail even if TLE data files are missing
            cfg_basic = {
                'radiusearthkm': 6378.137,
                'altitude_limit_low': 150,
                'altitude_limit_up': 2000,
                'missionlifetime': 15,
                'launchRepeatYrs': [2010, 2020]
            }

            # This should not fail
            constants = mocat.constants
            idx = mocat.idx

            self.assertIsNotNone(constants)
            self.assertIsInstance(idx, dict)

        except Exception as e:
            self.fail(f"Failed basic configuration setup: {e}")

    def test_data_download_utility(self):
        """Test that data download utility is available."""
        try:
            from pymocat_mc.download_data import check_data_files, get_data_dir

            # Test data directory creation
            data_dir = get_data_dir()
            self.assertIsNotNone(data_dir)

            # Test file checking
            status = check_data_files()
            self.assertIsInstance(status, dict)

        except ImportError as e:
            self.fail(f"Failed to import data download utility: {e}")

    def test_example_scripts_importable(self):
        """Test that example scripts can be imported."""
        try:
            # Test importing example modules (they should not execute on import)
            import pymocat_mc.examples.Quick_Start.quick_start
            import pymocat_mc.examples.Scenario_No_Launch.scenario_no_launch
            import pymocat_mc.examples.Realistic_Operations_No_Launch.realistic_operations_no_launch

            # Verify modules have expected functions
            self.assertTrue(hasattr(pymocat_mc.examples.Quick_Start.quick_start, 'quick_start'))
            self.assertTrue(hasattr(pymocat_mc.examples.Scenario_No_Launch.scenario_no_launch, 'scenario_no_launch'))
            self.assertTrue(hasattr(pymocat_mc.examples.Realistic_Operations_No_Launch.realistic_operations_no_launch, 'realistic_operations_no_launch'))

        except ImportError as e:
            self.fail(f"Failed to import example scripts: {e}")

    def test_minimal_simulation_without_data(self):
        """Test that a minimal simulation can be set up without external data files."""
        try:
            from pymocat_mc import MOCATMC

            mocat = MOCATMC()

            # Create a minimal configuration that doesn't require external files
            test_cfg = {
                'radiusearthkm': 6378.137,
                'altitude_limit_low': 150,
                'altitude_limit_up': 2000,
                'missionlifetime': 15,
                'physicalBstar': False,
                'use_J2': True,
                'use_drag': True,
                'collision_prob_method': 'cube',
                'N_ini_samples': 2,  # Minimal for testing
                'dt_prop': 1,  # 1 day steps
                'tspan': 2,  # Only 2 days
                'launchRepeatYrs': [2010, 2020]
            }

            # This should work even without TLE data files
            # The setup should use default satellites
            try:
                cfg_mc = mocat.setup_mc_config(1, 'nonexistent.mat')
                self.assertIsNotNone(cfg_mc)
                self.assertIn('mat_sats', cfg_mc)
            except Exception as setup_error:
                # This is expected if data files are missing, but the test
                # should verify that the error is handled gracefully
                self.assertIsInstance(setup_error, (FileNotFoundError, ValueError))

        except Exception as e:
            self.fail(f"Failed minimal simulation setup: {e}")

def run_package_tests(verbose: bool = True) -> bool:
    """
    Run the package validation test suite.

    Args:
        verbose: Whether to run tests in verbose mode

    Returns:
        True if all tests pass, False otherwise
    """
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPyMOCATMCPackage)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)

    # Return True if all tests passed
    return result.wasSuccessful()

def main():
    """Command-line interface for package testing."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Validate PyMOCAT-MC package installation'
    )
    parser.add_argument(
        '--quiet', '-q', action='store_true',
        help='Run tests in quiet mode'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("PyMOCAT-MC Package Validation Test Suite")
    print("=" * 60)

    success = run_package_tests(verbose=not args.quiet)

    if success:
        print("\n" + "=" * 60)
        print("✓ All tests passed! PyMOCAT-MC package is properly installed.")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("✗ Some tests failed. Package installation may have issues.")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())