# GitHub Pages Setup Guide

This file provides instructions for enabling GitHub Pages for the Spond Payment Reporting web app.

## Enable GitHub Pages

1. Go to your repository on GitHub: https://github.com/jtracey93/spond-payment-reporting

2. Click on **Settings** (top navigation bar)

3. In the left sidebar, click **Pages** (under "Code and automation")

4. Under "Build and deployment":
   - **Source**: Select "Deploy from a branch"
   - **Branch**: Select `main` (or the branch where this code is merged)
   - **Folder**: Select `/docs`
   - Click **Save**

5. Wait a few minutes for GitHub to build and deploy your site

6. Once deployed, your site will be available at:
   ```
   https://jtracey93.github.io/spond-payment-reporting/
   ```

## Verify Deployment

- GitHub will show a green checkmark and the URL at the top of the Pages settings when deployment is successful
- Click on the "Visit site" button to test the web app

## Custom Domain (Optional)

If you want to use a custom domain:

1. In the GitHub Pages settings, enter your custom domain in the "Custom domain" field
2. Add the appropriate DNS records with your domain provider
3. Enable "Enforce HTTPS" after DNS propagation

## Troubleshooting

### Site not loading
- Ensure the branch and folder are correctly selected
- Check that the `.nojekyll` file exists in the `/docs` folder
- Wait 5-10 minutes after enabling Pages for the first time

### 404 errors
- Verify all files are in the `/docs` folder
- Check that `index.html` exists
- Ensure the branch is up to date

### CORS errors when using the app
- This is expected - the app makes API calls to Spond's servers
- CORS policies are controlled by Spond, not by this application
- If you encounter CORS issues, you may need to use the Python CLI tool instead

## Files Required for GitHub Pages

The following files must be present in the `/docs` folder:

- `index.html` - Main application page
- `app.js` - Application JavaScript
- `styles.css` - Application styles
- `README.md` - Web app documentation
- `.nojekyll` - Tells GitHub Pages not to use Jekyll processing

All these files are already included in this repository.
