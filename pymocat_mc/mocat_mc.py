"""
MIT Orbital Capacity Assessment Toolbox - Monte Carlo (MOCAT-MC)
Python Implementation - Fixed Version with Lazy Imports

Authors: Richard Linares, Daniel Jang, Davide Gusmini, Andrea D'Ambrosio,
         Pablo Machuca, Peng Mun Siew

Python implementation maintaining full compatibility with MATLAB version.
"""

import numpy as np
import pandas as pd
import scipy.io as sio
from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Optional, Union
import warnings
import sys
import os

class MOCATMC:
    """
    Main MOCAT-MC simulation class with lazy imports.
    """

    def __init__(self):
        """Initialize the class with minimal dependencies."""
        self._constants = None
        self._idx = None
        self._supporting_functions = {}

    @property
    def constants(self):
        """Lazy load constants."""
        if self._constants is None:
            CfgMCConstants = self._get_supporting_function('cfg_mc_constants', 'CfgMCConstants')
            self._constants = CfgMCConstants()
        return self._constants

    @property
    def idx(self):
        """Lazy load indices."""
        if self._idx is None:
            get_idx = self._get_supporting_function('get_idx', 'get_idx')
            self._idx = get_idx()
        return self._idx

    def _get_supporting_function(self, module_name, function_name):
        """Dynamically import supporting functions as needed."""
        key = f"{module_name}.{function_name}"

        if key not in self._supporting_functions:
            # Try package import first
            try:
                module = __import__(f'pymocat_mc.supporting_functions.{module_name}',
                                  fromlist=[function_name])
                self._supporting_functions[key] = getattr(module, function_name)
            except ImportError:
                try:
                    # Fall back to sys.path approach
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    support_dir = os.path.join(current_dir, 'supporting_functions')
                    if support_dir not in sys.path:
                        sys.path.insert(0, support_dir)

                    module = __import__(module_name)
                    self._supporting_functions[key] = getattr(module, function_name)
                except ImportError as e:
                    raise ImportError(f"Could not import {module_name}.{function_name}. "
                                    f"Make sure the package is properly installed. Error: {e}")

        return self._supporting_functions[key]

    def setup_mc_config(self, rng_seed: int, ic_file: str) -> Dict:
        """
        Set up configuration for MC run.

        Args:
            rng_seed: Random seed
            ic_file: Initial conditions file containing mat_sats matrix

        Returns:
            cfg_mc: Configuration dictionary for main_mc
        """
        # Set random seed
        np.random.seed(rng_seed)

        # Initialize configuration
        cfg_mc = {}

        # Constants
        for key, value in self.constants.__dict__.items():
            cfg_mc[key] = value

        # Scenario parameters
        cfg_mc['PMD'] = 0.95
        cfg_mc['alph'] = 0.01
        cfg_mc['alph_a'] = 0
        cfg_mc['orbtol'] = 5
        cfg_mc['step_control'] = 2
        cfg_mc['P_frag'] = 0
        cfg_mc['P_frag_cutoff'] = int(100 * 0.18)
        cfg_mc['altitude_limit_low'] = 200
        cfg_mc['altitude_limit_up'] = 2000
        cfg_mc['missionlifetime'] = 8

        t0_prop = 0
        nyears = 100
        tf_prop = cfg_mc['YEAR2MIN'] * nyears 
        cfg_mc['dt_days'] = 5
        delta_t = cfg_mc['dt_days'] * cfg_mc['DAY2MIN']
        cfg_mc['tsince'] = np.arange(t0_prop, t0_prop + tf_prop + delta_t, delta_t)
        cfg_mc['n_time'] = len(cfg_mc['tsince'])

        # Launches
        simulation = 'TLE'
        launch_model = 'no_launch'
        cfg_mc['launchRepeatYrs'] = [2018, 2022]
        cfg_mc['launchRepeatSmooth'] = 0

        # Lazy load supporting functions
        fillin_physical_parameters = self._get_supporting_function('fillin_physical_parameters', 'fillin_physical_parameters')
        init_sim = self._get_supporting_function('init_sim', 'init_sim')
        fillin_atmosphere = self._get_supporting_function('fillin_atmosphere', 'fillin_atmosphere')

        # Prepare initial condition population
        fillin_physical_parameters()

        # Initialize initial condition population and launches
        cfg_mc = init_sim(cfg_mc, simulation, launch_model, ic_file)

        # Initialize shell information
        param_ssem = {
            'N_shell': 36,
            'h_min': cfg_mc['altitude_limit_low'],
            'h_max': cfg_mc['altitude_limit_up'],
            're': cfg_mc['radiusearthkm']
        }
        param_ssem['R02'] = np.linspace(
            param_ssem['h_min'], param_ssem['h_max'],
            param_ssem['N_shell'] + 1)
        cfg_mc['paramSSEM'] = param_ssem

        # Propagator settings
        cfg_mc['use_sgp4'] = False
        cfg_mc['skipCollisions'] = 0
        cfg_mc['max_frag'] = np.inf
        cfg_mc['CUBE_RES'] = 50
        cfg_mc['collision_alt_limit'] = 45000

        # Atmosphere
        fillin_atmosphere()

        # Output settings
        cfg_mc['animation'] = 'no'
        cfg_mc['save_diaryName'] = ''
        cfg_mc['save_output_file'] = 0
        cfg_mc['saveMSnTimesteps'] = 146

        # Filename save
        filename_save = f'TLEIC_year{cfg_mc["time0"].year}_rand{rng_seed}.mat'
        cfg_mc['filename_save'] = filename_save
        cfg_mc['n_save_checkpoint'] = np.inf

        return cfg_mc

    def main_mc(self, mc_config: Union[Dict, str], rng_seed: Optional[int] = None):
        """
        Execute main Monte Carlo simulation.
        Delegates to the full implementation in supporting_functions/main_mc.py.
        """
        from pymocat_mc.supporting_functions.main_mc import main_mc as _main_mc
        return _main_mc(mc_config, rng_seed)

    def _datetime_to_julian(self, dt: datetime) -> float:
        """Convert datetime to Julian date."""
        a = (14 - dt.month) // 12
        y = dt.year + 4800 - a
        m = dt.month + 12 * a - 3
        return dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045 + \
               (dt.hour - 12) / 24 + dt.minute / 1440 + dt.second / 86400 + dt.microsecond / 86400000000


def quick_start():
    """
    Execute quick start function equivalent to Quick_Start.m.
    """
    print("PyMOCAT-MC Quick Start")

    # Initialize MOCAT-MC
    mocat = MOCATMC()

    # Initial condition file
    ic_file = '2020.mat'

    # MOCAT MC configuration
    seed = 1

    print('MC configuration starting...')
    cfg_mc = mocat.setup_mc_config(seed, ic_file)
    print(f'Seed {seed}')

    # MOCAT MC evolution
    print(f'Initial Population:  {cfg_mc["mat_sats"].shape[0]} sats')
    print('Starting main_mc...')

    nS, nD, nN, nB, mat_sats = mocat.main_mc(cfg_mc, seed)

    # MOCAT MC postprocess
    total = nS + nD + nN + nB
    ratio = nS / total if total > 0 else 0
    print('Quick Start scenario done!')
    print(f'Final object counts: S={nS}, D={nD}, N={nN}, B={nB}')
    print(f'Satellite ratio: {ratio:.6f}')

    return nS, nD, nN, nB, mat_sats


if __name__ == "__main__":
    quick_start()