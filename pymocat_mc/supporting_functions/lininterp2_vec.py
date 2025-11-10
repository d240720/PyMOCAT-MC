"""
Vectorized linear interpolation for 2D data

Fast bilinear interpolation given sets of X, Y, and V values, and x, y query arrays.
Assumes X and Y values are in strictly increasing order.

Differences from numpy/scipy built-ins:
- Much faster for multiple point queries
- If coordinate is exactly on the spot, doesn't look at neighbors
- Extends values off the ends instead of giving NaN
- Vectorized for processing multiple query points simultaneously

Args:
    X: array of x coordinates (strictly increasing)
    Y: array of y coordinates (strictly increasing)
    V: 2D array of values, shape (len(X), len(Y))
    x: array of query x points
    y: array of query y points

Returns:
    v: array of interpolated values
"""

import numpy as np
import warnings


def lininterp2_vec(X, Y, V, x, y):
    """
    Vectorized bilinear interpolation for 2D data

    Args:
        X: array of x coordinates (strictly increasing)
        Y: array of y coordinates (strictly increasing)
        V: 2D array of values, shape (len(X), len(Y))
        x: array of query x points
        y: array of query y points

    Returns:
        v: array of interpolated values
    """

    X = np.asarray(X).flatten()
    Y = np.asarray(Y).flatten()
    V = np.asarray(V)
    x = np.asarray(x).flatten()
    y = np.asarray(y).flatten()

    if (len(X) != V.shape[0]) or (len(Y) != V.shape[1]):
        raise ValueError('[length(X), length(Y)] does not match size(V)')

    # Find x interpolation indices for all query points
    pindexx = np.zeros(len(x), dtype=int)
    indexx = np.zeros(len(x), dtype=int)
    slopex = np.zeros(len(x))

    for i in range(len(x)):
        # Find last index where x[i] >= X
        pindexx_candidates = np.where(x[i] >= X)[0]
        if len(pindexx_candidates) > 0:
            pindexx[i] = pindexx_candidates[-1]
        else:
            pindexx[i] = -1  # Use -1 to indicate NaN

        # Find first index where x[i] <= X
        indexx_candidates = np.where(x[i] <= X)[0]
        if len(indexx_candidates) > 0:
            indexx[i] = indexx_candidates[0]
        else:
            indexx[i] = -1  # Use -1 to indicate NaN

    # Handle boundary conditions
    isnan_pindexx = (pindexx == -1)
    isnan_indexx = (indexx == -1)

    pindexx[isnan_pindexx] = indexx[isnan_pindexx]
    indexx[isnan_indexx] = pindexx[isnan_indexx]

    # Calculate x slopes
    isnotequal_x = (pindexx != indexx)
    if np.any(isnotequal_x):
        Xp = X[pindexx[isnotequal_x]]
        slopex[isnotequal_x] = ((x[isnotequal_x] - Xp) /
                               (X[indexx[isnotequal_x]] - Xp))

    # Find y interpolation indices for all query points
    pindexy = np.zeros(len(y), dtype=int)
    indexy = np.zeros(len(y), dtype=int)
    slopey = np.zeros(len(y))

    for i in range(len(y)):
        # Find last index where y[i] >= Y
        pindexy_candidates = np.where(y[i] >= Y)[0]
        if len(pindexy_candidates) > 0:
            pindexy[i] = pindexy_candidates[-1]
        else:
            pindexy[i] = -1  # Use -1 to indicate NaN

        # Find first index where y[i] <= Y
        indexy_candidates = np.where(y[i] <= Y)[0]
        if len(indexy_candidates) > 0:
            indexy[i] = indexy_candidates[0]
        else:
            indexy[i] = -1  # Use -1 to indicate NaN

    # Handle boundary conditions
    isnan_pindexy = (pindexy == -1)
    isnan_indexy = (indexy == -1)

    pindexy[isnan_pindexy] = indexy[isnan_pindexy]
    indexy[isnan_indexy] = pindexy[isnan_indexy]

    # Calculate y slopes
    isnotequal_y = (pindexy != indexy)
    if np.any(isnotequal_y):
        Yp = Y[pindexy[isnotequal_y]]
        slopey[isnotequal_y] = ((y[isnotequal_y] - Yp) /
                               (Y[indexy[isnotequal_y]] - Yp))

    # Handle case where x and y arrays have different lengths
    if len(x) != len(y):
        # Broadcast to compatible shapes
        x_len = len(x)
        y_len = len(y)

        if x_len == 1:
            # Single x, multiple y
            pindexx = np.repeat(pindexx, y_len)
            indexx = np.repeat(indexx, y_len)
            slopex = np.repeat(slopex, y_len)
        elif y_len == 1:
            # Multiple x, single y
            pindexy = np.repeat(pindexy, x_len)
            indexy = np.repeat(indexy, x_len)
            slopey = np.repeat(slopey, x_len)
        else:
            raise ValueError("x and y arrays must have same length or one must have length 1")

    # Vectorized bilinear interpolation
    num_rows = V.shape[0]

    # Convert 2D indices to linear indices for V
    idx_00 = pindexx + pindexy * num_rows  # V[pindexx, pindexy]
    idx_10 = indexx + pindexy * num_rows   # V[indexx, pindexy]
    idx_01 = pindexx + indexy * num_rows   # V[pindexx, indexy]
    idx_11 = indexx + indexy * num_rows    # V[indexx, indexy]

    # Bilinear interpolation formula
    v = (V.flat[idx_00] * (1 - slopex) * (1 - slopey) +
         V.flat[idx_10] * slopex * (1 - slopey) +
         V.flat[idx_01] * (1 - slopex) * slopey +
         V.flat[idx_11] * slopex * slopey)

    return v
