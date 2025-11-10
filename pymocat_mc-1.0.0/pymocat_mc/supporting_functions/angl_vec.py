"""
Angle between two vectors (vectorized)

This function calculates the angle between corresponding vectors in two arrays.

Args:
    vec1: First vector array (N x 3)
    vec2: Second vector array (N x 3)

Returns:
    angles: Array of angles in radians (N,)
"""

import numpy as np


def angl_vec(vec1, vec2):
    """
    Calculate angle between two vectors (vectorized)

    Args:
        vec1: array of vectors (N x 3)
        vec2: array of vectors (N x 3)

    Returns:
        angles: array of angles in radians (N,)
    """
    # Ensure inputs are numpy arrays
    vec1 = np.atleast_2d(vec1)
    vec2 = np.atleast_2d(vec2)

    # Calculate magnitudes
    mag1 = np.sqrt(np.sum(vec1**2, axis=1))
    mag2 = np.sqrt(np.sum(vec2**2, axis=1))

    # Calculate dot product
    dot_product = np.sum(vec1 * vec2, axis=1)

    # Calculate cosine of angle
    cos_angle = dot_product / (mag1 * mag2)

    # Clamp to [-1, 1] to avoid numerical errors
    cos_angle = np.clip(cos_angle, -1.0, 1.0)

    # Calculate angle
    angles = np.arccos(cos_angle)

    return angles
