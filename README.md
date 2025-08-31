# PyMOCAT-MC

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.16831016.svg)](https://doi.org/10.5281/zenodo.16831016)

**PyMOCAT-MC** is a Python implementation of the MIT Orbital Capacity Assessment Toolbox - Monte Carlo (MOCAT-MC), originally written in MATLAB. This toolbox enables Monte Carlo-based analysis of orbital capacity, debris, and satellite population evolution, supporting research and engineering in space situational awareness and orbital risk. The Python implementation maintains full compatibility with the original MATLAB version while leveraging modern Python scientific computing libraries.

---

## Statement of Need

As the orbital environment becomes increasingly congested with satellite deployments and large-scale constellations, modeling space traffic and debris risk has become crucial for space sustainability research. The original MATLAB MOCAT-MC toolbox is a leading framework for orbital capacity assessment, but it limits accessibility and hinders integration with modern Python-based data science and machine learning workflows that are central to contemporary space research.

PyMOCAT-MC addresses these barriers by providing a functionally equivalent, open-source Python implementation that maintains full compatibility with the original while improving performance and accessibility. This enables broader adoption in the space research community and integration with state-of-the-art scientific computing tools.

## Comparison to Similar Software

PyMOCAT-MC fills a unique niche in the orbital mechanics software ecosystem:

- **Original MATLAB MOCAT-MC**: Proprietary, excellent algorithms but limited accessibility due to licensing costs and integration barriers with modern Python workflows
- **Astropy/Poliastro**: General orbital mechanics libraries, but lack specialized Monte Carlo debris evolution and collision modeling capabilities
- **MOCAT-pySSEM**: Related source-sink environmental modeling tool, but focuses on different aspects of space environment modeling
- **Commercial debris analysis tools**: Often proprietary and expensive, with limited customization options

PyMOCAT-MC uniquely combines the proven algorithms of MATLAB MOCAT-MC with open-source accessibility, performance improvements, and seamless integration with the Python scientific computing ecosystem.

## Software Purpose
PyMOCAT-MC provides a flexible, extensible framework for simulating the evolution of satellite populations and debris in Earth orbit. It is designed for:
- Assessing orbital capacity and congestion
- Modeling satellite launches, collisions, and fragmentation
- Evaluating the impact of megaconstellations
- Supporting policy and engineering studies in orbital risk
- Enabling integration with Python ML/data science ecosystems

---

## Installation

### Install from PyPI (Recommended)

```bash
pip install pymocat-mc
```

### Install from Source

Clone the repository and install in development mode:

```bash
git clone https://github.com/rushilkukreja/PyMOCAT-MC.git
cd PyMOCAT-MC
pip install -e .

# Verify installation works
python3 tests/run_tests.py
```

### Verify Installation

After installation, verify everything works:

```bash
# Run all tests
python3 tests/run_tests.py

# Quick functionality check
cd python_implementation && python3 -c "from mocat_mc import MOCATMC; print('+ PyMOCAT-MC installed successfully')"
```

### Install with Development Dependencies

For contributors and developers:

```bash
git clone https://github.com/rushilkukreja/PyMOCAT-MC.git
cd PyMOCAT-MC
pip install -e ".[dev]"

# Or use automated setup (creates virtual environment)
python3 setup_environment.py
```

### Requirements

- Python >= 3.8
- numpy >= 1.21.0
- scipy >= 1.7.0
- pandas >= 1.3.0
- matplotlib >= 3.5.0

All dependencies will be automatically installed with pip.

---
## Usage
### Quick Start

Example scripts are provided in the `examples/` directory:

```bash
cd python_implementation
python examples/Quick_Start/quick_start.py
```

For a scenario without launches:

```bash
python examples/Scenario_No_Launch/scenario_no_launch.py
```

For a realistic operations scenario without future launches:

```bash
python examples/Realistic_Operations_No_Launch/realistic_operations_no_launch.py
```

### Custom Configuration

```python
from mocat_mc import MOCATMC

# Initialize MOCAT-MC
mocat = MOCATMC()

# Setup configuration
cfg_mc = mocat.setup_mc_config(rng_seed=1, ic_file='2020.mat')

# Customize simulation parameters
cfg_mc['tspan'] = 30  # Simulation duration
cfg_mc['N_ini_samples'] = 10  # Number of initial orbit samples
cfg_mc['prop']['dt_TL'] = 90  # Time step in days

# Run simulation
results = mocat.run_simulation(cfg_mc)

print(f"Final counts - Satellites: {results['nS']}, Derelicts: {results['nD']}, Debris: {results['nN']}, Rocket Bodies: {results['nB']}")
```

---

## Data

Supporting data files are provided in the `python_implementation/supporting_data/` directory:

- **TLE Historic Data** (`TLEhistoric/`): CSV and MAT files containing Two-Line Element sets for satellites from 2000–2023. See the included `readme.txt` for details and data sources.
- **Atmospheric Density Model**: `dens_jb2008_032020_022224.mat` - JB2008 atmospheric density data
- **Launch Schedules**: `megaconstellationLaunches.xlsx` - Planned megaconstellation launch data

---

## Project Structure

```
PyMOCAT-MC/
├── python_implementation/
│   ├── mocat_mc.py                    # Main MOCAT-MC class
│   ├── examples/
│   │   ├── Quick_Start/
│   │   │   ├── quick_start.py         # Basic simulation example
│   │   │   └── quick_start_with_plots.py  # Example with visualizations
│   │   ├── Realistic_Operations_No_Launch/
│   │   │   └── realistic_operations_no_launch.py  # Realistic operations without launches
│   │   └── Scenario_No_Launch/
│   │       └── scenario_no_launch.py  # Decay-only scenario
│   ├── supporting_functions/
│   │   ├── cfg_mc_constants.py        # Physical constants
│   │   ├── get_idx.py                 # Matrix index definitions
│   │   ├── categorize_obj.py          # Object categorization
│   │   ├── init_sim.py                # Simulation initialization
│   │   ├── main_mc.py                 # Main Monte Carlo engine
│   │   ├── prop_mit_vec.py            # MIT orbital propagator
│   │   ├── collision_prob_vec.py      # Collision probability
│   │   ├── cube_vec_v3.py             # Cube method for conjunctions
│   │   ├── frag_col_sbm_vec.py        # Collision fragmentation model
│   │   ├── orbcontrol_vec.py          # Orbit control/station-keeping
│   │   ├── fillin_atmosphere.py       # Atmospheric model interface
│   │   ├── fillin_physical_parameters.py  # Object physical properties
│   │   └── [additional utilities...]
│   ├── supporting_data/
│   │   ├── TLEhistoric/               # Historical TLE data (2000-2023)
│   │   ├── dens_jb2008_032020_022224.mat  # Atmospheric density data
│   │   └── megaconstellationLaunches.xlsx  # Launch schedules
├── tests/                             # Main test suite
│   ├── run_tests.py                   # Python test runner (cross-platform)
│   ├── run_tests.sh                   # Bash test runner (Unix/macOS)
│   ├── test_basic_functionality_simple.py  # Core functionality tests
│   ├── test_import.py                 # Import and data loading tests
│   ├── minimal_test.py                # Minimal 2-step simulation test
│   ├── test_simple_run.py             # Single time-step test
│   └── README.md                      # Test suite documentation
├── comparison_tests/                  # Python vs MATLAB comparison tests
│   ├── test_all_scenarios.py          # Comprehensive comparison across all scenarios
│   ├── test_quick_scenarios.py        # Quick validation tests for basic scenarios
│   ├── accuracy_error_data.csv        # Accuracy error measurements data
│   └── accuracy_error_data.json       # Accuracy error data in JSON format
├── analysis_figures/                  # Analysis and visualization scripts
│   ├── plot_total_object_counts.py    # Generate total object count comparison plots
│   ├── plot_execution_time.py         # Visualize execution time performance
│   ├── plot_object_type_heatmap.py    # Create heatmap of object type percentages
│   ├── plot_computational_efficiency.py # Analyze computational efficiency metrics
│   ├── measure_accuracy_errors.py     # Calculate accuracy errors between implementations
│   ├── plot_error_analysis.py         # Generate error distribution plots
│   ├── total_object_counts.png        # Output: Object count comparison visualization
│   ├── execution_time_comparison.png  # Output: Performance comparison chart
│   ├── object_type_percentage_heatmap.png # Output: Object type distribution heatmap
│   ├── computational_efficiency_analysis.png # Output: Efficiency analysis chart
│   └── error_box_plots.png            # Output: Error distribution visualization
├── MATLAB_implementation/             # Original MATLAB implementation
├── paper/                             # JOSS paper and figures
├── setup_environment.py               # Automated environment setup
├── requirements.txt                   # Python dependencies
├── pyproject.toml                     # Modern Python packaging configuration
├── setup.py                           # Traditional Python packaging
├── CONTRIBUTING.md                    # Contribution guidelines
├── TESTING.md                         # Detailed testing instructions
├── LICENSE                            # MIT License
├── CITATION.cff                       # Citation metadata
└── README.md                          # This file
```

---

## Testing

Run the test suite using our custom test runners:

```bash
# Recommended: Run all tests with Python runner
python3 tests/run_tests.py

# Alternative: Use bash runner (Unix/macOS only)
./tests/run_tests.sh

# Individual tests
python3 tests/test_basic_functionality_simple.py
python3 tests/test_import.py
python3 tests/minimal_test.py
python3 tests/test_simple_run.py
```

For detailed testing instructions and troubleshooting, see [TESTING.md](TESTING.md).

---

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on how to submit pull requests, report issues, and contribute to the project.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Citation

If you use PyMOCAT-MC in your research, please cite:

```bibtex
@software{kukreja2025pymocatmc,
  author = {Kukreja, Rushil and Oughton, Edward J. and Lavezzi, Giovanni and 
            Zucchelli, Enrico M. and Jang, Daniel and Linares, Richard},
  title = {PyMOCAT-MC: A Python Implementation of the MIT Orbital Capacity 
           Assessment Toolbox Monte Carlo Module},
  year = {2025},
  url = {https://github.com/rushilkukreja/PyMOCAT-MC},
  doi = {10.5281/zenodo.16831016}
}
```

---

## Contributors

- **Rushil Kukreja**, Student, Thomas Jefferson High School for Science and Technology
- **Dr. Edward J. Oughton**, Assistant Professor, George Mason University
- **Dr. Giovanni Lavezzi**, Research Scientist, Massachusetts Institute of Technology
- **Dr. Enrico M. Zucchelli**, Postdoctoral Associate, Massachusetts Institute of Technology
- **Dr. Daniel Jang**, Technical Staff, Lincoln Laboratory
- **Dr. Richard Linares**, Associate Professor, Massachusetts Institute of Technology