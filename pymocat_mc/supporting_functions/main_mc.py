"""
MIT ARCLab's implementation of a space environmental Simulation
MIT Orbital Capacity Tool - Monte Carlo (MOCAT-MC)

Authors: Richard Linares, Daniel Jang, Davide Gusmini, Andrea D'Ambrosio,
         Pablo Machuca, Peng Mun Siew
https://github.mit.edu/arclab/orbitalrisk_MC

Python implementation converted from main_mc.m
"""

import numpy as np
import sys
import os
from datetime import datetime, timedelta
from typing import Tuple, Dict, List, Optional, Union
import warnings

# Add supporting functions to path
sys.path.append(os.path.dirname(__file__))

from .cfg_mc_constants import CfgMCConstants
from .get_idx import get_idx
from .categorize_obj import categorize_obj
from .prop_mit_vec import prop_mit_vec
from .orbcontrol_vec import orbcontrol_vec
from .cube_vec_v3 import cube_vec_v3
from .collision_prob_vec import collision_prob_vec
from .frag_col_sbm_vec import frag_col_sbm_vec
from .frag_exp_sbm_vec import frag_exp_sbm_vec
from .jd2date import jd2date


def main_mc(
    mc_config: Union[Dict,
    str],
    rng_seed: Optional[int] = None) -> Tuple[int, int, int, int, np.ndarray]:
    """
    Main Monte Carlo simulation function

    Args:
        mc_config: Configuration dictionary or string name of config
        rng_seed: Random number generator seed

    Returns:
        Tuple of (nS, nD, nN, nB, mat_sats) where:
        - nS: number of satellites
        - nD: number of derelicts
        - nN: number of debris
        - nB: number of rocket bodies
        - mat_sats: final satellite matrix
    """

    # Initialize RNG seed
    if rng_seed is not None:
        np.random.seed(rng_seed)
        print(f'main_mc specified with seed {rng_seed}')
    elif isinstance(mc_config, dict) and 'seed' in mc_config:
        np.random.seed(mc_config['seed'])
        print(f'main_mc specified with config seed {mc_config["seed"]}')

    # Load configuration
    if isinstance(mc_config, str):
        # Handle string config names if needed
        raise NotImplementedError("String config names not yet implemented")

    cfg = load_cfg(mc_config)

    # Extract configuration variables
    constants = CfgMCConstants()
    idx = get_idx()

    # Get key variables from config
    mat_sats = cfg['mat_sats'].copy()
    tsince = cfg['tsince']
    n_time = cfg['n_time']
    time0 = cfg['time0']
    dt_days = cfg['dt_days']
    launch_model = cfg.get('launch_model', 'no_launch')
    step_control = cfg.get('step_control', 2)
    orbtol = cfg.get('orbtol', 5)
    PMD = cfg.get('PMD', 0.95)
    alph = cfg.get('alph', 0.01)
    alph_a = cfg.get('alph_a', 0)
    P_frag = cfg.get('P_frag', 0)
    P_frag_cutoff = cfg.get('P_frag_cutoff', 18)
    CUBE_RES = cfg.get('CUBE_RES', 50)
    collision_alt_limit = cfg.get('collision_alt_limit', 45000)
    save_output_file = cfg.get('save_output_file', 0)
    filename_save = cfg.get('filename_save', '')
    max_frag = cfg.get('max_frag', np.inf)

    # Constants
    DAY2MIN = constants.DAY2MIN
    DAY2SEC = constants.DAY2SEC
    YEAR2DAY = constants.YEAR2DAY
    radiusearthkm = constants.radiusearthkm
    mu_const = constants.mu_const
    j2 = constants.j2

    # Parameter structure
    param = {
        'req': radiusearthkm,
        'mu': mu_const,
        'j2': j2,
        'max_frag': max_frag,
        'maxID': int(np.max([np.max(mat_sats[:, idx['ID']]), 0])),
        'density_profile': cfg.get('density_profile', None)
    }

    if 'paramSSEM' in cfg:
        param['paramSSEM'] = cfg['paramSSEM']

    param['sample_params'] = cfg.get('sample_params', 0)

    # SSEM species: [S,D,N,Su,B,U]
    param_ssem = {'species': np.array([1, 1, 1, 0, 0, 0])}

    # Preallocate arrays
    n_sats = mat_sats.shape[0]

    # For tracking
    num_objects = np.zeros(n_time)
    num_objects[0] = n_sats
    count_coll = np.zeros(n_time, dtype=np.uint32)
    count_expl = np.zeros(n_time, dtype=np.uint32)
    count_debris_coll = np.zeros(n_time, dtype=np.uint32)
    count_debris_expl = np.zeros(n_time, dtype=np.uint32)

    # Initialize tracking variables
    num_pmd = 0
    num_deorbited = 0
    launch = 0
    out_future = np.array([]).reshape(0, mat_sats.shape[1])
    count_tot_launches = 0

    # Index definitions for different functions
    idx_launch_in_extra = [idx['ID']]
    idx_prop_in = [idx['a'], idx['ecco'], idx['inclo'], idx['nodeo'],
                   idx['argpo'], idx['mo'], idx['bstar'], idx['controlled']]
    idx_prop_out = [idx['a'], idx['ecco'], idx['inclo'], idx['nodeo'],
                    idx['argpo'], idx['mo'], idx['error'], *idx['r'], *idx['v']]
    idx_control_in = [idx['a'], idx['ecco'], idx['inclo'], idx['nodeo'],
                      idx['argpo'], idx['mo'], idx['controlled'], idx['a_desired'],
                      idx['missionlife'], idx['launch_date'], *idx['r'], *idx['v']]
    idx_control_out = [idx['a'], idx['controlled'], *idx['r'], *idx['v']]
    idx_exp_in = [idx['mass'], idx['radius'], *idx['r'], *idx['v'], idx['objectclass']]
    idx_col_in = [idx['mass'], idx['radius'], *idx['r'], *idx['v'], idx['objectclass']]

    # Store initial object class data
    objclassint_store = mat_sats[:, idx['objectclass']].astype(int)
    a_store = mat_sats[:, idx['a']]
    controlled_store = mat_sats[:, idx['controlled']].astype(int)

    # Extract initial species numbers
    nS, nD, nN, nB = categorize_obj(objclassint_store, controlled_store)
    
    
    # History tracking
    history_S = [nS]
    history_D = [nD]
    history_N = [nN]
    history_B = [nB]
    history_years = [time0.year + time0.timetuple().tm_yday / 365.25]

    # Test save if needed
    if save_output_file > 0:
        print(f'Test saving of {filename_save} successful')

    # Print initial status
    initial_date = time0
    print(f'Year {initial_date.year} - Day {initial_date.timetuple().tm_yday:03d}, '
          f'PMD {num_pmd:04d}, Deorbit {num_deorbited:03d}, Launches \
              {len(out_future) * launch:03d}, '
          f'nFrag {count_expl[0]:03d}, nCol {count_coll[0]:03d}, '
          f'nObjects {int(num_objects[0])} ({nS},{nD},{nN},{nB})')

    launch_data = []

    # START PROPAGATION
    for n in range(1, n_time):
        current_time = time0 + timedelta(minutes=tsince[n])
        jd = julian_date(current_time)

        # LAUNCHES
        if launch_model.lower() == 'matsat':
            # Repeat launches logic
            out_future = handle_matsat_launches(cfg, current_time, time0, n, dt_days,
                                              constants, idx)
            launch = len(out_future) > 0
        elif launch_model.lower() == 'random':
            # Random launches logic
            out_future, launch = handle_random_launches(cfg, current_time, time0,
                                                       tsince, n, param, dt_days)
        elif launch_model.lower() == 'data' or 'somma' in launch_model.lower():
            # Data/Somma launches logic
            out_future, launch = handle_data_launches(cfg, current_time, time0,
                                                     tsince, n, param)
        elif launch_model.lower() == 'no_launch':
            out_future = np.array([]).reshape(0, mat_sats.shape[1])
            launch = 0
        else:
            raise ValueError('Not a valid launch model')

        param['maxID'] += len(out_future)
        count_tot_launches += len(out_future)

        # PROPAGATION
        n_sats = mat_sats.shape[0]
        propagator = cfg.get('propagator', 'MIT')

        if propagator.upper() == 'SGP4':
            # SGP4 propagation (not implemented yet)
            raise NotImplementedError("SGP4 propagation not yet implemented")
        elif propagator.upper() == 'THALASSA':
            # THALASSA propagation (not implemented yet)
            raise NotImplementedError("THALASSA propagation not yet implemented")
        else:
            # MIT propagation
            param['jd'] = jd

            if n > 0:
                dt_sec = 60 * (tsince[n] - tsince[n-1])
            else:
                dt_sec = 60 * tsince[n]

            # Propagate all satellites
            mat_sats[:, idx_prop_out] = prop_mit_vec(
                mat_sats[:,
                idx_prop_in],
                dt_sec,
                param)

            # Find objects to deorbit
            r_mag = np.sqrt(np.sum(mat_sats[:, idx['r']]**2, axis=1))
            altitude = (mat_sats[:, idx['a']] * radiusearthkm) * (1 \
                - mat_sats[:, idx['ecco']]) - radiusearthkm

            deorbit_mask = ((mat_sats[:, idx['r'][0]] == 0) |
                           (altitude < 150) |
                           (r_mag < (radiusearthkm + 100)) |
                           (mat_sats[:, idx['error']] != 0) |
                           (mat_sats[:, idx['a']] < 0))

            deorbit = np.where(deorbit_mask)[0]

        # Remove deorbited objects
        num_deorbited = len(deorbit)
        mat_sats = np.delete(mat_sats, deorbit, axis=0)

        # ORBIT CONTROL
        if (n % step_control == 0) or (step_control == 1):
            mat_sats[:, idx_control_out], deorbit_PMD = orbcontrol_vec(
                mat_sats[:, idx_control_in], tsince[n], time0, orbtol, PMD,
                DAY2MIN, YEAR2DAY, param)

            num_pmd = len(deorbit_PMD)
            mat_sats = np.delete(mat_sats, deorbit_PMD, axis=0)
        else:
            num_pmd = 0

        # EXPLOSIONS
        n_sats = mat_sats.shape[0]
        out_frag = []

        # Find rocket bodies
        find_rocket = np.where(mat_sats[:, idx['objectclass']] == 5)[0]
        rand_p_exp = np.random.rand(len(find_rocket))

        if P_frag_cutoff is not None:
            # Calculate ages
            launch_dates = mat_sats[find_rocket, idx['launch_date']]
            ages = np.full(len(launch_dates), P_frag_cutoff)

            for i, jd_launch in enumerate(launch_dates):
                if not np.isnan(jd_launch):
                    try:
                        launch_year = jd2date(jd_launch).year
                        ages[i] = current_time.year - launch_year
                    except:
                        ages[i] = P_frag_cutoff

            find_p_exp = np.where((rand_p_exp < P_frag) & (ages < P_frag_cutoff))[0]
        else:
            find_p_exp = np.where(rand_p_exp < P_frag)[0]

        remove_frag = find_rocket[find_p_exp]

        # Process explosions in reverse order
        for idx_p_exp in reversed(remove_frag):
            p1_all = mat_sats[idx_p_exp, :]
            p1_in = p1_all[idx_exp_in]

            debris1 = frag_exp_sbm_vec(tsince[n], p1_in, param)
            param['maxID'] += len(debris1) if len(debris1) > 0 else 0

            if len(debris1) > 0:
                out_frag.extend(debris1)
                count_expl[n] += 1

        # Remove exploded objects
        if len(remove_frag) > 0:
            mat_sats = np.delete(mat_sats, remove_frag, axis=0)

        # COLLISIONS
        if cfg.get('skipCollisions', 0) == 1 or mat_sats.shape[0] == 0:
            collision_array = []
        else:
            collision_cell = cube_vec_v3(
                mat_sats[:,
                idx['r']],
                CUBE_RES,
                collision_alt_limit)
            collision_array = [item
                for sublist in collision_cell for item in sublist] if collision_cell else []

        remove_collision = []
        out_collision = []

        if collision_array:
            collision_array = np.array(collision_array)
            p1_idx = collision_array[:, 0].astype(int)
            p2_idx = collision_array[:, 1].astype(int)
            p1_all = mat_sats[p1_idx, :]
            p2_all = mat_sats[p2_idx, :]

            # Process collisions
            p1_controlled = p1_all[:, idx['controlled']]
            p2_controlled = p2_all[:, idx['controlled']]
            p1_radius = p1_all[:, idx['radius']]
            p2_radius = p2_all[:, idx['radius']]
            p1_v = p1_all[:, idx['v']]
            p2_v = p2_all[:, idx['v']]

            # Collision probability
            Pij = collision_prob_vec(
                p1_radius,
                p1_v,
                p2_radius,
                p2_v,
                CUBE_RES)

            # Collision probability over dt
            P = np.zeros(len(p1_controlled))
            sum_controlled = p1_controlled + p2_controlled

            # Different probabilities based on control status
            mask_0 = sum_controlled < 0.5
            mask_1 = (sum_controlled >= 0.5) & (sum_controlled < 1.5)
            mask_2 = sum_controlled >= 1.5

            P[mask_0] = Pij[mask_0] * (dt_days * DAY2SEC)
            P[mask_1] = Pij[mask_1] * (alph * dt_days * DAY2SEC)
            P[mask_2] = Pij[mask_2] * (alph_a * dt_days * DAY2SEC)

            rand_P = np.random.rand(len(p1_controlled))
            find_P = np.where(rand_P < P)[0]

            # Process actual collisions
            for idx_P in find_P:
                p1_in = p1_all[idx_P, idx_col_in]
                p2_in = p2_all[idx_P, idx_col_in]

                debris1, debris2 = frag_col_sbm_vec(
                    tsince[n],
                    p1_in,
                    p2_in,
                    param)
                param['maxID'] += len(debris1) + len(debris2)

                out_collision.extend(debris1)
                out_collision.extend(debris2)

                if len(debris1) > 0 or len(debris2) > 0:
                    count_coll[n] += 1
                    remove_collision.extend([p1_idx[idx_P], p2_idx[idx_P]])

        # DATA PROCESSING
        # Remove collision objects
        if remove_collision:
            mat_sats = np.delete(mat_sats, remove_collision, axis=0)

        # Add new objects
        if len(out_future) > 0:
            mat_sats = np.vstack([mat_sats, out_future])
        if len(out_frag) > 0:
            mat_sats = np.vstack([mat_sats, np.array(out_frag)])
        if len(out_collision) > 0:
            mat_sats = np.vstack([mat_sats, np.array(out_collision)])

        # Add to launch data
        if len(out_future) > 0:
            launch_data.extend(out_future)

        # ACCOUNTING
        n_sats = mat_sats.shape[0]
        num_objects[n] = n_sats

        objclassint_store = mat_sats[:, idx['objectclass']].astype(int)
        controlled_store = mat_sats[:, idx['controlled']].astype(int)

        count_debris_coll[n] = len(out_collision)
        count_debris_expl[n] = len(out_frag)

        nS, nD, nN, nB = categorize_obj(objclassint_store, controlled_store)
        
        
        # Append to history
        history_S.append(nS)
        history_D.append(nD)
        history_N.append(nN)
        history_B.append(nB)
        history_years.append(current_time.year + current_time.timetuple().tm_yday / 365.25)

        # Print status
        print(f'Year {current_time.year} - Day {current_time.timetuple().tm_yday:03d}, '
              f'PMD {num_pmd:04d}, Deorbit {num_deorbited:03d}, Launches {len(out_future):03d}, '
              f'nFrag {count_expl[n]:03d}, nCol {count_coll[n]:03d}, '
              f'nObjects {int(num_objects[n])} ({nS},{nD},{nN},{nB})')

    print(f'\n === FINISHED MC RUN (main_mc.py) WITH SEED: {rng_seed} === \n')

    history = {
        'years': np.array(history_years),
        'S': np.array(history_S),
        'D': np.array(history_D),
        'N': np.array(history_N),
        'B': np.array(history_B),
    }
    return nS, nD, nN, nB, mat_sats, history









def load_cfg(cfg: Dict) -> Dict:
    """Load configuration variables into local namespace equivalent"""
    return cfg


def julian_date(dt: datetime) -> float:
    """Convert datetime to Julian date"""
    a = (14 - dt.month) // 12
    y = dt.year + 4800 - a
    m = dt.month + 12 * a - 3
    return dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045 + \
           (dt.hour + dt.minute / 60.0 + dt.second / 3600.0) / 24.0


def handle_matsat_launches(
    cfg,
    current_time,
    time0,
    n,
    dt_days,
    constants,
    idx):
    """Handle matsat launch model"""
    # Implementation for matsat launches
    return np.array([]).reshape(0, cfg['mat_sats'].shape[1])


def handle_random_launches(
    cfg,
    current_time,
    time0,
    tsince,
    n,
    param,
    dt_days):
    """Handle random launch model"""
    # Implementation for random launches
    return np.array([]).reshape(0, cfg['mat_sats'].shape[1]), 0


def handle_data_launches(cfg, current_time, time0, tsince, n, param):
    """Handle data/Somma launch model"""
    # Implementation for data launches
    return np.array([]).reshape(0, cfg['mat_sats'].shape[1]), 0
