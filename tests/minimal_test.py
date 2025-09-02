#!/usr/bin/env python3
"""
Minimal test to verify MOCAT-MC is working
"""

import numpy as np
import sys
import os

# Add python_implementation directory to path
sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
    '..',
    'python_implementation'))

try:
    from mocat_mc import MOCATMC
    print("Successfully imported MOCATMC")
    
    # Try to initialize
    mocat = MOCATMC()
    print("Successfully initialized MOCATMC")
    
    # Try to setup config
    cfg_mc = mocat.setup_mc_config(1, '2020.mat')
    print(f"Successfully created config with {cfg_mc['mat_sats'].shape[0]} initial objects")
    
    # Set minimal simulation
    cfg_mc['n_time'] = 2  # Just 2 time steps
    cfg_mc['skipCollisions'] = 1
    cfg_mc['launch_model'] = 'no_launch'
    cfg_mc['P_frag'] = 0
    
    print("Running minimal simulation...")
    nS, nD, nN, nB, mat_sats = mocat.main_mc(cfg_mc, 1)
    
    print(f"SUCCESS! Final counts: S={nS}, D={nD}, N={nN}, B={nB}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()