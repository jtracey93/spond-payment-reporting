# Spond Payment Reporting Tool

<a href="https://www.buymeacoffee.com/jacktracey" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

A Python tool for generating payment reports from the Spond club management system. This tool helps club administrators track outstanding payments and generate detailed Excel reports.

## Features

- 🔐 Email/password authentication via the [spond](https://pypi.org/project/spond/) library — no need to extract bearer tokens from browser developer tools
- 📊 Excel reports with summary and detailed views
- 🖥️ Command-line interface for easy automation
- 🔄 Proper error handling and retry logic
- 📱 Modern Python package structure for easy installation

## Installation

### Option 1: Install from Source

```bash
# Clone the repository
git clone https://github.com/jtracey93/spond-payment-reporting.git
cd spond-payment-reporting

# Install the package
pip install -e .
```

### Option 2: Install Dependencies Only

If you prefer to run the script directly:

```bash
pip install -r requirements.txt
```

## Quick Start

### Using the Command-Line Tool

After installation, you can use the `spond-report` command:

```bash
# Interactive mode (recommended for first-time users)
# Will prompt for your Spond email, password, and club ID
spond-report

# Specify output file
spond-report -o my_report.xlsx

# Provide email directly (will prompt for password securely)
spond-report --email user@example.com --club-id YOUR_CLUB_ID

# Legacy: provide bearer token directly (useful for automation)
spond-report --bearer-token YOUR_TOKEN --club-id YOUR_CLUB_ID

# Reset saved configuration
spond-report --reset-config
```

### Using as a Python Module

```python
from spond_reporting import SpondAPI, PaymentReportGenerator

# Authenticate with email/password (recommended)
api = SpondAPI.from_credentials("your@email.com", "your_password", "your_club_id")

# Or use a bearer token directly (legacy)
# api = SpondAPI("your_bearer_token", "your_club_id")

# Fetch data
members, member_map = api.get_members()
payments = api.get_payments()

# Generate report
generator = PaymentReportGenerator()
granular_rows, stats = generator.process_payment_data(payments, member_map, api)
excel_file = generator.generate_excel_report(granular_rows, "report.xlsx")
```

## Authentication

The tool supports two authentication methods:

### 1. Email/Password Login (Recommended)

Simply use your Spond account email and password. The tool uses the [spond](https://pypi.org/project/spond/) library to authenticate securely. Your password is never stored — only your email and club ID are saved for convenience.

```bash
# Interactive mode will prompt for email, password, and club ID
spond-report

# Or provide email via CLI (password prompted securely)
spond-report --email user@example.com --club-id YOUR_CLUB_ID
```

### 2. Bearer Token (Legacy)

If you prefer, you can still use a bearer token extracted from browser developer tools:

1. Log into Spond Club in your web browser
2. Open Developer Tools (F12)
3. Go to the Network tab
4. Refresh the page or navigate to another section
5. Look for API requests to `api.spond.com`
6. In the request headers, find the `authorization` header
7. Copy the value after "Bearer " (it's a long string)

### Getting Your Club ID

1. In the browser Network tab, look for the `x-spond-clubid` header in API requests
2. Copy this value (it's a GUID like `12345678-1234-1234-1234-123456789ABC`)

## Usage Examples

### Basic Usage

```bash
# Run interactively
spond-report
```

The tool will prompt you for your credentials and offer to save your Club ID for future use.

### Advanced Usage

```bash
# Generate report with custom filename
spond-report -o "monthly_report_$(date +%Y%m%d).xlsx"

# Use in a script with environment variables (legacy bearer token)
export SPOND_BEARER_TOKEN="your_token_here"
export SPOND_CLUB_ID="your_club_id_here"
spond-report --bearer-token "$SPOND_BEARER_TOKEN" --club-id "$SPOND_CLUB_ID"

# Provide email via CLI (password will be prompted securely)
spond-report --email user@example.com --club-id "$SPOND_CLUB_ID"

# Verbose output for debugging
spond-report --verbose
```

### Title Filtering

Filter payments by title to focus on specific types of payments. Supports single or multiple filters:

```bash
# Single filter examples
spond-report --title-filter "2025"              # All 2025 payments
spond-report --title-filter "Match Fee"         # All match fees
spond-report --title-filter "Membership"        # Membership payments
spond-report --title-filter "T20"               # T20 tournaments
spond-report --title-filter "Donation"          # Donation payments

# Multiple filters (AND logic) - payment must contain ALL terms
spond-report --title-filter "Match Fee" --title-filter "2025"    # 2025 match fees only
spond-report --title-filter "T20" --title-filter "2025"          # 2025 T20 matches only
spond-report --title-filter "1st XI" --title-filter "2025"       # First team 2025 matches
spond-report --title-filter "Away" --title-filter "2025"         # Away matches in 2025

# Complete examples with output files
spond-report --title-filter "Match Fee" --title-filter "2025" --output "2025_match_fees.xlsx"
spond-report --title-filter "Membership" --output "membership_outstanding.xlsx"
spond-report --title-filter "T20" --title-filter "2025" --output "t20_2025.xlsx"
```

**Filter Results Example:**
- All payments: 141 outstanding items
- `--title-filter "2025"`: 85 outstanding items  
- `--title-filter "Match Fee"`: 100 outstanding items
- `--title-filter "Match Fee" --title-filter "2025"`: 44 outstanding items
- `--title-filter "T20" --title-filter "2025"`: 13 outstanding items

## Output

The tool generates an Excel file with two sheets:

1. **Summary**: Aggregated view showing total amount owed per member
2. **Granular Details**: Detailed breakdown of each unpaid payment

## Configuration

The tool can save your email and Club ID in a configuration file for convenience:

- **Location**: `~/.spond-reporting/config.json`
- **Permissions**: Automatically set to read-only for the user (600)
- **Security**: Passwords are never saved; only email and Club ID are stored

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/jtracey93/spond-payment-reporting.git
cd spond-payment-reporting

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/

# Lint code
flake8 src/
```

### Project Structure

```
spond-payment-reporting/
├── src/
│   └── spond_reporting/
│       ├── __init__.py
│       ├── api.py          # Spond API client
│       ├── cli.py          # Command-line interface
│       ├── config.py       # Configuration management
│       └── report.py       # Report generation
├── python/                 # Original script location
├── pwsh/                   # PowerShell version
├── setup.py
├── requirements.txt
└── README.md
```

## Security Considerations

- 🔒 Passwords are prompted securely and never saved to disk
- 🏠 Config files are stored in your home directory with restricted permissions
- ⚠️ Legacy bearer token mode is still available but email/password login is recommended
- 🔄 The [spond](https://pypi.org/project/spond/) library handles authentication, so you no longer need to manually extract tokens from browser developer tools

## Troubleshooting

### Common Issues

1. **"Authentication failed"**: Check your email and password are correct
2. **"HTTP 401/403 errors"**: Check your club ID, or try re-authenticating
3. **"No outstanding payments found"**: All payments may be up to date!

### Getting Help

```bash
# Show help
spond-report --help

# Enable verbose output for debugging
spond-report --verbose

# Reset configuration if you're having issues
spond-report --reset-config
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is not officially affiliated with Spond. Use at your own risk and ensure you comply with Spond's terms of service.
