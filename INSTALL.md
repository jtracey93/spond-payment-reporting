# Installation and Usage Guide

## Quick Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jtracey93/spond-payment-reporting.git
   cd spond-payment-reporting
   ```

2. **Install the package:**
   ```bash
   pip install -e .
   ```

3. **Run the tool:**
   ```bash
   spond-report
   ```

## For Developers

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/jtracey93/spond-payment-reporting.git
cd spond-payment-reporting

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/

# Lint code
flake8 src/
```

### Package Structure

```
src/spond_reporting/
├── __init__.py          # Package initialization
├── api.py              # Spond API client
├── cli.py              # Command-line interface
├── config.py           # Configuration management
└── report.py           # Report generation
```

## Building Distribution

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Upload to PyPI (when ready)
twine upload dist/*
```

## Environment Variables

For automation, you can use environment variables:

```bash
export SPOND_BEARER_TOKEN="your_token_here"
export SPOND_CLUB_ID="your_club_id_here"
spond-report --bearer-token "$SPOND_BEARER_TOKEN" --club-id "$SPOND_CLUB_ID"
```
