"""
Delta-V calculation for spacecraft fragments.

Reference: SPACE DEBRIS, Model and Risk Analysis
eq(3.42)

Args:
    Am: area-to-mass ratio in m^2/kg (array or scalar)
    s: event type ('exp' for explosion, 'col' for collision)

Returns:
    z: delta-V in m/s (array or scalar)

Reference: Space Debris Model and Risk Analysis
"""

import numpy as np
import warnings


def func_dv(Am, s):
    """
    Calculate delta-V for spacecraft fragments.

    Args:
        Am: area-to-mass ratio in m^2/kg (array or scalar)
        s: event type ('exp' for explosion, 'col' for collision)

    Returns:
        z: delta-V in m/s (array or scalar)
    """

    # Ensure Am is numpy array
    Am = np.atleast_1d(Am)

    # Calculate mu based on event type
    if s == 'exp':
        mu = 0.2 * np.log10(Am) + 1.85  # explosion
    elif s == 'col':
        mu = 0.9 * np.log10(Am) + 2.9   # collision
    else:
        warnings.warn('exp/col not specified; using explosion parameter')
        mu = 0.2 * np.log10(Am) + 1.85  # default to explosion

    # Standard deviation
    sigma = 0.4

    # Generate random component
    N = mu + sigma * np.random.randn(*mu.shape)

    # Calculate delta-V
    z = 10**N  # m/s

    # Return scalar if input was scalar
    if z.shape == (1,):
        return z[0]

    return z
