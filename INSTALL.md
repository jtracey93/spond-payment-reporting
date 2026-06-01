# Installation and Usage Guide

This guide walks you through installing and using the Spond Payment Reporting tool step by step.

## Step 1: Install Python

You need Python 3.8 or newer. If you're not sure whether you have it, open a terminal and type:

```bash
python --version
```

If you see a version number (e.g. `Python 3.12.4`), you're good. If not:

- **Windows**: Download from [python.org](https://www.python.org/downloads/). During installation, **tick "Add Python to PATH"** — this is important!
- **Mac**: Download from [python.org](https://www.python.org/downloads/) or run `brew install python` if you use Homebrew.

## Step 2: Download the Tool

Open a terminal (Command Prompt or PowerShell on Windows, Terminal on Mac) and run:

```bash
git clone https://github.com/jtracey93/spond-payment-reporting.git
cd spond-payment-reporting
```

> **Don't have git?** You can download the code as a ZIP from the GitHub page instead — click the green "Code" button, then "Download ZIP". Unzip it and open a terminal in that folder.

## Step 3: Install the Tool

```bash
pip install -e .
```

This installs everything you need, including the automated browser login.

> **Tip**: If `pip` doesn't work, try `pip3` instead.

## Step 4: Run It

```bash
spond-report
```

The first time you run it, the tool will:

1. Open a browser so you can log in to Spond
2. Grab your login token
3. Show you a list of your clubs and ask you to pick one
4. Generate the payment report

After the first run, your token and club are saved so you can just run `spond-report` again without logging in.

## All Options

```
spond-report                                    # Run with saved settings
spond-report --login                            # Force a fresh browser login
spond-report --login --private                  # Login in InPrivate mode
spond-report --bearer-token TOKEN               # Use a specific token
spond-report --bearer-token TOKEN --club-id ID  # Use a specific token and club
spond-report -o my_report.xlsx                  # Save report with a custom name
spond-report --title-filter "2025"              # Only show 2025 payments
spond-report --title-filter "Match Fee"         # Only show match fees
spond-report --reset-config                     # Clear all saved settings
spond-report --help                             # Show all options
```

## Filtering Payments

Use `--title-filter` to narrow down the report. Filters are case-insensitive.

```bash
# One filter
spond-report --title-filter "2025"

# Multiple filters (must match ALL)
spond-report --title-filter "Match Fee" --title-filter "2025"

# Exclude payments matching a term (applied after --title-filter, can be used multiple times)
spond-report --title-filter "Match Fee" --exclude-title-filter "30th May"

# Save the filtered report
spond-report --title-filter "Match Fee" --title-filter "2025" -o "2025_match_fees.xlsx"
```

## Updating the Tool

To get the latest version:

```bash
cd spond-payment-reporting
git pull
pip install -e .
```

## Uninstalling

```bash
pip uninstall spond-payment-reporting
```

To also remove saved settings, delete the folder:
- **Windows**: `C:\Users\YourName\.spond-reporting\`
- **Mac/Linux**: `~/.spond-reporting/`

## For Developers

### Dev Setup

```bash
git clone https://github.com/jtracey93/spond-payment-reporting.git
cd spond-payment-reporting
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -e ".[dev]"
pytest
```

### Project Structure

```
src/spond_reporting/
├── __init__.py      # Package init
├── api.py           # Spond API client
├── browser.py       # Browser-based token extraction
├── cli.py           # Command-line interface
├── config.py        # Settings management
└── report.py        # Excel report generation
```
