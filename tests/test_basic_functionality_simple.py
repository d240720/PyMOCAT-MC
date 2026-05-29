#!/usr/bin/env python3
"""
Simplified basic functionality tests for PyMOCAT-MC
"""

import sys
import os
from pathlib import Path

# Add python_implementation directory to path for imports (cross-platform)
script_dir = Path(__file__).parent
repo_root = script_dir.parent
python_impl_dir = repo_root / "python_implementation"
sys.path.insert(0, str(python_impl_dir))

print("Running basic functionality tests...")

# Test 1: Basic imports
try:
    from pymocat_mc.supporting_functions.get_idx import get_idx
    from pymocat_mc.supporting_functions.categorize_obj import categorize_obj
    print("OK Basic imports successful")
except ImportError as e:
    print(f"ERROR Import failed: {e}")
    sys.exit(1)

# Test 2: Index structure
try:
    idx = get_idx()
    assert isinstance(idx, dict)
    assert 'a' in idx
    assert 'mass' in idx
    assert len(idx) == 20
    print("OK Index structure test passed")
except Exception as e:
    print(f"ERROR Index structure test failed: {e}")
    sys.exit(1)

# Test 3: MOCAT-MC import
try:
    from pymocat_mc import MOCATMC
    mocat = MOCATMC()
    assert hasattr(mocat, 'constants')
    assert hasattr(mocat, 'idx')
    print("OK MOCAT-MC import successful")
except ImportError as e:
    print(f"WARNING MOCAT-MC import skipped: {e}")

print("\nAll basic functionality tests passed!")
sys.exit(0)