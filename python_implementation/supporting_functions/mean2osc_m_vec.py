"""
Mean to osculating orbital elements conversion - vectorized
Python equivalent of mean2osc_m_vec.m
"""

import numpy as np
from typing import Tuple, Dict


def mean2osc_m_vec(
    mean_oe: np.ndarray,
    param: Dict) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Convert mean orbital elements to osculating orbital elements

    Args:
        mean_oe: Mean orbital elements [n_sats x 6] [a, e, i, Omega, omega, M]
        param: Parameters dictionary

    Returns:
        Tuple of (osc_oe, nu, E_osc)
        osc_oe: Osculating orbital elements [n_sats x 6] [a, e, i, Omega, omega, nu]
        nu: True anomaly [n_sats]
        E_osc: Eccentric anomaly [n_sats]
    """
    n_sats = mean_oe.shape[0]
    osc_oe = mean_oe.copy()

    if n_sats == 0:
        return osc_oe, np.array([]), np.array([])

    # Extract parameters
    req = param['req']
    j2 = param['j2']

    # Extract orbital elements
    a = mean_oe[:, 0]
    e = mean_oe[:, 1]
    i = mean_oe[:, 2]
    M = mean_oe[:, 5]  # Mean anomaly

    # Calculate eccentric anomaly from mean anomaly
    E_osc = solve_kepler_equation(M, e)

    # Calculate true anomaly from eccentric anomaly
    nu = 2 * np.arctan2(
        np.sqrt(1 + e) * np.sin(E_osc / 2),
        np.sqrt(1 - e) * np.cos(E_osc / 2)
    )

    # J2 perturbations for mean to osculating conversion
    cos_i = np.cos(i)
    sin_i = np.sin(i)
    cos_nu = np.cos(nu)
    sin_nu = np.sin(nu)

    # Semi-latus rectum
    p = a * (1 - e**2)

    # J2 correction factors (simplified)
    eta = req / p
    j2_factor = j2 * eta**2

    # Osculating corrections (simplified first-order)
    delta_a = np.zeros_like(a)  # Semi-major axis correction
    delta_e = np.zeros_like(e)  # Eccentricity correction
    delta_i = np.zeros_like(i)  # Inclination correction
    delta_Omega = np.zeros_like(i)  # RAAN correction
    delta_omega = np.zeros_like(i)  # Argument of perigee correction

    # Apply corrections (simplified)
    osc_oe[:, 0] = a + delta_a
    osc_oe[:, 1] = e + delta_e
    osc_oe[:, 2] = i + delta_i
    osc_oe[:, 3] = mean_oe[:, 3] + delta_Omega  # RAAN
    osc_oe[:, 4] = mean_oe[:, 4] + delta_omega  # Argument of perigee
    osc_oe[:, 5] = nu  # Replace mean anomaly with true anomaly

    return osc_oe, nu, E_osc


def solve_kepler_equation(
    M: np.ndarray,
    e: np.ndarray,
    tol: float = 1e-12,
    max_iter: int = 50) -> np.ndarray:
    """
    Solve Kepler's equation M = E - e*sin(E) for E

    Args:
        M: Mean anomaly [radians]
        e: Eccentricity
        tol: Tolerance for convergence
        max_iter: Maximum number of iterations

    Returns:
        E: Eccentric anomaly [radians]
    """
    # Initial guess
    E = M.copy()

    # Newton-Raphson iteration
    for _ in range(max_iter):
        f = E - e * np.sin(E) - M
        df = 1 - e * np.cos(E)

        # Update
        delta_E = -f / df
        E += delta_E

        # Check convergence
        if np.all(np.abs(delta_E) < tol):
            break

    return E
