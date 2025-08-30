# Testing PyMOCAT-MC

## Quick Start

### Automated Setup (Recommended)
```bash
# Create a clean environment with all dependencies
python3 setup_environment.py

# Activate the environment (follow instructions from setup script)
source pymocat_env/bin/activate  # On Unix/macOS
# or
pymocat_env\Scripts\activate     # On Windows

# Run tests
python3 tests/run_tests.py
```

### Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python3 tests/run_tests.py
```

## Test Scenarios

PyMOCAT-MC includes benchmark scenarios designed to validate specific physics modules:

### Basic Propagation
Tests orbital propagator without interference from collisions or launches. Validates pure orbital motion mechanics.

### Collision Test  
Tests collision detection algorithms, conjunction analysis, and fragmentation models. Focuses on collision physics validation.

### Atmospheric Drag
Validates atmospheric density models and drag effects at low altitudes where atmospheric drag dominates.

### Full Default
Comprehensive integration test using all default parameters. Serves as baseline for MATLAB comparison.

### Realistic Operations No Launch
Tests long-term space environment evolution using realistic operational parameters and failure rates.

## Test Runners

### Method 1: Python test runner (Cross-platform)
```bash
python3 tests/run_tests.py
```

### Method 2: Bash test runner (Unix/macOS)
```bash
./tests/run_tests.sh
```

### Method 3: Individual tests
```bash
# Basic functionality (~1s)
python3 tests/test_basic_functionality_simple.py

# Import test (~2s)
python3 tests/test_import.py

# Minimal simulation (~5s)
python3 tests/minimal_test.py

# Simple run test (~3s)
python3 tests/test_simple_run.py
```

## Test Structure

The test suite includes 4 essential tests that provide complete coverage:

1. **Basic Functionality Tests** (`test_basic_functionality_simple.py`)
   - Tests core imports and functions
   - Verifies data structures (get_idx, categorize_obj)
   - Tests MOCATMC class initialization
   - Fastest test (~1 second)

2. **Import Test** (`test_import.py`)
   - Verifies all required modules can be imported
   - Checks TLE data loading (finds 14,207 satellites)
   - Tests MOCATMC initialization
   - Validates file paths (~2 seconds)

3. **Minimal Simulation Test** (`minimal_test.py`)
   - Runs a minimal 2-step simulation
   - Verifies basic simulation pipeline
   - Tests end-to-end functionality (~5 seconds)

4. **Simple Run Test** (`test_simple_run.py`)
   - Runs a single time step simulation
   - Tests core simulation functionality
   - Quick smoke test (~3 seconds)

5. **Example Scripts** (run as integration tests)
   - Quick Start example (full year simulation)
   - Scenario No Launch example
   - Realistic Operations No Launch example

## Requirements

### System Requirements
- Python 3.8 or higher
- NumPy
- SciPy
- Matplotlib (for plotting examples)
- Pandas (optional, for data handling)

### Installing Dependencies

```bash
# Using pip
pip3 install numpy scipy matplotlib pandas

# Or using the requirements file
pip3 install -r requirements.txt
```

## Virtual Environment Setup (Optional)

If you want to use a virtual environment:

```bash
# Create a new virtual environment
python3 -m venv test_env

# Activate it
source test_env/bin/activate  # On Unix/macOS
# or
test_env\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
python tests/run_tests.py
```

## Known Issues and Solutions

### Issue 1: Import Errors
If you see `ModuleNotFoundError: No module named 'mocat_mc'`:
- Make sure you're running tests from the repository root directory
- The test scripts automatically add the correct paths

### Issue 2: pytest hangs
If pytest hangs during test collection:
- Use the provided `run_tests.py` script instead
- Or run individual test files directly with Python

## Expected Output

When all tests pass, you should see:
```
+ Basic functionality tests: PASSED
+ Import test: PASSED
+ Minimal simulation test: PASSED
+ Simple run test: PASSED
+ Quick Start example: PASSED

All tests passed!
```

## Warnings

You may see some warnings during test execution:
- `RuntimeWarning: invalid value encountered in cast` - This is expected for NaN handling
- `RuntimeWarning: divide by zero` - This occurs in edge cases and is properly handled

These warnings do not indicate test failures.

## Continuous Integration

For CI/CD pipelines, use:
```bash
python3 tests/run_tests.py
```

The script returns:
- Exit code 0: All tests passed
- Exit code 1: One or more tests failed