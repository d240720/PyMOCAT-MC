"""
Explosion fragmentation using SBM model - vectorized
Python equivalent of frag_exp_SBM_vec.m
"""

import numpy as np
from typing import Dict


def frag_exp_sbm_vec(
    tsince: float,
    p1_in: np.ndarray,
    param: Dict) -> np.ndarray:
    """
    Standard Breakup Model (SBM) for explosion fragmentation

    Args:
        tsince: Time since start [minutes]
        p1_in: Object properties [mass, radius, r, v, objectclass]
        param: Parameters dictionary

    Returns:
        debris: Debris fragments matrix [n_debris x 24]
    """
    # Extract object properties
    p1_mass = p1_in[0]
    p1_radius = p1_in[1]
    p1_r = p1_in[2:5]
    p1_v = p1_in[5:8]
    p1_objectclass = int(p1_in[8])

    # SBM parameters for explosions
    # Number of debris based on parent mass and object type
    if p1_objectclass == 5:  # Rocket body
        # Rocket bodies typically have more energetic breakups
        if p1_mass < 100:
            n_debris = 0  # Too small to fragment significantly
        elif p1_mass < 1000:
            n_debris = int(0.1 * p1_mass)
        else:
            n_debris = int(0.05 * p1_mass + 50)
    else:
        # Other object types
        if p1_mass < 50:
            n_debris = 0
        else:
            n_debris = int(0.05 * p1_mass)

    # Cap maximum number of debris
    n_debris = min(n_debris, 500)

    if n_debris == 0:
        return np.zeros((0, 24))

    # Generate debris fragments
    debris = generate_explosion_debris(
        n_debris, p1_mass, p1_radius, p1_r, p1_v, p1_objectclass, tsince, param
    )

    return debris


def generate_explosion_debris(n_debris: int, parent_mass: float, parent_radius: float,
                            parent_r: np.ndarray, parent_v: np.ndarray, parent_objectclass: int,
                            tsince: float, param: Dict) -> np.ndarray:
    """
    Generate debris fragments from an explosion

    Args:
        n_debris: Number of debris fragments to generate
        parent_mass: Parent object mass [kg]
        parent_radius: Parent object radius [m]
        parent_r: Parent object position [km]
        parent_v: Parent object velocity [km/s]
        parent_objectclass: Parent object class
        tsince: Time since start [minutes]
        param: Parameters dictionary

    Returns:
        debris: Debris fragments matrix [n_debris x 24]
    """
    if n_debris == 0:
        return np.zeros((0, 24))

    # Initialize debris matrix
    debris = np.zeros((n_debris, 24))

    # Generate debris properties using SBM for explosions
    # Size distribution (power law, similar to collisions but different
    # parameters)
    sizes = generate_explosion_size_distribution(n_debris, parent_mass)

    # Mass calculation (assuming spherical debris with density)
    debris_density = 2700  # kg/m^3 (aluminum)
    debris_masses = (4/3) * np.pi * (sizes/2)**3 * debris_density

    # Radius (half of characteristic length)
    debris_radii = sizes / 2

    # Velocity distribution for explosions (more isotropic than collisions)
    delta_v_mag = generate_explosion_velocity_distribution(
        n_debris,
        parent_mass,
        parent_objectclass)

    # Random velocity directions (isotropic distribution)
    theta = np.random.uniform(0, 2*np.pi, n_debris)
    # Uniform distribution on sphere
    phi = np.arccos(np.random.uniform(-1, 1, n_debris))

    delta_v = np.column_stack([
        delta_v_mag * np.sin(phi) * np.cos(theta),
        delta_v_mag * np.sin(phi) * np.sin(theta),
        delta_v_mag * np.cos(phi)
    ])

    # Position (slight random displacement from parent)
    # 1 m standard deviation
    position_noise = np.random.normal(0, 0.001, (n_debris, 3))
    debris_positions = parent_r + position_noise

    # Velocity (parent velocity + delta-V from explosion)
    debris_velocities = parent_v + delta_v

    # Convert positions and velocities to orbital elements
    mu = param['mu']
    req = param['req']

    for i in range(n_debris):
        r_vec = debris_positions[i, :] * 1000  # Convert to meters
        v_vec = debris_velocities[i, :] * 1000  # Convert to m/s

        # Calculate orbital elements (simplified)
        r_mag = np.linalg.norm(r_vec)
        v_mag = np.linalg.norm(v_vec)

        # Semi-major axis
        energy = v_mag**2 / 2 - mu * 1e9 / r_mag
        if energy >= 0:  # Hyperbolic orbit
            a = req + 150  # Set to minimum altitude
        else:
            a = -mu * 1e9 / (2 * energy) / 1000  # Convert back to km

        # Eccentricity (simplified)
        h_vec = np.cross(r_vec, v_vec)
        h_mag = np.linalg.norm(h_vec)
        if energy >= 0:
            e = 0.5  # Moderate eccentricity for hyperbolic case
        else:
            e = np.sqrt(1 + 2 * energy * h_mag**2 / (mu * 1e9)**2)

        # Clamp values to reasonable ranges
        # Normalize to Earth radii
        a = max(req + 150, min(a, req + 2000)) / req
        e = max(0, min(e, 0.99))

        # Fill debris matrix
        debris[i, 0] = a  # Semi-major axis
        debris[i, 1] = e  # Eccentricity
        debris[i, 2] = np.random.uniform(0, np.pi)  # Inclination
        debris[i, 3] = np.random.uniform(0, 2*np.pi)  # RAAN
        debris[i, 4] = np.random.uniform(0, 2*np.pi)  # Argument of perigee
        debris[i, 5] = np.random.uniform(0, 2*np.pi)  # Mean anomaly
        debris[i, 6] = 1e-5  # B* (small value)
        debris[i, 7] = debris_masses[i]  # Mass
        debris[i, 8] = debris_radii[i]  # Radius
        debris[i, 9] = 0  # Error
        debris[i, 10] = 0  # Controlled (debris is uncontrolled)
        debris[i, 11] = a  # Desired semi-major axis
        debris[i, 12] = 0  # Mission lifetime
        debris[i, 13] = 0  # Constellation flag
        debris[i, 14] = tsince  # Date created
        debris[i, 15] = tsince  # Launch date
        debris[i, 16:19] = debris_positions[i, :]  # Position
        debris[i, 19:22] = debris_velocities[i, :]  # Velocity
        debris[i, 22] = 3  # Object class (debris)
        debris[i, 23] = param['maxID'] + i + 1  # ID

    return debris


