"""
Map between mean and osculating orbital elements

Maps from mean to osculating elements if option>0
and osculating to mean if option<0 using analytical transformations.

Args:
    x: orbital elements [6x1]
        x[0] = semimajor axis (kilometers)
        x[1] = orbital eccentricity (0 <= e < 1)
        x[2] = orbital inclination (radians, 0 <= i <= pi)
        x[3] = right ascension of ascending node (radians, 0 <= raan <= 2*pi)
        x[4] = argument of perigee (radians, 0 <= argp <= 2*pi)
        x[5] = mean anomaly (radians, 0 <= M <= 2*pi)
    option: transformation direction (
        >0: mean to osculating,
        <0: osculating to mean)
    param: parameter structure containing mu, req, j2

Returns:
    y: transformed orbital elements [6x1]

Reference:
Appendix G from Junkins, John L., and Hanspeter Schaub.
Analytical mechanics of space systems. AIAA, 2009.
"""

import numpy as np


def mean_osculating_map(x, option, param):
    """
    Map between mean and osculating orbital elements

    Args:
        x: orbital elements [6x1]
        option: transformation direction (
            >0: mean to osculating,
            <0: osculating to mean)
        param: parameter structure

    Returns:
        y: transformed orbital elements [6x1]
    """

    x = np.asarray(x).flatten()

    a = x[0]
    e = x[1]
    inc = x[2]
    bigO = x[3]
    omega = x[4]
    Mo = x[5]

    mu = param['mu']
    re = param['req']
    J2 = param['j2']

    if option > 0:
        # Maps mean orbit elements to osculating orbit elements
        gam2 = (J2 / 2) * (re / a)**2
    else:
        # Maps osculating orbit elements to mean orbit elements
        gam2 = -(J2 / 2) * (re / a)**2

    # Solve Kepler's equation
    if (Mo > -np.pi and Mo < 0) or Mo > np.pi:
        E = Mo - e
    else:
        E = Mo + e

    Epw = Mo
    for k in range(1000):
        DeltaEpw = -(Mo - Epw + e * np.sin(Epw)) / (-1 + e * np.cos(Epw))
        Epw = Epw + DeltaEpw
        if abs(DeltaEpw) < 1e-14:
            break
    E = Epw

    eta = np.sqrt(1 - e**2)
    gam2_p = gam2 / eta**4

    theta = 2 * np.arctan(np.sqrt((1 + e) / (1 - e)) * np.tan(E / 2))

    ratio = (1 + e * np.cos(theta)) / (eta**2)

    # Calculate perturbations
    a_p = (a \
        + a * gam2 * ((3 * np.cos(inc)**2 - 1) * (ratio**3 - (1 / eta**3)) +
                          3 * (1 - np.cos(inc)**2) * ratio**3 * np.cos(2 * omega + 2 * theta)))

    Delta_e1 = ((gam2_p / 8) * e * eta**2 *
                (1 - 11 * np.cos(inc)**2 - 40 * (np.cos(inc)**4 / (1 - 5 * np.cos(inc)**2))) *
                np.cos(2 * omega))

    term1 = ((3 * np.cos(inc)**2 - 1) / (eta**6)) * (
        e * eta + (e / (1 + eta)) + 3 * np.cos(theta) +
        3 * e * np.cos(theta)**2 + e**2 * np.cos(theta)**3
    )
    term2 = (3 * (1 - np.cos(inc)**2) / (eta**6)) * (
        e + 3 * np.cos(theta) + 3 * e * np.cos(theta)**2 +
        e**2 * np.cos(theta)**3
    ) * np.cos(2 * omega + 2 * theta)
    term3 = gam2_p * (1 - np.cos(theta)**2) * (3 * np.cos(2 * omega \
        + theta) + np.cos(2 * omega + 3 * theta))

    Delta_e = Delta_e1 + (eta**2 / 2) * (gam2 * (term1 + term2) - term3)

    Delta_inc = (-(e * Delta_e1) / (eta**2 * np.tan(inc)) +
                 (gam2_p / 2) * np.cos(inc) * np.sqrt(1 - np.cos(inc)**2) *
                 (3 * np.cos(2 * omega + 2 * theta) +
                  3 * e * np.cos(2 * omega + theta) +
                  e * np.cos(2 * omega + 3 * theta)))

    angle_total = Mo + omega + bigO
    angle_total_p = (
        angle_total +
        (gam2_p / 8) * eta**3 * (
            1 - 11 * np.cos(inc)**2 -
            40 * (np.cos(inc)**4 / (1 - 5 * np.cos(inc)**2))
        ) +
        -(gam2_p / 16) * (
            2 + e**2 - 11 * (2 + 3 * e**2) * np.cos(inc)**2 -
            40 * (2 + 5 * e**2) * (np.cos(inc)**4 / (1 - 5 * np.cos(inc)**2)) -
            400 * e**2 * (np.cos(inc)**6 / (1 - 5 * np.cos(inc)**2)**2)
        ) +
                    (gam2_p / 4) * (-6 * (1 - 5 * np.cos(inc)**2) * \
                        (theta - Mo - e * np.sin(theta)) +
                                   (3 - 5 * np.cos(inc)**2) * (3 * np.sin(2 * omega + 2 * theta) +
                                                              3 * e * np.sin(2 * omega + theta) +
                                                              e * \
                                                                  np.sin(2 * omega + 3 * theta))) +
                    -(gam2_p / 8) * e**2 * np.cos(inc) * (11 + 80 * \
                        (np.cos(inc)**2 / (1 - 5 * np.cos(inc)**2)) +
                                                         200 * \
                                                             (np.cos(inc)**4 / (1 - 5 * np.cos(inc)**2)**2)) +
                    -(gam2_p / 2) * np.cos(inc) * (6 * (theta - Mo + e * np.sin(theta)) -
                                                  3 * np.sin(2 * omega + 2 * theta) -
                                                  3 * e * np.sin(2 * omega + theta) -
                                                  e * np.sin(2 * omega + 3 * theta)))

    eDelta_M = (
        (gam2_p / 8) * e * eta**3 * (
            1 - 11 * np.cos(inc)**2 - 40 * (np.cos(inc)**4 / (1 - 5 * np.cos(inc)**2))
        ) +
                -(gam2_p / 4) * eta**3 * (2 * (3 * np.cos(inc)**2 - \
                    1) * (ratio**2 * eta**2 + ratio + 1) * np.sin(theta) +
                                         3 * (1 - np.cos(inc)**2) * \
                                             ((-ratio**2 * eta**2 - ratio + 1) * np.sin(2 * omega + theta) +
                                                                    \
                                                                        (ratio**2 * eta**2 + ratio + 1/3) * np.sin(2 * omega + 3 * theta))))

    Delta_bigO = (-(gam2_p / 8) * e**2 * np.cos(inc) * (11 \
        + 80 * (np.cos(inc)**2) / (1 - 5 * np.cos(inc)**2) +
                                                        200 * \
                                                            (np.cos(inc)**4) / (1 - 5 * np.cos(inc)**2)**2) +
                  -(gam2_p / 2) * np.cos(inc) * (6 * (theta - Mo + e * np.sin(theta)) -
                                                 3 * np.sin(2 * omega + 2 * theta) -
                                                 3 * e * np.sin(2 * omega + theta) -
                                                 e * np.sin(2 * omega + 3 * theta)))

    d1 = (e + Delta_e) * np.sin(Mo) + eDelta_M * np.cos(Mo)
    d2 = (e + Delta_e) * np.cos(Mo) - eDelta_M * np.sin(Mo)

    Mo_p = np.arctan2(d1, d2)

    e_p = np.sqrt(d1**2 + d2**2)

    d3 = ((np.sin(inc / 2) \
        + np.cos(inc / 2) * (Delta_inc / 2)) * np.sin(bigO) +
          np.sin(inc / 2) * Delta_bigO * np.cos(bigO))
    d4 = ((np.sin(inc / 2) \
        + np.cos(inc / 2) * (Delta_inc / 2)) * np.cos(bigO) -
          np.sin(inc / 2) * Delta_bigO * np.sin(bigO))

    bigO_p = np.arctan2(d3, d4)

    inc_p = 2 * np.arcsin(np.sqrt(d3**2 + d4**2))

    omega_p = angle_total_p - Mo_p - bigO_p

    y = np.array([a_p, e_p, inc_p, bigO_p, omega_p, Mo_p])

    return y
