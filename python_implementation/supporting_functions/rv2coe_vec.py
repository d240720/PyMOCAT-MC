"""
Convert position and velocity vectors to classical orbital elements (vectorized)

This function finds the classical orbital elements given the geocentric
equatorial position and velocity vectors.

Author: David Vallado (original MATLAB), Python conversion from rv2coe_vec.m

Inputs:
    r           - ijk position vector            km (N x 3)
    v           - ijk velocity vector            km/s (N x 3)
    mu          - gravitational parameter        km3/s2

Outputs:
    p           - semilatus rectum               km
    a           - semimajor axis                 km
    ecc         - eccentricity
    incl        - inclination                    0.0 to pi rad
    omega       - longitude of ascending node    0.0 to 2pi rad
    argp        - argument of perigee            0.0 to 2pi rad
    nu          - true anomaly                   0.0 to 2pi rad
    m           - mean anomaly                   0.0 to 2pi rad
    arglat      - argument of latitude      (ci) 0.0 to 2pi rad
    truelon     - true longitude            (ce) 0.0 to 2pi rad
    lonper      - longitude of periapsis    (ee) 0.0 to 2pi rad

References:
    Vallado 2007, 121, alg 9, ex 2-5
"""

import numpy as np
import sys
import os

# Add supporting functions to path
sys.path.append(os.path.dirname(__file__))

from cross_vec import cross_vec
from angl_vec import angl_vec
from newtonnu_vec import newtonnu_vec


