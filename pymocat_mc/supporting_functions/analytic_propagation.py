"""
Analytic propagation of near-circular satellite orbits

This code includes the solution for the mean elements as a function of time.

Reference:
Martinusi, Vladimir, Lamberto Dell Elce, and Gaëtan Kerschen.
"Analytic propagation of near-circular satellite orbits in the atmosphere
of an oblate planet." Celestial Mechanics and Dynamical Astronomy 123,
no. 1 (2015): 85-103.

Args:
    input_oe: initial orbital elements [a, e, inc, RAAN, argp, M] (6x1)
    param: parameter structure containing:
        - req: Earth radius (km)
        - j2: J2 gravitational coefficient
        - mu: gravitational parameter (km^3/s^2)
        - density_profile: 'JB2008' or 'static'
        - Bstar: drag coefficient
        - t: current time
        - t_0: initial time
        - For JB2008: alt, dens_times, dens_value, jd

Returns:
    out_oe: propagated orbital elements [a, e, inc, RAAN, argp, M] (6x1)
    error: error flag (0=success, 1=failure)
"""

import numpy as np
import sys
import os

# Add supporting functions to path
sys.path.append(os.path.dirname(__file__))

from .lininterp1 import lininterp1
from .lininterp2 import lininterp2
from .densityexp import densityexp


def analytic_propagation(input_oe, param):
    """
    Analytic propagation of near-circular satellite orbits

    Args:
        input_oe: initial orbital elements [a, e, inc, RAAN, argp, M] (6x1)
        param: parameter structure

    Returns:
        out_oe: propagated orbital elements [a, e, inc, RAAN, argp, M] (6x1)
        error: error flag (0=success, 1=failure)
    """

    error = 0

    # Extract parameters
    re = param['req']
    J2 = param['j2']
    mu = param['mu']

    # Determine atmospheric density
    if param['density_profile'].upper() == 'JB2008':
        # JB2008 density model
        altitude = input_oe[0] - re

        # Check altitude bounds and get density
        if 200 < altitude < 2000:  # changes from 200-1100
            rho_0 = lininterp2(param['alt'][:, 0], param['dens_times'][0, :],
                              param['dens_value'], altitude, param['jd']) * (1000)**3
        else:
            if altitude > 1100:
                rho_0 = lininterp1(param['dens_times'][0, :], param['dens_value'][-1, :],
                                  param['jd']) * (1000)**3
            else:
                rho_0 = lininterp1(param['dens_times'][0, :], param['dens_value'][0, :],
                                  param['jd']) * (1000)**3

    elif param['density_profile'].upper() == 'STATIC':
        rho_0 = densityexp(input_oe[0] - re) * (1000)**3
    else:
        # Default to static exponential model
        rho_0 = densityexp(input_oe[0] - re) * (1000)**3

    # Calculate drag coefficient
    # rho_reference for Bstar is 0.157 in units of kg/(m^2 * re).
    # Using (1000^2 m^2/1 km^2) to convert A from m^2 to km^2, and dividing by 0.157 to scale
    # according to newly computed density rho_0 (kg/km^3)
    C_0 = max((abs(param['Bstar']) / (1e6 * 0.157)) * rho_0, 1e-16)

    k2 = mu * J2 * re**2 / 2

    t = param['t']
    t_0 = param['t_0']

    # Initial conditions
    a_0 = input_oe[0]
    e_0 = input_oe[1]
    inc_0 = input_oe[2]
    bigO_0 = input_oe[3]
    omega_0 = input_oe[4]
    Mo_0 = input_oe[5]

    c = np.cos(inc_0)
    n_0 = np.sqrt(mu) * a_0**(-3/2)

    alpha_0 = e_0 / np.sqrt(a_0)
    beta_0 = (np.sqrt(3) / 2) * e_0

    # Calculate new orbital elements
    tan_coeff = max(np.tan(np.arctan(beta_0) \
        - beta_0 * n_0 * a_0 * C_0 * (t - t_0)), 0)
    a = (a_0 / beta_0**2) * tan_coeff**2

    e = (1 / (np.sqrt(3) / 2)) * tan_coeff

    Mo = ((1/8) * (1/C_0) * (4/a + 3*alpha_0**2 * np.log(a/a_0)) -
          (1/8) * (1/C_0) * (4/a_0 + 3*alpha_0**2 * np.log(a_0/a_0)) +
          (3*k2*(3*c**2 - 1)) / (16*mu) * (1/C_0) * ((3*alpha_0**2/2) * 1/a**2 + 4/(3*a**3)) -
          (3*k2*(3*c**2 - 1)) / (16*mu) * (1/C_0) * ((3*alpha_0**2/2) * 1/a_0**2 + 4/(3*a_0**3)) +
          Mo_0)

    omega = ((3*k2*(5*c**2 - 1)) / (16*mu) * (1/C_0) * ((5*alpha_0**2/2) * 1/a**2 \
        + 4/(3*a**3)) -
             (3*k2*(5*c**2 - 1)) / (16*mu) * (1/C_0) * \
                 ((5*alpha_0**2/2) * 1/a_0**2 + 4/(3*a_0**3)) +
             omega_0)

    bigO = (-(3*k2*c) / (8*mu) * (1/C_0) * ((5*alpha_0**2/2) * 1/a**2 \
        + 4/(3*a**3)) +
            (3*k2*c) / (8*mu) * (1/C_0) * ((5*alpha_0**2/2) * 1/a_0**2 + 4/(3*a_0**3)) +
            bigO_0)

    # Check if results are real
    if (np.isreal(inc_0) and np.isreal(bigO) and np.isreal(omega) and np.isreal(Mo)):
        out_oe = np.array([a, e, inc_0 % (2*np.pi), bigO % (2*np.pi),
                          omega % (2*np.pi), Mo % (2*np.pi)])
    else:
        out_oe = input_oe.copy()
        error = 1

    return out_oe, error
