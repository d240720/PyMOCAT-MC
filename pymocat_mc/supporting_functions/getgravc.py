"""
Get gravitational constants.

Python equivalent of getgravc.m from Vallado's library.
"""

import numpy as np
from typing import Tuple


def getgravc(whichconst: int) -> Tuple[float, float, float, float, float, float, float, float]:
    """
    Retrieve gravitational constants.

    Args:
        whichconst: Which set of constants to use
                   72 - WGS-72
                   84 - WGS-84

    Returns:
        Tuple of (tumin, mu, radiusearthkm, xke, j2, j3, j4, j3oj2)
    """

    if whichconst == 72:
        # WGS-72 constants
        mu = 398600.8              # km^3/s^2
        radiusearthkm = 6378.135   # km
        xke = 0.0743669161         # er^3/2/min
        tumin = 1.0 / xke          # min/er^3/2
        j2 = 0.001082616
        j3 = -0.00000253881
        j4 = -0.00000165597
        j3oj2 = j3 / j2

    elif whichconst == 84:
        # WGS-84 constants
        mu = 398600.5              # km^3/s^2
        radiusearthkm = 6378.137   # km
        xke = 60.0 / np.sqrt(radiusearthkm**3 / mu)
        tumin = 1.0 / xke          # min/er^3/2
        j2 = 0.00108262998905
        j3 = -0.00000253215306
        j4 = -0.00000161098761
        j3oj2 = j3 / j2

    else:
        raise ValueError(f"Unsupported constant set: {whichconst}")

    return tumin, mu, radiusearthkm, xke, j2, j3, j4, j3oj2
