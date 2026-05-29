"""
Fill in physical parameters
Python equivalent of fillin_physical_parameters.m
"""

def fillin_physical_parameters(cfg_mc):
    cfg_mc['fillMassRadius'] = 2    # don't resample for now
    cfg_mc['initpopMultiplier'] = 1
    cfg_mc['physicalBstar'] = True
    return cfg_mc