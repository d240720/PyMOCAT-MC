"""
Resample existing data to fill in missing mass/radius info from DISCOS

Uses Gaussian Mixture Models to fill in missing mass and radius data for satellites
by sampling from distributions fitted to existing non-zero, non-outlier data.

Args:
    inmatsat: satellite matrix [N x 24] to be modified
    g1, g2, g3: optional group dictionaries with pre-fitted GM models

Returns:
    outmatsat: modified satellite matrix with filled mass/radius
    g1, g2, g3: group dictionaries with fitted GM models

Object classes:
  P,PMRO,Pfrag,Pdeb,RB,RBMRO,RBfrag,RBdeb,Deb,OtherDeb,Unkwn,untracked
  Grouped as: payload {1}, RB {5}, debris {2,3,4,6,7,8,9,10,11}
"""

import numpy as np
from sklearn.mixture import GaussianMixture
import warnings
import sys
import os

# Add supporting functions to path
sys.path.append(os.path.dirname(__file__))

from get_zero_groups import getZeroGroups


class GMDistribution:
    """Simple wrapper to mimic MATLAB's gmdistribution behavior"""

    def __init__(self, means=None, covariances=None):
        """Initialize the class."""
        if means is None or covariances is None:
            self.gm = None
            self.is_empty = True
        else:
            self.gm = GaussianMixture(n_components=1, random_state=42)
            # Fit with dummy data to set parameters
            dummy_data = np.random.multivariate_normal(
                means.flatten(),
                covariances,
                size=10)
            self.gm.fit(dummy_data)
            # Override with actual parameters
            self.gm.means_ = means.reshape(1, -1)
            self.gm.covariances_ = covariances.reshape(1, *covariances.shape)
            self.is_empty = False

    def random(self, n_samples):
        """Generate random samples"""
        if self.is_empty or self.gm is None:
            return np.empty((0, 2))
        return self.gm.sample(n_samples)[0]


def fillMassRadiusResample(inmatsat, *args):
    """
    Resample existing data to fill in missing mass/radius info

    Args:
        inmatsat: satellite matrix [N x 24] to be modified
        *args: optional group dictionaries with pre-fitted GM models

    Returns:
        outmatsat: modified satellite matrix with filled mass/radius
        g1, g2, g3: group dictionaries with fitted GM models
    """

    # MATSATS index DEFINITION (0-indexed for Python)
    idx_a = 0; idx_ecco = 1; idx_inclo = 2
    idx_nodeo = 3; idx_argpo = 4; idx_mo = 5
    idx_bstar = 6; idx_mass = 7; idx_radius = 8
    idx_error = 9; idx_controlled = 10; idx_a_desired = 11
    idx_missionlife = 12; idx_constel = 13; idx_date_created = 14
    idx_launch_date = 15
    idx_r = [16, 17, 18]
    idx_v = [19, 20, 21]
    idx_objectclass = 22; idx_ID = 23

    # Get zero groups
    g1, g2, g3 = getZeroGroups(inmatsat)

    # Check if pre-fitted GM models are provided
    if len(args) > 0 and hasattr(args[0], 'get') and 'gm' in args[0]:
        g1['gm'] = args[0]['gm']  # Use provided GM models
        g2['gm'] = args[1]['gm']
        g3['gm'] = args[2]['gm']
    else:
        # Fit new GM models

        # Group 1 (Payloads)
        X = inmatsat[g1['nzno'], [idx_radius, idx_mass]] if len(
            g1['nzno']) > 0 else np.empty((0,
            2))
        if X.shape[0] > 0:
            gm1 = GaussianMixture(n_components=1, random_state=42)
            gm1.fit(X)
            g1['gm'] = gm1
        else:
            g1['gm'] = GMDistribution()

        # Group 2 (Rocket Bodies)
        X = inmatsat[g2['nzno'], [idx_radius, idx_mass]] if len(
            g2['nzno']) > 0 else np.empty((0,
            2))
        if X.shape[0] > 0:
            gm2 = GaussianMixture(n_components=1, random_state=42)
            gm2.fit(X)
            g2['gm'] = gm2
        else:
            g2['gm'] = GMDistribution()

        # Group 3 (Debris)
        X = inmatsat[g3['nzno'], [idx_radius, idx_mass]] if len(
            g3['nzno']) > 0 else np.empty((0,
            2))
        if X.shape[0] > 0:
            gm3 = GaussianMixture(n_components=1, random_state=42)
            gm3.fit(X)
            g3['gm'] = gm3
        else:
            g3['gm'] = GMDistribution()

    # Fill in empty data from mat_sats via sampling
    outmatsat = inmatsat.copy()

    resampled_counts = [0, 0, 0]

    # Group 1 (Payloads)
    missing_indices = np.union1d(g1['zm'], g1['zr'])
    if len(missing_indices) > 0 and hasattr(g1['gm'], 'sample'):
        n_needed = len(missing_indices)
        # Sample 2x needed, remove negative entries, randomly choose n_needed
        try:
            cursamp = g1['gm'].sample(n_needed * 2)[0]
            # Remove negative entries
            valid_mask = np.all(cursamp > 0, axis=1)
            cursamp = cursamp[valid_mask]

            if len(cursamp) >= n_needed:
                outmatsat[missing_indices, [idx_radius, idx_mass]] = cursamp[:n_needed]
                resampled_counts[0] = n_needed
            else:
                warnings.warn(f"Not enough valid samples for group 1: \
                    {len(cursamp)} < {n_needed}")
        except Exception as e:
            warnings.warn(f"Error sampling for group 1: {e}")

    # Group 2 (Rocket Bodies)
    missing_indices = np.union1d(g2['zm'], g2['zr'])
    if len(missing_indices) > 0 and hasattr(g2['gm'], 'sample'):
        n_needed = len(missing_indices)
        try:
            cursamp = g2['gm'].sample(n_needed * 2)[0]
            # Remove negative entries
            valid_mask = np.all(cursamp > 0, axis=1)
            cursamp = cursamp[valid_mask]

            if len(cursamp) >= n_needed:
                outmatsat[missing_indices, [idx_radius, idx_mass]] = cursamp[:n_needed]
                resampled_counts[1] = n_needed
            else:
                warnings.warn(f"Not enough valid samples for group 2: \
                    {len(cursamp)} < {n_needed}")
        except Exception as e:
            warnings.warn(f"Error sampling for group 2: {e}")

    # Group 3 (Debris)
    missing_indices = np.union1d(g3['zm'], g3['zr'])
    if len(missing_indices) > 0 and hasattr(g3['gm'], 'sample'):
        n_needed = len(missing_indices)
        try:
            cursamp = g3['gm'].sample(n_needed * 2)[0]
            # Remove negative entries
            valid_mask = np.all(cursamp > 0, axis=1)
            cursamp = cursamp[valid_mask]

            if len(cursamp) >= n_needed:
                outmatsat[missing_indices, [idx_radius, idx_mass]] = cursamp[:n_needed]
                resampled_counts[2] = n_needed
            else:
                warnings.warn(f"Not enough valid samples for group 3: \
                    {len(cursamp)} < {n_needed}")
        except Exception as e:
            warnings.warn(f"Error sampling for group 3: {e}")

    print(f'Resampled {resampled_counts[0]}, {resampled_counts[1]}, {resampled_counts[2]} (g1,g2,g3) objects')

    return outmatsat, g1, g2, g3
