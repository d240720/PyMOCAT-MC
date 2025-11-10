"""
Convert osculating classical orbital elements to mean classical orbital elements

Converts osculating (instantaneous) orbital elements to mean orbital elements
(accounting for J2 perturbations).

Args:
    oeosc: osculating orbital elements [6x1]
        oeosc[0] = osculating semimajor axis (kilometers)
        oeosc[1] = osculating orbital eccentricity (0 <= e < 1)
        oeosc[2] = osculating orbital inclination (radians, 0 <= i <= pi)
        oeosc[3] = osculating right ascension of ascending node (
            radians,
            0 <= raan <= 2*pi)
        oeosc[4] = osculating argument of perigee (radians, 0 <= argp <= 2*pi)
        oeosc[5] = osculating true anomaly (radians, 0 <= ta <= 2*pi)
    param: parameter structure containing:
        req: Earth radius (km)
        j2: J2 gravitational coefficient

Returns:
    oemean: mean orbital elements [6x1]
        oemean[0] = mean semimajor axis (kilometers)
        oemean[1] = mean orbital eccentricity (0 <= e < 1)
        oemean[2] = mean orbital inclination (radians, 0 <= i <= pi)
        oemean[3] = mean right ascension of ascending node (
            radians,
            0 <= raan <= 2*pi)
        oemean[4] = mean argument of perigee (radians, 0 <= argp <= 2*pi)
        oemean[5] = mean true anomaly (radians, 0 <= ta <= 2*pi)

Reference: Orbital Mechanics with MATLAB
"""

import numpy as np
import sys
import os

# Add supporting functions to path
sys.path.append(os.path.dirname(__file__))

kepler1 import kepler1


def atan3(a, b):
    """
    Four-quadrant arctangent function similar to atan2
    """
    return np.arctan2(a, b)


