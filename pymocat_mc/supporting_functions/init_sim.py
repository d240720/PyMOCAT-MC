"""
Initialize simulation configuration.

Python equivalent of initSim.m.
"""

import numpy as np
import scipy.io as sio
from datetime import datetime, timedelta
from typing import Dict, Tuple
from .jd2date import jd2date
from .get_idx import get_idx


def init_sim(cfg: Dict, simulation: str, launch_model: str,
              ic_file: str) -> Dict:
    """
    Initialize simulation with initial conditions and launch configuration.

    Args:
        cfg: Configuration dictionary
        simulation: Simulation type ('TLE')
        launch_model: Launch model ('no_launch', 'random', 'matsat',
                                    'data', 'Somma')
        ic_file: Initial conditions file

    Returns:
        Updated configuration dictionary
    """
    # Get indices
    idx = get_idx()
    radiusearthkm = cfg['radiusearthkm']

    # Load initial conditions
    try:
        # Try to load MATLAB file - check multiple possible paths
        import os
        possible_paths = [
            ic_file,
            os.path.join('supporting_data', 'TLEhistoric', ic_file),
            os.path.join('..', 'supporting_data', 'TLEhistoric', ic_file),
            os.path.join('..', '..', 'supporting_data', 'TLEhistoric', ic_file)
        ]

        mat_data = None
        actual_path = None
        for path in possible_paths:
            try:
                mat_data = sio.loadmat(path)
                actual_path = path
                break
            except:
                continue

        if mat_data is None:
            raise FileNotFoundError(
                f"Could not find {ic_file} in any expected location")

        if 'mat_sats' in mat_data:
            mat_sats = mat_data['mat_sats']
        else:
            raise ValueError("mat_sats not found in file")

        if 'time0' in mat_data:
            # Handle MATLAB datetime conversion
            time0_matlab = mat_data['time0']
            if hasattr(time0_matlab, 'flat') and len(time0_matlab.flat) > 0:
                # Convert MATLAB serial date number to Python datetime
                time0 = (datetime.fromordinal(int(time0_matlab.flat[0]) - 366)
                         + timedelta(days=time0_matlab.flat[0] % 1))
            else:
                time0 = datetime(2020, 1, 1)  # Default
        else:
            time0 = datetime(2020, 1, 1)  # Default

        print(f'{mat_sats.shape[0]} satellite entries on {time0} '
              f'loaded from {actual_path}')

    except Exception as e:
        print(f'Error loading initial conditions: {e}')
        print('Creating default initial conditions...')

        # Create default initial conditions
        n_default_sats = 100
        mat_sats = create_default_satellites(n_default_sats, radiusearthkm)
        time0 = datetime(2020, 1, 1)

    # Calculate perigees and apogees
    a_all = mat_sats[:, idx['a']] * radiusearthkm
    e_all = mat_sats[:, idx['ecco']]
    ap_all = a_all * (1 - e_all)  # Perigee
    aa_all = a_all * (1 + e_all)  # Apogee

    # Filter objects by altitude limits
    altitude_mask = (
        (ap_all <= (cfg['altitude_limit_up'] + radiusearthkm)) &
        (ap_all >= (cfg['altitude_limit_low'] + radiusearthkm))
    )
    mat_sats = mat_sats[altitude_mask, :]

    # Step 1: resample missing mass/radius from GMM
    fill_method = cfg.get('fillMassRadius', 2)
    if fill_method == 2:
        from .fill_mass_radius_resample import fillMassRadiusResample
        mat_sats, _, _, _ = fillMassRadiusResample(mat_sats)

    # Step 2: fill any remaining zeros with simple defaults
    mat_sats = fill_missing_physical_params(mat_sats, idx)

    # Mark old payloads as derelict
    payload_mask = mat_sats[:, idx['objectclass']] == 1
    # Set controlled flag on for all payloads
    mat_sats[payload_mask, idx['controlled']] = 1

    derelict_threshold_year = time0.year - cfg['missionlifetime']

    # Find derelicts based on launch date
    launch_dates = mat_sats[:, idx['launch_date']]
    # Handle NaN values in launch dates
    valid_dates = ~np.isnan(launch_dates)
    derelict_mask = np.zeros(len(launch_dates), dtype=bool)

    for i, jd in enumerate(launch_dates):
        if valid_dates[i] and not np.isnan(jd):
            try:
                launch_year = jd2date(jd).year
                derelict_mask[i] = launch_year < derelict_threshold_year
            except:
                # If date conversion fails, assume it's not a derelict
                derelict_mask[i] = False
    # Set controlled flag off for derelicts
    mat_sats[derelict_mask, idx['controlled']] = 0

    # Set launch model
    if launch_model in ['no_launch', 'no']:
        repeat_launches = np.zeros((0, mat_sats.shape[1]))
        launch_mc_step = np.zeros((0, 23))
        additional_launches = np.zeros((0, 23))
        ind_launch = []
        ind_launch_add = []

    elif launch_model in ['random', 'matsat']:
        launch_mc_step = np.zeros((0, 23))
        additional_launches = np.zeros((0, 23))
        ind_launch = []
        ind_launch_add = []

        if launch_model == 'matsat':
            # Create repeat launches based on past launch performance
            # within the launch window
            launch_dates = mat_sats[:, idx['launch_date']]

            # Find objects launched within the specified year range
            valid_dates = ~np.isnan(launch_dates)
            ind_inlaunchwindow = np.zeros(len(launch_dates), dtype=bool)

            for i, jd in enumerate(launch_dates):
                if valid_dates[i]:
                    try:
                        launch_year = jd2date(jd).year
                        ind_inlaunchwindow[i] = (
                            launch_year >= cfg['launchRepeatYrs'][0]
                            and launch_year <= cfg['launchRepeatYrs'][1])
                    except:
                        ind_inlaunchwindow[i] = False

            repeat_launches = mat_sats[ind_inlaunchwindow, :].copy()

            # Remove constellations if needed
            # (Starlink: 260kg, OneWeb: 148kg)
            if len(repeat_launches) > 0:
                constellation_mask = (
                    (repeat_launches[:, idx['mass']] == 260) |
                    (repeat_launches[:, idx['mass']] == 148)
                )
                repeat_launches = repeat_launches[~constellation_mask, :]

                total_years = (cfg["launchRepeatYrs"][1]
                               - cfg["launchRepeatYrs"][0] + 1)
                print(f'TLE launch repeat selected '
                      f'({len(repeat_launches)} objects total over '
                      f'{total_years} years)')
            else:
                repeat_launches = np.zeros((0, mat_sats.shape[1]))
        else:
            # For 'random' model, start with empty repeat launches
            # In the future, this could be enhanced with
            # Poisson-distributed random launches
            repeat_launches = np.zeros((0, mat_sats.shape[1]))
            print('Random launch model: using empty launches '
                  '(can be enhanced with Poisson distribution)')

    elif launch_model in ['data', 'Somma']:
        launch_mc_step = np.zeros((0, 23))
        additional_launches = np.zeros((0, 23))
        ind_launch = []
        ind_launch_add = []

        if launch_model == 'matsat':
            # Create repeat launches based on historical data
            jds = mat_sats[:, idx['launch_date']]
            launch_years = np.array([jd2date(jd).year for jd in jds])

            in_launch_window = (
                (launch_years <= cfg['launchRepeatYrs'][1]) &
                (launch_years >= cfg['launchRepeatYrs'][0])
            )

            repeat_launches = mat_sats[in_launch_window, :]
            total_years = (cfg["launchRepeatYrs"][1]
                           - cfg["launchRepeatYrs"][0] + 1)
            print(f'TLE launch repeat selected '
                  f'({np.sum(in_launch_window)} objects total over '
                  f'{total_years} years)')
        else:
            repeat_launches = np.zeros((0, mat_sats.shape[1]))

    else:
        raise ValueError(f'Unknown launch model: {launch_model}')

    # Set constellation flags for Starlink and OneWeb
    # (mass-based identification)
    constellation_mask = ((mat_sats[:, idx['mass']] == 260)
                           | (mat_sats[:, idx['mass']] == 148))
    mat_sats[constellation_mask, idx['constel']] = 1

    # Add mission lifetime for controlled satellites
    controlled_mask = mat_sats[:, idx['controlled']] == 1
    mat_sats[controlled_mask, idx['missionlife']] = cfg['missionlifetime']

    # Add desired semi-major axis for controlled satellites
    mat_sats[controlled_mask, idx['a_desired']] = (
        mat_sats[controlled_mask, idx['a']])

    # Recalculate Bstar if using physical model
    if cfg.get('physicalBstar', False):
        # Bstar = 0.5 * Cd * A/m * rho0; rho0 = 0.157e6 kg/m^2/RE
        cd = 2.2  # Drag coefficient
        area_to_mass = mat_sats[:, idx['radius']]**2 / mat_sats[:, idx['mass']]
        mat_sats[:, idx['bstar']] = 0.5 * cd * area_to_mass * 0.157

    # Update configuration
    cfg_out = cfg.copy()
    cfg_out['a_all'] = a_all
    cfg_out['ap_all'] = ap_all
    cfg_out['aa_all'] = aa_all
    cfg_out['mat_sats'] = mat_sats
    cfg_out['repeatLaunches'] = (
        repeat_launches if 'repeat_launches' in locals()
        else np.zeros((0, mat_sats.shape[1])))
    cfg_out['time0'] = time0
    cfg_out['launchMC_step'] = launch_mc_step
    cfg_out['additional_launches'] = additional_launches
    cfg_out['ind_launch'] = ind_launch
    cfg_out['ind_launch_add'] = ind_launch_add
    cfg_out['launch_model'] = launch_model

    return cfg_out


