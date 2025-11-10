"""
Area-to-mass ratio calculation for spacecraft fragments.

NASA's new breakup model of evolve 4.0
Author: N.L.Johnson, P.H.Krisko, J.-C. Liou, P.D.Anz-Meador
Eq(6) pg 1381
Distribution function for spacecraft fragments with Lc(=d)>11cm

Args:
    d: characteristic length in meters (array)
    obj_class: object class identifier (scalar or array)

Returns:
    out: area-to-mass ratio in m^2/kg (array)

Reference: NASA breakup model evolve 4.0
"""

import numpy as np


def func_Am(d, obj_class):
    """
    Calculate area-to-mass ratio for spacecraft fragments.

    Args:
        d: characteristic length in meters (array or scalar)
        obj_class: object class identifier (scalar or array)

    Returns:
        out: area-to-mass ratio in m^2/kg (array)
    """

    # Ensure inputs are numpy arrays
    d = np.atleast_1d(d)

    num_obj = len(d)
    logds = np.log10(d)  # d in meters
    amsms = np.full((num_obj, 5), np.nan)  # store alpha, mu1, sig1, mu2, sig2

    # Check if rocket body related (class > 4.5 and < 8.5)
    is_rocket = (obj_class > 4.5) & (obj_class < 8.5)

    for ind in range(num_obj):
        logd = logds[ind]

        if np.isscalar(obj_class):
            rocket_body = is_rocket
        else:
            rocket_body = is_rocket[ind] if hasattr(
                is_rocket,
                '__len__') else is_rocket

        if rocket_body:  # Rocket-body related
            # alpha
            if logd <= -1.4:
                alpha = 1
            elif (-1.4 < logd) and (logd < 0):
                alpha = 1 - 0.3571 * (logd + 1.4)
            else:  # >= 0
                alpha = 0.5

            # mu1
            if logd <= -0.5:
                mu1 = -0.45
            elif (-0.5 < logd) and (logd < 0):
                mu1 = -0.45 - 0.9 * (logd + 0.5)
            else:  # >= 0
                mu1 = -0.9

            # sigma1
            sigma1 = 0.55

            # mu2
            mu2 = -0.9

            # sigma2
            if logd <= -1.0:
                sigma2 = 0.28
            elif (-1 < logd) and (logd < 0.1):
                sigma2 = 0.28 - 0.1636 * (logd + 1)
            else:  # >= 0.1
                sigma2 = 0.1

        else:  # Not rocket body
            # alpha
            if logd <= -1.95:
                alpha = 0
            elif (-1.95 < logd) and (logd < 0.55):
                alpha = 0.3 + 0.4 * (logd + 1.2)
            else:  # >= 0.55
                alpha = 1

            # mu1
            if logd <= -1.1:
                mu1 = -0.6
            elif (-1.1 < logd) and (logd < 0):
                mu1 = -0.6 - 0.318 * (logd + 1.1)
            else:  # >= 0
                mu1 = -0.95

            # sigma1
            if logd <= -1.3:
                sigma1 = 0.1
            elif (-1.3 < logd) and (logd < -0.3):
                sigma1 = 0.1 + 0.2 * (logd + 1.3)
            else:  # >= -0.3
                sigma1 = 0.3

            # mu2
            if logd <= -0.7:
                mu2 = -1.2
            elif (-0.7 < logd) and (logd < -0.1):
                mu2 = -1.2 - 1.333 * (logd + 0.7)
            else:  # >= -0.1
                mu2 = -2.0

            # sigma2
            if logd <= -0.5:
                sigma2 = 0.5
            elif (-0.5 < logd) and (logd < -0.3):
                sigma2 = 0.5 - (logd + 0.5)
            else:  # >= -0.3
                sigma2 = 0.3

        amsms[ind, :] = [alpha, mu1, sigma1, mu2, sigma2]

    # Generate random components
    N1 = amsms[:, 1] + amsms[:, 2] * np.random.randn(num_obj)
    N2 = amsms[:, 3] + amsms[:, 4] * np.random.randn(num_obj)

    # Calculate output (eq 3.40)
    out = 10**(amsms[:, 0] * N1 + (1 - amsms[:, 0]) * N2)

    # Return scalar if input was scalar
    if out.shape == (1,):
        return out[0]

    return out
