# Publishing to PyPI

This document describes how to publish PyMOCAT-MC to PyPI.

## Prerequisites

1. Register an account on [PyPI](https://pypi.org) and [TestPyPI](https://test.pypi.org)
2. Install the build and upload tools:
   ```bash
   pip install --upgrade build twine
   ```

## Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build the distribution packages
python -m build
```

This will create:
- `dist/pymocat-mc-1.0.0.tar.gz` (source distribution)
- `dist/pymocat_mc-1.0.0-py3-none-any.whl` (wheel distribution)

## Test on TestPyPI (Recommended)

1. Upload to TestPyPI:
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

2. Test installation from TestPyPI:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ pymocat-mc
   ```

## Publish to PyPI

Once testing is successful:

```bash
python -m twine upload dist/*
```

## Verify Installation

After publishing:

```bash
pip install pymocat-mc
python -c "from pymocat_mc import MOCATMC; print('Success!')"
```

## Update README

Once published to PyPI, update the README to remove "(Coming Soon)" from the PyPI installation section.