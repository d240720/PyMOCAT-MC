"""
Fill in atmosphere data.
Python equivalent of fillin_atmosphere.m.
"""
import numpy as np
import os
from scipy.io import loadmat

def fillin_atmosphere(cfg_mc):
    cfg_mc['density_profile'] = 'JB2008'

    possible_paths = [
        os.path.join(os.path.dirname(__file__), '..', 'supporting_data', 'dens_jb2008_032020_022224.mat'),
        os.path.join(os.path.dirname(__file__), '..', '..', 'supporting_data', 'dens_jb2008_032020_022224.mat'),
    ]

    fn = None
    for path in possible_paths:
        if os.path.exists(path):
            fn = os.path.abspath(path)
            break

    if fn is None:
        print('Warning: Could not find JB2008 file, falling back to static atmosphere')
        cfg_mc['density_profile'] = 'static'
        return cfg_mc

    data = loadmat(fn)
    dens_highvar = data['dens_highvar']
    months = dens_highvar['month'][0, 0].flatten()
    years = dens_highvar['year'][0, 0].flatten()
    alts = dens_highvar['alt'][0, 0].flatten()
    dens = dens_highvar['dens'][0, 0]

    def ymd_to_jd(year, month):
        from datetime import datetime
        dt = datetime(int(year), int(month), 1)
        a = (14 - dt.month) // 12
        y = dt.year + 4800 - a
        m = dt.month + 12 * a - 3
        return dt.day + (153*m + 2)//5 + 365*y + y//4 - y//100 + y//400 - 32045

    dens_times = np.array([ymd_to_jd(y, m) for y, m in zip(years, months)], dtype=float)
    dens_times2, alt2 = np.meshgrid(dens_times, alts)

    if 'param' not in cfg_mc:
        cfg_mc['param'] = {}
    cfg_mc['param']['dens_times'] = dens_times2
    cfg_mc['param']['alt'] = alt2
    cfg_mc['param']['dens_value'] = dens

    print(f'JB2008 atmosphere loaded: {len(alts)} altitude levels, {len(dens_times)} time steps')
    return cfg_mc