def generate_explosion_size_distribution(
    n_debris: int,
    parent_mass: float) -> np.ndarray:
    """
    Generate debris size distribution for explosions

    Args:
        n_debris: Number of debris fragments
        parent_mass: Parent object mass [kg]

    Returns:
        sizes: Debris characteristic lengths [m]
    """
    if n_debris == 0:
        return np.array([])

    # SBM power law parameters for explosions
    alpha = -2.7  # Slightly steeper than collisions
    min_size = 0.1  # Minimum size [m]

    # Maximum size depends on parent object size
    max_size = min(2.0, 0.1 * np.sqrt(parent_mass))  # Heuristic scaling

    # Generate power law distribution
    u = np.random.random(n_debris)
    if max_size <= min_size:
        sizes = np.full(n_debris, min_size)
    else:
        sizes = min_size * (1 \
            - u * (1 - (min_size/max_size)**(alpha+1)))**(1/(alpha+1))

    return sizes


def generate_explosion_velocity_distribution(n_debris: int, parent_mass: float,
                                           parent_objectclass: int) -> np.ndarray:
    """
    Generate debris velocity distribution for explosions

    Args:
        n_debris: Number of debris fragments
        parent_mass: Parent object mass [kg]
        parent_objectclass: Parent object class

    Returns:
        delta_v_mag: Delta-V magnitudes [km/s]
    """
    if n_debris == 0:
        return np.array([])

    # Explosion energy depends on object type and mass
    if parent_objectclass == 5:  # Rocket body
        # Rocket bodies have residual propellant
        base_energy = 1.0  # km/s
        mass_scaling = 0.1
    else:
        # Other objects (battery explosions, etc.)
        base_energy = 0.5  # km/s
        mass_scaling = 0.05

    # Mean delta-V scales with energy and inversely with mass
    mean_delta_v = base_energy + mass_scaling / np.sqrt(max(1, parent_mass))

    # Chi-squared distribution (more realistic for explosions)
    df = 3  # Degrees of freedom
    delta_v_mag = mean_delta_v * np.random.chisquare(df, n_debris) / df

    # Cap maximum delta-V
    max_delta_v = 3.0  # km/s
    delta_v_mag = np.minimum(delta_v_mag, max_delta_v)

    return delta_v_mag
