#!/usr/bin/env python3
"""
Scenario No Launch - Python Implementation
Equivalent of Scenario_No_Launch.m

This script runs multiple MOCAT-MC simulations with different random seeds
and plots the evolution of decayed objects over time.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add parent directories to path to import mocat_mc (go up to python_implementation)
current_dir = os.path.dirname(os.path.abspath(__file__))
python_impl_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(python_impl_dir)

from mocat_mc import MOCATMC


def scenario_no_launch():
    """
    Scenario No Launch - runs 3 simulations with different seeds
    and plots population evolution over time
    """
    print("=== Scenario No Launch ===")

    # Initialize MOCAT-MC
    mocat = MOCATMC()

    # Initial condition file
    ic_file = '2020.mat'

    # Time vector (not directly used in this scenario but kept for reference)
    t = np.arange(1, 362, 5)  # 1:5:361 in MATLAB

    # Run simulations for 3 different seeds
    # Initialize with placeholder size, will resize based on actual n_time
    deorbit_list_python = []

    for idx in range(3):
        seed = idx + 1  # Convert to 1-based indexing like MATLAB

        print('MC configuration starting...')
        cfg_mc = mocat.setup_mc_config(seed, ic_file)

        nyears = 100
        tf_prop = cfg_mc['YEAR2MIN'] * nyears * 0.10
        cfg_mc['dt_days'] = 5
        DeltaT = cfg_mc['dt_days'] * cfg_mc['DAY2MIN']
        cfg_mc['tsince'] = np.arange(0, tf_prop + DeltaT, DeltaT)
        cfg_mc['n_time'] = len(cfg_mc['tsince'])

        # Disable collisions for simplicity (like no-launch scenario typically does)
        cfg_mc['skipCollisions'] = 1

        print(f'Seed {seed}')

        print(f'Initial Population:  {cfg_mc["mat_sats"].shape[0]} sats')
        repeat_launches = cfg_mc.get('repeatLaunches', np.array([]))
        launches_per_year = len(repeat_launches) if len(repeat_launches) > 0 else 0
        print(f'Launches per year: {launches_per_year}')
        print('Starting main_mc...')

        # Run simulation with deorbit tracking
        nS, nD, nN, nB, mat_sats, deorbitlist_r = mocat.main_mc_with_deorbit_tracking(cfg_mc, seed)
        deorbit_list_python.append(deorbitlist_r)

        print(f'Simulation {seed} completed: {nS} satellites, {nD} derelicts, {nN} debris, {nB} rocket bodies')

    # Convert to numpy array for plotting
    deorbit_list_python = np.array(deorbit_list_python)

    # Create the population evolution plot
    create_population_evolution_plot(deorbit_list_python)

    print('Scenario No Launch completed successfully!')
    return deorbit_list_python


def create_population_evolution_plot(deorbit_list):
    """
    Create population evolution plot showing decayed objects over time

    Args:
        deorbit_list: 3x730 array of deorbit data for each seed
    """
    print('Creating population evolution plot...')

    # Time vector: (2020-2030), n_time steps
    n_time = deorbit_list.shape[1]
    time_years = np.linspace(2020, 2030, n_time)

    plt.figure(figsize=(12, 8))

    # Plot lines for each seed
    colors = ['blue', 'red', 'green']
    labels = ['Seed 1', 'Seed 2', 'Seed 3']

    for i in range(3):
        plt.plot(time_years, deorbit_list[i, :],
                linewidth=2, color=colors[i], label=labels[i])

    plt.legend()
    plt.xlabel('Time')
    plt.ylabel('Decayed Objects')
    plt.title('Population Evolution - Scenario No Launch')
    plt.xlim([2020, 2030])
    plt.grid(True, alpha=0.3)

    # Save with proper naming convention
    plt.tight_layout()
    plt.savefig('python_scenario_no_launch_figure_1_population_evolution.png',
                dpi=150, bbox_inches='tight')
    print('Saved: python_scenario_no_launch_figure_1_population_evolution.png')
    plt.show()


if __name__ == "__main__":
    deorbit_data = scenario_no_launch()
