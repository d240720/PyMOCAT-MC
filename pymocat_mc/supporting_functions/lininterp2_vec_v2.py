"""
Vectorized linear interpolation for 2D data (version 2)

Fast bilinear interpolation using numpy's digitize for improved performance.
Assumes X and Y values are in strictly increasing order.

Differences from matlab built-in:
- Much faster using digitize instead of loops
- If coordinate is exactly on the spot, doesn't look at neighbors
- Extends values off the ends with warnings instead of giving NaN

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


def lininterp2_vec_v2(X, Y, V, x, y):
    """
    Vectorized bilinear interpolation for 2D data (version 2)

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

    # Use digitize for efficient bin finding (equivalent to MATLAB's discretize)
    # digitize returns 1-based indices, subtract 1 for 0-based indexing
    pindexx = np.digitize(x, X) - 1
    indexx = pindexx + 1

    # Handle out-of-bounds for x
    if np.any((pindexx < 0) | (pindexx >= len(X) - 1)):
        raise ValueError(
            f'Input altitude (x=[{np.min(x):.6f}, {np.max(x):.6f}]) '
            f'is outside the range described by X(1)={X[0]:.6f} '
            f'and X(end)={X[-1]:.6f}. '
            'This should not have happened since '
            'analytical_propagator already checks for limits.')

    # Calculate x slopes
    Xp = X[pindexx]
    slopex = (x - Xp) / (X[indexx] - Xp)

    # Use digitize for y coordinates
    pindexy = np.digitize(y, Y) - 1
    indexy = pindexy + 1

    # Handle out-of-bounds for y with warnings and clamping
    out_of_bounds = (pindexy < 0) | (pindexy >= len(Y) - 1)
    if np.any(out_of_bounds):
        warnings.warn(
            f'Input time (y=[{np.min(y):.6f}, {np.max(y):.6f}]) '
            f'is outside the range described by Y(1)={Y[0]:.6f} '
            f'and Y(end)={Y[-1]:.6f}. '
            'Assign Y(1) value if y<Y(1) and Y(end) value if y>Y(end).')

        # Find indices outside range
        find_nan = np.where(out_of_bounds)[0]
        check_nan_above = y[find_nan] > Y[-1]  # y values above range
        idx_above = find_nan[check_nan_above]  # indices above range
        idx_below = find_nan[~check_nan_above]  # indices below range

        # Clamp values above range to last bin
        if len(idx_above) > 0:
            # -2 because 0-indexed and need valid upper bound
            pindexy[idx_above] = len(Y) - 2
            indexy[idx_above] = len(Y) - 1
            y = y.copy()  # Make a copy to avoid modifying input
            y[idx_above] = Y[-1]

        # Clamp values below range to first bin
        if len(idx_below) > 0:
            pindexy[idx_below] = 0
            indexy[idx_below] = 1
            y = y.copy() if 'y' not in locals() else y
            y[idx_below] = Y[0]

    # Calculate y slopes
    Yp = Y[pindexy]
    slopey = (y - Yp) / (Y[indexy] - Yp)

    # Vectorized bilinear interpolation using linear indexing
    num_rows = V.shape[0]

    # Convert 2D indices to linear indices
    idx_00 = pindexx + pindexy * num_rows     # V[pindexx, pindexy]
    idx_10 = indexx + pindexy * num_rows      # V[indexx, pindexy]
    idx_01 = pindexx + indexy * num_rows      # V[pindexx, indexy]
    idx_11 = indexx + indexy * num_rows       # V[indexx, indexy]

    # Bilinear interpolation formula
    v = (V.flat[idx_00] * (1 - slopex) * (1 - slopey) +
         V.flat[idx_10] * slopex * (1 - slopey) +
         V.flat[idx_01] * (1 - slopex) * slopey +
         V.flat[idx_11] * slopex * slopey)

    return v
