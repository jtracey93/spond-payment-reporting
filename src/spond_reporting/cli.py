#!/usr/bin/env python3
"""
Command-line interface for Spond Payment Reporting Tool
"""

import argparse
import sys
from pathlib import Path

from .config import Config
from .api import SpondAPI, SpondAPIError, fetch_clubs
from .browser import get_token_from_browser
from .report import PaymentReportGenerator


def main():
    """Main entry point for the CLI application"""
    parser = argparse.ArgumentParser(
        description="Generate payment reports from Spond club management system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  spond-report                          # Interactive: browser login + club selection
  spond-report -o my_report.xlsx        # Specify output file
  spond-report --title-filter "2025"    # Filter for payments containing "2025"
  spond-report --title-filter "Match Fee" --title-filter "2025"  # AND filtering
  spond-report --bearer-token TOKEN --club-id ID  # Provide token directly
  spond-report --bearer-token TOKEN               # Provide token, select club
  spond-report --login                  # Force browser login (ignore saved token)
  spond-report --reset-config           # Reset saved configuration

For more information, visit: https://github.com/jtracey93/spond-payment-reporting
        """
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output Excel file path (default: spond_payment_report.xlsx)'
    )
    
    parser.add_argument(
        '--bearer-token',
        type=str,
        help='Spond Bearer Token for authentication'
    )
    
    parser.add_argument(
        '--club-id',
        type=str,
        help='Spond Club ID (if not provided, available clubs will be listed for selection)'
    )
    
    parser.add_argument(
        '--login',
        action='store_true',
        help='Force browser login (ignore any saved token)'
    )
    
    parser.add_argument(
        '--private',
        action='store_true',
        help='Use InPrivate/Incognito mode for browser login (use if Edge crashes)'
    )
    
    parser.add_argument(
        '--title-filter',
        type=str,
        action='append',
        help='Filter payments by title containing this string (case-insensitive). Can be used multiple times for AND filtering.'
    )
    
    parser.add_argument(
        '--reset-config',
        action='store_true',
        help='Reset saved configuration'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Handle config reset
    if args.reset_config:
        config = Config()
        if config.config_file.exists():
            config.config_file.unlink()
            print("Configuration reset successfully")
        else:
            print("No configuration file found")
        return 0
    
    try:
        config = Config()
        
        # --- Determine bearer token ---
        if args.bearer_token:
            token = args.bearer_token
        elif args.login:
            # Force fresh browser login
            token = get_token_from_browser(force_private=args.private)
            config.save_credentials(club_id="", bearer_token=token, save_token=True)
        else:
            # Try saved config first
            saved = config.load_credentials()
            token = saved.get('bearer_token')
            if token:
                # Verify the saved token still works
                print("Using saved bearer token...")
                try:
                    fetch_clubs(token)
                except SpondAPIError:
                    print("Saved token has expired. Opening browser to log in again...")
                    token = get_token_from_browser(force_private=args.private)
                    config.save_credentials(
                        club_id=saved.get('club_id', ''),
                        bearer_token=token,
                        save_token=True,
                    )
            else:
                print("Spond Payment Reporting Tool v1.0.0")
                print("=====================================")
                print()
                print("No saved token found. Opening browser to log in...")
                token = get_token_from_browser(force_private=args.private)

        # --- Determine club ID ---
        club_id = args.club_id
        if not club_id:
            saved = config.load_credentials()
            club_id = saved.get('club_id') or None

        if not club_id:
            print("Fetching available clubs...")
            clubs = fetch_clubs(token)
            club_id = Config.select_club_interactive(clubs)

        # Save token + club for next time
        config.save_credentials(club_id=club_id, bearer_token=token, save_token=True)

        api = SpondAPI(token, club_id)
        
        # Fetch data
        print("Fetching members...")
        members, member_map = api.get_members()
        print(f"Found {len(members)} members")
        
        print("Fetching payments...")
        payments = api.get_payments()
        print(f"Found {len(payments)} payments")
        
        # Generate report
        report_generator = PaymentReportGenerator()
        
        print("Processing payment data...")
        granular_rows, summary_stats = report_generator.process_payment_data(
            payments, member_map, api, title_filters=args.title_filter
        )
        
        # Generate Excel file
        output_path = args.output or 'spond_payment_report.xlsx'
        excel_file = report_generator.generate_excel_report(granular_rows, output_path)
        
        # Print summary
        report_generator.print_summary(granular_rows, summary_stats)
        
        if excel_file:
            print(f"\nExcel report exported to: {excel_file}")
            print(f"Report contains {len(granular_rows)} unpaid payment records")
        
        return 0
        
    except SpondAPIError as e:
        print(f"Spond API Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
