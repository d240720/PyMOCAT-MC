"""
Bin MC population into SSEM altitude shells.
Python equivalent of Fast_MC2SSEM_population.
"""
import numpy as np

def mc2ssem_population(mat_sats, idx, param_ssem, radiusearthkm=6378.137):
    """
    Bin objects into altitude shells and count S, D, N per shell.

    Args:
        mat_sats: satellite matrix
        idx: index dictionary
        param_ssem: dict with 'R02' shell boundaries (km), 'N_shell'
        radiusearthkm: Earth radius in km

    Returns:
        pop: array [N_shell x 3] with columns [S, D, N] per shell
    """
    R02 = np.array(param_ssem['R02'])  # shell boundaries in km
    n_shells = len(R02) - 1

    # Compute perigee altitude for each object
    a_km = mat_sats[:, idx['a']] * radiusearthkm  # semi-major axis in km
    ecc = mat_sats[:, idx['ecco']]
    perigee_alt = a_km * (1 - ecc) - radiusearthkm  # perigee altitude km

    objclass = mat_sats[:, idx['objectclass']].astype(int)
    controlled = mat_sats[:, idx['controlled']].astype(int)

    pop = np.zeros((n_shells, 3), dtype=float)  # [S, D, N] per shell

    for i in range(n_shells):
        shell_mask = (perigee_alt >= R02[i]) & (perigee_alt < R02[i+1])

        obj_shell = objclass[shell_mask]
        ctrl_shell = controlled[shell_mask]

        # S: controlled payloads (class 1, controlled=1)
        pop[i, 0] = np.sum((obj_shell == 1) & (ctrl_shell == 1))
        # D: uncontrolled payloads (class 1, controlled=0)
        pop[i, 1] = np.sum((obj_shell == 1) & (ctrl_shell == 0))
        # N: debris (classes 3,4,6,7,8,...)
        pop[i, 2] = np.sum((obj_shell == 3) | (obj_shell == 4) | (obj_shell >= 6))

    return pop