def osc2mean(oeosc, param):
    """
    Convert osculating classical orbital elements to mean classical orbital elements

    Args:
        oeosc: osculating orbital elements [6x1]
        param: parameter structure

    Returns:
        oemean: mean orbital elements [6x1]
    """

    req = param['req']
    j2 = param['j2']

    pi2 = 2.0 * np.pi

    oetmp = oeosc.copy()

    # Convert true anomaly to mean anomaly
    a = np.sin(oetmp[5]) * np.sqrt(1.0 - oetmp[1] * oetmp[1])
    b = oetmp[1] + np.cos(oetmp[5])

    # Eccentric anomaly
    eanom = atan3(a, b)

    # Mean anomaly
    oetmp[5] = (eanom - oetmp[1] * np.sin(eanom)) % pi2

    aos = oetmp[0]
    eos = oetmp[1]
    ios = oetmp[2]
    ranos = oetmp[3]
    apos = oetmp[4]
    maos = oetmp[5]

    aa = 1.0 / 3.0 - 0.5 * np.sin(ios)**2
    bb = 0.5 * np.sin(ios)**2

    if eos < 0.01:
        # Near-circular orbit case
        lamos = (maos + apos) % pi2

        zos = eos * np.cos(apos)
        etaos = eos * np.sin(apos)

        sl = np.sin(lamos)
        cl = np.cos(lamos)
        s2l = np.sin(2 * lamos)
        c2l = np.cos(2 * lamos)
        s3l = np.sin(3 * lamos)
        c3l = np.cos(3 * lamos)
        s4l = np.sin(4 * lamos)
        c4l = np.cos(4 * lamos)

        s2i = np.sin(2 * ios)
        ci = np.cos(ios)

        am = aos
        im = ios
        ranm = ranos
        mam = maos
        lamm = lamos
        zm = zos
        etam = etaos

        # Iterative solution
        for n in range(5):
            asp = 3 * j2 * req * req / am * (bb * c2l + (1 - 3.5 * bb) *
                                           zm * cl + (1 - 2.5 * bb) * etam * sl + 3.5 * bb *
                                           (zm * c3l + etam * s3l))

            am = aos - asp

            isp = 3 * j2 / 8 * req * req / am**2 * s2i * (c2l - zm * cl +
                                                        etam * sl + 7/3 * (zm * c3l + etam * s3l))

            im = ios - isp
            ci = np.cos(im)
            s2i = np.sin(2 * im)
            bb = 0.5 * np.sin(im)**2

            ransp = 1.5 * j2 * req * req / am**2 * ci * \
                   (0.5 * s2l - 3.5 * zm * sl + 2.5 * etam * cl +
                    7/6 * (zm * s3l - etam * c3l))

            ranm = ranos - ransp

            lamsp = 1.5 * j2 * req * req / (am * am) * \
                   (-0.5 * (1 - 5 * bb) * s2l + (7 - 77/4 * bb) *
                    zm * sl - (6 - 55/4 * bb) * etam * cl - (7/6 - 77/12 * bb) *
                    (zm * s3l - etam * c3l))

            lamm = lamos - lamsp

            sl = np.sin(lamm)
            cl = np.cos(lamm)
            s2l = np.sin(2*lamm)
            c2l = np.cos(2*lamm)
            s3l = np.sin(3*lamm)
            c3l = np.cos(3*lamm)
            s4l = np.sin(4*lamm)
            c4l = np.cos(4*lamm)

            zsp = 1.5 * j2 * req * req / am**2 * ((1 - 2.5 * bb) * cl +
                                                7/6 * bb * c3l + (1.5 \
                                                    - 5 * bb) * zm * c2l + (2 - 3 * bb) *
                                                etam * s2l + 17/4 * bb * (zm * c4l + etam * s4l))

            zm = zos - zsp

            etasp = 1.5 * j2 * req * req / am**2 * ((1 - 3.5 * bb) * sl +
                                                  7/6 * bb * s3l + (1 \
                                                      - 6 * bb) * zm * s2l - (1.5 - 4 * bb) *
                                                  etam * c2l + 17/4 * \
                                                      bb * (zm * s4l - etam * c4l))

            etam = etaos - etasp

        em = np.sqrt(etam**2 + zm**2)

        apm = 0
        if em > 1.0e-8:
            apm = np.arctan2(etam, zm)

        # "mean" mean anomaly
        mam = (lamm - apm) % pi2

    else:
        # Non-circular orbit case
        pm = aos * (1 - eos**2)
        am = aos
        em = eos
        im = ios
        apm = apos
        ranm = ranos
        mam = maos

        _, tam = kepler1(mam, em)

        um = (apm + tam) % pi2
        hm = pm / (1 + em * np.cos(tam))

        # Iterative solution
        for n in range(5):
            asp = 3 * j2 * req * req / am * ((am/hm)**3 * (aa \
                + bb * np.cos(2*um)) -
                                           aa * (1 - em**2)**(-1.5))

            am = aos - asp

            isp = 3/8 * j2 * req**2 / pm**2 * np.sin(2*im) * (
                np.cos(2*um) + em * np.cos(tam + 2*apm) +
                1/3 * em * np.cos(3*tam + 2*apm)
            )

            im = ios - isp
            aa = 1/3 - 0.5 * np.sin(im)**2
            bb = 0.5 * np.sin(im)**2

            esp = 1.5 * j2 * req * req / am**2 * ((1 \
                - em**2) / em * ((am/hm)**3 *
                                                                   \
                                                                       (aa + bb * np.cos(2*um)) - aa * (1 - em**2)**(-1.5)) - bb / (em * (1 - em**2)) *
                                                (np.cos(2*um) + em * \
                                                    np.cos(tam + 2*apm) + em * np.cos(3*tam + 2*apm) / 3))

            em = eos - esp
            pm = am * (1.0 - em**2)
            hm = pm / (1.0 + em * np.cos(tam))

            tam = tam % (2.0 * np.pi)
            mam = mam % (2.0 * np.pi)

            if ((abs(tam - np.pi) <= 1.0e-06) \
                or (abs(mam - np.pi) <= 1.0e-06) or
                (abs(tam) <= 1.0e-06) or (abs(mam) <= 1.0e-06)):
                eqoc = 0
            else:
                eqoc = tam - mam

            ransp = -1.5 * j2 * (req/pm)**2 * np.cos(im) * (eqoc \
                + em * np.sin(tam) -
                                                           0.5 * \
                                                               np.sin(2*um) - 0.5 * em * np.sin(tam + 2*apm) - 1/6 * em * np.sin(3*tam + 2*apm))

            ranm = ranos - ransp

            apsp = 1.5 * j2 * (req/pm)**2 * ((2 - 5*bb) * (eqoc \
                + em * np.sin(tam)) +
                                           (1 - 3*bb) * ((1 - \
                                               0.25*em*em) * np.sin(tam) / em + 0.5 * np.sin(2*tam) +
                                                        em * \
                                                            np.sin(3*tam) / 12) - (0.5*bb + (0.5 - 15/8*bb) * em**2) / em * np.sin(tam + 2*apm) +
                                           em/8*bb * np.sin(tam - \
                                               2*apm) - 0.5*(1 - 5*bb) * np.sin(2*um) + (7/6*bb -
                                                                      \
                                                                                                             1/6*em**2*(1 - 19/4*bb)) / em * np.sin(3*tam + 2*apm) +
                                           0.75*bb * np.sin(4*tam + \
                                               2*apm) + em/8*bb * np.sin(5*tam + 2*apm))

            apm = apos - apsp

            masp = 1.5 * j2 * (req/pm)**2 * np.sqrt(1 \
                - em**2) / em * (-(1 - 3*bb) * ((1 - em**2/4) *
                                                                      \
                                                                                        np.sin(tam) + em/2 * np.sin(2*tam) + em**2/12 * np.sin(3*tam)) +
                                                                      \
                                                                          bb * (0.5*(1 + 1.25*em**2) * np.sin(tam + 2*apm) - em**2/8 * np.sin(tam - 2*apm) -
                                                                      \
                                                                                7/6*(1 - em**2/28) * np.sin(3*tam + 2*apm) - 0.75*em * np.sin(4*tam + 2*apm) -
                                                                      \
                                                                                em**2/8 * np.sin(5*tam + 2*apm)))

            mam = maos - masp

            _, tam = kepler1(mam, em)

            um = (apm + tam) % pi2

    oemean = np.zeros(6)
    oemean[0] = am
    oemean[1] = em
    oemean[2] = im
    oemean[3] = ranm % pi2
    oemean[4] = apm % pi2
    oemean[5] = mam % pi2

    # Convert mean anomaly back to true anomaly
    _, ta = kepler1(oemean[5], em)
    oemean[5] = ta

    return oemean
