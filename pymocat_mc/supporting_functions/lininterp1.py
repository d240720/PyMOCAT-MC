"""
Linear interpolation for 1D data

Fast linear interpolation given set of X and V values, and an x query.
Assumes X values are in strictly increasing order.

Differences from numpy/scipy built-ins:
- Much faster for single point queries
- If coordinate is exactly on the spot, doesn't look at neighbors
- Extends values off the ends instead of giving NaN

Args:
    X: array of x coordinates (strictly increasing)
    V: array of corresponding values
    x: query point

Returns:
    v: interpolated value
"""

import numpy as np
import warnings


def lininterp1(X, V, x):
    """
    Linear interpolation for 1D data

    Args:
        X: array of x coordinates (strictly increasing)
        V: array of corresponding values
        x: query point

    Returns:
        v: interpolated value
    """

    X = np.asarray(X)
    V = np.asarray(V)

    if len(X) != len(V):
        raise ValueError('X and V sizes do not match')

    # Find indices for interpolation
    pindex_mask = x >= X
    index_mask = x <= X

    # Get the last index where x >= X[i]
    pindex_candidates = np.where(pindex_mask)[0]
    pindex = pindex_candidates[-1] if len(pindex_candidates) > 0 else None

    # Get the first index where x <= X[i]
    index_candidates = np.where(index_mask)[0]
    index = index_candidates[0] if len(index_candidates) > 0 else None

    if pindex is None:
        warnings.warn('interpolating before beginning')
        pindex = index
        slope = 0
    elif index is None:
        warnings.warn('interpolating after end')
        index = pindex
        slope = 0
    elif pindex == index:
        slope = 0
    else:
        Xp = X[pindex]
        slope = (x - Xp) / (X[index] - Xp)

    v = V[pindex] * (1 - slope) + V[index] * slope

    return v
