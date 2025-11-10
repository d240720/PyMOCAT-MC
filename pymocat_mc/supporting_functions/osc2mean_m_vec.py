"""
Vectorized conversion of osculating to mean elements with mean anomaly output

Converts osculating orbital elements to mean orbital elements for multiple satellites,
outputting mean anomaly instead of true anomaly.

Args:
    x: osculating orbital elements [N x 6] where each row is:
        x[:,0] = osculating semimajor axis (kilometers)
        x[:,1] = osculating orbital eccentricity (0 <= e < 1)
        x[:,2] = osculating orbital inclination (radians, 0 <= i <= pi)
        x[:,3] = osculating right ascension of ascending node (
            radians,
            0 <= raan <= 2*pi)
        x[:,4] = osculating argument of perigee (radians, 0 <= argp <= 2*pi)
        x[:,5] = osculating mean anomaly (radians, 0 <= M <= 2*pi)
    param: parameter structure containing req, j2

Returns:
    mean_orbital_elements: mean orbital elements [N x 6] with mean anomaly
    theta_mean: mean true anomaly array (radians)

Reference: Orbital Mechanics with MATLAB
"""

import numpy as np
import warnings
import sys
import os

# Add supporting functions to path
sys.path.append(os.path.dirname(__file__))

osc2mean_vec import osc2mean_vec
kepler1_vec import kepler1_vec


def osc2mean_m_vec(x, param):
    """
    Vectorized conversion of osculating to mean elements with mean anomaly output

    Args:
        x: osculating orbital elements [N x 6]
        param: parameter structure

    Returns:
        mean_orbital_elements: mean orbital elements [N x 6] with mean anomaly
        theta_mean: mean true anomaly array (radians)
    """

    x = np.atleast_2d(x)

    # Convert from mean anomaly to true anomaly for each satellite
    e = x[:, 1]
    Mo = x[:, 5]  # Mean anomaly

    # Solve Kepler's equation using vectorized solver
    E, _ = kepler1_vec(Mo, e)

    # Convert eccentric anomaly to true anomaly
    theta = 2 * np.arctan(np.sqrt((1 + e) / (1 - e)) * np.tan(E / 2))

    # Check for hyperbolic orbits
    hyperbolic_mask = e > 1
    if np.any(hyperbolic_mask):
        warnings.warn('hyperbolic orbit(s) in osc2mean_m_vec')
        for i in np.where(hyperbolic_mask)[0]:
            print(f'e: {e[i]:.3e} \t theta: {theta[i]:.3e}')

    # Convert osculating elements to mean elements (with true anomaly)
    x_with_theta = x.copy()
    x_with_theta[:, 5] = theta
    oemean = osc2mean_vec(x_with_theta, param)

    # Compute the mean mean anomaly
    theta_mean = oemean[:, 5]  # Mean true anomaly
    e_mean = oemean[:, 1]      # Mean eccentricity

    # Convert mean true anomaly back to mean anomaly
    E_mean = 2 * np.arctan(np.sqrt((1 - e_mean) / (1 \
        + e_mean)) * np.tan(theta_mean / 2))
    M_mean = E_mean - e_mean * np.sin(E_mean)

    # Assemble output with mean anomaly instead of true anomaly
    mean_orbital_elements = oemean.copy()
    mean_orbital_elements[:, 5] = M_mean

    return mean_orbital_elements, theta_mean
