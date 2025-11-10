"""
Vectorized cross product function

This function returns the cross product of the input vectors, observing
the input ordering. Since the code does not have the error checking in
the NumPy function of the same name it is much faster for large arrays.

Args:
    a: First vector array (N x 3)
    b: Second vector array (N x 3)

Returns:
    c: Cross product array (N x 3)
"""

import numpy as np


def cross_vec(a, b):
    """
    Compute vectorized cross product of two arrays of vectors

    Args:
        a: array of vectors (N x 3)
        b: array of vectors (N x 3)

    Returns:
        c: cross product vectors (N x 3)
    """
    # Ensure inputs are numpy arrays
    a = np.atleast_2d(a)
    b = np.atleast_2d(b)

    # Compute cross product components
    c = np.column_stack([
        a[:, 1] * b[:, 2] - b[:, 1] * a[:, 2],  # x component
        a[:, 2] * b[:, 0] - b[:, 2] * a[:, 0],  # y component
        a[:, 0] * b[:, 1] - b[:, 0] * a[:, 1]   # z component
    ])

    return c