def create_default_satellites(n_sats: int, radiusearthkm: float) -> np.ndarray:
    """
    Create default satellite population for testing

    Args:
        n_sats: Number of satellites to create
        radiusearthkm: Earth radius in km

    Returns:
        mat_sats: Satellite matrix
    """
    mat_sats = np.zeros((n_sats, 24))

    # Semi-major axis (LEO range: 400-2000 km altitude)
    alt_min, alt_max = 400, 2000
    altitudes = np.random.uniform(alt_min, alt_max, n_sats)
    # Normalized to Earth radii
    mat_sats[:, 0] = (radiusearthkm + altitudes) / radiusearthkm

    # Eccentricity (mostly circular orbits)
    mat_sats[:, 1] = np.random.uniform(0, 0.1, n_sats)

    # Inclination (uniform distribution)
    mat_sats[:, 2] = np.random.uniform(0, np.pi, n_sats)

    # RAAN, argument of perigee, mean anomaly (uniform distributions)
    mat_sats[:, 3] = np.random.uniform(0, 2*np.pi, n_sats)  # RAAN
    # Argument of perigee
    mat_sats[:, 4] = np.random.uniform(0, 2*np.pi, n_sats)
    mat_sats[:, 5] = np.random.uniform(0, 2*np.pi, n_sats)  # Mean anomaly

    # Bstar (drag term)
    mat_sats[:, 6] = np.random.uniform(1e-5, 1e-3, n_sats)

    # Mass (kg) - typical satellite masses
    mat_sats[:, 7] = np.random.uniform(100, 5000, n_sats)

    # Radius (m) - estimated from mass
    density = 200  # kg/m^3 (average satellite density including empty space)
    volumes = mat_sats[:, 7] / density
    # Spherical approximation
    mat_sats[:, 8] = (3 * volumes / (4 * np.pi))**(1/3)

    # Error flag
    mat_sats[:, 9] = 0

    # Controlled flag (mix of controlled and uncontrolled)
    mat_sats[:, 10] = np.random.choice([0, 1], n_sats, p=[0.3, 0.7])

    # Mission lifetime
    mat_sats[:, 12] = np.random.uniform(5, 15, n_sats)

    # Launch dates (last 20 years)
    base_jd = 2451545.0  # J2000
    days_range = 20 * 365.25  # 20 years
    mat_sats[:, 15] = base_jd + np.random.uniform(0, days_range, n_sats)

    # Object class (mostly payloads and some rocket bodies)
    # 1=payload, 5=rocket body
    mat_sats[:, 22] = np.random.choice([1, 5], n_sats, p=[0.8, 0.2])

    # Object IDs
    mat_sats[:, 23] = np.arange(1, n_sats + 1)

    return mat_sats


