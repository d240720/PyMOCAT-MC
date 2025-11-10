"""
Exponential atmospheric density model

Simple exponential atmospheric density model for Earth.
Based on standard atmospheric models.

Args:
    h: altitude above Earth surface in km

Returns:
    rho: atmospheric density in kg/m^3
"""

import numpy as np


def densityexp(h):
    """
    Exponential atmospheric density model

    Args:
        h: altitude above Earth surface in km

    Returns:
        rho: atmospheric density in kg/m^3
    """

    # Simple exponential atmosphere model
    # Based on standard atmospheric parameters

    # Reference density at sea level (kg/m^3)
    rho_0 = 1.225

    # Scale height (km) - varies with altitude but use average
    H = 8.5

    # Exponential decay
    rho = rho_0 * np.exp(-h / H)

    return rho
