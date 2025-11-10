"""
Exponential atmospheric density model
Python equivalent of densityexp_vec function
"""

import numpy as np


def densityexp_vec(altitude_km):
    """
    Exponential atmospheric density model

    Args:
        altitude_km: Altitude above Earth surface in km

    Returns:
        density: Atmospheric density in kg/km^3
    """
    # Convert scalar to array if needed
    if np.isscalar(altitude_km):
        altitude_km = np.array([altitude_km])

    # Initialize density array
    density = np.zeros_like(altitude_km)

    # Exponential atmosphere model based on altitude ranges
    # These parameters approximate the US Standard Atmosphere

    # Below 25 km
    mask_low = altitude_km < 25
    if np.any(mask_low):
        h = altitude_km[mask_low]
        density[mask_low] = 1.225 * np.exp(-h / 8.5)  # kg/m^3

    # 25-30 km
    mask_25_30 = (altitude_km >= 25) & (altitude_km < 30)
    if np.any(mask_25_30):
        h = altitude_km[mask_25_30]
        density[mask_25_30] = 4.008e-2 * np.exp(-(h - 25) / 6.5)

    # 30-40 km
    mask_30_40 = (altitude_km >= 30) & (altitude_km < 40)
    if np.any(mask_30_40):
        h = altitude_km[mask_30_40]
        density[mask_30_40] = 1.841e-2 * np.exp(-(h - 30) / 7.0)

    # 40-50 km
    mask_40_50 = (altitude_km >= 40) & (altitude_km < 50)
    if np.any(mask_40_50):
        h = altitude_km[mask_40_50]
        density[mask_40_50] = 3.996e-3 * np.exp(-(h - 40) / 5.5)

    # 50-60 km
    mask_50_60 = (altitude_km >= 50) & (altitude_km < 60)
    if np.any(mask_50_60):
        h = altitude_km[mask_50_60]
        density[mask_50_60] = 1.027e-3 * np.exp(-(h - 50) / 5.2)

    # 60-70 km
    mask_60_70 = (altitude_km >= 60) & (altitude_km < 70)
    if np.any(mask_60_70):
        h = altitude_km[mask_60_70]
        density[mask_60_70] = 3.108e-4 * np.exp(-(h - 60) / 5.0)

    # 70-80 km
    mask_70_80 = (altitude_km >= 70) & (altitude_km < 80)
    if np.any(mask_70_80):
        h = altitude_km[mask_70_80]
        density[mask_70_80] = 8.283e-5 * np.exp(-(h - 70) / 4.5)

    # Above 80 km - exponential decay
    mask_high = altitude_km >= 80
    if np.any(mask_high):
        h = altitude_km[mask_high]
        # Exponential model for very high altitudes
        density[mask_high] = 1.908e-5 * np.exp(-(h - 80) / 27.0)

    # Convert from kg/m^3 to kg/km^3 (multiply by 1e9)
    density = density * 1e9

    # Ensure minimum density to avoid numerical issues
    density = np.maximum(density, 1e-18)

    return density
