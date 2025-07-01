# VS Code MCP Configuration for Spond Payment Reporting

Add this configuration to your VS Code settings.json to enable the Spond Payment Reporting MCP server:

```json
{
  "mcp.servers": {
    "spond-payment-reporting": {
      "command": "spond-mcp-server",
      "args": [],
      "transport": {
        "type": "stdio"
      }
    }
  }
}
```

## Prerequisites

1. **Install the package**: Make sure you have installed the spond-payment-reporting package:
   ```bash
   pip install -e .
   ```

2. **Configure credentials**: Set up your Spond credentials either by:
   - Running `spond-report` once interactively to save your Club ID
   - Setting environment variables:
     ```bash
     export SPOND_BEARER_TOKEN="your_token_here"
     export SPOND_CLUB_ID="your_club_id_here"
     ```

3. **Install VS Code MCP extension**: Install the Model Context Protocol extension for VS Code

## Available Tools

Once configured, you can ask the AI assistant in VS Code questions like:

- "How much does John Smith owe in match fees?"
- "Show me all outstanding 2025 payments"
- "What are the payment statistics for our club?"
- "Who owes money for T20 tournaments?"
- "Find members with 'wilson' in their name"

## Tool Details

### get_member_payment_summary
Get detailed payment information for a specific member including total owed and breakdown by payment type.

**Parameters:**
- `member_name` (required): Name of the member (case-insensitive partial match)

### get_all_outstanding_payments
Get list of all outstanding payments, optionally filtered by title.

**Parameters:**
- `title_filter` (optional): Filter for payment titles (e.g., "Match Fee", "2025")
- `limit` (optional): Maximum results to return (default: 50)

### get_payment_statistics
Get aggregated statistics about outstanding payments.

**Parameters:**
- `title_filter` (optional): Filter for payment titles

### search_members
Search for club members by name.

**Parameters:**
- `query` (required): Search term for member names

## Troubleshooting

If the MCP server doesn't work:

1. Check that the command is available:
   ```bash
   which spond-mcp-server
   ```

2. Test the server manually:
   ```bash
   spond-mcp-server
   ```

3. Check your credentials configuration:
   ```bash
   spond-report --help
   ```

4. Ensure you have the latest version of the VS Code MCP extension

## Security Notes

- Bearer tokens are sensitive credentials
- The MCP server will try to load credentials from your saved configuration
- You can also pass credentials as tool parameters (not recommended for security)
- Credentials are never logged or exposed in tool responses