def fill_missing_physical_params(
    mat_sats: np.ndarray,
    idx: Dict) -> np.ndarray:
    """
    Fill in missing physical parameters (mass, radius)

    Args:
        mat_sats: Satellite matrix
        idx: Index dictionary

    Returns:
        Updated satellite matrix
    """
    # Find objects with missing mass or radius
    missing_mass = mat_sats[:, idx['mass']] <= 0
    missing_radius = mat_sats[:, idx['radius']] <= 0

    # Use typical values based on object class
    if np.any(missing_mass):
        # Default masses by object class
        payload_mask = mat_sats[:, idx['objectclass']] == 1
        rb_mask = mat_sats[:, idx['objectclass']] == 5

        # Payloads: 100-5000 kg
        payload_count = np.sum(missing_mass & payload_mask)
        mat_sats[missing_mass & payload_mask, idx['mass']] = (
            np.random.uniform(100, 5000, payload_count))

        # Rocket bodies: 500-10000 kg
        rb_count = np.sum(missing_mass & rb_mask)
        mat_sats[missing_mass & rb_mask, idx['mass']] = (
            np.random.uniform(500, 10000, rb_count))

        # Other objects: 50-1000 kg
        other_mask = ~payload_mask & ~rb_mask
        other_count = np.sum(missing_mass & other_mask)
        mat_sats[missing_mass & other_mask, idx['mass']] = (
            np.random.uniform(50, 1000, other_count))

    if np.any(missing_radius):
        # Estimate radius from mass assuming average density
        density = 200  # kg/m^3
        volumes = mat_sats[missing_radius, idx['mass']] / density
        mat_sats[missing_radius, idx['radius']] = (
            (3 * volumes / (4 * np.pi))**(1/3))

    return mat_sats


def fillin_physical_parameters():
    """
    Placeholder for physical parameter filling (for compatibility)
    """
    pass


def fillin_atmosphere():
    """
    Placeholder for atmosphere setup (for compatibility)
    """
    pass
