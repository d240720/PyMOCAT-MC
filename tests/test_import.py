#!/usr/bin/env python3
"""Test basic imports and setup"""

print("Testing Python MOCAT-MC imports...")

try:
    import numpy as np
    print("OK NumPy imported successfully")
    
    import scipy
    print("OK SciPy imported successfully")
    
    import sys
    import os
    # Add python_implementation directory to path for mocat_mc import
    sys.path.insert(
        0,
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
        '..',
        'python_implementation'))
    
    from mocat_mc import MOCATMC
    print("OK MOCATMC imported successfully")
    
    # Try to initialize
    mocat = MOCATMC()
    print("OK MOCATMC initialized")
    
    # Check if we can load the initial conditions
    import scipy.io as sio
    from pathlib import Path
    
    # Find the 2020.mat file using multiple possible paths
    script_dir = Path(__file__).parent
    possible_paths = [
        script_dir / '..' / 'supporting_data' / 'TLEhistoric' / '2020.mat',
        script_dir / '..' / '..' / 'python_implementation' / \
            'supporting_data' / 'TLEhistoric' / '2020.mat',
        Path('python_implementation') / 'supporting_data' / 'TLEhistoric' / '2020.mat',
        Path('supporting_data') / 'TLEhistoric' / '2020.mat'
    ]
    
    data_found = False
    for ic_path in possible_paths:
        if ic_path.exists():
            try:
                data = sio.loadmat(str(ic_path))
                if 'mat_sats' in data:
                    print(f"OK Found 2020.mat with {data['mat_sats'].shape[0]} satellites at {ic_path}")
                    data_found = True
                    break
                else:
                    print(f"WARNING Found {ic_path} but no mat_sats data")
            except Exception as e:
                print(f"WARNING Found {ic_path} but couldn't load: {e}")
    
    if not data_found:
        print("WARNING Could not find 2020.mat file - tests will use synthetic data")
    
    print("\nPython setup appears to be working!")
    
except Exception as e:
    print(f"ERROR Error: {e}")
    import traceback
    traceback.print_exc()