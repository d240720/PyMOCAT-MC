"""
Convert mean classical orbital elements to osculating with mean anomaly output

Converts mean orbital elements to osculating orbital elements, outputting
mean anomaly instead of true anomaly for the osculating elements.

Args:
    x: mean orbital elements [6x1]
        x[0] = mean semimajor axis (kilometers)
        x[1] = mean orbital eccentricity (0 <= e < 1)
        x[2] = mean orbital inclination (radians, 0 <= i <= pi)
        x[3] = mean right ascension of ascending node (
            radians,
            0 <= raan <= 2*pi)
        x[4] = mean argument of perigee (radians, 0 <= argp <= 2*pi)
        x[5] = mean mean anomaly (radians, 0 <= M <= 2*pi)
    param: parameter structure containing mu, req, j2

Returns:
    osc_orbital_elements: osculating orbital elements [6x1] with mean anomaly
    theta_osc: osculating true anomaly (radians)

Reference: Orbital Mechanics with MATLAB
"""

import numpy as np
import warnings
import sys
import os

# Add supporting functions to path
sys.path.append(os.path.dirname(__file__))

mean2osc import mean2osc


def mean2osc_m(x, param):
    """
    Convert mean classical orbital elements to osculating with mean anomaly output

    Args:
        x: mean orbital elements [6x1]
        param: parameter structure

    Returns:
        osc_orbital_elements: osculating orbital elements [6x1] with mean anomaly
        theta_osc: osculating true anomaly (radians)
    """

    x = np.asarray(x).flatten()

    # Convert from mean anomaly to true anomaly
    e = x[1]
    Epw = x[5]  # Mean anomaly (M0)
    Mo = Epw

    # Solve Kepler's equation using Newton-Raphson iteration
    for l in range(1000):
        DeltaEpw = -(Mo - Epw + e * np.sin(Epw)) / (-1 + e * np.cos(Epw))
        Epw = Epw + DeltaEpw
        if abs(DeltaEpw) < 1e-14:
            break

    E = Epw  # Eccentric anomaly

    # Convert eccentric anomaly to true anomaly
    theta = 2 * np.arctan(np.sqrt((1 + e) / (1 - e)) * np.tan(E / 2))

    if e > 1:
        warnings.warn('hyperbolic orbit in mean2osc_m')
        print(f'e: {e:.3e} \t theta: {theta:.3e}')

    # Convert mean elements to osculating elements (with true anomaly)
    x_with_theta = np.concatenate([x[:5], [theta]])
    oeosc = mean2osc(x_with_theta, param)

    # Compute the osculating mean anomaly
    theta_osc = oeosc[5]  # Osculating true anomaly
    e_osc = oeosc[1]      # Osculating eccentricity

    # Convert osculating true anomaly back to mean anomaly
    E_osc = 2 * np.arctan(np.sqrt((1 - e_osc) / (1 \
        + e_osc)) * np.tan(theta_osc / 2))
    M_osc = E_osc - e_osc * np.sin(E_osc)

    # Assemble output with mean anomaly instead of true anomaly
    osc_orbital_elements = np.array([
        oeosc[0],  # semi-major axis
        oeosc[1],  # eccentricity
        oeosc[2],  # inclination
        oeosc[3],  # RAAN
        oeosc[4],  # argument of perigee
        M_osc      # mean anomaly (instead of true anomaly)
    ])

    return osc_orbital_elements, theta_osc
