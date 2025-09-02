"""
Configuration constants for MOCAT-MC.

Python equivalent of cfgMC_constants.m.
"""

import numpy as np
from .getgravc import getgravc


class CfgMCConstants:
    """
    Configuration constants for MOCAT-MC simulation.
    """

    def __init__(self):
        """Initialize the class."""
        # Set conversion units
        self.DAY2MIN = 60 * 24
        self.DAY2SEC = self.DAY2MIN * 60
        self.YEAR2DAY = 365.2425  # days(years(1))
        self.YEAR2MIN = self.YEAR2DAY * self.DAY2MIN
        self.rad = np.pi / 180

        # Global variables
        whichconst = 84
        tumin, mu_const, radiusearthkm, xke, j2, j3, j4, j3oj2 = getgravc(whichconst)

        self.tumin = tumin
        self.mu_const = mu_const
        self.radiusearthkm = radiusearthkm
        self.j2 = j2
        self.omega_earth = 2 * np.pi / self.DAY2SEC
