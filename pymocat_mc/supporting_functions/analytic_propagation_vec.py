"""
Analytic propagation vectorized implementation
Python equivalent of analytic_propagation_vec.m

Based on Martinusi, Vladimir, Lamberto Dell Elce, and Gaëtan Kerschen.
"Analytic propagation of near-circular satellite orbits
in the atmosphere of an oblate planet." Celestial Mechanics
and Dynamical Astronomy 123, no. 1 (2015): 85-103.
"""

import numpy as np
from typing import Tuple, Dict
from .densityexp_vec import densityexp_vec
from .lininterp1_vec import lininterp1_vec, lininterp2_vec_v2


def analytic_propagation_vec(
    input_oe: np.ndarray,
    param: Dict) -> Tuple[np.ndarray, np.ndarray]:
    """
    Analytic orbital propagation with atmospheric drag

    Args:
        input_oe: Input mean orbital elements [n_sats x 6] [a, e, i, Omega, omega, M]
        param: Parameters dictionary

    Returns:
        Tuple of (out_oe, errors)
    """
    n_sats = input_oe.shape[0]
    errors = np.zeros(n_sats)

    if n_sats == 0:
        return input_oe.copy(), errors

    # Extract parameters
    re = param['req']
    J2 = param['j2']
    mu = param['mu']
    t = param['t']
    t_0 = param['t_0']

    # Extract orbital elements
    a_0 = input_oe[:, 0]  # Semi-major axis (km)
    e_0 = input_oe[:, 1]  # Eccentricity
    inc_0 = input_oe[:, 2]  # Inclination (rad)
    bigO_0 = input_oe[:, 3]  # RAAN (rad)
    omega_0 = input_oe[:, 4]  # Argument of perigee (rad)
    Mo_0 = input_oe[:, 5]  # Mean anomaly (rad)

    # Calculate altitude above Earth surface
    a_minus_re = a_0 - re

    # Calculate atmospheric density
    if 'density_profile' in param and param['density_profile'] == 'JB2008':
        # JB2008 atmospheric model (if data available)
        rho_0 = np.zeros(len(a_0))

        if 'alt' in param and 'dens_times' in param and 'dens_value' in param:
            check_above = a_minus_re > param['alt'][-1, 0]
            check_below = a_minus_re < param['alt'][0, 0]
            check_in_range = ~check_above & ~check_below

            # Interpolate density for objects in range
            if np.any(check_in_range):
                rho_0[check_in_range] = lininterp2_vec_v2(
                    param['alt'][:, 0], param['dens_times'][0, :], param['dens_value'],
                    a_minus_re[check_in_range], param['jd']
                ) * 1e9

            # Handle objects above/below range
            if np.any(check_above):
                rho_0[check_above] = lininterp1_vec(
                    param['dens_times'][0, :], param['dens_value'][-1, :], param['jd']
                ) * 1e9

            if np.any(check_below):
                rho_0[check_below] = lininterp1_vec(
                    param['dens_times'][0, :], param['dens_value'][0, :], param['jd']
                ) * 1e9
        else:
            # Fallback to exponential model
            rho_0 = densityexp_vec(a_minus_re) * 1e9
    else:
        # Static exponential atmospheric model
        rho_0 = densityexp_vec(a_minus_re)

    # Calculate drag coefficient C_0
    # rho_reference for Bstar is 0.157 in units of kg/(m^2 * re)
    # Using (1000^2 m^2/1 km^2) to convert A from m^2 to km^2, and dividing by 0.157 to scale
    # according to newly computed density rho_0 (kg/km^3)
    Bstar = param.get('Bstar', np.ones(n_sats) * 1e-5)
    if np.isscalar(Bstar):
        Bstar = np.full(n_sats, Bstar)

    # Lower limit to avoid singularity
    C_0 = np.maximum((Bstar / (1e6 * 0.157)) * rho_0, 1e-20)

    # Calculate J2 parameter
    k2_over_mu = J2 * re**2 / 2  # k2 = mu*J2*re^2/2

    # Calculate initial conditions
    c = np.cos(inc_0)
    c_sq = c**2

    n_0 = np.sqrt(mu) * a_0**(-3/2)

    alpha0_sq = (e_0 / np.sqrt(a_0))**2

    beta_0 = (np.sqrt(3) / 2) * e_0

    # Calculate propagated orbital elements using analytic solution
    # Handle the case where beta_0 might be very small or zero
    tan_atan_beta0 = np.maximum(
        np.tan(np.arctan(beta_0) - beta_0 * n_0 * a_0 * C_0 * (t - t_0)),
        0
    )  # Lower limit on eccentricity and semi-major axis reduction

    a = (a_0 / beta_0**2) * tan_atan_beta0**2
    e = (2 / np.sqrt(3)) * tan_atan_beta0

    # Handle special case when beta_0 = 0 (circular orbits)
    check_beta = beta_0 == 0
    if np.any(check_beta):
        a0_beta = a_0[check_beta]
        a[check_beta] = a0_beta * (1 \
            - C_0[check_beta] * n_0[check_beta] * a0_beta * (t - t_0))
        e[check_beta] = 0  # Remain circular

    # Compute intermediate variables to avoid repetition
    a_sq = a**2
    four_thirds_over_a_cb = 4/3 / (a_sq * a)
    a0_sq = a_0**2
    four_thirds_over_a0_cb = 4/3 / (a0_sq * a_0)
    alpha0sq_over_asq = alpha0_sq / a_sq
    alpha0sq_over_a0sq = alpha0_sq / a0_sq

    # Calculate mean anomaly
    # Protect against division by zero and log of negative numbers
    a_ratio = np.maximum(a / a_0, 1e-10)
    Mo = (0.5 / a - 0.5 / a_0 + 3/8 * alpha0_sq * np.log(a_ratio)) / C_0 + \
         3 * k2_over_mu / 16 * (3 * c_sq - 1) * \
         (1.5 * (alpha0sq_over_asq - alpha0sq_over_a0sq) + \
             four_thirds_over_a_cb - four_thirds_over_a0_cb) / C_0 + Mo_0

    # Calculate intermediate term for omega and RAAN
    five_a0sq_over2_tau2_plus_4thirds_over_tau3_over_C0 = \
        (2.5 * (alpha0sq_over_asq - alpha0sq_over_a0sq) + \
            four_thirds_over_a_cb - four_thirds_over_a0_cb) / C_0

    # Calculate argument of perigee
    omega = 3 * k2_over_mu / 16 * (5 * c_sq - 1) * five_a0sq_over2_tau2_plus_4thirds_over_tau3_over_C0 \
        + omega_0

    # Calculate RAAN
    bigO = -3 * k2_over_mu / 8 * c * five_a0sq_over2_tau2_plus_4thirds_over_tau3_over_C0 \
        + bigO_0

    # Assemble output orbital elements
    out_oe = np.column_stack([
        a,
        e,
        np.mod(inc_0, 2 * np.pi),  # Inclination (normalized)
        np.mod(bigO, 2 * np.pi),   # RAAN (normalized)
        np.mod(omega, 2 * np.pi),  # Argument of perigee (normalized)
        np.mod(Mo, 2 * np.pi)      # Mean anomaly (normalized)
    ])

    # Check for numerical errors
    not_real = ~np.isreal(inc_0) | ~np.isreal(bigO) | ~np.isreal(omega) | ~np.isreal(Mo)
    errors[not_real] = 1
    out_oe[not_real, :] = input_oe[not_real, :]

    # Additional error checks
    # Negative or zero semi-major axis
    errors[out_oe[:, 0] <= 0] = 1

    # Eccentricity out of bounds
    errors[out_oe[:, 1] < 0] = 1
    errors[out_oe[:, 1] >= 1] = 1

    # Perigee below Earth surface (100 km safety margin)
    perigee_alt = out_oe[:, 0] * (1 - out_oe[:, 1]) - re
    errors[perigee_alt < 100] = 1

    return out_oe, errors
