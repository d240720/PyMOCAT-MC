"""
Create new satellite objects from fragmentation information (vectorized)

Create TLE-style satellite objects from fragment data after collisions or explosions

Args:
    ep: epoch (time)
    r_parent: parent position vector [3] in km
    v_parent: parent velocity vector [3] in km/s
    class_parent: parent object class
    fragments: fragment data [N x 8]: [diam, Area, AMR, m, total_dv, dv_X, dv_Y, dv_Z]
    max_frag: maximum number of fragments to process
    mu: gravitational parameter (km^3/s^2)
    req: Earth radius (km)
    maxID: maximum ID used so far

Returns:
    mat_frag: fragment satellite matrix [num_fragments x 24]
              [a,ecco,inclo,nodeo,argpo,mo,bstar,mass,radius,
               errors,controlled,a_desired,missionlife,constel,
               date_created,launch_date,r,v,frag_objectclass,ID_frag]
"""

import numpy as np
import warnings
import sys
import os

# Add supporting functions to path
sys.path.append(os.path.dirname(__file__))

from rv2coe_vec import rv2coe_vec
from filter_objclass_fragments_int import filter_objclass_fragments_int


def func_create_tlesv2_vec(ep, r_parent, v_parent, class_parent, fragments,
                          max_frag, mu, req, maxID):
    """
    Create new satellite objects from fragmentation information

    Args:
        ep: epoch (time)
        r_parent: parent position vector [3] in km
        v_parent: parent velocity vector [3] in km/s
        class_parent: parent object class
        fragments: fragment data [N x 8]: [diam, Area, AMR, m, total_dv, dv_X, dv_Y, dv_Z]
        max_frag: maximum number of fragments to process
        mu: gravitational parameter (km^3/s^2)
        req: Earth radius (km)
        maxID: maximum ID used so far

    Returns:
        mat_frag: fragment satellite matrix [num_fragments x 24]
    """

    # Ensure inputs are numpy arrays
    r_parent = np.array(r_parent)
    v_parent = np.array(v_parent)
    fragments = np.atleast_2d(fragments)

    # Check fragment count vs max_frag
    if fragments.shape[0] > max_frag:
        warnings.warn(f'number of fragments {fragments.shape[0]} exceeds '
                     f'number of max_frag specified {max_frag}')

    n_frag = min(fragments.shape[0], max_frag)

    # Sort by mass to minimize mass conservation issues when limited by n_frag
    # Sort by mass (column 3, 0-indexed), largest first
    mass_sort_idx = np.argsort(fragments[:, 3])[::-1]
    fragments = fragments[mass_sort_idx[:n_frag], :]

    # Calculate fragment velocities (add delta-V to parent velocity)
    v = np.zeros((n_frag, 3))
    v[:, 0] = fragments[:, 5] + v_parent[0]  # dv_X + v0_x
    v[:, 1] = fragments[:, 6] + v_parent[1]  # dv_Y + v0_y
    v[:, 2] = fragments[:, 7] + v_parent[2]  # dv_Z + v0_z

    # All fragments start at parent position
    r = np.tile(r_parent, (n_frag, 1))

    # Convert position and velocity to orbital elements
    p, a, ecc, incl, omega, argp, nu, m, arglat, truelon, lonper = rv2coe_vec(
        r,
        v,
        mu)

    # Keep only elliptical orbits (reject hyperbolic fragments)
    idx_a = np.where(a > 0)[0]
    num_a = len(idx_a)

    if num_a == 0:
        # Return empty array if no valid fragments
        return np.empty((0, 24))

    # Extract valid orbital elements
    a_valid = a[idx_a] / req  # Normalize by Earth radius
    ecco = ecc[idx_a]
    inclo = incl[idx_a]
    nodeo = omega[idx_a]
    argpo = argp[idx_a]
    mo = m[idx_a]

    # Calculate Bstar parameter
    # https://en.wikipedia.org/wiki/BSTAR
    rho_0 = 0.157  # rho_0 in units of kg/(m^2*Re)
    A_M = fragments[idx_a, 2]  # Area to mass ratio in units of m^2/kg
    bstar = (0.5 * 2.2 * rho_0) * A_M  # Bstar in units of 1/re

    # Fragment physical properties
    mass = fragments[idx_a, 3]
    radius = fragments[idx_a, 0] / 2  # diameter to radius

    # Initialize other parameters
    errors = np.zeros(num_a)
    controlled = np.zeros(num_a)
    a_desired = np.full(num_a, np.nan)
    missionlife = np.full(num_a, np.nan)
    constel = np.zeros(num_a)
    date_created = np.full(num_a, ep)
    launch_date = np.full(num_a, np.nan)

    # Assign object class to fragments according to parent particle
    frag_objectclass = np.full(
        num_a,
        filter_objclass_fragments_int(class_parent))

    # Generate IDs for new fragments
    ID_frag = np.linspace(maxID + 1, maxID + num_a, num_a)

    # Assemble fragment matrix
    mat_frag = np.column_stack([
        a_valid, ecco, inclo, nodeo, argpo, mo, bstar, mass, radius,
        errors, controlled, a_desired, missionlife, constel,
        date_created, launch_date, r[idx_a, :], v[idx_a, :],
        frag_objectclass, ID_frag
    ])

    return mat_frag
