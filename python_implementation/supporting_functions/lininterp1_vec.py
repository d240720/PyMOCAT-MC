"""
Linear interpolation functions
Python equivalent of lininterp1_vec and lininterp2_vec_v2
"""

import numpy as np


def lininterp1_vec(x_data, y_data, x_query):
    """
    1D linear interpolation vectorized

    Args:
        x_data: Data points x coordinates
        y_data: Data points y coordinates
        x_query: Query point x coordinate

    Returns:
        Interpolated y value
    """
    return np.interp(x_query, x_data, y_data)


def lininterp2_vec_v2(x_data, y_data, z_data, x_query, y_query):
    """
    2D linear interpolation vectorized

    Args:
        x_data: 1D array of x coordinates
        y_data: 1D array of y coordinates
        z_data: 2D array of z values [len(x_data) x len(y_data)]
        x_query: Query x coordinates (can be array)
        y_query: Query y coordinate (scalar)

    Returns:
        Interpolated z values
    """
    from scipy.interpolate import RegularGridInterpolator

    # Create interpolator
    interp = RegularGridInterpolator((x_data, y_data), z_data,
                                   bounds_error=False, fill_value=None)

    # Convert scalar x_query to array if needed
    if np.isscalar(x_query):
        x_query = np.array([x_query])

    # Create query points
    if np.isscalar(y_query):
        query_points = np.column_stack(
            [x_query,
            np.full_like(x_query,
            y_query)])
    else:
        query_points = np.column_stack([x_query, y_query])

    # Interpolate
    result = interp(query_points)

    return result
