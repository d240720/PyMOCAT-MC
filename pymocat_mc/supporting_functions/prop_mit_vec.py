"""
MIT propagator vectorized implementation.

Python equivalent of prop_mit_vec.m.
"""

import numpy as np
from typing import Tuple, Dict
from .analytic_propagation_vec import analytic_propagation_vec
from .mean2osc_m_vec import mean2osc_m_vec
from .oe2rv_vec import oe2rv_vec


def prop_mit_vec(mat_sat_in: np.ndarray, t: float, param: Dict) -> np.ndarray:
    """
    Execute MIT propagator vectorized implementation.

    Args:
        mat_sat_in: Input satellite matrix [a,ecco,inclo,nodeo,argpo,mo,Bstar,controlled]
        t: Time in seconds
        param: Parameters dictionary containing req, mu, etc.

    Returns:
        mat_sat_out: Output satellite matrix [a,ecco,inclo,nodeo,argpo,mo,errors,r_eci,v_eci]
    """
    req = param['req']

    # Set parameters
    param_copy = param.copy()
    param_copy['t'] = t  # in units of seconds
    param_copy['t_0'] = 0  # in units of seconds

    n_sat = mat_sat_in.shape[0]

    # Convert to mean orbital elements (scale semi-major axis)
    in_mean_oe = np.column_stack([
        req * mat_sat_in[:, 0],  # Scale semi-major axis
        mat_sat_in[:, 1:6]       # Other orbital elements unchanged
    ])

    # Handle Bstar
    bstar = np.abs(mat_sat_in[:, 6])
    bstar[bstar < 1e-12] = 9.7071e-05

    # Preallocate output
    out_mean_oe = np.zeros((n_sat, 6))
    errors = np.zeros(n_sat)

    # Check if a de-orbit has already happened or if controlled
    idx_notdecay = (in_mean_oe[:, 0] * (1 - in_mean_oe[:, 1])) > (req + 150)
    idx_controlled = mat_sat_in[:, 7] == 1
    # objects that haven't decayed and are not controlled
    idx_propagate = idx_notdecay & ~idx_controlled

    if np.any(idx_propagate):
        param_copy['Bstar'] = bstar[idx_propagate]
        out_mean_oe[idx_propagate, :], errors[idx_propagate] = analytic_propagation_vec(
            in_mean_oe[idx_propagate, :], param_copy
        )

    # Decayed or controlled, assign input value
    out_mean_oe[~idx_propagate, :] = in_mean_oe[~idx_propagate, :]

    # Update mean anomaly of controlled objects, all other orbital elements remain the same
    if np.any(idx_controlled):
        mean_motion = np.sqrt(param_copy['mu'] \
            / out_mean_oe[idx_controlled, 0]**3)
        out_mean_oe[idx_controlled, 5] += mean_motion * t

    # Check if decayed or hyperbolic
    check_alt_ecc = ((out_mean_oe[:, 0] * (1 - out_mean_oe[:, 1])) > (req \
        + 150)) & (out_mean_oe[:, 1] < 1)
    errors[~check_alt_ecc] = 1

    # Mean to osculating orbital elements
    osc_oe = np.zeros((n_sat, 6))
    e_osc = np.zeros(np.sum(check_alt_ecc))

    if np.any(check_alt_ecc):
        osc_oe[check_alt_ecc, :], _, e_osc = mean2osc_m_vec(
            out_mean_oe[check_alt_ecc,
            :],
            param_copy)

    # Scale semi-major axis back
    out_mean_oe[:, 0] = out_mean_oe[:, 0] / req
    osc_oe[~check_alt_ecc, :] = out_mean_oe[~check_alt_ecc, :]

    # Osculating orbital elements to state vector
    r_eci = np.zeros((n_sat, 3))
    v_eci = np.zeros((n_sat, 3))

    if np.any(check_alt_ecc):
        r_eci[check_alt_ecc, :], v_eci[check_alt_ecc, :] = oe2rv_vec(
            osc_oe[check_alt_ecc, :], e_osc, param_copy
        )

    # Combine output
    mat_sat_out = np.column_stack([out_mean_oe, errors, r_eci, v_eci])

    return mat_sat_out
