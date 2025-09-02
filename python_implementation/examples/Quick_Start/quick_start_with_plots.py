#!/usr/bin/env python3
"""
Quick Start with Comprehensive Plots
Python equivalent of Quick_Start_with_plots.m

This script runs the MOCAT-MC simulation and creates comprehensive
visualization plots of the results.
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


def quick_start_with_plots():
    """
    Quick Start function with comprehensive plotting functionality
    Equivalent to Quick_Start_with_plots.m
    """
    print("Quick Start with Comprehensive Plots")

    # Initialize MOCAT-MC
    mocat = MOCATMC()

    # Initial condition file
    ic_file = '2020.mat'

    # MOCAT MC configuration
    seed = 1  # random number generator seed

    print('MC configuration starting...')
    cfg_mc = mocat.setup_mc_config(seed, ic_file)

    # Keep same parameters as MATLAB Quick_Start (P_frag=0, 1 year, no_launch)
    print(f'Seed {seed}')

    # MOCAT MC evolution
    print(f'Initial Population:  {cfg_mc["mat_sats"].shape[0]} sats')
    print(f'Launches per year: {len(cfg_mc.get("repeatLaunches", []))}')
    print('Starting main_mc...')

    nS, nD, nN, nB, mat_sats = mocat.main_mc(cfg_mc, seed)

    # MOCAT MC postprocess: ratio of satellite (SR) among all space objects
    ratio = nS / (nS + nD + nN + nB)
    print('Quick Start under no launch scenario done!')
    print(f'Satellite ratio in all space objects after evolution: {ratio:.6f}')

    # Create Comprehensive Plots
    print('Creating plots...')
    create_comprehensive_plots(nS, nD, nN, nB, mat_sats, mocat.idx)

    print('All plots created successfully!')
    return nS, nD, nN, nB, mat_sats


def create_comprehensive_plots(nS, nD, nN, nB, mat_sats, idx):
    """
    Create comprehensive plots of simulation results

    Args:
        nS, nD, nN, nB: Object counts by type
        mat_sats: Final satellite matrix
        idx: Index dictionary
    """

    # Calculate derived quantities
    altitudes = (mat_sats[:, idx['a']] - 1) * 6378.137  # Convert to km
    inclinations = np.rad2deg(mat_sats[:, idx['inclo']])

    # Figure 1: Population Summary
    plt.figure(figsize=(15, 10))

    plt.subplot(2, 2, 1)
    objects = [nS, nD, nN, nB]
    labels = ['Satellites', 'Derelicts', 'Debris', 'Rocket Bodies']
    colors = ['blue', 'red', 'green', 'magenta']
    plt.bar(labels, objects, color=colors)
    plt.title('Final Population Distribution')
    plt.ylabel('Number of Objects')
    plt.grid(True)
    plt.xticks(rotation=45)

    plt.subplot(2, 2, 2)
    plt.pie(objects, labels=labels, colors=colors, autopct='%1.1f%%')
    plt.title('Population Distribution (Pie Chart)')

    plt.subplot(2, 2, 3)
    plt.hist(altitudes, bins=20, alpha=0.7, edgecolor='black')
    plt.xlabel('Altitude (km)')
    plt.ylabel('Number of Objects')
    plt.title('Altitude Distribution')
    plt.grid(True)

    plt.subplot(2, 2, 4)
    plt.hist(inclinations, bins=20, alpha=0.7, edgecolor='black')
    plt.xlabel('Inclination (degrees)')
    plt.ylabel('Number of Objects')
    plt.title('Inclination Distribution')
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(
        'python_quick_start_figure_1_population_summary.png',
        dpi=150,
        bbox_inches='tight')
    plt.show()

    # Figure 2: Orbital Elements Analysis
    plt.figure(figsize=(15, 5))

    plt.subplot(1, 3, 1)
    plt.scatter(mat_sats[:, idx['ecco']], altitudes, alpha=0.6)
    plt.xlabel('Eccentricity')
    plt.ylabel('Altitude (km)')
    plt.title('Eccentricity vs Altitude')
    plt.grid(True)

    plt.subplot(1, 3, 2)
    plt.scatter(inclinations, altitudes, alpha=0.6)
    plt.xlabel('Inclination (degrees)')
    plt.ylabel('Altitude (km)')
    plt.title('Inclination vs Altitude')
    plt.grid(True)

    plt.subplot(1, 3, 3)
    unique_classes = np.unique(mat_sats[:, idx['objectclass']])
    class_counts = [np.sum(
        mat_sats[:,
        idx['objectclass']] == cls) for cls in unique_classes]
    plt.bar(unique_classes, class_counts, alpha=0.7, edgecolor='black')
    plt.xlabel('Object Class')
    plt.ylabel('Number of Objects')
    plt.title('Object Class Distribution')
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(
        'python_quick_start_figure_2_orbital_elements.png',
        dpi=150,
        bbox_inches='tight')
    plt.show()

    # Figure 3: 3D Position Plot
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    r = mat_sats[:, idx['r']]
    scatter = ax.scatter(
        r[:,
        0],
        r[:,
        1],
        r[:,
        2],
        c=altitudes,
        s=20,
        alpha=0.6,
        cmap='viridis')
    plt.colorbar(scatter, label='Altitude (km)')
    ax.set_xlabel('X (km)')
    ax.set_ylabel('Y (km)')
    ax.set_zlabel('Z (km)')
    ax.set_title('3D Object Positions (colored by altitude)')
    plt.savefig(
        'python_quick_start_figure_3_3d_positions.png',
        dpi=150,
        bbox_inches='tight')
    plt.show()

    # Figure 4: Altitude vs Eccentricity with Object Types
    plt.figure(figsize=(12, 8))

    colors_obj = ['blue', 'red', 'green', 'magenta']
    labels_obj = ['Satellites', 'Derelicts', 'Debris', 'Rocket Bodies']

    # Find indices for each object type
    sat_idx = mat_sats[:, idx['controlled']] == 1
    derelict_idx = (
        mat_sats[:,
        idx['controlled']] == 0) & (mat_sats[:,
        idx['objectclass']] == 1)
    debris_idx = mat_sats[:, idx['objectclass']] == 3
    rb_idx = mat_sats[:, idx['objectclass']] == 2

    indices = [sat_idx, derelict_idx, debris_idx, rb_idx]

    for i, (
        mask,
        color,
        label) in enumerate(zip(indices,
        colors_obj,
        labels_obj)):
        if np.any(mask):
            plt.scatter(mat_sats[mask, idx['ecco']], altitudes[mask],
                       c=color, label=label, alpha=0.6, s=20)

    plt.xlabel('Eccentricity')
    plt.ylabel('Altitude (km)')
    plt.title('Altitude vs Eccentricity by Object Type')
    plt.legend()
    plt.grid(True)
    plt.savefig(
        'python_quick_start_figure_4_altitude_eccentricity.png',
        dpi=150,
        bbox_inches='tight')
    plt.show()

    # Figure 5: Summary Statistics
    plt.figure(figsize=(15, 10))

    plt.subplot(2, 2, 1)
    stats_data = [np.mean(
        altitudes),
        np.std(altitudes),
        np.min(altitudes),
        np.max(altitudes)]
    stats_labels = ['Mean', 'Std', 'Min', 'Max']
    plt.bar(stats_labels, stats_data)
    plt.title('Altitude Statistics (km)')
    plt.grid(True)

    plt.subplot(2, 2, 2)
    stats_ecc = [np.mean(
        mat_sats[:,
        idx['ecco']]),
        np.std(mat_sats[:,
        idx['ecco']]),
                 np.min(
                     mat_sats[:,
                     idx['ecco']]),
                     np.max(mat_sats[:,
                     idx['ecco']])]
    plt.bar(stats_labels, stats_ecc)
    plt.title('Eccentricity Statistics')
    plt.grid(True)

    plt.subplot(2, 2, 3)
    stats_mass = [np.mean(
        mat_sats[:,
        idx['mass']]),
        np.std(mat_sats[:,
        idx['mass']]),
                  np.min(
                      mat_sats[:,
                      idx['mass']]),
                      np.max(mat_sats[:,
                      idx['mass']])]
    plt.bar(stats_labels, stats_mass)
    plt.title('Mass Statistics (kg)')
    plt.grid(True)

    plt.subplot(2, 2, 4)
    stats_radius = [np.mean(
        mat_sats[:,
        idx['radius']]),
        np.std(mat_sats[:,
        idx['radius']]),
                    np.min(
                        mat_sats[:,
                        idx['radius']]),
                        np.max(mat_sats[:,
                        idx['radius']])]
    plt.bar(stats_labels, stats_radius)
    plt.title('Radius Statistics (m)')
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(
        'python_quick_start_figure_5_summary_statistics.png',
        dpi=150,
        bbox_inches='tight')
    plt.show()

    # Print summary statistics
    total_objects = nS + nD + nN + nB
    print('\n=== SUMMARY STATISTICS ===')
    print(f'Total Objects: {total_objects}')
    print(f'Satellites: {nS} ({100*nS/total_objects:.1f}%)')
    print(f'Derelicts: {nD} ({100*nD/total_objects:.1f}%)')
    print(f'Debris: {nN} ({100*nN/total_objects:.1f}%)')
    print(f'Rocket Bodies: {nB} ({100*nB/total_objects:.1f}%)')
    print(f'Mean Altitude: {np.mean(altitudes):.1f} km')
    print(f'Altitude Range: {np.min(altitudes):.1f} - {np.max(altitudes):.1f} km')
    print(f'Mean Eccentricity: {np.mean(mat_sats[:, idx["ecco"]]):.3f}')
    print(f'Mean Mass: {np.mean(mat_sats[:, idx["mass"]]):.1f} kg')
    print(f'Mean Radius: {np.mean(mat_sats[:, idx["radius"]]):.2f} m')


if __name__ == "__main__":
    quick_start_with_plots()
