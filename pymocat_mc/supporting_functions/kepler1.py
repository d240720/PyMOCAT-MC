"""
Solve Kepler's equation for circular, elliptic and hyperbolic orbits
using Danby's method

Input:
    manom = mean anomaly (radians)
    ecc   = orbital eccentricity (non-dimensional)

Output:
    eanom = eccentric anomaly (radians)
    tanom = true anomaly (radians)

Reference: Orbital Mechanics with MATLAB
"""

import numpy as np


def kepler1(manom, ecc):
    """
    Solve Kepler's equation for a single orbit

    Args:
        manom: mean anomaly (radians)
        ecc: orbital eccentricity (non-dimensional)

    Returns:
        eanom: eccentric anomaly (radians)
        tanom: true anomaly (radians)
    """

    # Define convergence criterion
    ktol = 1.0e-10
    pi2 = 2.0 * np.pi

    # Normalize mean anomaly
    xma = manom - pi2 * np.fix(manom / pi2)

    # Initial guess
    if ecc == 0.0:
        # Circular orbit
        tanom = xma
        eanom = xma
        return eanom, tanom
    elif ecc < 1.0:
        # Elliptic orbit
        eanom = xma + 0.85 * np.sign(np.sin(xma)) * ecc
    else:
        # Hyperbolic orbit
        eanom = np.log(2.0 * xma / ecc + 1.8)

    # Perform iterations
    niter = 0

    while True:
        if ecc < 1:
            # Elliptic orbit
            s = ecc * np.sin(eanom)
            c = ecc * np.cos(eanom)

            f = eanom - s - xma
            fp = 1 - c
            fpp = s
            fppp = c
        else:
            # Hyperbolic orbit
            s = ecc * np.sinh(eanom)
            c = ecc * np.cosh(eanom)

            f = s - eanom - xma
            fp = c - 1
            fpp = s
            fppp = c

        niter += 1

        # Check for convergence
        if abs(f) <= ktol or niter > 20:
            break

        # Update eccentric anomaly using Danby's method
        delta = -f / fp
        deltastar = -f / (fp + 0.5 * delta * fpp)
        deltak = -f / (fp + 0.5 * deltastar * fpp +
                      deltastar * deltastar * fppp / 6)

        eanom = eanom + deltak

    if niter > 20:
        print('\n\n   more than 20 iterations in kepler1 \n\n')
        return eanom, np.nan

    # Compute true anomaly
    if ecc < 1:
        # Elliptic orbit
        sta = np.sqrt(1 - ecc * ecc) * np.sin(eanom)
        cta = np.cos(eanom) - ecc
    else:
        # Hyperbolic orbit
        sta = np.sqrt(ecc * ecc - 1) * np.sinh(eanom)
        cta = ecc - np.cosh(eanom)

    tanom = np.arctan2(sta, cta)

    return eanom, tanom
