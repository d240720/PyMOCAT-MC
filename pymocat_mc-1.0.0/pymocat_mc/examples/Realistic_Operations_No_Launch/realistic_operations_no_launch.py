"""
Realistic Operations No Launch Scenario
Custom scenario for comparing Python vs MATLAB implementations

Modern space operations parameters without future launches, high-resolution simulation
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pymocat_mc import MOCATMC


def realistic_operations_no_launch():
    """
    Realistic operations scenario without future launches
    """
    print("=== Realistic Operations No Launch Scenario ===")

    # Initialize MOCAT-MC
    mocat = MOCATMC()

    # Fixed parameters for reproducibility
    seed = 42
    ic_file = '2020.mat'

    print(f'Running with seed {seed} and IC file {ic_file}')
    print('Configuring realistic operations parameters (no launches)...')

    # Get base configuration
    cfg_mc = mocat.setup_mc_config(seed, ic_file)

    # === CUSTOM SCENARIO MODIFICATIONS ===

    # Launch configuration (not used since launch_model='no_launch')
    print('- No future launches (launch_model = no_launch)')
    cfg_mc['launchRepeatYrs'] = [2018, 2022]  # Not used with no_launch model
    cfg_mc['launchRepeatSmooth'] = 1  # Not used with no_launch model

    print('- Modern space operations: 85% PMD compliance, 6-unit missions')
    cfg_mc['PMD'] = 0.85
    cfg_mc['missionlifetime'] = int(100 * 0.06)
    cfg_mc['alph'] = 0.02

    print('- High-resolution simulation with 5-day time steps')
    nyears = 100
    tf_prop = cfg_mc['YEAR2MIN'] * nyears * 0.05
    cfg_mc['dt_days'] = 5
    DeltaT = cfg_mc['dt_days'] * cfg_mc['DAY2MIN']
    cfg_mc['tsince'] = np.arange(0, tf_prop + DeltaT, DeltaT)
    cfg_mc['n_time'] = len(cfg_mc['tsince'])

    # Enable limited explosions
    print('- Limited explosions enabled: 5e-7 probability, max 500 fragments')
    cfg_mc['P_frag'] = 5e-7  # Low but non-zero explosion rate
    cfg_mc['max_frag'] = 500  # Reasonable fragment limit

    # Print initial conditions
    initial_pop = cfg_mc['mat_sats'].shape[0]
    repeat_launches = cfg_mc.get('repeatLaunches', np.array([]))
    launches_per_year = len(repeat_launches) if len(repeat_launches) > 0 else 0

    print(f'Initial Population: {initial_pop} objects')
    print(f'Launches per year: {launches_per_year}')
    print(f'Simulation steps: {cfg_mc["n_time"]} time steps')
    print('Starting simulation...')

    # Run simulation
    nS, nD, nN, nB, mat_sats = mocat.main_mc(cfg_mc, seed)

    # Print results
    total_objects = nS + nD + nN + nB
    ratio = nS / total_objects if total_objects > 0 else 0.0

    print(f'\n=== SIMULATION COMPLETE ===')
    print(f'Initial Population: {initial_pop}')
    print(f'Final Population: {total_objects}')
    print(f'Population Change: {total_objects - initial_pop:+d} ({100*(total_objects - initial_pop)/initial_pop:+.1f}%)')
    print(f'Final Distribution:')
    print(f'  Satellites: {nS} ({100*nS/total_objects:.1f}%)')
    print(f'  Derelicts: {nD} ({100*nD/total_objects:.1f}%)')
    print(f'  Debris: {nN} ({100*nN/total_objects:.1f}%)')
    print(f'  Rocket Bodies: {nB} ({100*nB/total_objects:.1f}%)')
    print(f'Satellite ratio: {ratio:.4f}')

    # Create comprehensive plots
    create_comprehensive_plots(
        nS,
        nD,
        nN,
        nB,
        mat_sats,
        'python_realistic_ops_no_launch')

    # Return results for comparison
    return {
        'seed': seed,
        'initial_pop': initial_pop,
        'nS': nS, 'nD': nD, 'nN': nN, 'nB': nB,
        'total_objects': total_objects,
        'satellite_ratio': ratio,
        'mat_sats': mat_sats,
        'cfg_mc': cfg_mc
    }


def create_comprehensive_plots(nS, nD, nN, nB, mat_sats, prefix):
    """
    Create comprehensive plots matching the existing plot structure
    """
    print('\nCreating comprehensive plots...')

    # Define indices (Python uses 0-based indexing)
    idx_a = 0
    idx_ecco = 1
    idx_inclo = 2
    idx_nodeo = 3
    idx_argpo = 4
    idx_mo = 5
    idx_bstar = 6
    idx_mass = 7
    idx_radius = 8
    idx_controlled = 10
    idx_objectclass = 22
    idx_r = [16, 17, 18]
    idx_v = [19, 20, 21]

    # Calculate derived quantities
    altitudes = (mat_sats[:, idx_a] - 1) * 6378.137  # Convert to km
    inclinations = np.rad2deg(mat_sats[:, idx_inclo])

    # Figure 1: Population Summary
    fig1, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))

    # Subplot 1: Bar chart
    ax1.bar(
        ['Satellites',
        'Derelicts',
        'Debris',
        'Rocket Bodies'],
        [nS,
        nD,
        nN,
        nB])
    ax1.set_title('Final Population Distribution - Realistic Operations No Launch')
    ax1.set_ylabel('Number of Objects')
    ax1.grid(True, alpha=0.3)

    # Subplot 2: Pie chart
    labels = ['Satellites', 'Derelicts', 'Debris', 'Rocket Bodies']
    sizes = [nS, nD, nN, nB]
    ax2.pie(sizes, labels=labels, autopct='%1.1f%%')
    ax2.set_title('Population Distribution (Pie Chart)')

    # Subplot 3: Altitude distribution
    ax3.hist(altitudes, bins=20, alpha=0.7, edgecolor='black')
    ax3.set_xlabel('Altitude (km)')
    ax3.set_ylabel('Number of Objects')
    ax3.set_title('Altitude Distribution')
    ax3.grid(True, alpha=0.3)

    # Subplot 4: Inclination distribution
    ax4.hist(inclinations, bins=20, alpha=0.7, edgecolor='black')
    ax4.set_xlabel('Inclination (degrees)')
    ax4.set_ylabel('Number of Objects')
    ax4.set_title('Inclination Distribution')
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        f'{prefix}_figure_1_population_summary.png',
        dpi=150,
        bbox_inches='tight')
    print(f'Saved: {prefix}_figure_1_population_summary.png')
    plt.close()

    # Figure 2: Orbital Elements Analysis
    fig2, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Eccentricity vs Altitude
    axes[0].scatter(mat_sats[:, idx_ecco], altitudes, alpha=0.6, s=20)
    axes[0].set_xlabel('Eccentricity')
    axes[0].set_ylabel('Altitude (km)')
    axes[0].set_title('Eccentricity vs Altitude')
    axes[0].grid(True, alpha=0.3)

    # Inclination vs Altitude
    axes[1].scatter(inclinations, altitudes, alpha=0.6, s=20)
    axes[1].set_xlabel('Inclination (degrees)')
    axes[1].set_ylabel('Altitude (km)')
    axes[1].set_title('Inclination vs Altitude')
    axes[1].grid(True, alpha=0.3)

    # Object Class Distribution
    axes[2].hist(
        mat_sats[:,
        idx_objectclass],
        bins=range(1,
        12),
        alpha=0.7,
        edgecolor='black')
    axes[2].set_xlabel('Object Class')
    axes[2].set_ylabel('Number of Objects')
    axes[2].set_title('Object Class Distribution')
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        f'{prefix}_figure_2_orbital_elements.png',
        dpi=150,
        bbox_inches='tight')
    print(f'Saved: {prefix}_figure_2_orbital_elements.png')
    plt.close()

    # Figure 3: 3D Position Plot
    fig3 = plt.figure(figsize=(10, 8))
    ax3d = fig3.add_subplot(111, projection='3d')

    r = mat_sats[:, idx_r]
    scatter = ax3d.scatter(
        r[:,
        0],
        r[:,
        1],
        r[:,
        2],
        c=altitudes,
        s=20,
        cmap='viridis')

    ax3d.set_xlabel('X (km)')
    ax3d.set_ylabel('Y (km)')
    ax3d.set_zlabel('Z (km)')
    ax3d.set_title('3D Object Positions (colored by altitude) - Realistic Ops No Launch')

    # Set equal aspect ratio
    max_range = np.array([r[:,0].max()-r[:,0].min(),
                         r[:,1].max()-r[:,1].min(),
                         r[:,2].max()-r[:,2].min()]).max() / 2.0
    mid_x = (r[:,0].max()+r[:,0].min()) * 0.5
    mid_y = (r[:,1].max()+r[:,1].min()) * 0.5
    mid_z = (r[:,2].max()+r[:,2].min()) * 0.5
    ax3d.set_xlim(mid_x - max_range, mid_x + max_range)
    ax3d.set_ylim(mid_y - max_range, mid_y + max_range)
    ax3d.set_zlim(mid_z - max_range, mid_z + max_range)

    plt.colorbar(scatter, ax=ax3d, label='Altitude (km)')
    plt.tight_layout()
    plt.savefig(
        f'{prefix}_figure_3_3d_positions.png',
        dpi=150,
        bbox_inches='tight')
    print(f'Saved: {prefix}_figure_3_3d_positions.png')
    plt.close()

    # Figure 4: Altitude vs Eccentricity with Object Types
    fig4, ax = plt.subplots(figsize=(10, 6))

    colors = ['blue', 'red', 'green', 'magenta']
    labels = ['Satellites', 'Derelicts', 'Debris', 'Rocket Bodies']

    # Find indices for each object type
    sat_idx = mat_sats[:, idx_controlled] == 1
    derelict_idx = (
        mat_sats[:,
        idx_controlled] == 0) & (mat_sats[:,
        idx_objectclass] == 1)
    debris_idx = mat_sats[:, idx_objectclass] == 3
    rb_idx = mat_sats[:, idx_objectclass] == 2

    indices = [sat_idx, derelict_idx, debris_idx, rb_idx]

    for i, (idx_mask, color, label) in enumerate(zip(indices, colors, labels)):
        if np.any(idx_mask):
            ax.scatter(mat_sats[idx_mask, idx_ecco], altitudes[idx_mask],
                      c=color, alpha=0.6, s=20, label=label)

    ax.set_xlabel('Eccentricity')
    ax.set_ylabel('Altitude (km)')
    ax.set_title('Altitude vs Eccentricity by Object Type - Realistic Ops No Launch')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        f'{prefix}_figure_4_altitude_eccentricity.png',
        dpi=150,
        bbox_inches='tight')
    print(f'Saved: {prefix}_figure_4_altitude_eccentricity.png')
    plt.close()

    # Figure 5: Summary Statistics
    fig5, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))

    # Altitude Statistics
    stats_data = [np.mean(
        altitudes),
        np.std(altitudes),
        np.min(altitudes),
        np.max(altitudes)]
    ax1.bar(['Mean', 'Std', 'Min', 'Max'], stats_data)
    ax1.set_title('Altitude Statistics (km)')
    ax1.grid(True, alpha=0.3)

    # Eccentricity Statistics
    stats_ecc = [np.mean(mat_sats[:, idx_ecco]), np.std(mat_sats[:, idx_ecco]),
                 np.min(mat_sats[:, idx_ecco]), np.max(mat_sats[:, idx_ecco])]
    ax2.bar(['Mean', 'Std', 'Min', 'Max'], stats_ecc)
    ax2.set_title('Eccentricity Statistics')
    ax2.grid(True, alpha=0.3)

    # Mass Statistics
    stats_mass = [np.mean(
        mat_sats[:,
        idx_mass]),
        np.std(mat_sats[:,
        idx_mass]),
                  np.min(mat_sats[:, idx_mass]), np.max(mat_sats[:, idx_mass])]
    ax3.bar(['Mean', 'Std', 'Min', 'Max'], stats_mass)
    ax3.set_title('Mass Statistics (kg)')
    ax3.grid(True, alpha=0.3)

    # Radius Statistics
    stats_radius = [np.mean(
        mat_sats[:,
        idx_radius]),
        np.std(mat_sats[:,
        idx_radius]),
                    np.min(
                        mat_sats[:,
                        idx_radius]),
                        np.max(mat_sats[:,
                        idx_radius])]
    ax4.bar(['Mean', 'Std', 'Min', 'Max'], stats_radius)
    ax4.set_title('Radius Statistics (m)')
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        f'{prefix}_figure_5_summary_statistics.png',
        dpi=150,
        bbox_inches='tight')
    print(f'Saved: {prefix}_figure_5_summary_statistics.png')
    plt.close()

    # Print summary statistics
    print(f'\n=== DETAILED STATISTICS ===')
    print(f'Mean Altitude: {np.mean(altitudes):.1f} km')
    print(f'Altitude Range: {np.min(altitudes):.1f} - {np.max(altitudes):.1f} km')
    print(f'Mean Eccentricity: {np.mean(mat_sats[:, idx_ecco]):.4f}')
    print(f'Mean Mass: {np.mean(mat_sats[:, idx_mass]):.1f} kg')
    print(f'Mean Radius: {np.mean(mat_sats[:, idx_radius]):.3f} m')

    print('\nAll Python plots created and saved successfully!')


if __name__ == "__main__":
    results = realistic_operations_no_launch()
