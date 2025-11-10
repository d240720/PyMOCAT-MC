"""
Collision model following NASA EVOLVE 4.0 standard breakup model (2001).

With the revision in ODQN "Proper Implementation of the 1998 NASA Breakup Model" (2011).

Collision fragmentation using the NASA Standard Breakup Model (SBM) for vectorized processing.

Args:
    ep: epoch
    p1_in: object 1 [mass, radius, r[3], v[3], objectclass] (9 elements)
    p2_in: object 2 [mass, radius, r[3], v[3], objectclass] (9 elements)
    param: parameter structure containing max_frag, mu, req, maxID

Returns:
    debris1: fragment matrix for object 1 [N1 x 24]
    debris2: fragment matrix for object 2 [N2 x 24]

References:
    Johnson, N. L., et al. "NASA's New Breakup Model of EVOLVE 4.0" 2001
    Klinkrad, "Space Debris: Models and Risk Analysis" 2006
    MASTER-8-Final-Report

Key algorithm:
1) Determine if catastrophic collision (> 40 J/g)
2) N(d) = 0.1 * m_e^0.75 * d^-1.71
   - if catastrophic: m_e = total mass
   - if non-catastrophic: m_e = m_p*v_i^2
3) Sample bottom-up until "total mass" is reached
4) Create remnant objects for mass conservation
"""

import numpy as np
import warnings
import sys
import os

# Add supporting functions to path
sys.path.append(os.path.dirname(__file__))

func_Am import func_Am
from func_dv import func_dv
func_create_tlesv2_vec import func_create_tlesv2_vec


