"""
Matrix indices for satellite data structure.

Python equivalent of getidx.m.

Defines column indices for the satellite matrix structure used throughout MOCAT-MC.
"""

# Direct variable assignments matching MATLAB getidx.m
idx_a = 0           # Semi-major axis (MATLAB: 1, Python: 0-indexed)
idx_ecco = 1        # Eccentricity
idx_inclo = 2       # Inclination
idx_nodeo = 3       # Right ascension of ascending node
idx_argpo = 4       # Argument of perigee
idx_mo = 5          # Mean anomaly
idx_bstar = 6       # B* drag term
idx_mass = 7        # Mass
idx_radius = 8      # Radius
idx_error = 9       # Error flag
idx_controlled = 10 # Controlled flag
idx_a_desired = 11  # Desired semi-major axis
idx_missionlife = 12 # Mission lifetime
idx_constel = 13    # Constellation flag
idx_date_created = 14 # Date created
idx_launch_date = 15  # Launch date
idx_r = [16, 17, 18]  # Position vector [x, y, z]
idx_v = [19, 20, 21]  # Velocity vector [vx, vy, vz]
idx_objectclass = 22  # Object class
idx_ID = 23           # Object ID


def get_idx():
    """
    Get matrix indices for satellite data structure

    Returns:
        Dictionary containing all matrix indices
    """
    return {
        'a': idx_a,
        'ecco': idx_ecco,
        'inclo': idx_inclo,
        'nodeo': idx_nodeo,
        'argpo': idx_argpo,
        'mo': idx_mo,
        'bstar': idx_bstar,
        'mass': idx_mass,
        'radius': idx_radius,
        'error': idx_error,
        'controlled': idx_controlled,
        'a_desired': idx_a_desired,
        'missionlife': idx_missionlife,
        'constel': idx_constel,
        'date_created': idx_date_created,
        'launch_date': idx_launch_date,
        'r': idx_r,
        'v': idx_v,
        'objectclass': idx_objectclass,
        'ID': idx_ID
    }
