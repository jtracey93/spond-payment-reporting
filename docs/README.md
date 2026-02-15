# Spond Payment Reporting - Web App

This is a static web application that provides the same payment reporting functionality as the Python CLI tool, but accessible through any modern web browser.

## 🌐 Live Demo

**Access the app here:** [https://jtracey93.github.io/spond-payment-reporting/](https://jtracey93.github.io/spond-payment-reporting/)

## Features

- 📊 **View Payment Data**: See all unpaid payment requests from your Spond club
- 🔍 **Filter & Search**: Search by member name, payment name, or currency
- 📈 **Multiple Views**: 
  - Granular Details: See every individual unpaid payment
  - Summary by Member: See total amounts owed per member
- 💾 **Export Data**: Download your data as CSV, Excel, or PDF
- 🔒 **Secure**: All processing happens in your browser - no data is sent to any third-party server
- 📱 **Responsive**: Works on desktop, tablet, and mobile devices

## How to Use

### 1. Get Your Bearer Token

To use this app, you need a bearer token from Spond:

1. Log in to [club.spond.com](https://club.spond.com/) in your browser
2. Press **F12** to open Developer Tools
3. Click the **Network** tab
4. Refresh the page
5. Click on any request to `api.spond.com` in the list
6. Look for the **Authorization** header on the right side
7. Copy the long string after "Bearer " — that's your token

⚠️ **Important**: Keep your bearer token private! Don't share it with anyone.

### 2. Get Your Club ID

You can either:

- **Option A**: Click the "Fetch Clubs" button in the app (it will show you all clubs associated with your token, and you can select one)
- **Option B**: Enter your club ID directly if you already know it

### 3. Load Payment Data

1. Enter your bearer token
2. Enter or select your club ID
3. Click "Load Payment Data"
4. Wait for the data to load (this may take a few moments depending on how many payments you have)

### 4. Analyze Your Data

- Use the **Search** box to filter by any text (member name, payment name, etc.)
- Use the **Sort By** dropdown to reorder the data
- Switch between **Granular Details** and **Summary by Member** views
- Export your filtered view as CSV, Excel, or PDF

## Technical Details

- **Pure HTML/CSS/JavaScript**: No frameworks or build tools required
- **Client-side only**: All API calls are made directly from your browser to Spond's API
- **No data storage**: Your token and data are never stored on any server
- **GitHub Pages**: Hosted for free on GitHub Pages

## Privacy & Security

- This app does not store, log, or transmit your bearer token to any third-party service
- All API calls are made directly from your browser to Spond's official API
- Your payment data never leaves your browser except when making API calls to Spond
- The source code is open source and can be audited in this repository

## Browser Compatibility

This app works on all modern browsers:
- ✅ Chrome/Edge (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Opera

## Limitations

- Bearer tokens expire periodically - you'll need to get a new one when yours expires
- CORS restrictions may apply (if you encounter issues, try using a different browser)
- PDF export uses the browser's print functionality

## Troubleshooting

### "Failed to load data" error
- Check that your bearer token is correct and hasn't expired
- Verify your club ID is correct
- Try getting a fresh token from Spond

### CORS errors in console
- Some browsers may block cross-origin requests
- Try using Chrome/Edge with CORS extensions, or use the Python CLI tool instead

### Data not loading
- Ensure you have a stable internet connection
- Check that you have access to the club in Spond
- Verify the token hasn't expired (tokens typically last 30-60 days)

## Support

For issues, questions, or feature requests, please open an issue on [GitHub](https://github.com/jtracey93/spond-payment-reporting/issues).

## Related

For a command-line version of this tool with more features (automated login, browser integration), see the main [README](../README.md).
