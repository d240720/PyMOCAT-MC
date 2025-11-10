"""
Collision probability calculation - vectorized.

Python equivalent of collision_prob_vec.m.
"""

import numpy as np


def collision_prob_vec(p1_radius: np.ndarray, p1_v: np.ndarray,
                      p2_radius: np.ndarray, p2_v: np.ndarray,
                      cube_res: float) -> np.ndarray:
    """
    Calculate collision probability for object pairs.

    Args:
        p1_radius: Radius of first objects [n_pairs]
        p1_v: Velocity of first objects [n_pairs x 3]
        p2_radius: Radius of second objects [n_pairs]
        p2_v: Velocity of second objects [n_pairs x 3]
        cube_res: Cube resolution

    Returns:
        pr: Collision probabilities [n_pairs]
    """
    # Cross-sectional collision area
    sigma = (p1_radius + p2_radius)**2 * (np.pi / 1e6)

    # Volume of the cube
    du = cube_res**3

    # Relative velocity magnitude
    v_imp = np.sqrt(np.sum((p1_v - p2_v)**2, axis=1))

    # Collision probability
    pr = v_imp / du * sigma

    return pr
