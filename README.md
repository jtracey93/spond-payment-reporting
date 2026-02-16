# Spond Payment Reporting Tool

<a href="https://www.buymeacoffee.com/jacktracey" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

A simple tool for generating payment reports from the Spond club management system. It helps club administrators see who still owes money and produces an Excel spreadsheet you can share with your committee.

## 🌐 Web App Available!

**New!** You can now use this tool directly in your browser without installing anything:

👉 **[Launch Web App](https://jtracey93.github.io/spond-payment-reporting/)** 👈

The web app provides the same functionality with an easy-to-use interface, filtering, sorting, and export capabilities.

⚠️ **Note:** The web app requires a CORS browser extension to work (see [CORS workarounds](docs/README.md#cors-workarounds)). For a hassle-free experience, use the Python CLI tool below.

[Learn more about the web app →](docs/README.md)

---

## What It Does

- Connects to your Spond club account
- Downloads all payment information
- Creates an Excel report showing who has outstanding payments
- Lets you filter by payment name (e.g. "Match Fee", "2025", "Membership")
- **Web version**: View and analyze data in your browser with filtering, sorting, and export options
- **CLI version**: Reliable, no CORS restrictions, automated login support

## Getting Started

### Option 1: Use the Web App (Browser-Based)

Visit **[https://jtracey93.github.io/spond-payment-reporting/](https://jtracey93.github.io/spond-payment-reporting/)** and follow the on-screen instructions.

**Important:** You'll need to install a CORS browser extension. See [CORS workarounds](docs/README.md#cors-workarounds) for details.

### Option 2: Install the Command-Line Tool (Recommended)

#### 1. Install Python

If you don't already have Python installed:

- **Windows**: Download from [python.org](https://www.python.org/downloads/) and run the installer. **Tick the "Add Python to PATH" checkbox** during installation.
- **Mac**: Download from [python.org](https://www.python.org/downloads/) or install via `brew install python`.

#### 2. Download This Tool

Open a terminal (Command Prompt on Windows, Terminal on Mac) and run:

```bash
git clone https://github.com/jtracey93/spond-payment-reporting.git
cd spond-payment-reporting
pip install -e .
```

> **Tip:** If `pip` doesn't work, try `pip3` instead.

#### 3. Run It

```bash
spond-report
```

That's it! The tool will walk you through the rest.

## How to Log In

The tool needs a "bearer token" from Spond to access your club data. There are two ways to get one:

### Option A: Browser Login (Easiest)

The tool will:

1. Open a browser window to the Spond Club login page
2. You log in as normal (including any 2FA/SMS verification)
3. The tool grabs your login token automatically
4. The token is saved so you don't have to log in every time

Just run `spond-report` and follow the prompts.

### Option B: Copy the Token Manually

If you don't want to install the browser extras, the tool will open the Spond login page in your browser and show you how to copy the token:

1. Log in to [club.spond.com](https://club.spond.com/) in your browser
2. Press **F12** to open Developer Tools
3. Click the **Network** tab
4. Refresh the page
5. Click on any request to `api.spond.com` in the list
6. Look for the **Authorization** header on the right side
7. Copy the long string after "Bearer " — that's your token

Then paste it when the tool asks, or pass it directly:

```bash
spond-report --bearer-token YOUR_TOKEN_HERE
```

### Choosing Your Club

The first time you run the tool, it will show you a list of clubs on your account and ask you to pick one:

```
Available clubs:
  1. My Cricket Club (abc12345-...)
  2. Another Club (def67890-...)

Select a club (1-2): 1
Selected: My Cricket Club
```

Your choice is saved so you won't be asked again.

## Common Commands

| What you want to do | Command |
|---|---|
| Run with all defaults | `spond-report` |
| Save the report with a specific name | `spond-report -o my_report.xlsx` |
| Show only 2025 payments | `spond-report --title-filter "2025"` |
| Show only match fees | `spond-report --title-filter "Match Fee"` |
| Show only 2025 match fees | `spond-report --title-filter "Match Fee" --title-filter "2025"` |
| Force a fresh browser login | `spond-report --login` |
| Login in InPrivate mode | `spond-report --login --private` |
| Pass a token directly | `spond-report --bearer-token YOUR_TOKEN` |
| Pass a token and club ID directly | `spond-report --bearer-token YOUR_TOKEN --club-id YOUR_CLUB_ID` |
| Clear all saved settings | `spond-report --reset-config` |
| Show help | `spond-report --help` |

## Filtering Payments

You can narrow down the report to specific payments using `--title-filter`. The filter checks if the payment name contains the text you provide (not case-sensitive).

**One filter:**
```bash
spond-report --title-filter "2025"
```

**Multiple filters (AND logic)** — payment must match ALL filters:
```bash
spond-report --title-filter "Match Fee" --title-filter "2025"
```

**Save the filtered report:**
```bash
spond-report --title-filter "Match Fee" --title-filter "2025" -o "2025_match_fees.xlsx"
```

### Example Results

| Filters used | Outstanding items |
|---|---|
| None (all payments) | 141 |
| `"2025"` | 85 |
| `"Match Fee"` | 100 |
| `"Match Fee"` + `"2025"` | 44 |
| `"T20"` + `"2025"` | 13 |

## What the Report Looks Like

The Excel file contains two sheets:

1. **Summary** — one row per member showing the total amount they owe
2. **Granular Details** — every individual unpaid payment broken out

## Where Settings Are Saved

Your token and club ID are saved in a file at:

- **Windows**: `C:\Users\YourName\.spond-reporting\config.json`
- **Mac/Linux**: `~/.spond-reporting/config.json`

To clear everything and start fresh: `spond-report --reset-config`

## Troubleshooting

| Problem | What to do |
|---|---|
| "Token has expired" | Run `spond-report --login` to log in again |
| Browser won't open (already running) | Close all browser windows (check system tray), then re-run |
| Browser opens then crashes | Run `spond-report --login --private` to use InPrivate mode |
| Tool can't find your clubs | Check your token is correct — try logging in again |
| "HTTP 401/403 errors" | Your token has expired — log in again |
| No payments showing | All payments might be up to date! Try removing filters. |
| `pip` command not found | Try `pip3` instead, or reinstall Python with "Add to PATH" ticked |

## Development

### Setting Up a Dev Environment

```bash
git clone https://github.com/jtracey93/spond-payment-reporting.git
cd spond-payment-reporting
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -e ".[dev,browser]"
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

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

This tool is not officially affiliated with Spond. Use at your own risk and ensure you comply with Spond's terms of service.