def frag_col_sbm_vec(ep, p1_in, p2_in, param):
    """
    Collision model following NASA EVOLVE 4.0 standard breakup model

    Args:
        ep: epoch
        p1_in: object 1 [mass, radius, r[3], v[3], objectclass] (9 elements)
        p2_in: object 2 [mass, radius, r[3], v[3], objectclass] (9 elements)
        param: parameter structure containing max_frag, mu, req, maxID

    Returns:
        debris1: fragment matrix for object 1 [N1 x 24]
        debris2: fragment matrix for object 2 [N2 x 24]
    """

    LB = 0.1  # 10 cm lower bound; L_c

    # Convert inputs to numpy arrays
    p1_in = np.asarray(p1_in)
    p2_in = np.asarray(p2_in)

    # Ensure p1_mass > p2_mass, or p1_radius>p2_radius if p1_mass=p2_mass
    if (p1_in[0] < p2_in[0] or
        (p1_in[0] == p2_in[0] and p1_in[1] < p2_in[1])):
        temp1 = p1_in.copy()
        temp2 = p2_in.copy()
        p1_in = temp2
        p2_in = temp1

    p1_mass = p1_in[0]
    p1_radius = p1_in[1]
    p1_r = p1_in[2:5]
    p1_v = p1_in[5:8]
    p1_objclass = p1_in[8]

    p2_mass = p2_in[0]
    p2_radius = p2_in[1]
    p2_r = p2_in[2:5]
    p2_v = p2_in[5:8]
    p2_objclass = p2_in[8]

    # Calculate collision parameters
    dv = np.linalg.norm(p1_v - p2_v)  # km/s
    catastrophRatio = (p2_mass * (dv * 1000)**2) / (2 * p1_mass * 1000)  # J/g

    # Determine collision type
    if catastrophRatio < 40:
        # Non-catastrophic collision
        M = p2_mass * dv**2  # kg*km^2/s^2
        isCatastrophic = 0
    else:
        # Catastrophic collision
        M = p1_mass + p2_mass
        isCatastrophic = 1

    # Calculate number of fragments
    num = int(0.1 * M**(0.75) * LB**(-1.71) -
              0.1 * M**(0.75) * min([1, 2*p1_radius])**(-1.71))

    # Create diameter distribution
    dd_edges = np.logspace(np.log10(LB), np.log10(min([1, 2*p1_radius])), 200)
    log10_dd = np.log10(dd_edges)
    dd_means = 10**(log10_dd[:-1] + np.diff(log10_dd)/2)

    # Generate fragment size distribution
    nddcdf = 0.1 * M**(0.75) * dd_edges**(-1.71)  # Cumulative distribution
    ndd = np.maximum(0, -np.diff(nddcdf))  # PDF count for bins
    floor_ndd = np.floor(ndd).astype(int)
    rand_sampling = np.random.rand(len(ndd))
    add_sampling = (rand_sampling > (1 - (ndd - floor_ndd))).astype(int)

    # Create fragment diameter samples
    d_pdf = np.repeat(dd_means, floor_ndd + add_sampling)
    if len(d_pdf) == 0:
        return np.array([]).reshape(0, 24), np.array([]).reshape(0, 24)

    d = d_pdf[np.random.permutation(len(d_pdf))]

    # Calculate fragment properties
    A = 0.556945 * d**(2.0047077)  # Area from eq 2.72
    Am = func_Am(d, p1_objclass)  # Area-to-mass ratio
    m = A / Am  # Mass

    # Initialize remnant arrays
    m_rem = d_rem = A_rem = Am_rem = np.array([])
    idx_rem1 = idx_rem2 = np.array([], dtype=int)

    # Handle mass distribution based on collision type
    if np.sum(m) < M:
        m_remSum = M - np.sum(m)

        if isCatastrophic:
            # Catastrophic collision - distribute remnant mass randomly
            if m_remSum > 0:
                remDist = np.random.rand(np.random.randint(2, 9))
                m_rem = m_remSum * remDist / np.sum(remDist)

                # Calculate remnant diameters using parent densities
                d_rem = np.zeros(len(m_rem))
                # Randomly assign remnants to parent objects
                rem_assignment = np.random.randint(0, 2, len(m_rem))

                d_rem[rem_assignment == 0] = ((m_rem[rem_assignment == 0] / p1_mass \
                    * p1_radius**3)**(1/3)) * 2
                d_rem[rem_assignment == 1] = ((m_rem[rem_assignment == 1] / p2_mass \
                    * p2_radius**3)**(1/3)) * 2

                # Calculate remnant properties
                Am_rem = func_Am(d_rem, p1_objclass)
                A_rem = m_rem * Am_rem

                # Remove too small remnants
                valid_rem = (d_rem >= LB) | (m_rem >= M/1000)
                m_rem = m_rem[valid_rem]
                d_rem = d_rem[valid_rem]
                A_rem = A_rem[valid_rem]
                Am_rem = Am_rem[valid_rem]
                rem_assignment = rem_assignment[valid_rem]

                idx_rem1 = np.where(rem_assignment == 0)[0]
                idx_rem2 = np.where(rem_assignment == 1)[0]
        else:
            # Non-catastrophic collision - single remnant
            if m_remSum > 0:
                # Assign remnant to larger object by default
                m_rem = np.array([m_remSum])
                d_rem = np.array([(m_remSum / p1_mass \
                    * p1_radius**3)**(1/3) * 2])
                Am_rem = func_Am(d_rem, p1_objclass)
                A_rem = m_rem * Am_rem

                # Remove if too small
                if d_rem[0] >= LB or m_rem[0] >= M/1000:
                    idx_rem1 = np.array([0])
                else:
                    m_rem = d_rem = A_rem = Am_rem = np.array([])

    # Check mass conservation
    total_mass = np.sum(m) + np.sum(m_rem)
    if abs(total_mass - M) > M * 0.05:
        warnings.warn(f'Total sum of debris mass ({total_mass:.1f} kg) differs from '
                     f'"mass" of original objects ({M:.1f} kg)')

    # Calculate delta-V vectors
    all_Am = np.concatenate([Am, Am_rem]) if len(Am_rem) > 0 else Am
    if len(all_Am) == 0:
        return np.array([]).reshape(0, 24), np.array([]).reshape(0, 24)

    dv_vals = func_dv(all_Am, 'col') / 1000  # km/s

    # Generate random unit vectors
    u = np.random.rand(len(dv_vals)) * 2 - 1
    theta = np.random.rand(len(dv_vals)) * 2 * np.pi
    v = np.sqrt(1 - u**2)
    p = np.column_stack([v * np.cos(theta), v * np.sin(theta), u])

    dv_vec = p * dv_vals[:, np.newaxis]

    # Create fragment arrays
    all_d = np.concatenate([d, d_rem]) if len(d_rem) > 0 else d
    all_A = np.concatenate([A, A_rem]) if len(A_rem) > 0 else A
    all_m = np.concatenate([m, m_rem]) if len(m_rem) > 0 else m

    fragments = np.column_stack([
        all_d, all_A, all_Am, all_m, dv_vals,
        dv_vec[:, 0], dv_vec[:, 1], dv_vec[:, 2]
    ])

    # Distribute fragments between satellites
    if len(fragments) == 0:
        return np.array([]).reshape(0, 24), np.array([]).reshape(0, 24)

    # Simple assignment based on size and mass constraints
    n_frags = len(d)
    n_rems = len(m_rem)

    # Assign fragments larger than smaller satellite to larger satellite
    largeidx = np.zeros(len(fragments), dtype=bool)
    smallidx = np.zeros(len(fragments), dtype=bool)

    if n_frags > 0:
        large_frag_mask = (d > p2_radius*2) | (m > p2_mass)
        largeidx[:n_frags] = large_frag_mask

    # Assign remnants based on pre-calculated indices
    if n_rems > 0:
        if len(idx_rem1) > 0:
            largeidx[n_frags + idx_rem1] = True
        if len(idx_rem2) > 0:
            smallidx[n_frags + idx_rem2] = True

    # Assign remaining fragments to fill mass budgets
    assignedidx = largeidx | smallidx
    idx_unassigned = np.where(~assignedidx)[0]

    if len(idx_unassigned) > 0:
        # Shuffle unassigned fragments
        np.random.shuffle(idx_unassigned)

        # Calculate current mass assignments
        mass_large = np.sum(fragments[largeidx, 3]) if np.any(largeidx) else 0
        mass_small = np.sum(fragments[smallidx, 3]) if np.any(smallidx) else 0

        # Assign fragments to fill larger satellite first
        for idx in idx_unassigned:
            if mass_large + fragments[idx, 3] <= p1_mass:
                largeidx[idx] = True
                mass_large += fragments[idx, 3]
            else:
                smallidx[idx] = True
                mass_small += fragments[idx, 3]

    # Create final fragment arrays
    fragments1_idx = np.where(largeidx)[0]
    fragments2_idx = np.where(smallidx)[0]

    fragments1 = fragments[fragments1_idx] if len(
        fragments1_idx) > 0 else np.array([]).reshape(0,
        8)
    fragments2 = fragments[fragments2_idx] if len(
        fragments2_idx) > 0 else np.array([]).reshape(0,
        8)

    # Remove fragments smaller than LB
    if len(fragments1) > 0:
        fragments1 = fragments1[fragments1[:, 0] >= LB]
    if len(fragments2) > 0:
        fragments2 = fragments2[fragments2[:, 0] >= LB]

    # Create debris objects using func_create_tlesv2_vec
    try:
        if len(fragments1) > 0:
            debris1 = func_create_tlesv2_vec(ep, p1_r, p1_v, p1_objclass,
                                           fragments1, param['max_frag'],
                                           param['mu'], param['req'], param['maxID'])
            param['maxID'] = param['maxID'] + len(debris1)
        else:
            debris1 = np.array([]).reshape(0, 24)

        if len(fragments2) > 0:
            debris2 = func_create_tlesv2_vec(ep, p2_r, p2_v, p2_objclass,
                                           fragments2, param['max_frag'],
                                           param['mu'], param['req'], param['maxID'])
        else:
            debris2 = np.array([]).reshape(0, 24)

    except Exception as e:
        warnings.warn(f'Error in func_create_tlesv2_vec: {e}')
        return np.array([]).reshape(0, 24), np.array([]).reshape(0, 24)

    return debris1, debris2
