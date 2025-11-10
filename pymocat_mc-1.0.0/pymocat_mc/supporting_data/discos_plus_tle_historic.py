#!/usr/bin/env python3
"""
Merge TLE and DISCOS data - for historic TLEs (YYYY.csv)
Python equivalent of discos_plus_TLE_historic.m

This script processes TLE CSV files and DISCOS data to create
combined satellite datasets for MOCAT-MC simulations.

Based on: supporting_data/TLEhistoric/discos_plus_TLE_historic.m
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.io import loadmat, savemat
import glob
import time
import os
from datetime import datetime
import warnings

# Add parent directories to path for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from supporting_functions.objclass2int import objclass2int
    from supporting_functions.getidx import get_idx
    from supporting_functions.jd2date import jd2date
except ImportError:
    print("Warning: Some supporting functions not available. Creating stub functions.")
    def objclass2int(obj_class, mode=1):
        """Stub function for object class conversion"""
        if isinstance(obj_class, str):
            # Basic mapping for common object types
            class_map = {
                'PAYLOAD': 1, 'ROCKET BODY': 2, 'DEBRIS': 3,
                'UNKNOWN': 10, 'OTHER DEBRIS': 10
            }
            return class_map.get(obj_class.upper(), 10)
        return obj_class

    def get_idx():
        """Return standard index mapping"""
        idx = {}
        idx['a'] = 0; idx['ecco'] = 1; idx['inclo'] = 2
        idx['nodeo'] = 3; idx['argpo'] = 4; idx['mo'] = 5
        idx['bstar'] = 6; idx['mass'] = 7; idx['radius'] = 8
        idx['error'] = 9; idx['controlled'] = 10; idx['a_desired'] = 11
        idx['missionlife'] = 12; idx['constel'] = 13; idx['date_created'] = 14
        idx['launch_date'] = 15; idx['r'] = [16, 17, 18]; idx['v'] = [19, 20, 21]
        idx['objectclass'] = 22; idx['ID'] = 23
        return idx


def julian_date_from_string(date_str):
    """Convert date string to Julian date"""
    try:
        if pd.isna(date_str) or date_str == '':
            return np.nan
        dt = pd.to_datetime(date_str)
        # Julian date calculation
        a = (14 - dt.month) // 12
        y = dt.year + 4800 - a
        m = dt.month + 12 * a - 3
        jd = dt.day \
            + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        return float(jd)
    except:
        return np.nan


def process_discos_plus_tle_historic():
    """
    Main function to merge TLE and DISCOS data for historic datasets
    """
    print("=== DISCOS + TLE Historic Data Processing ===")
    start_time = time.time()

    # Constants
    RADIUS_EARTH_KM = 6378.137

    # Get index mapping
    idx = get_idx()

    # Find CSV files
    csv_files = glob.glob('*.csv')
    if not csv_files:
        print("No CSV files found in current directory")
        return

    print(f"Found {len(csv_files)} CSV files")

    # Load DISCOS data
    discos_file = 'd_2023.mat'
    if not os.path.exists(discos_file):
        print(f"Warning: {discos_file} not found. Skipping DISCOS data integration.")
        d = None
    else:
        print(f"Loading DISCOS data from {discos_file}...")
        discos_data = loadmat(discos_file)
        d = discos_data.get('d', None)
        if d is not None:
            print(f'DISCOS data number of objects: {len(d)}')
            if len(d) > 0:
                print('DISCOS data headers:')
                if hasattr(d[0], 'dtype') and d[0].dtype.names:
                    print(d[0].dtype.names)

    # Process DISCOS data if available
    dd = None
    ddsatnos = None
    if d is not None:
        dd, ddsatnos = process_discos_data(d)

    # Process each CSV file
    for file_idx, csv_file in enumerate(csv_files):
        if file_idx < 16:  # Skip first 16 files as in MATLAB version
            continue

        print(f"\n=== Processing {csv_file} ===")

        try:
            # Read TLE data
            print(f"Reading TLE data from {csv_file}...")
            tle_data = pd.read_csv(csv_file)

            # Remove duplicates, keeping last entry per NORAD ID
            if 'NORAD_CAT_ID' in tle_data.columns:
                tle_data = tle_data.drop_duplicates(
                    subset='NORAD_CAT_ID',
                    keep='last')

            print(f'TLE data number of unique objects: {len(tle_data)}')

            # Filter out temporary satellite IDs (> 80000)
            sat_ids = tle_data['NORAD_CAT_ID'].values
            temp_sats = sat_ids > 80000
            temp_count = np.sum(temp_sats)

            print(f'{temp_count} of {len(sat_ids)} ({temp_count/len(sat_ids)*100:.1f}%) '
                  f'TLE satnos are > 80000 (temporary designations); removing...')

            tle_data = tle_data[tle_data['NORAD_CAT_ID'] <= 80000]
            sat_ids = tle_data['NORAD_CAT_ID'].values

            # Process DISCOS data for these satellites
            dmass, dradius, dobj = process_satellite_data(
                sat_ids,
                dd,
                ddsatnos)

            # Create combined mat_sats matrix
            mat_sats = create_combined_matsats(
                tle_data,
                dmass,
                dradius,
                dobj,
                RADIUS_EARTH_KM)

            # Save the results
            output_file = csv_file.replace('.csv', '.mat')
            savemat(output_file, {'mat_sats': mat_sats})
            print(f'SAVED: {output_file}')

            # Create diagnostic plots
            create_diagnostic_plots(mat_sats, idx, RADIUS_EARTH_KM, csv_file)

        except Exception as e:
            print(f"Error processing {csv_file}: {str(e)}")
            continue

    elapsed_time = time.time() - start_time
    print(f"\n=== Processing Complete ({elapsed_time:.1f} seconds) ===")


def process_discos_data(d):
    """Process DISCOS data to extract relevant information"""
    print("Processing DISCOS data...")

    # Extract attributes (assuming d is structured data)
    dd = []
    ddsatnos = []

    # This is a simplified version - actual implementation would depend on
    # the exact structure of the DISCOS .mat file
    try:
        for i, entry in enumerate(d):
            if hasattr(
                entry,
                'attributes') or (hasattr(entry,
                'dtype') and 'attributes' in entry.dtype.names):
                # Extract satellite number if available
                attrs = entry['attributes'] if hasattr(
                    entry,
                    'attributes') else entry[entry.dtype.names.index('attributes')]
                if 'satno' in attrs and attrs['satno'] is not None and attrs['satno'] != '':
                    dd.append(attrs)
                    ddsatnos.append(int(attrs['satno']))
    except Exception as e:
        print(f"Warning: Could not process DISCOS data structure: {e}")
        return None, None

    if dd:
        print(f'{len(dd)} / {len(d)} DISCOS data has NORAD satellite number '
              f'({len(dd)/len(d)*100:.1f}%)')

        # Remove duplicates
        unique_satnos, unique_indices = np.unique(ddsatnos, return_index=True)
        dd = [dd[i] for i in unique_indices]
        ddsatnos = unique_satnos.tolist()

        print(f'After removing duplicates: {len(dd)} unique DISCOS entries')

    return dd, ddsatnos


def process_satellite_data(sat_ids, dd, ddsatnos):
    """Extract mass, radius, and object class from DISCOS data"""
    n_sats = len(sat_ids)
    dmass = np.zeros(n_sats)
    dradius = np.zeros(n_sats)
    dobj = np.full(n_sats, np.nan)
    missing_satnos = []

    if dd is None or ddsatnos is None:
        print("No DISCOS data available - using default values")
        return dmass, dradius, dobj

    print("Extracting satellite physical properties from DISCOS...")

    # Statistics tracking
    has_xsect = 0
    has_diameter = 0
    has_mass = 0

    for i, sat_id in enumerate(sat_ids):
        try:
            # Find matching DISCOS entry
            discos_idx = None
            if sat_id in ddsatnos:
                discos_idx = ddsatnos.index(sat_id)

            if discos_idx is not None:
                discos_entry = dd[discos_idx]

                # Extract mass
                if 'mass' in discos_entry and discos_entry['mass'] is not None:
                    dmass[i] = float(discos_entry['mass'])
                    has_mass += 1

                # Extract radius (prefer xSectAvg)
                if 'xSectAvg' in discos_entry and discos_entry['xSectAvg'] is not None:
                    dradius[i] = np.sqrt(float(discos_entry['xSectAvg']) / np.pi)
                    has_xsect += 1
                elif 'diameter' in discos_entry and discos_entry['diameter'] is not None:
                    dradius[i] = float(discos_entry['diameter']) / 2.0
                    has_diameter += 1

                # Extract object class
                if 'objectClass' in discos_entry and discos_entry['objectClass'] is not None:
                    try:
                        dobj[i] = objclass2int(discos_entry['objectClass'], 1)
                    except:
                        print(f'Warning: Unknown object class for NORAD {sat_id}: '
                              f'{discos_entry["objectClass"]} --> Other Debris (10)')
                        dobj[i] = 10

            # Special cases (as in MATLAB version)
            elif sat_id == 53239 or sat_id == 54216:
                dobj[i] = 1  # Chinese payloads
            else:
                missing_satnos.append(sat_id)

        except Exception as e:
            print(f"Warning: Error processing satellite {sat_id}: {e}")
            missing_satnos.append(sat_id)

    # Print statistics
    n_matched = len(sat_ids) - len(missing_satnos)
    if n_matched > 0:
        print(f'Percentage of matched DISCOS objects with attributes:')
        print(f'  xSectAvg: {has_xsect/n_matched*100:.1f}%')
        print(f'  diameter: {has_diameter/n_matched*100:.1f}%')
        print(f'  mass: {has_mass/n_matched*100:.1f}%')

    print(f'{len(missing_satnos)} of {len(sat_ids)} ({len(missing_satnos)/len(sat_ids)*100:.1f}%) '
          f'TLE objects are missing from DISCOS')

    return dmass, dradius, dobj


def create_combined_matsats(tle_data, dmass, dradius, dobj, radius_earth_km):
    """Create combined mat_sats matrix from TLE and DISCOS data"""
    n_sats = len(tle_data)

    # Initialize arrays
    zeros_array = np.zeros(n_sats)
    nans_array = np.full(n_sats, np.nan)

    # Required TLE columns (handle missing columns gracefully)
    def get_column_safe(df, col_name, default=0.0):
        """Get column safe."""
        if col_name in df.columns:
            return df[col_name].values
        else:
            print(f"Warning: Column '{col_name}' not found, using default value {default}")
            return np.full(len(df), default)

    # Extract TLE data
    semimajor_axis = get_column_safe(
        tle_data,
        'SEMIMAJOR_AXIS') / radius_earth_km
    eccentricity = get_column_safe(tle_data, 'ECCENTRICITY')
    inclination = np.deg2rad(get_column_safe(tle_data, 'INCLINATION'))
    ra_of_asc_node = np.deg2rad(get_column_safe(tle_data, 'RA_OF_ASC_NODE'))
    arg_of_pericenter = np.deg2rad(
        get_column_safe(tle_data,
        'ARG_OF_PERICENTER'))
    mean_anomaly = np.deg2rad(get_column_safe(tle_data, 'MEAN_ANOMALY'))
    bstar = get_column_safe(tle_data, 'BSTAR')
    norad_cat_id = get_column_safe(tle_data, 'NORAD_CAT_ID')

    # Handle launch dates
    launch_dates = zeros_array.copy()
    if 'LAUNCH_DATE' in tle_data.columns:
        for i, date_str in enumerate(tle_data['LAUNCH_DATE']):
            launch_dates[i] = julian_date_from_string(date_str)

    # Create mat_sats matrix following MOCAT-MC format
    # [a, ecco, inclo, nodeo, argpo, mo, bstar, mass, radius,
    #  error, controlled, a_desired, missionlife, constel, date_created,
    #  launch_date, r1, r2, r3, v1, v2, v3, objectclass, ID]

    mat_sats = np.column_stack([
        semimajor_axis,      # col 1: a
        eccentricity,        # col 2: ecco
        inclination,         # col 3: inclo
        ra_of_asc_node,      # col 4: nodeo
        arg_of_pericenter,   # col 5: argpo
        mean_anomaly,        # col 6: mo
        bstar,               # col 7: bstar
        dmass,               # col 8: mass
        dradius,             # col 9: radius
        zeros_array,         # col 10: error
        zeros_array,         # col 11: controlled
        zeros_array,         # col 12: a_desired
        zeros_array,         # col 13: missionlife
        zeros_array,         # col 14: constel
        nans_array,          # col 15: date_created
        launch_dates,        # col 16: launch_date
        zeros_array,         # col 17: r1
        zeros_array,         # col 18: r2
        zeros_array,         # col 19: r3
        zeros_array,         # col 20: v1
        zeros_array,         # col 21: v2
        zeros_array,         # col 22: v3
        dobj,                # col 23: objectclass
        norad_cat_id         # col 24: ID
    ])

    print(f"Created mat_sats matrix with shape: {mat_sats.shape}")
    return mat_sats


def create_diagnostic_plots(mat_sats, idx, radius_earth_km, filename):
    """Create diagnostic plots for the processed data"""
    print(f"Creating diagnostic plots for {filename}...")

    try:
        fig, axes = plt.subplots(3, 5, figsize=(20, 15))
        fig.suptitle(f'Diagnostic Plots - {filename}', fontsize=16)

        # Plot 1: Altitude vs Eccentricity
        altitudes = (mat_sats[:, idx['a']] - 1) * radius_earth_km
        axes[0,0].scatter(altitudes, mat_sats[:, idx['ecco']], alpha=0.6, s=1)
        axes[0,0].set_xlabel('Altitude (km)')
        axes[0,0].set_ylabel('Eccentricity')
        axes[0,0].grid(True, alpha=0.3)

        # Plot 2: Inclination histogram
        inclinations_deg = np.rad2deg(mat_sats[:, idx['inclo']])
        axes[0,1].hist(inclinations_deg, bins=30, alpha=0.7, edgecolor='black')
        axes[0,1].set_xlabel('Inclination (degrees)')
        axes[0,1].set_ylabel('Count')
        axes[0,1].grid(True, alpha=0.3)

        # Plot 3: RAAN histogram
        raan_deg = np.rad2deg(mat_sats[:, idx['nodeo']])
        axes[0,2].hist(raan_deg, bins=30, alpha=0.7, edgecolor='black')
        axes[0,2].set_xlabel('RAAN (degrees)')
        axes[0,2].set_ylabel('Count')
        axes[0,2].grid(True, alpha=0.3)

        # Plot 4: Argument of perigee histogram
        argp_deg = np.rad2deg(mat_sats[:, idx['argpo']])
        axes[0,3].hist(argp_deg, bins=30, alpha=0.7, edgecolor='black')
        axes[0,3].set_xlabel('Arg of Perigee (degrees)')
        axes[0,3].set_ylabel('Count')
        axes[0,3].grid(True, alpha=0.3)

        # Plot 5: Mean anomaly histogram
        ma_deg = np.rad2deg(mat_sats[:, idx['mo']])
        axes[0,4].hist(ma_deg, bins=30, alpha=0.7, edgecolor='black')
        axes[0,4].set_xlabel('Mean Anomaly (degrees)')
        axes[0,4].set_ylabel('Count')
        axes[0,4].grid(True, alpha=0.3)

        # Plot 6: B* histogram
        valid_bstar = mat_sats[:, idx['bstar']][~np.isnan(
            mat_sats[:,
            idx['bstar']])]
        if len(valid_bstar) > 0:
            axes[1,0].hist(valid_bstar, bins=50, alpha=0.7, edgecolor='black')
            axes[1,0].set_xlabel('B*')
            axes[1,0].set_ylabel('Count')
            axes[1,0].set_yscale('log')
            axes[1,0].grid(True, alpha=0.3)

        # Plot 7: Mass histogram
        valid_mass = mat_sats[:, idx['mass']][mat_sats[:, idx['mass']] > 0]
        if len(valid_mass) > 0:
            axes[1,1].hist(valid_mass, bins=50, alpha=0.7, edgecolor='black')
            axes[1,1].set_xlabel('Mass (kg)')
            axes[1,1].set_ylabel('Count')
            axes[1,1].set_yscale('log')
            axes[1,1].set_xlim(np.percentile(valid_mass, [0, 99.95]))
            axes[1,1].grid(True, alpha=0.3)

        # Plot 8: Radius histogram
        valid_radius = mat_sats[:, idx['radius']][mat_sats[:, idx['radius']] > 0]
        if len(valid_radius) > 0:
            axes[1,2].hist(valid_radius, bins=50, alpha=0.7, edgecolor='black')
            axes[1,2].set_xlabel('Radius (m)')
            axes[1,2].set_ylabel('Count')
            axes[1,2].set_yscale('log')
            axes[1,2].set_xlim(np.percentile(valid_radius, [0, 99.95]))
            axes[1,2].grid(True, alpha=0.3)

        # Plot 9: Launch date histogram
        valid_launch_dates = mat_sats[:, idx['launch_date']][~np.isnan(
            mat_sats[:,
            idx['launch_date']])]
        if len(valid_launch_dates) > 0:
            axes[1,3].hist(
                valid_launch_dates,
                bins=30,
                alpha=0.7,
                edgecolor='black')
            axes[1,3].set_xlabel('Launch Date (Julian)')
            axes[1,3].set_ylabel('Count')
            axes[1,3].grid(True, alpha=0.3)

        # Plot 10: Object class histogram
        valid_objclass = mat_sats[:, idx['objectclass']][~np.isnan(
            mat_sats[:,
            idx['objectclass']])]
        if len(valid_objclass) > 0:
            axes[1,4].hist(
                valid_objclass,
                bins=range(1,
                12),
                alpha=0.7,
                edgecolor='black')
            axes[1,4].set_xlabel('Object Class')
            axes[1,4].set_ylabel('Count')
            axes[1,4].grid(True, alpha=0.3)

        # Plot 11: Mass vs Radius
        mass_radius_valid = (
            mat_sats[:,
            idx['mass']] > 0) & (mat_sats[:,
            idx['radius']] > 0)
        if np.any(mass_radius_valid):
            axes[2,0].scatter(mat_sats[mass_radius_valid, idx['radius']],
                            mat_sats[mass_radius_valid, idx['mass']],
                            alpha=0.6, s=1)
            axes[2,0].set_xlabel('Radius (m)')
            axes[2,0].set_ylabel('Mass (kg)')
            axes[2,0].set_yscale('log')
            axes[2,0].grid(True, alpha=0.3)

        # Hide unused subplots
        for i in range(1, 5):
            axes[2,i].set_visible(False)

        plt.tight_layout()
        plot_filename = f'python_diagnostic_{filename.replace(".csv", "")}.png'
        plt.savefig(plot_filename, dpi=150, bbox_inches='tight')
        print(f'Saved diagnostic plot: {plot_filename}')
        plt.close()

    except Exception as e:
        print(f"Warning: Could not create diagnostic plots: {e}")


if __name__ == "__main__":
    # Change to the directory containing the CSV files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    process_discos_plus_tle_historic()
