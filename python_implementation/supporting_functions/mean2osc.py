"""
Convert mean classical orbital elements to osculating classical orbital elements.

Converts mean orbital elements (affected by J2 perturbations) to osculating
(instantaneous) orbital elements.

Args:
    oemean: mean orbital elements [6x1]
        oemean[0] = mean semimajor axis (kilometers)
        oemean[1] = mean orbital eccentricity (0 <= e < 1)
        oemean[2] = mean orbital inclination (radians, 0 <= i <= pi)
        oemean[3] = mean right ascension of ascending node (
            radians,
            0 <= raan <= 2*pi)
        oemean[4] = mean argument of perigee (radians, 0 <= argp <= 2*pi)
        oemean[5] = mean true anomaly (radians, 0 <= ta <= 2*pi)
    param: parameter structure containing:
        mu: gravitational parameter (km^3/s^2)
        req: Earth radius (km)
        j2: J2 gravitational coefficient

Returns:
    oeosc: osculating orbital elements [6x1]
        oeosc[0] = osculating semimajor axis (kilometers)
        oeosc[1] = osculating orbital eccentricity (0 <= e < 1)
        oeosc[2] = osculating orbital inclination (radians, 0 <= i <= pi)
        oeosc[3] = osculating right ascension of ascending node (
            radians,
            0 <= raan <= 2*pi)
        oeosc[4] = osculating argument of perigee (radians, 0 <= argp <= 2*pi)
        oeosc[5] = osculating true anomaly (radians, 0 <= ta <= 2*pi)

Reference: Orbital Mechanics with MATLAB
"""

import numpy as np
import sys
import os

# Add supporting functions to path
sys.path.append(os.path.dirname(__file__))

from kepler1 import kepler1


def atan3(y, x):
    """
    Four-quadrant arctangent function similar to atan2 but with different behavior
    """
    return np.arctan2(y, x)


def anomly(nflg, ain, e):
    """
    Orbital anomaly conversion function

    Args:
        nflg: conversion flag
              1,2: mean anomaly to eccentric/true anomaly
              3,4: eccentric anomaly to mean/true anomaly
              5,6: true anomaly to mean/eccentric anomaly
        ain: input anomaly
        e: eccentricity

    Returns:
        aout: output anomaly
    """

    if nflg in [1, 2]:
        am = ain
    elif nflg in [3, 4]:
        ea = ain
    elif nflg in [5, 6]:
        f = ain

    if nflg == 1 or nflg == 2:
        ea, _ = kepler1(am, e)

    if nflg == 2 or nflg == 4:
        f = 2.0 * np.arctan(np.sqrt((1.0 + e) / (1.0 - e)) * np.tan(ea / 2.0))

    if nflg == 5 or nflg == 6:
        ea = 2.0 * np.arctan(np.sqrt((1.0 - e) / (1.0 + e)) * np.tan(f / 2.0))

    if nflg == 5 or nflg == 3:
        am = ea - e * np.sin(ea)

    if nflg in [1, 6]:
        aout = ea
    elif nflg in [2, 4]:
        aout = f
    elif nflg in [3, 5]:
        aout = am

    return aout


def delm(x, param):
    """
    J2 effect on orbital elements

    Args:
        x: orbital elements [6x1]
        param: parameter structure

    Returns:
        dx: J2 perturbations to orbital elements [6x1]
    """

    mu = param['mu']
    req = param['req']
    j2 = param['j2']

    pi2 = 2.0 * np.pi

    a = x[0]
    e = x[1]
    ai = x[2]
    an = x[3]
    w = x[4]
    am = x[5]

    f = anomly(2, am, e)
    f = (f + pi2) % pi2
    am = (am + pi2) % pi2

    si = np.sin(ai)
    ci = np.cos(ai)
    ti = si / ci
    si2 = si * si
    ci2 = ci * ci

    sf = np.sin(f)
    cf = np.cos(f)
    s2f = np.sin(2.0 * f)

    u = f + w
    e2 = e * e
    esf = e * sf

    d1 = 1.0 - e2
    d2 = np.sqrt(d1)
    d3 = e * cf
    d4 = 1.0 + d3
    d42 = d4 * d4
    d5 = 1.0 + d2
    d6 = (3.0 * ci2 - 1.0) / d5

    p = a * d1
    d7 = np.sqrt(mu / p)
    r = p / d4
    rdot = d7 * esf

    twou = 2.0 * u
    twow = 2.0 * w

    s2u = np.sin(twou)
    c2u = np.cos(twou)

    sf2w = np.sin(f + twow)
    d8 = 3.0 * f + twow
    s3f2w = np.sin(d8)

    cf2w = np.cos(f + twow)
    c3f2w = np.cos(d8)

    q1 = j2 * (req / p)**2

    di = 0.75 * q1 * si * ci * (c2u + e * cf2w + e / 3.0 * c3f2w)

    dp = 2.0 * p * ti * di

    dummy1 = f - am + esf - 0.5 * s2u - 0.5 * e * sf2w - e * s3f2w / 6.0

    dn = -1.5 * q1 * ci * dummy1

    dr = -0.25 * p * q1 * ((3.0 * ci2 - 1.0) *
                           (2.0 * d2 / d4 + d3 / d5 + 1.0) - si2 * c2u)

    drdot = 0.25 * d7 * q1 * (d6 * esf * (d2 * d5 + d42) -
                              2.0 * si2 * d42 * s2u)

    du = -0.125 * q1 * (6.0 * (1.0 - 5.0 * ci2) * (f - am) +
                        4.0 * esf * ((1.0 - 6.0 * ci2) - d6) -
                        d6 * e2 * s2f + 2.0 * (5.0 * ci2 - 2.0) * e * sf2w +
                        (7.0 * ci2 - 1.0) * s2u + 2.0 * ci2 * e * s3f2w)

    pnw = p + dp
    ainw = ai + di
    annw = an + dn
    rnw = r + dr
    rdotnw = rdot + drdot
    unw = u + du

    aa = pnw / rnw - 1.0
    bb = np.sqrt(pnw / mu) * rdotnw

    enw2 = aa * aa + bb * bb
    enw = np.sqrt(enw2)

    xfnw = np.arctan2(bb, aa)

    anw = pnw / (1.0 - enw2)
    wnw = unw - xfnw

    amnw = anomly(5, xfnw, enw)

    dx = np.zeros(6)
    dx[0] = anw - a
    dx[1] = enw - e
    dx[2] = ainw - ai
    dx[3] = annw - an
    dx[4] = wnw - w
    dx[5] = amnw - am

    return dx


def mean2osc(oemean, param):
    """
    Convert mean classical orbital elements to osculating classical orbital elements

    Args:
        oemean: mean orbital elements [6x1]
        param: parameter structure

    Returns:
        oeosc: osculating orbital elements [6x1]
    """

    pi2 = 2.0 * np.pi

    oewrk = oemean.copy()

    # Compute J2 effect on orbital elements
    doe = delm(oemean, param)

    oeosc = oewrk + doe

    # Normalize angles to [0, 2*pi]
    for i in range(2, 6):
        oeosc[i] = (oeosc[i] + pi2) % pi2

    return oeosc
