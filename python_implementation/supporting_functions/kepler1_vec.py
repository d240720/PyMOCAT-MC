"""
Solve Kepler's equation for circular, elliptic and hyperbolic orbits (vectorized)
using Danby's method

Input:
    manom = mean anomaly (radians) - array
    ecc   = orbital eccentricity (non-dimensional) - array

Output:
    eanom = eccentric anomaly (radians) - array

Reference: Orbital Mechanics with MATLAB
"""

import numpy as np


def kepler1_vec(manom, ecc):
    """
    Solve Kepler's equation for multiple orbits (vectorized)

    Args:
        manom: mean anomaly (radians) - array
        ecc: orbital eccentricity (non-dimensional) - array

    Returns:
        eanom: eccentric anomaly (radians) - array
    """

    # Ensure inputs are numpy arrays
    manom = np.atleast_1d(manom)
    ecc = np.atleast_1d(ecc)

    # Define convergence criterion
    ktol = 1.0e-10
    pi2 = 2.0 * np.pi

    # Normalize mean anomaly
    xma = manom - pi2 * np.fix(manom / pi2)

    # Initialize output
    eanom = np.zeros_like(ecc)

    # Initial guess based on orbit type
    check_ecc_0 = (ecc == 0)  # circular orbit
    check_ecc_above_1 = (ecc >= 1.0)  # hyperbolic orbit
    check_ecc_hyp = np.where(check_ecc_above_1)[0]
    # elliptical, not circular
    check_ecc_ellip = np.where(~check_ecc_above_1 & ~check_ecc_0)[0]

    # Circular orbit
    eanom[check_ecc_0] = xma[check_ecc_0]

    # Elliptic orbit
    if len(check_ecc_ellip) > 0:
        eanom[check_ecc_ellip] = (xma[check_ecc_ellip] +
                                 0.85 * np.sign(np.sin(xma[check_ecc_ellip])) *
                                 ecc[check_ecc_ellip])

    # Hyperbolic orbit
    if len(check_ecc_hyp) > 0:
        eanom[check_ecc_hyp] = np.log(2.0 * xma[check_ecc_hyp] / ecc[check_ecc_hyp] \
            + 1.8)

    # Perform iterations
    niter = 0

    # Keep track of indices that still need iteration
    check_ecc_ellip_temp = check_ecc_ellip.copy()
    check_ecc_hyp_temp = check_ecc_hyp.copy()

    while (len(check_ecc_ellip_temp) > 0 or len(check_ecc_hyp_temp) > 0):

        # Initialize arrays for current iteration
        fe = np.array([])
        fpe = np.array([])
        fppe = np.array([])
        fpppe = np.array([])

        fh = np.array([])
        fph = np.array([])
        fpph = np.array([])
        fppph = np.array([])

        # Elliptic orbit calculations
        if len(check_ecc_ellip_temp) > 0:
            se = ecc[check_ecc_ellip_temp] \
                * np.sin(eanom[check_ecc_ellip_temp])
            ce = ecc[check_ecc_ellip_temp] \
                * np.cos(eanom[check_ecc_ellip_temp])

            fe = eanom[check_ecc_ellip_temp] - se - xma[check_ecc_ellip_temp]
            fpe = 1 - ce
            fppe = se
            fpppe = ce

        # Hyperbolic orbit calculations
        if len(check_ecc_hyp_temp) > 0:
            sh = ecc[check_ecc_hyp_temp] * np.sinh(eanom[check_ecc_hyp_temp])
            ch = ecc[check_ecc_hyp_temp] * np.cosh(eanom[check_ecc_hyp_temp])

            fh = sh - eanom[check_ecc_hyp_temp] - xma[check_ecc_hyp_temp]
            fph = ch - 1
            fpph = sh
            fppph = ch

        niter += 1

        # Check for convergence
        if len(fe) > 0:
            idx_above_e = np.abs(fe) > ktol
            check_ecc_ellip_temp = check_ecc_ellip_temp[idx_above_e]
            fe = fe[idx_above_e]
            fpe = fpe[idx_above_e]
            fppe = fppe[idx_above_e]
            fpppe = fpppe[idx_above_e]
        else:
            idx_above_e = np.array([], dtype=bool)

        if len(fh) > 0:
            idx_above_h = np.abs(fh) > ktol
            check_ecc_hyp_temp = check_ecc_hyp_temp[idx_above_h]
            fh = fh[idx_above_h]
            fph = fph[idx_above_h]
            fpph = fpph[idx_above_h]
            fppph = fppph[idx_above_h]
        else:
            idx_above_h = np.array([], dtype=bool)

        if niter > 20 or (len(check_ecc_ellip_temp) == 0 and len(check_ecc_hyp_temp) == 0):
            break

        # Combine elliptic and hyperbolic cases
        check_f = np.concatenate([check_ecc_ellip_temp, check_ecc_hyp_temp])
        f = np.concatenate([fe, fh])
        fp = np.concatenate([fpe, fph])
        fpp = np.concatenate([fppe, fpph])
        fppp = np.concatenate([fpppe, fppph])

        # Update eccentric anomaly using Danby's method
        delta = -f / fp
        deltastar = -f / (fp + 0.5 * delta * fpp)
        deltak = -f / (fp + 0.5 * deltastar * fpp +
                      deltastar * deltastar * fppp / 6)

        eanom[check_f] = eanom[check_f] + deltak

    if niter > 20:
        print('\n\n   more than 20 iterations in kepler1_vec \n\n')

    return eanom
