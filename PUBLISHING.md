# Publishing to PyPI

This document explains how to publish the Spond Payment Reporting Tool to PyPI so others can install it with `pip install spond-payment-reporting`.

## Prerequisites

1. **PyPI Account**: Create accounts on both:
   - [TestPyPI](https://test.pypi.org/) (for testing)
   - [PyPI](https://pypi.org/) (for production)

2. **API Tokens**: Generate API tokens for both platforms

3. **Install Tools**:
   ```bash
   pip install build twine
   ```

## Build the Package

```bash
# Clean any previous builds
rm -rf dist/ build/ *.egg-info/

# Build the package
python -m build
```

This creates:
- `dist/spond_payment_reporting-1.0.0.tar.gz` (source distribution)
- `dist/spond_payment_reporting-1.0.0-py3-none-any.whl` (wheel)

## Test on TestPyPI First

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ spond-payment-reporting
```

## Publish to PyPI

Once tested successfully:

```bash
# Upload to PyPI
python -m twine upload dist/*
```

## Using API Tokens

Create a `.pypirc` file in your home directory:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = your-test-api-token-here
```

## Automation with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish Python Package

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish package
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

## Versioning

Update version in `setup.py` and `src/spond_reporting/__init__.py` before publishing.

## After Publishing

Users can then install with:

```bash
pip install spond-payment-reporting
```

And use with:

```bash
spond-report
```
