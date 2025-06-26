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
pip install build

# Build the package
python -m build
```

## Environment Variables

For automation, you can use environment variables:

```bash
export SPOND_BEARER_TOKEN="your_token_here"
export SPOND_CLUB_ID="your_club_id_here"
spond-report --bearer-token "$SPOND_BEARER_TOKEN" --club-id "$SPOND_CLUB_ID"
```

## Advanced Usage Examples

### Title Filtering

The tool supports powerful filtering by payment titles. You can use single or multiple filters:

#### Single Filter Examples
```bash
# Filter for all 2025 payments
spond-report --title-filter "2025"

# Filter for all match fees
spond-report --title-filter "Match Fee"

# Filter for membership payments
spond-report --title-filter "Membership"

# Filter for T20 tournaments
spond-report --title-filter "T20"

# Filter for donations
spond-report --title-filter "Donation"
```

#### Multiple Filter Examples (AND Logic)
Use multiple `--title-filter` flags to find payments containing ALL specified terms:

```bash
# Find only 2025 match fees
spond-report --title-filter "Match Fee" --title-filter "2025"

# Find only 2025 T20 matches
spond-report --title-filter "T20" --title-filter "2025"

# Find specific team matches in 2025
spond-report --title-filter "1st XI" --title-filter "2025"

# Find away matches in 2025
spond-report --title-filter "Away" --title-filter "2025"

# Find specific opponent matches
spond-report --title-filter "Match Fee" --title-filter "Cuckfield"
```

#### Complete Command Examples
```bash
# Generate 2025 match fees report with custom output
spond-report --title-filter "Match Fee" --title-filter "2025" --output "2025_match_fees.xlsx"

# Generate T20 tournament report for 2025
spond-report --title-filter "T20" --title-filter "2025" --output "t20_2025.xlsx"

# Generate membership payments report
spond-report --title-filter "Membership" --output "membership_outstanding.xlsx"

# Generate specific team report
spond-report --title-filter "1st XI" --title-filter "2025" --output "first_team_2025.xlsx"

# Verbose output with multiple filters
spond-report --title-filter "Match Fee" --title-filter "Away" --title-filter "2025" --verbose
```

#### Filter Results Summary
- **No filters**: All outstanding payments across all payment types
- **Single filter**: Payments containing that specific term
- **Multiple filters**: Payments containing ALL specified terms (intersection)
- **Case-insensitive**: Filters work regardless of capitalization

Example filter results:
- All payments: 141 outstanding items
- `--title-filter "2025"`: 85 outstanding items  
- `--title-filter "Match Fee"`: 100 outstanding items
- `--title-filter "Match Fee" --title-filter "2025"`: 44 outstanding items
- `--title-filter "T20" --title-filter "2025"`: 13 outstanding items
