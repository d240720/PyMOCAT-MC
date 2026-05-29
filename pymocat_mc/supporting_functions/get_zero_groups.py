"""
Group satellites by object class and identify zero mass/radius entries

Categorizes satellites into three groups:
- g1: Payloads (object class 1)
- g2: Rocket Bodies (object class 5)
- g3: All debris (all other object classes)

For each group, identifies:
- allclass: all entries of this class
- zr: entries with zero radius
- zm: entries with zero mass
- nz: entries with non-zero radius and mass
- nzno: entries with non-zero radius and mass, excluding outliers

Args:
    inmatsat: satellite matrix [N x 24] with columns:
              [a,ecco,inclo,nodeo,argpo,mo,bstar,mass,radius,
               errors,controlled,a_desired,missionlife,constel,
               date_created,launch_date,r,v,objectclass,ID]

Returns:
    g1, g2, g3: group dictionaries with keys 'allclass', 'zr', 'zm', 'nz', 'nzno'
"""

import numpy as np
from scipy import stats


def getZeroGroups(inmatsat):
    """
    Group satellites by object class and identify zero mass/radius entries

    Args:
        inmatsat: satellite matrix [N x 24]

    Returns:
        g1, g2, g3: group dictionaries
    """

    # Column indices
    idx_mass = 7        # 0-indexed (was 8 in MATLAB)
    idx_radius = 8      # 0-indexed (was 9 in MATLAB)
    idx_objectclass = 22 # 0-indexed (was 23 in MATLAB)

    # Initialize groups
    g1 = {'allclass': np.array([], dtype=int)}  # group 1: payloads
    g2 = {'allclass': np.array([], dtype=int)}  # group 2: RBs
    g3 = {'allclass': np.array([], dtype=int)}  # group 3: all debris

    # Process each object class
    for ii in range(1, 13):  # 1 to 12 inclusive
        # boolean mask for this object class
        msinds = inmatsat[:, idx_objectclass] == ii
        class_indices = np.where(msinds)[0]  # convert to indices

        if ii == 1:  # Payloads
            g1['allclass'] = class_indices
            if len(g1['allclass']) > 0:
                # Find zero radius entries
                zero_radius_mask = inmatsat[g1['allclass'], idx_radius] == 0
                g1['zr'] = g1['allclass'][zero_radius_mask]

                # Find zero mass entries
                zero_mass_mask = inmatsat[g1['allclass'], idx_mass] == 0
                g1['zm'] = g1['allclass'][zero_mass_mask]

                # Find non-zero radius and mass entries
                zero_indices = np.union1d(g1['zr'], g1['zm'])
                g1['nz'] = np.setdiff1d(g1['allclass'], zero_indices)

                # Find non-zero, non-outlier entries
                if len(g1['nz']) > 0:
                    radius_values = inmatsat[g1['nz'], idx_radius]
                    mass_values = inmatsat[g1['nz'], idx_mass]

                    # Identify outliers using modified Z-score method
                    # Use MAD-based outlier detection matching MATLAB's isoutlier
                    radius_median = np.median(radius_values)
                    radius_mad = np.median(np.abs(radius_values - radius_median))
                    radius_outliers = np.abs(radius_values - radius_median) > 3 * 1.4826 * radius_mad

                    mass_median = np.median(mass_values)
                    mass_mad = np.median(np.abs(mass_values - mass_median))
                    mass_outliers = np.abs(mass_values - mass_median) > 3 * 1.4826 * mass_mad

                    outlier_mask = radius_outliers | mass_outliers
                    g1['nzno'] = g1['nz'][~outlier_mask]
                else:
                    g1['nzno'] = np.array([], dtype=int)
            else:
                g1['zr'] = np.array([], dtype=int)
                g1['zm'] = np.array([], dtype=int)
                g1['nz'] = np.array([], dtype=int)
                g1['nzno'] = np.array([], dtype=int)

        elif ii == 5:  # Rocket Bodies
            g2['allclass'] = class_indices
            if len(g2['allclass']) > 0:
                # Find zero radius entries
                zero_radius_mask = inmatsat[g2['allclass'], idx_radius] == 0
                g2['zr'] = g2['allclass'][zero_radius_mask]

                # Find zero mass entries
                zero_mass_mask = inmatsat[g2['allclass'], idx_mass] == 0
                g2['zm'] = g2['allclass'][zero_mass_mask]

                # Find non-zero radius and mass entries
                zero_indices = np.union1d(g2['zr'], g2['zm'])
                g2['nz'] = np.setdiff1d(g2['allclass'], zero_indices)

                # Find non-zero, non-outlier entries
                if len(g2['nz']) > 0:
                    radius_values = inmatsat[g2['nz'], idx_radius]
                    mass_values = inmatsat[g2['nz'], idx_mass]

                    # Identify outliers using modified Z-score method
                    # Use MAD-based outlier detection matching MATLAB's isoutlier
                    radius_median = np.median(radius_values)
                    radius_mad = np.median(np.abs(radius_values - radius_median))
                    radius_outliers = np.abs(radius_values - radius_median) > 3 * 1.4826 * radius_mad

                    mass_median = np.median(mass_values)
                    mass_mad = np.median(np.abs(mass_values - mass_median))
                    mass_outliers = np.abs(mass_values - mass_median) > 3 * 1.4826 * mass_mad

                    outlier_mask = radius_outliers | mass_outliers
                    g2['nzno'] = g2['nz'][~outlier_mask]
                else:
                    g2['nzno'] = np.array([], dtype=int)
            else:
                g2['zr'] = np.array([], dtype=int)
                g2['zm'] = np.array([], dtype=int)
                g2['nz'] = np.array([], dtype=int)
                g2['nzno'] = np.array([], dtype=int)

        else:  # All debris (other classes)
            g3['allclass'] = np.union1d(g3['allclass'], class_indices)

    # Process group 3 (all debris)
    if len(g3['allclass']) > 0:
        # Find zero radius entries
        zero_radius_mask = inmatsat[g3['allclass'], idx_radius] == 0
        g3['zr'] = g3['allclass'][zero_radius_mask]

        # Find zero mass entries
        zero_mass_mask = inmatsat[g3['allclass'], idx_mass] == 0
        g3['zm'] = g3['allclass'][zero_mass_mask]

        # Find non-zero radius and mass entries
        zero_indices = np.union1d(g3['zr'], g3['zm'])
        g3['nz'] = np.setdiff1d(g3['allclass'], zero_indices)

        # Find non-zero, non-outlier entries
        if len(g3['nz']) > 0:
            radius_values = inmatsat[g3['nz'], idx_radius]
            mass_values = inmatsat[g3['nz'], idx_mass]

            # Use MAD-based outlier detection matching MATLAB's isoutlier
            radius_median = np.median(radius_values)
            radius_mad = np.median(np.abs(radius_values - radius_median))
            radius_outliers = np.abs(radius_values - radius_median) > 3 * 1.4826 * radius_mad

            mass_median = np.median(mass_values)
            mass_mad = np.median(np.abs(mass_values - mass_median))
            mass_outliers = np.abs(mass_values - mass_median) > 3 * 1.4826 * mass_mad

            outlier_mask = radius_outliers | mass_outliers
            g3['nzno'] = g3['nz'][~outlier_mask]
        else:
            g3['nzno'] = np.array([], dtype=int)
    else:
        g3['zr'] = np.array([], dtype=int)
        g3['zm'] = np.array([], dtype=int)
        g3['nz'] = np.array([], dtype=int)
        g3['nzno'] = np.array([], dtype=int)

    return g1, g2, g3
