"""
Linear interpolation for 2D data

Fast bilinear interpolation given sets of X, Y, and V values, and x, y query points.
Assumes X and Y values are in strictly increasing order.

Differences from numpy/scipy built-ins:
- Much faster for single point queries
- If coordinate is exactly on the spot, doesn't look at neighbors
- Extends values off the ends instead of giving NaN

Args:
    X: array of x coordinates (strictly increasing)
    Y: array of y coordinates (strictly increasing)
    V: 2D array of values, shape (len(X), len(Y))
    x: query x point
    y: query y point

Returns:
    v: interpolated value
"""

import numpy as np
import warnings


def lininterp2(X, Y, V, x, y):
    """
    Bilinear interpolation for 2D data

    Args:
        X: array of x coordinates (strictly increasing)
        Y: array of y coordinates (strictly increasing)
        V: 2D array of values, shape (len(X), len(Y))
        x: query x point
        y: query y point

    Returns:
        v: interpolated value
    """

    X = np.asarray(X)
    Y = np.asarray(Y)
    V = np.asarray(V)

    if (len(X) != V.shape[0]) or (len(Y) != V.shape[1]):
        raise ValueError('[length(X), length(Y)] does not match size(V)')

    # Find x interpolation indices
    pindexx_mask = x >= X
    indexx_mask = x <= X

    pindexx_candidates = np.where(pindexx_mask)[0]
    pindexx = pindexx_candidates[-1] if len(pindexx_candidates) > 0 else None

    indexx_candidates = np.where(indexx_mask)[0]
    indexx = indexx_candidates[0] if len(indexx_candidates) > 0 else None

    if pindexx is None:
        warnings.warn('interpolating x value before beginning')
        pindexx = indexx
        slopex = 0
    elif indexx is None:
        warnings.warn('interpolating x value after end')
        indexx = pindexx
        slopex = 0
    elif pindexx == indexx:
        slopex = 0
    else:
        Xp = X[pindexx]
        slopex = (x - Xp) / (X[indexx] - Xp)

    # Find y interpolation indices
    pindexy_mask = y >= Y
    indexy_mask = y <= Y

    pindexy_candidates = np.where(pindexy_mask)[0]
    pindexy = pindexy_candidates[-1] if len(pindexy_candidates) > 0 else None

    indexy_candidates = np.where(indexy_mask)[0]
    indexy = indexy_candidates[0] if len(indexy_candidates) > 0 else None

    if pindexy is None:
        warnings.warn('interpolating y value before beginning')
        pindexy = indexy
        slopey = 0
    elif indexy is None:
        warnings.warn('interpolating y value after end')
        indexy = pindexy
        slopey = 0
    elif pindexy == indexy:
        slopey = 0
    else:
        Yp = Y[pindexy]
        slopey = (y - Yp) / (Y[indexy] - Yp)

    # Bilinear interpolation
    v = (V[pindexx, pindexy] * (1 - slopex) * (1 - slopey) +
         V[indexx, pindexy] * slopex * (1 - slopey) +
         V[pindexx, indexy] * (1 - slopex) * slopey +
         V[indexx, indexy] * slopex * slopey)

    return v
