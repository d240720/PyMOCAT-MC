"""
Orbital elements to position/velocity vectors - vectorized
Python equivalent of oe2rv_vec.m
"""

import numpy as np
from typing import Tuple, Dict


def oe2rv_vec(
    osc_oe: np.ndarray,
    E_osc: np.ndarray,
    param: Dict) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert osculating orbital elements to position and velocity vectors

    Args:
        osc_oe: Osculating orbital elements [n_sats x 6] [a, e, i, Omega, omega, nu]
        E_osc: Eccentric anomaly [n_sats]
        param: Parameters dictionary

    Returns:
        Tuple of (r_eci, v_eci)
        r_eci: Position vectors in ECI frame [n_sats x 3] [km]
        v_eci: Velocity vectors in ECI frame [n_sats x 3] [km/s]
    """
    n_sats = osc_oe.shape[0]

    if n_sats == 0:
        return np.zeros((0, 3)), np.zeros((0, 3))

    # Extract parameters
    mu = param['mu']

    # Extract orbital elements
    a = osc_oe[:, 0]  # Semi-major axis
    e = osc_oe[:, 1]  # Eccentricity
    i = osc_oe[:, 2]  # Inclination
    Omega = osc_oe[:, 3]  # RAAN
    omega = osc_oe[:, 4]  # Argument of perigee
    nu = osc_oe[:, 5]  # True anomaly

    # Calculate position and velocity in perifocal coordinates
    p = a * (1 - e**2)  # Semi-latus rectum
    r_mag = p / (1 + e * np.cos(nu))  # Radius magnitude

    # Position in perifocal frame
    r_pqw = np.column_stack([
        r_mag * np.cos(nu),
        r_mag * np.sin(nu),
        np.zeros(n_sats)
    ])

    # Velocity in perifocal frame
    sqrt_mu_p = np.sqrt(mu / p)
    v_pqw = np.column_stack([
        -sqrt_mu_p * np.sin(nu),
        sqrt_mu_p * (e + np.cos(nu)),
        np.zeros(n_sats)
    ])

    # Transformation matrices from perifocal to ECI
    cos_Omega = np.cos(Omega)
    sin_Omega = np.sin(Omega)
    cos_omega = np.cos(omega)
    sin_omega = np.sin(omega)
    cos_i = np.cos(i)
    sin_i = np.sin(i)

    # Rotation matrix elements
    R11 = cos_Omega * cos_omega - sin_Omega * sin_omega * cos_i
    R12 = -cos_Omega * sin_omega - sin_Omega * cos_omega * cos_i
    R13 = sin_Omega * sin_i

    R21 = sin_Omega * cos_omega + cos_Omega * sin_omega * cos_i
    R22 = -sin_Omega * sin_omega + cos_Omega * cos_omega * cos_i
    R23 = -cos_Omega * sin_i

    R31 = sin_omega * sin_i
    R32 = cos_omega * sin_i
    R33 = cos_i

    # Transform position to ECI
    r_eci = np.column_stack([
        R11 * r_pqw[:, 0] + R12 * r_pqw[:, 1] + R13 * r_pqw[:, 2],
        R21 * r_pqw[:, 0] + R22 * r_pqw[:, 1] + R23 * r_pqw[:, 2],
        R31 * r_pqw[:, 0] + R32 * r_pqw[:, 1] + R33 * r_pqw[:, 2]
    ])

    # Transform velocity to ECI
    v_eci = np.column_stack([
        R11 * v_pqw[:, 0] + R12 * v_pqw[:, 1] + R13 * v_pqw[:, 2],
        R21 * v_pqw[:, 0] + R22 * v_pqw[:, 1] + R23 * v_pqw[:, 2],
        R31 * v_pqw[:, 0] + R32 * v_pqw[:, 1] + R33 * v_pqw[:, 2]
    ])

    return r_eci, v_eci
