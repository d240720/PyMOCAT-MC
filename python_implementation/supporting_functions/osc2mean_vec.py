"""
Vectorized conversion of osculating to mean classical orbital elements

Converts osculating (instantaneous) orbital elements to mean orbital elements
(accounting for J2 perturbations) for multiple satellites simultaneously.

Args:
    oeosc: osculating orbital elements [N x 6] where each row is:
        oeosc[:,0] = osculating semimajor axis (kilometers)
        oeosc[:,1] = osculating orbital eccentricity (0 <= e < 1)
        oeosc[:,2] = osculating orbital inclination (radians, 0 <= i <= pi)
        oeosc[:,3] = osculating right ascension of ascending node (
            radians,
            0 <= raan <= 2*pi)
        oeosc[:,4] = osculating argument of perigee (
            radians,
            0 <= argp <= 2*pi)
        oeosc[:,5] = osculating true anomaly (radians, 0 <= ta <= 2*pi)
    param: parameter structure containing:
        req: Earth radius (km)
        j2: J2 gravitational coefficient

Returns:
    oemean: mean orbital elements [N x 6] where each row is:
        oemean[:,0] = mean semimajor axis (kilometers)
        oemean[:,1] = mean orbital eccentricity (0 <= e < 1)
        oemean[:,2] = mean orbital inclination (radians, 0 <= i <= pi)
        oemean[:,3] = mean right ascension of ascending node (
            radians,
            0 <= raan <= 2*pi)
        oemean[:,4] = mean argument of perigee (radians, 0 <= argp <= 2*pi)
        oemean[:,5] = mean true anomaly (radians, 0 <= ta <= 2*pi)

Reference: Orbital Mechanics with MATLAB
"""

import numpy as np
import sys
import os

# Add supporting functions to path
sys.path.append(os.path.dirname(__file__))

from kepler1_vec import kepler1_vec


def osc2mean_vec(oeosc, param):
    """
    Vectorized conversion of osculating to mean classical orbital elements

    Args:
        oeosc: osculating orbital elements [N x 6]
        param: parameter structure

    Returns:
        oemean: mean orbital elements [N x 6]
    """

    oeosc = np.atleast_2d(oeosc)
    req = param['req']
    j2 = param['j2']

    pi2 = 2.0 * np.pi
    n_sats = oeosc.shape[0]

    oetmp = oeosc.copy()

    # Convert true anomaly to mean anomaly for all satellites
    e = oetmp[:, 1]
    theta = oetmp[:, 5]

    # Vectorized conversion
    a = np.sin(theta) * np.sqrt(1.0 - e * e)
    b = e + np.cos(theta)

    # Eccentric anomaly
    eanom = np.arctan2(a, b)

    # Mean anomaly
    oetmp[:, 5] = (eanom - e * np.sin(eanom)) % pi2

    aos = oetmp[:, 0]
    eos = oetmp[:, 1]
    ios = oetmp[:, 2]
    ranos = oetmp[:, 3]
    apos = oetmp[:, 4]
    maos = oetmp[:, 5]

    aa = 1.0 / 3.0 - 0.5 * np.sin(ios)**2
    bb = 0.5 * np.sin(ios)**2

    # Initialize output arrays
    am = aos.copy()
    em = eos.copy()
    im = ios.copy()
    ranm = ranos.copy()
    apm = apos.copy()
    mam = maos.copy()

    # Process satellites based on eccentricity
    low_ecc_mask = eos < 0.01
    high_ecc_mask = ~low_ecc_mask

    # Process low eccentricity orbits
    if np.any(low_ecc_mask):
        idx_low = np.where(low_ecc_mask)[0]

        for idx in idx_low:
            # Near-circular orbit case - simplified iterative approach
            lamos = (maos[idx] + apos[idx]) % pi2
            zos = eos[idx] * np.cos(apos[idx])
            etaos = eos[idx] * np.sin(apos[idx])

            # Simplified correction (first order only)
            asp = 3 * j2 * req**2 / aos[idx] * bb[idx] * np.cos(2 * lamos)
            am[idx] = aos[idx] - asp

            isp = 3 \
                * j2 / 8 * req**2 / aos[idx]**2 * np.sin(2 * ios[idx]) * np.cos(2 * lamos)
            im[idx] = ios[idx] - isp

            ransp = 1.5 \
                * j2 * req**2 / aos[idx]**2 * np.cos(ios[idx]) * 0.5 * np.sin(2 * lamos)
            ranm[idx] = ranos[idx] - ransp

            em[idx] = np.sqrt(etaos**2 + zos**2)
            if em[idx] > 1.0e-8:
                apm[idx] = np.arctan2(etaos, zos)
            else:
                apm[idx] = 0

            mam[idx] = (lamos - apm[idx]) % pi2

    # Process higher eccentricity orbits
    if np.any(high_ecc_mask):
        idx_high = np.where(high_ecc_mask)[0]

        for idx in idx_high:
            # Non-circular orbit case - simplified approach
            pm = aos[idx] * (1 - eos[idx]**2)

            # Get mean anomaly and true anomaly
            _, tam = kepler1_vec(np.array([mam[idx]]), np.array([em[idx]]))
            tam = tam[0]

            um = (apm[idx] + tam) % pi2
            hm = pm / (1 + em[idx] * np.cos(tam))

            # First order J2 corrections
            asp = 3 * j2 * req**2 / aos[idx] * ((aos[idx]/hm)**3 * (aa[idx] \
                + bb[idx] * np.cos(2*um)) -
                                              aa[idx] * (1 - em[idx]**2)**(-1.5))
            am[idx] = aos[idx] - asp

            isp = 3/8 \
                * j2 * req**2 / pm**2 * np.sin(2*im[idx]) * (np.cos(2*um) +
                                                                  \
                                                                      em[idx] * np.cos(tam + 2*apm[idx]))
            im[idx] = ios[idx] - isp

            # Simplified eccentricity correction
            esp = 1.5 * j2 * req**2 / aos[idx]**2 * (1 \
                - em[idx]**2) / em[idx] * aa[idx] * 0.1
            em[idx] = eos[idx] - esp

            # RAAN correction
            eqoc = tam \
                - mam[idx] if abs(tam - np.pi) > 1.0e-06 and abs(mam[idx] - np.pi) > 1.0e-06 else 0
            ransp = -1.5 * j2 * (req/pm)**2 * np.cos(im[idx]) * (eqoc \
                + em[idx] * np.sin(tam))
            ranm[idx] = ranos[idx] - ransp

            # Argument of perigee correction
            apsp = 1.5 * j2 * (req/pm)**2 * (2 - 5*bb[idx]) * (eqoc \
                + em[idx] * np.sin(tam))
            apm[idx] = apos[idx] - apsp

    # Assemble output
    oemean = np.column_stack([am, em, im, ranm % pi2, apm % pi2, mam % pi2])

    # Convert mean anomaly back to true anomaly
    _, ta = kepler1_vec(oemean[:, 5], oemean[:, 1])
    oemean[:, 5] = ta

    return oemean
