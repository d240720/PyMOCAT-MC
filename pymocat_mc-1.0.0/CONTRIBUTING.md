# Contributing to PyMOCAT-MC

We welcome contributions to PyMOCAT-MC! By participating in this project, you agree to abide by our community standards of respectful, inclusive, and collaborative behavior.

## How to Contribute

### Reporting Issues

- Use the [GitHub Issues](https://github.com/rushilkukreja/PyMOCAT-MC/issues) page to report bugs
- Include Python version, operating system, and error messages
- Provide minimal reproducible examples when possible

### Submitting Changes

1. **Fork the repository** and create a feature branch
2. **Install development dependencies**: `pip install -e ".[dev]"`
3. **Run tests** to ensure everything works: `python tests/run_tests.py`
4. **Make your changes** following the existing code style
5. **Add tests** for new functionality
6. **Update documentation** if needed
7. **Submit a pull request** with a clear description of changes

## Development Setup

```bash
git clone https://github.com/rushilkukreja/PyMOCAT-MC.git
cd PyMOCAT-MC
pip install -e ".[dev]"
python tests/run_tests.py
```

## Code Guidelines

- Follow existing code style and naming conventions
- Add docstrings for new functions and classes
- Include type hints where appropriate
- Ensure compatibility with Python 3.8+
- Run tests before submitting: `python tests/run_tests.py`

## Areas for Contribution

- Performance optimizations
- Documentation improvements
- New simulation scenarios
- Visualization enhancements

## Testing

Before submitting any changes:

1. **Run the test suite**: `python tests/run_tests.py`
2. **Verify all tests pass**: Look for "All tests passed!"
3. **Test on your target platform** (Windows/macOS/Linux)
4. **Add new tests** for any new functionality

## Code Review Process

1. All submissions require review before merging
2. We may ask for changes or improvements
3. Once approved, maintainers will merge your contribution
4. Keep pull requests focused on a single feature or fix

## Getting Help

- Open an issue for questions about contributing
- Reach out to maintainers for guidance
- Check existing issues and pull requests for similar work

Thank you for contributing to PyMOCAT-MC!