# Spond Payment Reporting - Web App

This is a static web application that provides the same payment reporting functionality as the Python CLI tool, but accessible through any modern web browser.

## ⚠️ Important: CORS Limitation

**The web app may not work in all browsers due to CORS (Cross-Origin Resource Sharing) restrictions.** Spond's API doesn't allow direct browser-based requests from GitHub Pages.

### If the app hangs or fails to load data:

1. **Install a CORS browser extension** (recommended for web app):
   - Chrome/Edge: Search for "Allow CORS" or "CORS Unblock" in the extension store
   - Firefox: Search for "CORS Everywhere"
   - Enable the extension only when using this app, then disable it for security
   
2. **Use the Python CLI tool instead** (works reliably without CORS issues):
   - See [installation instructions](../README.md#option-2-install-the-command-line-tool)
   - No CORS restrictions, works everywhere

See [CORS Workarounds](#cors-workarounds) section below for more details.

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

**Note:** CORS restrictions may prevent the app from working without a browser extension. See [CORS Workarounds](#cors-workarounds) below.

## CORS Workarounds

**Why this is needed:** Browsers block requests to different domains (Spond's API) for security. This is called CORS (Cross-Origin Resource Sharing).

### Option 1: Browser Extension (Easiest for Web App)

Install a CORS extension to allow the web app to access Spond's API:

**For Chrome/Edge:**
1. Go to your browser's extension store
2. Search for "Allow CORS: Access-Control-Allow-Origin" or "CORS Unblock"
3. Install the extension
4. Click the extension icon to enable it
5. Reload this web app and try again
6. **Important:** Disable the extension when you're done for security

**For Firefox:**
1. Go to Firefox Add-ons
2. Search for "CORS Everywhere" or "Allow CORS"
3. Install the add-on
4. Enable it from the toolbar
5. Reload this web app
6. **Important:** Disable when not in use

**Security Note:** CORS extensions bypass browser security. Only enable them when using this app, and only install extensions from trusted sources.

### Option 2: Python CLI Tool (Recommended)

The Python command-line tool has **no CORS restrictions** and works reliably:
- See [installation instructions](../README.md#option-2-install-the-command-line-tool)
- Same features as the web app
- No browser extensions needed
- Works on all operating systems

### Option 3: Local Proxy Server (Advanced)

Run a local proxy server that forwards requests to Spond's API. This requires technical setup and is beyond the scope of this guide.

## Limitations

- Bearer tokens expire periodically - you'll need to get a new one when yours expires
- CORS restrictions require browser extensions or using the Python CLI tool
- PDF export uses the browser's print functionality

## Troubleshooting

### App hangs or "Failed to load data" error
- **Most common cause:** CORS restriction. Install a CORS browser extension (see above)
- Check that your bearer token is correct and hasn't expired
- Verify your club ID is correct
- Try the Python CLI tool instead (no CORS issues)

### CORS errors in console
- This is the expected behavior when Spond's API blocks browser requests
- Solution: Install a CORS browser extension or use the Python CLI tool
- Try using Chrome/Edge with CORS extensions, or use the Python CLI tool instead

### Data not loading
- Ensure you have a stable internet connection
- Check that you have access to the club in Spond
- Verify the token hasn't expired (tokens typically last 30-60 days)

## Support

For issues, questions, or feature requests, please open an issue on [GitHub](https://github.com/jtracey93/spond-payment-reporting/issues).

## Related

For a command-line version of this tool with more features (automated login, browser integration), see the main [README](../README.md).