def rv2coe_vec(r, v, mu):
    """
    Convert position and velocity vectors to classical orbital elements

    Args:
        r: position vectors (N x 3) in km
        v: velocity vectors (N x 3) in km/s
        mu: gravitational parameter in km3/s2

    Returns:
        tuple of orbital elements:
        (p, a, ecc, incl, omega, argp, nu, m, arglat, truelon, lonper)
    """

    # Constants
    small = 1e-8
    infinite = 999999.9
    undefined = 999999.1
    twopi = 2.0 * np.pi
    halfpi = np.pi * 0.5

    # Ensure inputs are numpy arrays
    r = np.atleast_2d(r)
    v = np.atleast_2d(v)

    # Preallocation
    num_el = r.shape[0]
    a = np.zeros(num_el)
    p = np.zeros(num_el)
    ecc = np.zeros(num_el)
    incl = np.zeros(num_el)
    omega = np.zeros(num_el)
    argp = np.zeros(num_el)
    nu = np.zeros(num_el)
    m = np.zeros(num_el)
    arglat = np.zeros(num_el)
    truelon = np.zeros(num_el)
    lonper = np.zeros(num_el)

    # Implementation
    magr = np.sqrt(np.sum(r**2, axis=1))
    magv = np.sqrt(np.sum(v**2, axis=1))

    # Find h, n and e vectors
    hbar = cross_vec(r, v)
    magh = np.sqrt(np.sum(hbar**2, axis=1))
    check_small = magh > small
    idx_small = np.where(check_small)[0]
    sum_check_small = np.sum(check_small)

    if sum_check_small > 0:
        # Line of nodes vector
        nbar = np.zeros((sum_check_small, 3))
        nbar[:, 0] = -hbar[idx_small, 1]
        nbar[:, 1] = hbar[idx_small, 0]
        magn = np.sqrt(np.sum(nbar**2, axis=1))

        # Extract values for valid orbits
        magr_check = magr[idx_small]
        magv_check = magv[idx_small]
        magh_check = magh[idx_small]
        r_check = r[idx_small, :]
        v_check = v[idx_small, :]

        # Calculate eccentricity vector
        c1 = magv_check**2 - mu / magr_check
        rdotv = np.sum(r_check * v_check, axis=1)
        ebar = np.zeros((sum_check_small, 3))
        ebar[:, 0] = (c1 * r_check[:, 0] - rdotv * v_check[:, 0]) / mu
        ebar[:, 1] = (c1 * r_check[:, 1] - rdotv * v_check[:, 1]) / mu
        ebar[:, 2] = (c1 * r_check[:, 2] - rdotv * v_check[:, 2]) / mu
        ecci = np.sqrt(np.sum(ebar**2, axis=1))

        # Find a, e and semi-latus rectum
        sme = (magv_check**2 * 0.5) - (mu / magr_check)
        check_sme = np.abs(sme) > small
        a[idx_small[check_sme]] = -mu / (2.0 * sme[check_sme])
        a[idx_small[~check_sme]] = infinite
        p[idx_small] = magh_check**2 / mu

        # Find inclination
        hk = hbar[idx_small, 2] / magh_check
        # Clamp to [-1, 1] to avoid numerical errors
        hk = np.clip(hk, -1.0, 1.0)
        incli = np.arccos(hk)

        # Determine type of orbit for later use
        # [0,1,2,3] = [ei,ee,ce,ci], ei is default
        typeorbit = np.zeros(sum_check_small, dtype=int)
        check_ecc = ecci < small
        check_notecc = ~check_ecc
        idx_ecc = np.where(check_ecc)[0]
        idx_notecc = np.where(check_notecc)[0]

        if len(idx_ecc) > 0:
            check_in = (incli[idx_ecc] < small) | (np.abs(incli[idx_ecc] \
                - np.pi) < small)
            # Circular equatorial
            typeorbit[idx_ecc[check_in]] = 2
            # Circular inclined
            typeorbit[idx_ecc[~check_in]] = 3

        # Elliptical, parabolic, hyperbolic equatorial
        if len(idx_notecc) > 0:
            check_eq = (incli[idx_notecc] < small) | (np.abs(incli[idx_notecc] \
                - np.pi) < small)
            typeorbit[idx_notecc[check_eq]] = 1

        # Find longitude of ascending node
        check_magn = magn > small
        if np.any(check_magn):
            temp = nbar[check_magn, 0] / magn[check_magn]
            temp = np.clip(temp, -1.0, 1.0)
            omega_temp = np.arccos(temp)
            check_nbar = nbar[check_magn, 1] < 0.0
            omega_temp[check_nbar] = twopi - omega_temp[check_nbar]
            omega[idx_small[check_magn]] = omega_temp
            omega[idx_small[~check_magn]] = undefined
        else:
            omega[idx_small] = undefined

        # Find argument of perigee
        check_ei = typeorbit == 0
        if np.any(check_ei):
            argp_temp = angl_vec(nbar[check_ei, :], ebar[check_ei, :])
            check_ebar = ebar[check_ei, 2] < 0.0
            argp_temp[check_ebar] = twopi - argp_temp[check_ebar]
            argp[idx_small[check_ei]] = argp_temp
            argp[idx_small[~check_ei]] = undefined
        else:
            argp[idx_small] = undefined

        # Find true anomaly at epoch
        check_e = typeorbit < 1.5
        if np.any(check_e):
            nu_temp = angl_vec(ebar[check_e, :], r_check[check_e, :])
            check_rdotv = rdotv[check_e] < 0.0
            nu_temp[check_rdotv] = twopi - nu_temp[check_rdotv]
            nu[idx_small[check_e]] = nu_temp
            nu[idx_small[~check_e]] = undefined
        else:
            nu[idx_small] = undefined

        # Find argument of latitude - circular inclined
        check_ci = typeorbit == 3
        if np.any(check_ci):
            arglat_temp = angl_vec(nbar[check_ci, :], r_check[check_ci, :])
            check_r = r_check[check_ci, 2] < 0.0
            arglat_temp[check_r] = twopi - arglat_temp[check_r]
            arglat[idx_small[check_ci]] = arglat_temp
            m[idx_small[check_ci]] = arglat_temp
            arglat[idx_small[~check_ci]] = undefined
        else:
            arglat[idx_small] = undefined

        # Find longitude of perigee - elliptical equatorial
        if len(idx_notecc) > 0:
            check_ee = typeorbit[idx_notecc] == 1
            idx_ee = idx_notecc[check_ee]

            if len(idx_ee) > 0:
                temp = ebar[idx_ee, 0] / ecci[idx_ee]
                temp = np.clip(temp, -1.0, 1.0)
                lonper_temp = np.arccos(temp)
                check_ebar = ebar[idx_ee, 1] < 0.0
                lonper_temp[check_ebar] = twopi - lonper_temp[check_ebar]
                check_incl = incli[idx_ee] > halfpi
                lonper_temp[check_incl] = twopi - lonper_temp[check_incl]
                lonper[idx_small[idx_ee]] = lonper_temp
                lonper[idx_small[idx_notecc[~check_ee]]] = undefined
            else:
                lonper[idx_small[idx_notecc]] = undefined

        # Find true longitude - circular equatorial
        check_magr = (magr_check > 0) & (typeorbit == 2)
        if np.any(check_magr):
            temp = r_check[check_magr, 0] / magr_check[check_magr]
            temp = np.clip(temp, -1.0, 1.0)
            truelon_temp = np.arccos(temp)
            check_r = r_check[check_magr, 1] < 0.0
            truelon_temp[check_r] = twopi - truelon_temp[check_r]
            check_incl = incli[check_magr] > halfpi
            truelon_temp[check_incl] = twopi - truelon_temp[check_incl]
            truelon[idx_small[check_magr]] = truelon_temp
            m[idx_small[check_magr]] = truelon_temp
            truelon[idx_small[~check_magr]] = undefined
        else:
            truelon[idx_small] = undefined

        # Find mean anomaly for all orbits
        if np.any(check_e):
            _, m_temp = newtonnu_vec(ecci[check_e], nu[idx_small[check_e]])
            m[idx_small[check_e]] = m_temp

        # Assign calculated values
        ecc[idx_small] = ecci
        incl[idx_small] = incli

    # Handle small angular momentum cases
    idx_notsmall = np.where(~check_small)[0]
    if len(idx_notsmall) > 0:
        p[idx_notsmall] = undefined
        a[idx_notsmall] = undefined
        ecc[idx_notsmall] = undefined
        incl[idx_notsmall] = undefined
        omega[idx_notsmall] = undefined
        argp[idx_notsmall] = undefined
        nu[idx_notsmall] = undefined
        m[idx_notsmall] = undefined
        arglat[idx_notsmall] = undefined
        truelon[idx_notsmall] = undefined
        lonper[idx_notsmall] = undefined

    return p, a, ecc, incl, omega, argp, nu, m, arglat, truelon, lonper
