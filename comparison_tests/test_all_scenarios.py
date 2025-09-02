#!/usr/bin/env python3
"""
Comprehensive test suite for MOCAT-MC Python implementation
Tests all major functions and scenarios for MATLAB comparison
"""

import numpy as np
import sys
import os
import time
from datetime import datetime

# Add python_implementation directory to path to import mocat_mc
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
    '..',
    'python_implementation'))

from mocat_mc import MOCATMC


class MOCATTestSuite:
    """MOCATTestSuite class."""
    def __init__(self):
        """Initialize the class."""
        self.mocat = MOCATMC()
        self.results = {}
        
    def run_test(self, test_name, seed, config_modifier, ic_file='2020.mat'):
        """Run a single test scenario"""
        print(f"\n{'='*60}")
        print(f"Running Test: {test_name}")
        print(f"Seed: {seed}, IC File: {ic_file}")
        print(f"{'='*60}")
        
        try:
            # Start timer
            start_time = time.time()
            
            # Setup configuration
            cfg_mc = self.mocat.setup_mc_config(seed, ic_file)
            
            # Apply test-specific modifications
            config_modifier(cfg_mc)
            
            # Get initial stats
            initial_pop = cfg_mc['mat_sats'].shape[0]
            n_time = cfg_mc['n_time']
            dt_days = cfg_mc['dt_days']
            
            # Run simulation
            nS, nD, nN, nB, mat_sats = self.mocat.main_mc(cfg_mc, seed)
            
            # Calculate results
            elapsed_time = time.time() - start_time
            total_objects = nS + nD + nN + nB
            
            # Store results
            result = {
                'test_name': test_name,
                'seed': seed,
                'success': True,
                'initial_pop': initial_pop,
                'final_pop': total_objects,
                'nS': nS,
                'nD': nD,
                'nN': nN,
                'nB': nB,
                'n_time_steps': n_time,
                'dt_days': dt_days,
                'elapsed_time': elapsed_time,
                'satellite_ratio': nS / total_objects if total_objects > 0 else 0,
                'population_change': total_objects - initial_pop,
                'config': {k: v
                    for k, v in cfg_mc.items() if k not in ['mat_sats', 'tsince']},
                'error': None
            }
            
            print(f"Initial Population: {initial_pop}")
            print(f"Final Population: {total_objects} (change: {total_objects - initial_pop:+d})")
            print(f"Final Counts - S: {nS}, D: {nD}, N: {nN}, B: {nB}")
            print(f"Satellite Ratio: {result['satellite_ratio']:.4f}")
            print(f"Execution Time: {elapsed_time:.2f} seconds")
            
        except Exception as e:
            print(f"ERROR in test {test_name}: {str(e)}")
            result = {
                'test_name': test_name,
                'seed': seed,
                'success': False,
                'error': str(e)
            }
            
        self.results[test_name] = result
        return result
    
    # Test configuration functions
    def basic_propagation_config(self, cfg):
        """Test 1: Basic propagation without collisions"""
        cfg['n_time'] = 10
        cfg['skipCollisions'] = 1
        cfg['launch_model'] = 'no_launch'
        cfg['P_frag'] = 0
        
    def collision_detection_config(self, cfg):
        """Test 2: Collision detection"""
        cfg['dt_days'] = 1
        cfg['CUBE_RES'] = 100
        cfg['alph'] = 0.01
        cfg['alph_a'] = 0
        cfg['skipCollisions'] = 0
        cfg['n_time'] = 36  # ~6 months with daily steps
        
    def fragmentation_config(self, cfg):
        """Test 3: Fragmentation/explosion test"""
        cfg['P_frag'] = 1e-5
        cfg['P_frag_cutoff'] = 20
        cfg['max_frag'] = 100
        cfg['n_time'] = 36  # ~6 months
        
    def orbit_control_config(self, cfg):
        """Test 4: Orbit control test"""
        cfg['orbtol'] = 10
        cfg['step_control'] = 5
        cfg['PMD'] = 0.90
        cfg['missionlifetime'] = 5
        
    def no_launch_config(self, cfg):
        """Test 5: No launch baseline"""
        cfg['launch_model'] = 'no_launch'
        cfg['n_time'] = 73  # 1 year
        
    def matsat_launch_config(self, cfg):
        """Test 6: MatSat launch model"""
        cfg['launch_model'] = 'matsat'
        cfg['launchRepeatYrs'] = [2018, 2022]
        cfg['launchRepeatSmooth'] = 0
        cfg['n_time'] = 146  # 2 years
        
    def matsat_smooth_config(self, cfg):
        """Test 7: MatSat with smoothing"""
        cfg['launch_model'] = 'matsat'
        cfg['launchRepeatYrs'] = [2015, 2020]
        cfg['launchRepeatSmooth'] = 1
        cfg['n_time'] = 219  # 3 years
        
    def atmospheric_drag_config(self, cfg):
        """Test 8: Atmospheric drag focus"""
        cfg['altitude_limit_low'] = 200
        cfg['altitude_limit_up'] = 600
        cfg['dt_days'] = 0.5
        cfg['n_time'] = 182  # 3 months with half-day steps
        
    def high_activity_config(self, cfg):
        """Test 9: High activity period"""
        cfg['launch_model'] = 'matsat'
        cfg['launchRepeatYrs'] = [2019, 2022]
        cfg['launchRepeatSmooth'] = 0
        cfg['missionlifetime'] = 5
        cfg['PMD'] = 0.90
        cfg['alph'] = 0.02
        cfg['n_time'] = 365  # 5 years
        
    def extreme_altitude_config(self, cfg):
        """Test 10: Extreme altitude test"""
        cfg['altitude_limit_low'] = 150
        cfg['altitude_limit_up'] = 50000
        cfg['collision_alt_limit'] = 50000
        cfg['n_time'] = 73  # 1 year
        
    def mixed_scenario_config(self, cfg):
        """Test 11: Mixed launch and collision"""
        cfg['launch_model'] = 'matsat'
        cfg['launchRepeatYrs'] = [2018, 2020]
        cfg['skipCollisions'] = 0
        cfg['alph'] = 0.05
        cfg['CUBE_RES'] = 100
        cfg['n_time'] = 146  # 2 years
        
    def full_integration_config(self, cfg):
        """Test 12: Full integration with defaults"""
        # Use all defaults - 1 year simulation
        pass
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*80)
        print("MOCAT-MC PYTHON IMPLEMENTATION TEST SUITE")
        print(f"Started at: {datetime.now()}")
        print("="*80)
        
        # Define all test scenarios
        test_scenarios = [
            # Basic functionality tests
            ("Basic Propagation", 42, self.basic_propagation_config),
            ("Collision Detection", 123, self.collision_detection_config),
            ("Fragmentation Test", 999, self.fragmentation_config),
            ("Orbit Control", 777, self.orbit_control_config),
            
            # Launch model tests
            ("No Launch Baseline", 100, self.no_launch_config),
            ("MatSat Launch", 200, self.matsat_launch_config),
            ("MatSat Smoothed", 300, self.matsat_smooth_config),
            
            # Environmental tests
            ("Atmospheric Drag", 333, self.atmospheric_drag_config),
            ("Extreme Altitudes", 1100, self.extreme_altitude_config),
            
            # Complex scenarios
            ("High Activity Period", 500, self.high_activity_config),
            ("Mixed Launch/Collision", 600, self.mixed_scenario_config),
            ("Full Integration", 1, self.full_integration_config),
        ]
        
        # Run each test
        for test_name, seed, config_func in test_scenarios:
            self.run_test(test_name, seed, config_func)
        
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*80)
        print("TEST RESULTS SUMMARY")
        print("="*80)
        
        successful = sum(
            1 for r in self.results.values() if r.get('success',
            False))
        total = len(self.results)
        
        print(f"\nTotal Tests: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {total - successful}")
        
        print("\nDetailed Results:")
        print(f"{'Test Name':<25} {'Status':<10} {'Initial':<8} {'Final':<8} {'S':<6} {'D':<6} {'N':<6} {'B':<6} {'Time(s)':<8}")
        print("-" * 100)
        
        for test_name, result in self.results.items():
            if result.get('success', False):
                print(f"{test_name:<25} {'PASS':<10} "
                      f"{result['initial_pop']:<8} {result['final_pop']:<8} "
                      f"{result['nS']:<6} {result['nD']:<6} "
                      f"{result['nN']:<6} {result['nB']:<6} "
                      f"{result['elapsed_time']:<8.2f}")
            else:
                print(f"{test_name:<25} {'FAIL':<10} Error: {result.get('error', 'Unknown')}")
        
        # Save results to file
        self.save_results()
        
    def save_results(self):
        """Save results to file for MATLAB comparison"""
        import json
        
        filename = f"python_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\nResults saved to: {filename}")


if __name__ == "__main__":
    # Run test suite
    test_suite = MOCATTestSuite()
    test_suite.run_all_tests()