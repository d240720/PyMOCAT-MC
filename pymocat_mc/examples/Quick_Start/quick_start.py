"""
Quick Start example for MOCAT-MC Python implementation
Python equivalent of Quick_Start.m
"""

import numpy as np
from pymocat_mc import MOCATMC


def quick_start():
    """
    Quick Start example
    """
    print("Quick Start")

    # Clear any previous state
    np.random.seed(42)  # For reproducible results

    # Initialize MOCAT-MC
    mocat = MOCATMC()

    # Initial condition file (use default if not found)
    ic_file = '2020.mat'

    # MOCAT MC configuration
    seed = 1  # random number generator seed

    print('MC configuration starting...')
    cfg_mc = mocat.setup_mc_config(seed, ic_file)
    print(f'Seed {seed}')

    # MOCAT MC evolution
    initial_pop = cfg_mc['mat_sats'].shape[0]
    repeat_launches = cfg_mc.get('repeatLaunches', np.array([]))
    launches_per_year = len(repeat_launches) if len(repeat_launches) > 0 else 0

    print(f'Initial Population:  {initial_pop} sats')
    print(f'Launches per year: {launches_per_year}')
    print('Starting main_mc...')

    nS, nD, nN, nB, mat_sats, history = mocat.main_mc(cfg_mc, seed)

    # MOCAT MC postprocess: ratio of satellite (SR) among all space objects
    total_objects = nS + nD + nN + nB
    if total_objects > 0:
        ratio = nS / total_objects
    else:
        ratio = 0.0

    print('Quick Start under no launch scenario done!')
    print(f'Satellite ratio in all space objects after evolution: {ratio:.6f}')

    # Plot time series
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(history['years'], history['S'], label='Active Satellites (S)')
    ax.plot(history['years'], history['D'], label='Derelicts (D)')
    ax.plot(history['years'], history['N'], label='Debris (N)')
    ax.plot(history['years'], history['B'], label='Rocket Bodies (B)')
    ax.plot(history['years'], history['S'] + history['D'] + history['N'] + history['B'],
            label='Total', linestyle='--', color='black')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Objects')
    ax.set_title('LEO Object Population Over Time')
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    plt.savefig('timeseries.png')
    plt.show()

    return nS, nD, nN, nB, mat_sats, history


if __name__ == "__main__":
    quick_start()
