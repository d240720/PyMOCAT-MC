"""
Categorize objects into satellites, derelicts, debris, and rocket bodies.

Python equivalent of categorizeObj.m.
"""

import numpy as np
from typing import Tuple


def categorize_obj(
    objint_st: np.ndarray,
    cont_st: np.ndarray) -> Tuple[int, int, int, int]:
    """
    Separate satellites into satellite, derelict, nonusable/debris, rocket body.

    Args:
        objint_st: Array of object class indices
        cont_st: Array of control indices

    Returns:
        Tuple of (nS, nD, nN, nB)
        nS: satellite numbers
        nD: derelict numbers
        nN: debris numbers
        nB: rocket body numbers

    Object classes:
        P(payload), PMRO(debris), Pfrag(debris), Pdeb(debris), RB(rocket body),
        RBMRO(
            debris),
            RBfrag(debris),
            RBdeb(debris),
            Deb(debris),
            OtherDeb(debris),
        Unkwn(debris), untracked(debris)

    Categories:
        S: satellite, object class 1 and control index 1
        D: derelict, object class 1 and control index 0
        N: nonusable/debris, object class 3,4,6,7,8,9..
        B: rocket body, object class 5
    """
    # Convert to numpy arrays if not already
    objint_st = np.asarray(objint_st)
    cont_st = np.asarray(cont_st)

    # Count satellites (controlled payloads)
    nS = np.sum((objint_st == 1) & (cont_st == 1))

    # Count derelicts (uncontrolled payloads)
    nD = np.sum((objint_st == 1) & (cont_st == 0))

    # Count debris (object classes 3, 4, 6, 7, 8, 9, ...)
    nN = np.sum((objint_st == 3) | (objint_st == 4) | (objint_st >= 6))

    # Count rocket bodies (object class 5)
    nB = np.sum(objint_st == 5)

    return int(nS), int(nD), int(nN), int(nB)
