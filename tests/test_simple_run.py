#!/usr/bin/env python3
"""Simple test run with 1 time step"""

import numpy as np
import sys
import os
import time

sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
    '..',
    'python_implementation'))

try:
    from pymocat_mc import MOCATMC
    
    print("Running simple 1-step simulation...")
    start_time = time.time()
    
    # Initialize
    mocat = MOCATMC()
    
    # Setup with minimal config
    cfg_mc = mocat.setup_mc_config(42, '2020.mat')
    
    # Extremely minimal simulation
    cfg_mc['n_time'] = 1  # Just 1 time step
    cfg_mc['skipCollisions'] = 1
    cfg_mc['launch_model'] = 'no_launch'
    cfg_mc['P_frag'] = 0
    
    print(f"Initial population: {cfg_mc['mat_sats'].shape[0]}")
    print("Starting simulation...")
    
    # Run simulation
    nS, nD, nN, nB, mat_sats = mocat.main_mc(cfg_mc, 42)
    
    elapsed = time.time() - start_time
    total = nS + nD + nN + nB
    
    print(f"SUCCESS!")
    print(f"Results: S={nS}, D={nD}, N={nN}, B={nB} (Total: {total})")
    print(f"Time: {elapsed:.2f} seconds")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()