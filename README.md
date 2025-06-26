# Spond Payment Reporting Tool

A Python tool for generating payment reports from the Spond club management system. This tool helps club administrators track outstanding payments and generate detailed Excel reports.

## Features

- 🔐 Secure credential management with optional local storage
- 📊 Excel reports with summary and detailed views
- 🖥️ Command-line interface for easy automation
- 🔄 Proper error handling and retry logic
- 📱 Modern Python package structure for easy installation

## Installation

### Option 1: Install from Source (Recommended for now)

```bash
# Clone the repository
git clone https://github.com/jtracey93/spond-payment-reporting.git
cd spond-payment-reporting

# Install the package
pip install -e .
```

### Option 2: Install from PyPI (Coming Soon)

```bash
pip install spond-payment-reporting
```

### Option 3: Install Dependencies Only

If you prefer to run the script directly:

```bash
pip install -r requirements.txt
```

## Quick Start

### Using the Command-Line Tool

After installation, you can use the `spond-report` command:

```bash
# Interactive mode (recommended for first-time users)
spond-report

# Specify output file
spond-report -o my_report.xlsx

# Provide credentials directly (useful for automation)
spond-report --bearer-token YOUR_TOKEN --club-id YOUR_CLUB_ID

# Reset saved configuration
spond-report --reset-config
```

### Using as a Python Module

```python
from spond_reporting import SpondAPI, PaymentReportGenerator

# Initialize API client
api = SpondAPI("your_bearer_token", "your_club_id")

# Fetch data
members, member_map = api.get_members()
payments = api.get_payments()

# Generate report
generator = PaymentReportGenerator()
granular_rows, stats = generator.process_payment_data(payments, member_map, api)
excel_file = generator.generate_excel_report(granular_rows, "report.xlsx")
```

## Getting Your Credentials

You'll need two pieces of information from Spond:

### 1. Bearer Token
1. Log into Spond Club in your web browser
2. Open Developer Tools (F12)
3. Go to the Network tab
4. Refresh the page or navigate to another section
5. Look for API requests to `api.spond.com`
6. In the request headers, find the `authorization` header
7. Copy the value after "Bearer " (it's a long string)

### 2. Club ID
1. In the same network requests, look for the `x-spond-clubid` header
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

# Use in a script with environment variables
export SPOND_BEARER_TOKEN="your_token_here"
export SPOND_CLUB_ID="your_club_id_here"
spond-report --bearer-token "$SPOND_BEARER_TOKEN" --club-id "$SPOND_CLUB_ID"

# Verbose output for debugging
spond-report --verbose
```

## Output

The tool generates an Excel file with two sheets:

1. **Summary**: Aggregated view showing total amount owed per member
2. **Granular Details**: Detailed breakdown of each unpaid payment

## Configuration

The tool can save your Club ID (and optionally your Bearer Token) in a configuration file:

- **Location**: `~/.spond-reporting/config.json`
- **Permissions**: Automatically set to read-only for the user (600)
- **Security**: Bearer tokens are not saved by default for security reasons

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

- 🔒 Bearer tokens are sensitive credentials - never commit them to version control
- 🏠 Config files are stored in your home directory with restricted permissions
- ⚠️ Be cautious when saving bearer tokens to config files
- 🔄 Bearer tokens may expire and need to be refreshed periodically

## Troubleshooting

### Common Issues

1. **"JSON Decode Error"**: Usually indicates an expired bearer token
2. **"HTTP 401/403 errors"**: Check your bearer token and club ID
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