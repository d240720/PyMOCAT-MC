#!/usr/bin/env python3
"""
Configuration for MC run - Historic TLE Setup
Python equivalent of setupTLE_LNT_historic.m

This script configures MOCAT-MC for historic TLE scenarios with
long-term evolution studies.

Based on: supporting_data/TLEhistoric/setupTLE_LNT_historic.m
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from scipy.io import loadmat, savemat
from scipy.stats import multivariate_normal
import os
import sys
import warnings

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from supporting_functions.getgravc import getgravc
    from supporting_functions.getidx import get_idx
    from supporting_functions.jd2date import jd2date
    from supporting_functions.objclass2int import objclass2int
except ImportError:
    print("Warning: Some supporting functions not available. Creating stub functions.")

    def getgravc(whichconst=84):
        """Stub function for gravitational constants"""
        # WGS84 constants
        tumin = 13.446851121  # time units per minute
        mu_const = 398600.5  # km^3/s^2
        radiusearthkm = 6378.137  # km
        xke = 60.0  # minutes per second
        j2 = 0.00108262998905  # J2 coefficient
        j3 = -0.00000253215306  # J3 coefficient
        j4 = -0.00000161098761  # J4 coefficient
        j3oj2 = j3 / j2
        return tumin, mu_const, radiusearthkm, xke, j2, j3, j4, j3oj2

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

    def jd2date(jd):
        """Convert Julian date to datetime"""
        # Simple conversion - may need refinement
        import datetime as dt
        epoch = dt.datetime(1858, 11, 17)  # Modified Julian Date epoch
        return epoch + dt.timedelta(days=jd - 2400000.5)

    def objclass2int(obj_class, mode=1):
        """Stub function for object class conversion"""
        if isinstance(obj_class, str):
            class_map = {
                'PAYLOAD': 1, 'ROCKET BODY': 2, 'DEBRIS': 3,
                'UNKNOWN': 10, 'OTHER DEBRIS': 10
            }
            return class_map.get(obj_class.upper(), 10)
        return obj_class


def setup_tle_lnt_historic(rng_seed=1, tle_year=2020):
    """
    Configuration for historic TLE Monte Carlo runs

    Args:
        rng_seed: Random number generator seed
        tle_year: Year for TLE data (>=2000)

    Returns:
        cfg_mc: Configuration dictionary for MOCAT-MC
    """
    print(f"=== Setting up TLE LNT Historic Configuration (Year: {tle_year}, Seed: {rng_seed}) ===")

    # Initialize configuration dictionary
    cfg_mc = {}

    # Set conversion units
    cfg_mc['DAY2MIN'] = 60 * 24
    cfg_mc['DAY2SEC'] = cfg_mc['DAY2MIN'] * 60
    cfg_mc['YEAR2DAY'] = 365.2425  # days per year
    cfg_mc['YEAR2MIN'] = cfg_mc['YEAR2DAY'] * cfg_mc['DAY2MIN']
    cfg_mc['rad'] = np.pi / 180

    # Global gravitational constants
    whichconst = 84
    tumin, mu_const, radiusearthkm, xke, j2, j3, j4, j3oj2 = getgravc(whichconst)
    cfg_mc['tumin'] = tumin
    cfg_mc['mu_const'] = mu_const
    cfg_mc['radiusearthkm'] = radiusearthkm
    cfg_mc['j2'] = j2
    cfg_mc['omega_earth'] = 2 * np.pi / cfg_mc['DAY2SEC']

    # Scenario parameters
    cfg_mc['PMD'] = 0.4  # Post mission disposal rate (40%)
    cfg_mc['PMDconstel'] = 0.9  # Constellation PMD rate (90%)
    cfg_mc['PMDrb'] = 0.55  # Rocket body PMD rate (55%)
    cfg_mc['alph'] = 0.01  # Active control failure probability

    # LNT effectiveness function: radius-dependent collision avoidance
    cfg_mc['rad2pLNTfunc'] = lambda x: 1.0 / (1.0 + np.exp(-25 * (x - 0.3)))

    cfg_mc['alph_a'] = 0
    cfg_mc['orbtol'] = 5
    cfg_mc['step_control'] = 2
    cfg_mc['P_frag'] = 0
    cfg_mc['P_frag_cutoff'] = int(100 * 0.18)
    cfg_mc['altitude_limit_low'] = 200
    cfg_mc['altitude_limit_up'] = 2000
    cfg_mc['missionlifetime'] = int(100 * 0.08)

    cfg_mc['time0'] = datetime(tle_year, 1, 1)
    t0_prop = 0
    nyears = 100
    tf_prop = cfg_mc['YEAR2MIN'] * nyears * 2.0
    cfg_mc['dt_days'] = 5  # Time step [days]
    DeltaT = cfg_mc['dt_days'] * cfg_mc['DAY2MIN']
    cfg_mc['tsince'] = np.arange(t0_prop, t0_prop + tf_prop + DeltaT, DeltaT)
    cfg_mc['n_time'] = len(cfg_mc['tsince'])

    print(f"Simulation setup: {cfg_mc['n_time']} time steps")

    # Launch configuration
    cfg_mc['total_launch_per_year'] = 0
    cfg_mc['launch_increase_per_year'] = 0
    launch_frequency = 13  # days
    TLElaunchRepeat = 1  # Use repeat launches (ESA style)
    cfg_mc['launchRepeatYrs'] = [2001, 2000]  # Launch repeat years
    cfg_mc['launchRepeatSmooth'] = 0  # No smoothing

    # Constellation configuration
    cfg_mc['constellationFile'] = ''
    cfg_mc['constellationSheet'] = ''
    cfg_mc = setup_constellation(cfg_mc)

    # Initial population modification parameters
    cfg_mc['fillMassRadius'] = 2  # Resampling method for missing data
    cfg_mc['initpopMultiplier'] = 1  # Population multiplier
    cfg_mc['physicalBstar'] = 1  # Recalculate B* from physical parameters

    # Initialize simulation
    print("Initializing simulation...")
    cfg_mc = init_sim(cfg_mc, 'TLE', TLElaunchRepeat, tle_year)

    # Propagator settings
    cfg_mc['use_sgp4'] = False  # Use analytic propagator

    # Collision settings
    cfg_mc['skipCollisions'] = 0  # Enable collisions
    cfg_mc['max_frag'] = np.inf  # No fragment limit
    cfg_mc['CUBE_RES'] = 50  # Cube resolution [km]
    cfg_mc['collision_alt_limit'] = 45000  # Collision altitude limit [km]

    # Atmospheric model
    cfg_mc['density_profile'] = 'JB2008'
    cfg_mc = init_jb2008(cfg_mc)

    # Animation and output settings
    cfg_mc['animation'] = 'no'
    cfg_mc['save_diaryName'] = ''
    cfg_mc['save_output_file'] = 11
    cfg_mc['saveMSnTimesteps'] = 146  # Save every ~2 years

    # Parameter SSEM for TLE simulation
    if cfg_mc['save_output_file'] >= 3:
        paramSSEM = {}
        paramSSEM['N_shell'] = 36
        paramSSEM['h_min'] = cfg_mc['altitude_limit_low']
        paramSSEM['h_max'] = cfg_mc['altitude_limit_up']
        paramSSEM['R02'] = np.linspace(paramSSEM['h_min'], paramSSEM['h_max'],
                                      paramSSEM['N_shell'] + 1)
        paramSSEM['re'] = radiusearthkm
        cfg_mc['paramSSEM'] = paramSSEM

    # Output filename
    timestamp = datetime.now().strftime('%Y%m%dT%H%M%S')
    cfg_mc['filename_save'] = f'TLE_{timestamp}_{rng_seed}.mat'
    cfg_mc['n_save_checkpoint'] = np.inf

    print("Configuration complete!")
    return cfg_mc


def init_jb2008(cfg_mc):
    """Initialize JB2008 atmospheric density model"""
    print("Initializing JB2008 atmospheric model...")

    try:
        # Load density data
        density_file = 'dens_jb2008_032020_022224.mat'
        if not os.path.exists(density_file):
            print(f"Warning: {density_file} not found. Using simplified atmospheric model.")
            return cfg_mc

        dens_data = loadmat(density_file)
        dens_highvar = dens_data['dens_highvar']

        # Extract time information
        months = dens_highvar['month'][0, 0].flatten()
        years = dens_highvar['year'][0, 0].flatten()
        altitudes = dens_highvar['alt'][0, 0].flatten()
        densities = dens_highvar['dens'][0, 0]

        # Convert to Julian dates
        dens_times = np.zeros(len(months))
        for k in range(len(months)):
            dt = datetime(int(years[k]), int(months[k]), 1)
            # Convert to Julian date
            a = (14 - dt.month) // 12
            y = dt.year + 4800 - a
            m = dt.month + 12 * a - 3
            jd = dt.day \
                + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
            dens_times[k] = jd

        # Create meshgrid for interpolation
        dens_times_grid, alt_grid = np.meshgrid(dens_times, altitudes)

        # Store in configuration
        if 'param' not in cfg_mc:
            cfg_mc['param'] = {}
        cfg_mc['param']['dens_times'] = dens_times_grid
        cfg_mc['param']['alt'] = alt_grid
        cfg_mc['param']['dens_value'] = densities

        print(f"JB2008 data loaded: {len(altitudes)} altitude levels, {len(dens_times)} time points")

    except Exception as e:
        print(f"Warning: Could not load JB2008 data: {e}")
        print("Using simplified atmospheric model instead.")

    return cfg_mc


def init_sim(cfg, simulation, tle_launch_repeat, tle_year):
    """Initialize simulation with TLE data and launch configuration"""
    print("Initializing simulation with TLE data...")

    # Get gravitational constants
    whichconst = 84
    tumin, mu, radiusearthkm, xke, j2, j3, j4, j3oj2 = getgravc(whichconst)

    # Load TLE data
    try:
        tle_filename = f"{tle_year}.mat"
        if not os.path.exists(tle_filename):
            print(f"Error: {tle_filename} not found for TLE data")
            raise FileNotFoundError(f"{tle_filename} not found")

        tle_data = loadmat(tle_filename)
        mat_sats = tle_data['mat_sats']
        print(f"{mat_sats.shape[0]} satellite entries loaded from {tle_filename}")

        # Compute orbital parameters
        a_all = mat_sats[:, 0] * radiusearthkm  # Semi-major axis in km
        e_all = mat_sats[:, 1]  # Eccentricity
        ap_all = a_all * (1 - e_all)  # Perigee
        aa_all = a_all * (1 + e_all)  # Apogee

    except Exception as e:
        print(f"Current directory: {os.getcwd()}")
        raise RuntimeError(f"Initial population (.mat) not found: {e}")

    # Filter objects by altitude limits
    altitude_filter = ((ap_all > (cfg['altitude_limit_up'] + radiusearthkm)) |
                      (ap_all < (cfg['altitude_limit_low'] + radiusearthkm)))
    mat_sats = mat_sats[~altitude_filter]
    print(f"After altitude filtering: {mat_sats.shape[0]} objects remain")

    # Set launch model
    if not tle_launch_repeat:
        launch_model = 'random'
    else:
        launch_model = 'matsat'

    # Fill in missing physical parameters
    print(f"Filling missing physical parameters (method: {cfg['fillMassRadius']})")
    if cfg['fillMassRadius'] == 0:
        g1, g2, g3 = get_zero_groups(mat_sats)
    elif cfg['fillMassRadius'] == 1:
        mat_sats, g1, g2, g3 = fill_mass_radius_esa(mat_sats)
    elif cfg['fillMassRadius'] == 2:
        mat_sats, g1, g2, g3 = fill_mass_radius_resample(mat_sats)
    else:
        raise ValueError("fillMassRadius must be 0, 1, or 2")

    # Get indices
    idx = get_idx()

    # Mark old payloads as derelict
    payload_inds = mat_sats[:, idx['objectclass']] == 1
    # Set controlled flag for payloads
    mat_sats[payload_inds, idx['controlled']] = 1

    # Turn off control for old payloads (beyond mission lifetime) - matching MATLAB exactly
    launch_dates = mat_sats[:, idx['launch_date']]
    # MATLAB: ind_matsat_old = jd2date(mat_sats(:, idx_launch_date)) <
    # year(cfg.time0) - cfg.missionlifetime;
    cutoff_year = cfg['time0'].year - cfg['missionlifetime']
    cutoff_date = datetime(cutoff_year, 1, 1)  # January 1st of cutoff year

    old_payload_mask = np.zeros(len(mat_sats), dtype=bool)
    for i, jd in enumerate(launch_dates):
        if not np.isnan(jd):
            try:
                launch_dt = jd2date(jd)
                # Match MATLAB's exact date comparison (not just year)
                if hasattr(launch_dt, 'year') and launch_dt < cutoff_date:
                    old_payload_mask[i] = True
            except:
                continue

    mat_sats[old_payload_mask, idx['controlled']] = 0
    print(f"Marked {np.sum(old_payload_mask)} old payloads as uncontrolled")

    # Multiply initial population if specified
    if cfg['initpopMultiplier'] != 1:
        mat_sats = multiply_initial_pop(cfg, mat_sats, g1, g2, g3)

    # Set up launch configuration
    launch_mc_step = np.zeros((0, 23))
    ind_launch = []
    ind_launch_add = []

    if launch_model == 'matsat':
        # Set up repeat launches
        jds = mat_sats[:, idx['launch_date']]
        launch_years = []

        for jd in jds:
            if not np.isnan(jd):
                try:
                    dt = jd2date(jd)
                    if hasattr(dt, 'year'):
                        launch_years.append(dt.year)
                    else:
                        launch_years.append(np.nan)
                except:
                    launch_years.append(np.nan)
            else:
                launch_years.append(np.nan)

        launch_years = np.array(launch_years)
        launch_window = ((launch_years >= cfg['launchRepeatYrs'][0]) &
                        (launch_years <= cfg['launchRepeatYrs'][1]) &
                        ~np.isnan(launch_years))

        cfg['repeatLaunches'] = mat_sats[launch_window]

        if cfg['constellationFile']:
            # Remove constellations from repeat launches (simplified check)
            constellation_idx = (
                (cfg['repeatLaunches'][:,
                idx['mass']] == 260) |
                               (cfg['repeatLaunches'][:, idx['mass']] == 148))
            cfg['repeatLaunches'] = cfg['repeatLaunches'][~constellation_idx]
            print(f"TLE launch repeat: {cfg['repeatLaunches'].shape[0]} objects, "
                  f"omitted {np.sum(constellation_idx)} constellation objects")
        else:
            print(f"TLE launch repeat: {cfg['repeatLaunches'].shape[0]} objects "
                  f"over {cfg['launchRepeatYrs'][1] - cfg['launchRepeatYrs'][0] + 1} years")

    # Set constellation flags
    constellation_idx = ((mat_sats[:, idx['mass']] == 260) |
                        (mat_sats[:, idx['mass']] == 148))
    mat_sats[constellation_idx, idx['constel']] = 1

    if 'repeatLaunches' in cfg and len(cfg['repeatLaunches']) > 0:
        constellation_idx_repeat = (
            (cfg['repeatLaunches'][:,
            idx['mass']] == 260) |
                                   (
                                       cfg['repeatLaunches'][:,
                                       idx['mass']] == 148))
        cfg['repeatLaunches'][constellation_idx_repeat, idx['constel']] = 1

    # Add mission lifetime to controlled satellites
    controlled_sats = mat_sats[:, idx['controlled']] == 1
    mat_sats[controlled_sats, idx['missionlife']] = cfg['missionlifetime']

    if 'repeatLaunches' in cfg and len(cfg['repeatLaunches']) > 0:
        controlled_repeat = cfg['repeatLaunches'][:, idx['controlled']] == 1
        cfg['repeatLaunches'][controlled_repeat, idx['missionlife']] = cfg['missionlifetime']

    # Set desired semi-major axis for controlled satellites
    mat_sats[controlled_sats, idx['a_desired']] = mat_sats[controlled_sats, idx['a']]

    # Recalculate B* if specified
    if cfg['physicalBstar']:
        print("Recalculating B* from physical parameters...")
        # B* = 0.5 * Cd * A/m * rho0, where rho0 = 0.157
        cd = 2.2  # Drag coefficient
        area = np.pi * mat_sats[:, idx['radius']]**2  # Cross-sectional area
        mass = mat_sats[:, idx['mass']]

        # Avoid division by zero
        valid_mass = mass > 0
        mat_sats[valid_mass, idx['bstar']] = (0.5 * cd * area[valid_mass] /
                                             mass[valid_mass] * 0.157)

        if 'repeatLaunches' in cfg and len(cfg['repeatLaunches']) > 0:
            area_repeat = np.pi * cfg['repeatLaunches'][:, idx['radius']]**2
            mass_repeat = cfg['repeatLaunches'][:, idx['mass']]
            valid_mass_repeat = mass_repeat > 0
            cfg['repeatLaunches'][valid_mass_repeat, idx['bstar']] = (
                0.5 * cd * area_repeat[valid_mass_repeat] /
                mass_repeat[valid_mass_repeat] * 0.157)

    # Store results in configuration
    cfg['a_all'] = a_all
    cfg['ap_all'] = ap_all
    cfg['aa_all'] = aa_all
    cfg['mat_sats'] = mat_sats
    cfg['launchMC_step'] = launch_mc_step
    cfg['ind_launch'] = ind_launch
    cfg['ind_launch_add'] = ind_launch_add
    cfg['launch_model'] = launch_model

    if 'repeatLaunches' not in cfg:
        cfg['repeatLaunches'] = np.zeros((0, 24))

    print(f"Simulation initialized with {mat_sats.shape[0]} objects")
    return cfg


def get_zero_groups(mat_sats):
    """Group satellites by type and identify missing physical parameters"""
    idx = get_idx()

    # Initialize groups
    g1 = {'allclass': [], 'zr': [], 'zm': [], 'nz': [], 'nzno': []}  # Payloads
    # Rocket bodies
    g2 = {'allclass': [], 'zr': [], 'zm': [], 'nz': [], 'nzno': []}
    g3 = {'allclass': [], 'zr': [], 'zm': [], 'nz': [], 'nzno': []}  # Debris

    for obj_class in range(1, 13):
        obj_indices = np.where(mat_sats[:, idx['objectclass']] == obj_class)[0]

        if obj_class == 1:  # Payloads
            g1['allclass'] = obj_indices
            g1['zr'] = obj_indices[mat_sats[obj_indices, idx['radius']] == 0]
            g1['zm'] = obj_indices[mat_sats[obj_indices, idx['mass']] == 0]
            g1['nz'] = np.setdiff1d(
                g1['allclass'],
                np.union1d(g1['zr'],
                g1['zm']))

            # Remove outliers (simplified)
            if len(g1['nz']) > 0:
                radii = mat_sats[g1['nz'], idx['radius']]
                masses = mat_sats[g1['nz'], idx['mass']]
                # Simple outlier detection (could be improved)
                r_q75, r_q25 = np.percentile(radii, [75, 25])
                m_q75, m_q25 = np.percentile(masses, [75, 25])
                r_iqr = r_q75 - r_q25
                m_iqr = m_q75 - m_q25
                r_outliers = ((radii < (r_q25 - 1.5 * r_iqr)) |
                             (radii > (r_q75 + 1.5 * r_iqr)))
                m_outliers = ((masses < (m_q25 - 1.5 * m_iqr)) |
                             (masses > (m_q75 + 1.5 * m_iqr)))
                g1['nzno'] = g1['nz'][~(r_outliers | m_outliers)]

        elif obj_class == 5:  # Rocket bodies
            g2['allclass'] = obj_indices
            g2['zr'] = obj_indices[mat_sats[obj_indices, idx['radius']] == 0]
            g2['zm'] = obj_indices[mat_sats[obj_indices, idx['mass']] == 0]
            g2['nz'] = np.setdiff1d(
                g2['allclass'],
                np.union1d(g2['zr'],
                g2['zm']))

            if len(g2['nz']) > 0:
                radii = mat_sats[g2['nz'], idx['radius']]
                masses = mat_sats[g2['nz'], idx['mass']]
                r_q75, r_q25 = np.percentile(radii, [75, 25])
                m_q75, m_q25 = np.percentile(masses, [75, 25])
                r_iqr = r_q75 - r_q25
                m_iqr = m_q75 - m_q25
                r_outliers = ((radii < (r_q25 - 1.5 * r_iqr)) |
                             (radii > (r_q75 + 1.5 * r_iqr)))
                m_outliers = ((masses < (m_q25 - 1.5 * m_iqr)) |
                             (masses > (m_q75 + 1.5 * m_iqr)))
                g2['nzno'] = g2['nz'][~(r_outliers | m_outliers)]

        else:  # All other objects -> debris
            g3['allclass'] = np.union1d(g3['allclass'], obj_indices)

    # Process debris group
    if len(g3['allclass']) > 0:
        g3['zr'] = g3['allclass'][mat_sats[g3['allclass'], idx['radius']] == 0]
        g3['zm'] = g3['allclass'][mat_sats[g3['allclass'], idx['mass']] == 0]
        g3['nz'] = np.setdiff1d(g3['allclass'], np.union1d(g3['zr'], g3['zm']))

        if len(g3['nz']) > 0:
            radii = mat_sats[g3['nz'], idx['radius']]
            masses = mat_sats[g3['nz'], idx['mass']]
            r_q75, r_q25 = np.percentile(radii, [75, 25])
            m_q75, m_q25 = np.percentile(masses, [75, 25])
            r_iqr = r_q75 - r_q25
            m_iqr = m_q75 - m_q25
            r_outliers = ((radii < (r_q25 - 1.5 * r_iqr)) |
                         (radii > (r_q75 + 1.5 * r_iqr)))
            m_outliers = ((masses < (m_q25 - 1.5 * m_iqr)) |
                         (masses > (m_q75 + 1.5 * m_iqr)))
            g3['nzno'] = g3['nz'][~(r_outliers | m_outliers)]

    return g1, g2, g3


def fill_mass_radius_esa(mat_sats):
    """Fill missing mass/radius using ESA method (RCS-based)"""
    print("Using ESA method for filling missing physical parameters...")

    # This is a simplified version - real implementation would use SATCAT data
    idx = get_idx()

    # Get groups
    g1, g2, g3 = get_zero_groups(mat_sats)

    # Fill missing radii with default values based on object type
    # Large: 10 m^2 -> radius = sqrt(10/pi)
    # Medium: 1 m^2 -> radius = sqrt(1/pi)
    # Small: 0.1 m^2 -> radius = sqrt(0.1/pi)

    mat_sats_out = mat_sats.copy()

    # Simple assignment based on object class
    no_radius = mat_sats_out[:, idx['radius']] == 0
    payload_no_radius = no_radius & (mat_sats_out[:, idx['objectclass']] == 1)
    debris_no_radius = no_radius & (mat_sats_out[:, idx['objectclass']] > 2)

    # Payloads -> Large (10 m^2)
    mat_sats_out[payload_no_radius, idx['radius']] = np.sqrt(10 / np.pi)

    # Debris -> Small (0.1 m^2)
    mat_sats_out[debris_no_radius, idx['radius']] = np.sqrt(0.1 / np.pi)

    # Other objects -> Medium (1 m^2)
    still_no_radius = mat_sats_out[:, idx['radius']] == 0
    mat_sats_out[still_no_radius, idx['radius']] = np.sqrt(1 / np.pi)

    # Fill missing masses (spherical aluminum, 2710 kg/m^3)
    no_mass = mat_sats_out[:, idx['mass']] == 0
    radii = mat_sats_out[no_mass, idx['radius']]
    mat_sats_out[no_mass, idx['mass']] = (4/3) * np.pi * radii**3 * 2710

    print(f"Filled radius for {np.sum(no_radius)} objects")
    print(f"Filled mass for {np.sum(no_mass)} objects")

    # Update groups with simple Gaussian models
    aluminum_density = 2710  # kg/m^3
    large_radius = np.sqrt(10 / np.pi)
    large_mass = (4/3) * np.pi * large_radius**3 * aluminum_density
    small_radius = np.sqrt(0.1 / np.pi)
    small_mass = (4/3) * np.pi * small_radius**3 * aluminum_density

    # Create simple Gaussian mixture models
    g1['gm'] = multivariate_normal(
        [large_radius,
        large_mass],
        [[0.1,
        0],
        [0,
        100]])
    g2['gm'] = multivariate_normal(
        [large_radius,
        large_mass],
        [[0.1,
        0],
        [0,
        100]])
    g3['gm'] = multivariate_normal(
        [small_radius,
        small_mass],
        [[0.01,
        0],
        [0,
        10]])

    return mat_sats_out, g1, g2, g3


def fill_mass_radius_resample(mat_sats, g1=None, g2=None, g3=None):
    """Fill missing mass/radius using resampling method"""
    print("Using resampling method for filling missing physical parameters...")

    idx = get_idx()

    if g1 is None:
        g1, g2, g3 = get_zero_groups(mat_sats)

        # Fit Gaussian mixture models to existing data
        if len(g1['nzno']) > 1:
            data = mat_sats[g1['nzno']][:, [idx['radius'], idx['mass']]]
            mean = np.mean(data, axis=0)
            cov = np.cov(data.T)
            g1['gm'] = multivariate_normal(mean, cov)

        if len(g2['nzno']) > 1:
            data = mat_sats[g2['nzno']][:, [idx['radius'], idx['mass']]]
            mean = np.mean(data, axis=0)
            cov = np.cov(data.T)
            g2['gm'] = multivariate_normal(mean, cov)

        if len(g3['nzno']) > 1:
            data = mat_sats[g3['nzno']][:, [idx['radius'], idx['mass']]]
            mean = np.mean(data, axis=0)
            cov = np.cov(data.T)
            g3['gm'] = multivariate_normal(mean, cov)

    mat_sats_out = mat_sats.copy()

    # Fill missing data by sampling from fitted distributions
    for group in [g1, g2, g3]:
        if 'gm' in group:
            missing_indices = np.union1d(group['zm'], group['zr'])
            if len(missing_indices) > 0:
                # Sample more than needed and filter out negative values
                n_needed = len(missing_indices)
                samples = group['gm'].rvs(n_needed * 2)
                if samples.ndim == 1:
                    samples = samples.reshape(1, -1)

                # Remove negative samples
                valid_samples = samples[(
                    samples[:,
                    0] > 0) & (samples[:,
                    1] > 0)]

                if len(valid_samples) >= n_needed:
                    mat_sats_out[missing_indices, [idx['radius'], \
                        idx['mass']]] = valid_samples[:n_needed]
                else:
                    print(f"Warning: Not enough valid samples for group, using defaults")

    return mat_sats_out, g1, g2, g3


def multiply_initial_pop(cfg, mat_sats, g1, g2, g3):
    """Multiply initial population by specified factor"""
    multiplier = cfg['initpopMultiplier']

    if multiplier == 1:
        return mat_sats

    print(f"Multiplying initial population by factor: {multiplier}")

    if multiplier < 1:
        # Subsample population
        n1 = int(len(g1['allclass']) * multiplier)
        n2 = int(len(g2['allclass']) * multiplier)
        n3 = int(len(g3['allclass']) * multiplier)

        indices1 = np.random.choice(g1['allclass'], n1, replace=True)
        indices2 = np.random.choice(g2['allclass'], n2, replace=True)
        indices3 = np.random.choice(g3['allclass'], n3, replace=True)

        all_indices = np.concatenate([indices1, indices2, indices3])
        return mat_sats[all_indices]

    elif multiplier > 1:
        # Add extra satellites
        extra_factor = multiplier - 1
        n1 = int(len(g1['allclass']) * extra_factor)
        n2 = int(len(g2['allclass']) * extra_factor)
        n3 = int(len(g3['allclass']) * extra_factor)

        extra_indices1 = np.random.choice(g1['allclass'], n1, replace=True)
        extra_indices2 = np.random.choice(g2['allclass'], n2, replace=True)
        extra_indices3 = np.random.choice(g3['allclass'], n3, replace=True)

        extra_sats = mat_sats[np.concatenate(
            [extra_indices1,
            extra_indices2,
            extra_indices3])]

        # Zero out mass and radius for resampling
        idx = get_idx()
        extra_sats[:, [idx['mass'], idx['radius']]] = 0

        if cfg['fillMassRadius'] > 0:
            extra_sats, _, _, _ = fill_mass_radius_resample(
                extra_sats,
                g1,
                g2,
                g3)

        # Randomize orbital angles
        extra_sats[:, [idx['argpo'], idx['mo']]] = 2 \
            * np.pi * np.random.rand(len(extra_sats), 2)

        return np.vstack([mat_sats, extra_sats])

    return mat_sats


def setup_constellation(cfg):
    """Setup constellation configuration"""
    if cfg['constellationFile']:
        print(f"Loading constellation data from {cfg['constellationFile']}")
        try:
            # This would load constellation data from Excel/CSV
            # Simplified for now
            cfg['constellation'] = []
        except Exception as e:
            print(f"Warning: Could not load constellation file: {e}")
            cfg['constellation'] = []
    else:
        cfg['constellation'] = []

    return cfg


if __name__ == "__main__":
    # Example usage
    import argparse

    parser = argparse.ArgumentParser(description='Setup TLE LNT Historic Configuration')
    parser.add_argument('--seed', type=int, default=1, help='Random seed')
    parser.add_argument('--year', type=int, default=2020, help='TLE year')

    args = parser.parse_args()

    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Setup configuration
    cfg = setup_tle_lnt_historic(args.seed, args.year)

    # Save configuration
    output_file = f'python_setup_tle_lnt_historic_{args.year}_{args.seed}.mat'
    savemat(output_file, {'cfg_mc': cfg})
    print(f"Configuration saved to: {output_file}")
