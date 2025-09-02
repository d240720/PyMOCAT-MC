#!/usr/bin/env python3
"""
Generate real timeseries data from actual Python simulation runs
This script runs the Full Default scenario and captures time evolution data
"""

import sys
import os
import numpy as np
import json
from datetime import datetime

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
python_dir = os.path.join(root_dir, 'python_implementation')
sys.path.append(python_dir)

from mocat_mc import MOCATMC


def run_and_save_timeseries():
    """Run Full Default scenario and save real timeseries data"""
    
    print("Running Full Default scenario to generate real timeseries data...")
    print("This will take approximately 1-2 seconds...")
    
    # Initialize MOCAT-MC
    mocat = MOCATMC()
    
    # Setup configuration for Full Default scenario (1 year)
    cfg_mc = mocat.setup_mc_config(rng_seed=1, ic_file='2020.mat')
    
    # Run simulation
    start_time = datetime.now()
    nS, nD, nN, nB, mat_sats = mocat.main_mc(cfg_mc, 1)
    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds()
    
    print(f"Simulation completed in {execution_time:.2f} seconds")
    
    # Extract timeseries data
    def extract_timeseries(val, n_time):
        """Extract timeseries from simulation output"""
        if hasattr(val, 'tolist'):
            return val.tolist()
        elif hasattr(val, '__len__'):
            return list(val)
        else:
            # Single value - this shouldn't happen for timeseries
            return [val] * n_time
    
    n_time = cfg_mc['n_time']
    
    # Save Python timeseries data
    python_timeseries = {
        'scenario': 'Full Default',
        'description': 'Real timeseries data from Python MOCAT-MC simulation',
        'execution_time': execution_time,
        'n_time': n_time,
        'tsince': cfg_mc['tsince'].tolist(),
        'time_years': (cfg_mc['tsince'] / (365.25 * 1440)).tolist(),
        'nS': extract_timeseries(nS, n_time),
        'nD': extract_timeseries(nD, n_time),
        'nN': extract_timeseries(nN, n_time),
        'nB': extract_timeseries(nB, n_time),
        'final_counts': {
            'nS': int(nS[-1] if hasattr(nS, '__len__') else nS),
            'nD': int(nD[-1] if hasattr(nD, '__len__') else nD),
            'nN': int(nN[-1] if hasattr(nN, '__len__') else nN),
            'nB': int(nB[-1] if hasattr(nB, '__len__') else nB)
        },
        'timestamp': datetime.now().isoformat()
    }
    
    # Calculate total population over time
    total_pop = []
    for i in range(n_time):
        total = (python_timeseries['nS'][i] + 
                python_timeseries['nD'][i] + 
                python_timeseries['nN'][i] + 
                python_timeseries['nB'][i])
        total_pop.append(total)
    python_timeseries['total_population'] = total_pop
    
    # Save to file
    output_file = os.path.join(current_dir, 'python_full_default_timeseries.json')
    with open(output_file, 'w') as f:
        json.dump(python_timeseries, f, indent=2)
    
    print(f"Saved Python timeseries data to: {output_file}")
    print(f"Final population counts:")
    print(f"  Active Satellites (S): {python_timeseries['final_counts']['nS']}")
    print(f"  Derelicts (D): {python_timeseries['final_counts']['nD']}")
    print(f"  Debris (N): {python_timeseries['final_counts']['nN']}")
    print(f"  Rocket Bodies (B): {python_timeseries['final_counts']['nB']}")
    print(f"  Total: {python_timeseries['final_counts']['nS'] + python_timeseries['final_counts']['nD'] + python_timeseries['final_counts']['nN'] + python_timeseries['final_counts']['nB']}")
    
    return python_timeseries


if __name__ == "__main__":
    run_and_save_timeseries()