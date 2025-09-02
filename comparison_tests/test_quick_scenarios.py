#!/usr/bin/env python3
"""
Quick test scenarios for MOCAT-MC Python implementation
Runs key tests with reduced time steps for faster execution
"""

import numpy as np
import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
    '..',
    'python_implementation'))

from mocat_mc import MOCATMC


def run_quick_test(test_name, seed, ic_file='2020.mat'):
    """Run a quick test scenario"""
    mocat = MOCATMC()
    
    print(f"\n{'='*50}")
    print(f"Test: {test_name}")
    print(f"Seed: {seed}")
    print(f"{'='*50}")
    
    try:
        start_time = time.time()
        
        # Setup base configuration
        cfg_mc = mocat.setup_mc_config(seed, ic_file)
        
        # Apply test-specific settings
        if test_name == "Basic Propagation":
            cfg_mc['n_time'] = 5  # Very short
            cfg_mc['skipCollisions'] = 1
            cfg_mc['P_frag'] = 0
            cfg_mc['launch_model'] = 'no_launch'
            
        elif test_name == "Collision Test":
            cfg_mc['n_time'] = 10
            cfg_mc['dt_days'] = 5
            cfg_mc['skipCollisions'] = 0
            cfg_mc['CUBE_RES'] = 50
            cfg_mc['launch_model'] = 'no_launch'
            
        elif test_name == "Launch Test":
            cfg_mc['n_time'] = 20
            cfg_mc['launch_model'] = 'matsat'
            cfg_mc['launchRepeatYrs'] = [2018, 2020]
            cfg_mc['skipCollisions'] = 1
            
        elif test_name == "Fragmentation Test":
            cfg_mc['n_time'] = 10
            cfg_mc['P_frag'] = 1e-4  # Higher probability for testing
            cfg_mc['max_frag'] = 50
            cfg_mc['skipCollisions'] = 1
            
        elif test_name == "Full Integration":
            cfg_mc['n_time'] = 15
            # All features enabled with defaults
            
        # Get initial stats
        initial_pop = cfg_mc['mat_sats'].shape[0]
        
        # Run simulation
        nS, nD, nN, nB, mat_sats = mocat.main_mc(cfg_mc, seed)
        
        # Calculate results
        elapsed_time = time.time() - start_time
        total_objects = nS + nD + nN + nB
        
        # Print results
        print(f"Initial Population: {initial_pop}")
        print(f"Final Population: {total_objects}")
        print(f"Change: {total_objects - initial_pop:+d}")
        print(f"S={nS}, D={nD}, N={nN}, B={nB}")
        print(f"Time: {elapsed_time:.2f}s")
        
        return {
            'test': test_name,
            'success': True,
            'initial': initial_pop,
            'final': total_objects,
            'nS': nS, 'nD': nD, 'nN': nN, 'nB': nB,
            'time': elapsed_time
        }
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {
            'test': test_name,
            'success': False,
            'error': str(e)
        }


def main():
    """Run quick test suite"""
    print("MOCAT-MC Python Quick Test Suite")
    print("="*50)
    
    tests = [
        ("Basic Propagation", 42),
        ("Collision Test", 123),
        ("Launch Test", 200),
        ("Fragmentation Test", 999),
        ("Full Integration", 1)
    ]
    
    results = []
    for test_name, seed in tests:
        result = run_quick_test(test_name, seed)
        results.append(result)
    
    # Print summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    
    print(f"\n{'Test':<20} {'Status':<10} {'Initial':<8} {'Final':<8} {'Time':<8}")
    print("-"*60)
    
    for r in results:
        if r['success']:
            print(f"{r['test']:<20} {'PASS':<10} {r['initial']:<8} {r['final']:<8} {r['time']:<8.2f}s")
        else:
            print(f"{r['test']:<20} {'FAIL':<10} Error: {r.get('error', '')}")
    
    # Save results
    import json
    with open('quick_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\nResults saved to quick_test_results.json")


if __name__ == "__main__":
    main()