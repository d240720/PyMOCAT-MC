"""
Cube method for collision detection - vectorized version 3.

Python equivalent of cube_vec_v3.m.
"""

import numpy as np
from typing import List
from itertools import combinations


def cube_vec_v3(
    X: np.ndarray,
    cube_res: float,
    collision_alt_limit: float) -> List[np.ndarray]:
    """
    Execute cube method for collision detection.

    Only consider RSO below collision_alt_limit for collision.

    Args:
        X: Position matrix [n_objects x 3]
        cube_res: Cube resolution for collision detection
        collision_alt_limit: Altitude limit for collision consideration

    Returns:
        List of arrays containing pairs of object indices that could collide
    """
    # Only consider RSO below collision_alt_limit for collision
    idx_invalid = np.any(np.abs(X.T) > collision_alt_limit, axis=0)
    X = X.copy()
    X[idx_invalid, :] = np.nan

    # Discretize positions
    X_dis = np.floor(X[:, :3] / cube_res)

    # Shift origin such that X_dis is always positive
    shift_lim = int(np.nanmax(np.abs(X_dis))) + 10
    X_dis = X_dis + shift_lim
    shift_lim2 = 2 * shift_lim

    # Create unique index for each cube
    X_idx = (X_dis[:, 0] * (shift_lim2 * shift_lim2) +
             X_dis[:, 1] * shift_lim2 +
             X_dis[:, 2])

    # Find duplicates (objects in same cube)
    unique_vals, unique_idx = np.unique(X_idx, return_inverse=True)

    # Find which values appear more than once
    counts = np.bincount(unique_idx)
    duplicate_mask = counts > 1

    if not np.any(duplicate_mask):
        return []

    # Get indices of objects in cubes with multiple objects
    duplicate_cube_indices = np.where(duplicate_mask)[0]

    res = []
    for cube_idx in duplicate_cube_indices:
        # Find all objects in this cube
        objects_in_cube = np.where(unique_idx == cube_idx)[0]

        # Generate all pairs (combinations of 2)
        if len(objects_in_cube) >= 2:
            pairs = np.array(list(combinations(objects_in_cube, 2)))
            res.append(pairs)

    return res
