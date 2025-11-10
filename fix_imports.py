#!/usr/bin/env python3
"""
Script to fix all imports in supporting_functions files to use proper package imports.
"""

import os
import re

def fix_imports_in_file(filepath):
    """Fix imports in a single file."""

    # Map of old import to new import
    import_mappings = {
        r'from ([a-z_]+) import (.+)': r'from . import \1\nfrom .\1 import \2',
        r'^import ([a-z_]+)$': r'from . import \1',
    }

    # Special cases for specific imports
    special_mappings = {
        'from analytic_propagation_vec import analytic_propagation_vec': 'from .analytic_propagation_vec import analytic_propagation_vec',
        'from get_zero_groups import getZeroGroups': 'from .get_zero_groups import getZeroGroups',
        'from cfg_mc_constants import CfgMCConstants': 'from .cfg_mc_constants import CfgMCConstants',
        'from get_idx import get_idx': 'from .get_idx import get_idx',
        'from categorize_obj import categorize_obj': 'from .categorize_obj import categorize_obj',
        'from prop_mit_vec import prop_mit_vec': 'from .prop_mit_vec import prop_mit_vec',
        'from orbcontrol_vec import orbcontrol_vec': 'from .orbcontrol_vec import orbcontrol_vec',
        'from collision_prob_vec import collision_prob_vec': 'from .collision_prob_vec import collision_prob_vec',
        'from frag_col_sbm_vec import frag_col_sbm_vec': 'from .frag_col_sbm_vec import frag_col_sbm_vec',
        'from frag_exp_sbm_vec import frag_exp_sbm_vec': 'from .frag_exp_sbm_vec import frag_exp_sbm_vec',
        'from func_dv import func_dv': 'from .func_dv import func_dv',
        'from fillin_atmosphere import fillin_atmosphere': 'from .fillin_atmosphere import fillin_atmosphere',
        'from fillin_physical_parameters import fillin_physical_parameters': 'from .fillin_physical_parameters import fillin_physical_parameters',
        'from jd2date import jd2date': 'from .jd2date import jd2date',
        'from func_Am import func_Am': 'from .func_Am import func_Am',
        'from osc2mean_vec import osc2mean_vec': 'from .osc2mean_vec import osc2mean_vec',
        'from mean2osc_vec import mean2osc_vec': 'from .mean2osc_vec import mean2osc_vec',
        'from osc2mean_m_vec import osc2mean_m_vec': 'from .osc2mean_m_vec import osc2mean_m_vec',
        'from mean2osc_m_vec import mean2osc_m_vec': 'from .mean2osc_m_vec import mean2osc_m_vec',
        'from cube_vec_v3 import cube_vec_v3': 'from .cube_vec_v3 import cube_vec_v3',
        'from densityexp_vec import densityexp_vec': 'from .densityexp_vec import densityexp_vec',
        'from filter_objclass_fragments_int import filter_objclass_fragments_int': 'from .filter_objclass_fragments_int import filter_objclass_fragments_int',
        'from func_create_tlesv2_vec import func_create_tlesv2_vec': 'from .func_create_tlesv2_vec import func_create_tlesv2_vec',
        'from lininterp1 import lininterp1': 'from .lininterp1 import lininterp1',
        'from lininterp1_vec import lininterp1_vec': 'from .lininterp1_vec import lininterp1_vec',
        'from lininterp2 import lininterp2': 'from .lininterp2 import lininterp2',
        'from lininterp2_vec import lininterp2_vec': 'from .lininterp2_vec import lininterp2_vec',
        'from lininterp2_vec_v2 import lininterp2_vec_v2': 'from .lininterp2_vec_v2 import lininterp2_vec_v2',
        'from kepler1 import kepler1': 'from .kepler1 import kepler1',
        'from kepler1_vec import kepler1_vec': 'from .kepler1_vec import kepler1_vec',
        'from newtonnu_vec import newtonnu_vec': 'from .newtonnu_vec import newtonnu_vec',
        'from oe2rv_vec import oe2rv_vec': 'from .oe2rv_vec import oe2rv_vec',
        'from rv2coe_vec import rv2coe_vec': 'from .rv2coe_vec import rv2coe_vec',
        'from cross_vec import cross_vec': 'from .cross_vec import cross_vec',
        'from angl_vec import angl_vec': 'from .angl_vec import angl_vec',
        'from getgravc import getgravc': 'from .getgravc import getgravc',
        'from mean_osculating_map import mean_osculating_map': 'from .mean_osculating_map import mean_osculating_map',
        'from mean2osc import mean2osc': 'from .mean2osc import mean2osc',
        'from mean2osc_m import mean2osc_m': 'from .mean2osc_m import mean2osc_m',
        'from osc2mean import osc2mean': 'from .osc2mean import osc2mean',
        'from densityexp import densityexp': 'from .densityexp import densityexp',
    }

    with open(filepath, 'r') as f:
        content = f.read()

    # Apply special mappings
    for old_import, new_import in special_mappings.items():
        content = content.replace(old_import, new_import)

    return content

# Get all Python files in supporting_functions
supporting_functions_dir = 'python_implementation/supporting_functions'
python_files = [f for f in os.listdir(supporting_functions_dir)
                if f.endswith('.py') and f != '__init__.py']

print(f"Found {len(python_files)} Python files to process")

# Process each file
for filename in python_files:
    filepath = os.path.join(supporting_functions_dir, filename)
    print(f"Processing {filename}...")

    try:
        new_content = fix_imports_in_file(filepath)
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"  ✓ Fixed imports in {filename}")
    except Exception as e:
        print(f"  ✗ Error processing {filename}: {e}")

print("\nImport fixing complete!")