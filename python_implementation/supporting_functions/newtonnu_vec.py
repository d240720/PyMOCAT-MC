"""
Newton-Raphson method for finding mean anomaly from eccentric anomaly (vectorized)

This function converts eccentric anomaly to mean anomaly for elliptical orbits.

Args:
    ecc: eccentricity array
    nu: true anomaly array (radians)

Returns:
    eccentric_anomaly: eccentric anomaly array (radians)
    mean_anomaly: mean anomaly array (radians)
"""

import numpy as np


def newtonnu_vec(ecc, nu):
    """
    Find mean anomaly and eccentric anomaly from true anomaly (vectorized)

    Args:
        ecc: eccentricity array
        nu: true anomaly array (radians)

    Returns:
        tuple: (eccentric_anomaly, mean_anomaly) in radians
    """
    # Ensure inputs are numpy arrays
    ecc = np.atleast_1d(ecc)
    nu = np.atleast_1d(nu)

    # Initialize output arrays
    eccentric_anomaly = np.zeros_like(ecc)
    mean_anomaly = np.zeros_like(ecc)

    # Handle circular orbits (ecc = 0)
    circular = (ecc == 0)
    eccentric_anomaly[circular] = nu[circular]
    mean_anomaly[circular] = nu[circular]

    # Handle elliptical orbits (0 < ecc < 1)
    elliptical = (ecc > 0) & (ecc < 1)
    if np.any(elliptical):
        # Calculate eccentric anomaly from true anomaly
        sqrt_term = np.sqrt((1 - ecc[elliptical]) / (1 + ecc[elliptical]))
        tan_half_nu = np.tan(nu[elliptical] / 2)
        tan_half_e = sqrt_term * tan_half_nu
        eccentric_anomaly[elliptical] = 2 * np.arctan(tan_half_e)

        # Calculate mean anomaly from eccentric anomaly
        e_anom = eccentric_anomaly[elliptical]
        mean_anomaly[elliptical] = e_anom - ecc[elliptical] * np.sin(e_anom)

    # Handle parabolic orbits (ecc = 1)
    parabolic = (ecc == 1)
    if np.any(parabolic):
        # For parabolic orbits, use different formulation
        tan_half_nu = np.tan(nu[parabolic] / 2)
        mean_anomaly[parabolic] = tan_half_nu + (tan_half_nu**3) / 3
        # No eccentric anomaly for parabolic
        eccentric_anomaly[parabolic] = nu[parabolic]

    # Handle hyperbolic orbits (ecc > 1)
    hyperbolic = (ecc > 1)
    if np.any(hyperbolic):
        # Calculate hyperbolic eccentric anomaly
        sqrt_term = np.sqrt((ecc[hyperbolic] - 1) / (ecc[hyperbolic] + 1))
        tan_half_nu = np.tan(nu[hyperbolic] / 2)
        tanh_half_h = sqrt_term * tan_half_nu
        eccentric_anomaly[hyperbolic] = 2 * np.arctanh(tanh_half_h)

        # Calculate mean anomaly for hyperbolic orbit
        h_anom = eccentric_anomaly[hyperbolic]
        mean_anomaly[hyperbolic] = ecc[hyperbolic] * np.sinh(h_anom) - h_anom

    return eccentric_anomaly, mean_anomaly
