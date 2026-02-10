#!/usr/bin/env python3
"""
Command-line interface for Spond Payment Reporting Tool
"""

import argparse
import sys
from pathlib import Path

from .config import Config
from .api import SpondAPI, SpondAPIError, _authenticate, fetch_clubs
from .report import PaymentReportGenerator


def main():
    """Main entry point for the CLI application"""
    parser = argparse.ArgumentParser(
        description="Generate payment reports from Spond club management system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  spond-report                          # Interactive mode with prompts
  spond-report -o my_report.xlsx        # Specify output file
  spond-report --title-filter "2025"    # Filter for payments containing "2025"
  spond-report --title-filter "Match Fee" --title-filter "2025"  # Filter for payments containing BOTH "Match Fee" AND "2025"
  spond-report --title-filter "Match Fee" --output matches.xlsx  # Filter match fees only
  spond-report --email user@example.com                          # Login and select club interactively
  spond-report --email user@example.com --club-id ID  # Provide email directly (will prompt for password)
  spond-report --bearer-token TOKEN --club-id ID  # Legacy: provide bearer token directly
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
        '--email',
        type=str,
        help='Spond account email address for authentication'
    )
    
    parser.add_argument(
        '--bearer-token',
        type=str,
        help='(Legacy) Spond Bearer Token for authentication'
    )
    
    parser.add_argument(
        '--club-id',
        type=str,
        help='Spond Club ID (if not provided, available clubs will be listed for selection)'
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
        # Initialize components
        config = Config()
        
        # Get credentials and create API client
        if args.bearer_token and args.club_id:
            # Legacy: bearer token provided directly
            if args.verbose:
                print("Using bearer token from command line arguments")
            api = SpondAPI(args.bearer_token, args.club_id)
        elif args.email and args.club_id:
            # Email provided via CLI - prompt for password
            import getpass
            password = getpass.getpass('Enter your Spond password: ')
            if args.verbose:
                print(f"Authenticating with Spond as {args.email}...")
            print("Logging in to Spond...")
            api = SpondAPI.from_credentials(args.email, password, args.club_id)
            print("Login successful!")
        elif args.email and not args.club_id:
            # Email provided but no club ID - authenticate then select club
            import getpass
            password = getpass.getpass('Enter your Spond password: ')
            if args.verbose:
                print(f"Authenticating with Spond as {args.email}...")
            print("Logging in to Spond...")
            token = _authenticate(args.email, password)
            print("Login successful!")
            print("Fetching available clubs...")
            clubs = fetch_clubs(token)
            club_id = Config.select_club_interactive(clubs)
            api = SpondAPI(token, club_id)
        else:
            print("Spond Payment Reporting Tool v1.0.0")
            print("=====================================")
            print()
            email, password_or_token, club_id = config.get_credentials_interactive()
            
            if email:
                # Email/password authentication via spond library
                if not password_or_token:
                    print("Error: Password is required")
                    return 1
                print("Logging in to Spond...")
                token = _authenticate(email, password_or_token)
                print("Login successful!")
                
                if not club_id:
                    # No club ID - fetch available clubs for interactive selection
                    print("Fetching available clubs...")
                    clubs = fetch_clubs(token)
                    club_id = Config.select_club_interactive(clubs)
                    # Offer to save the selected club ID
                    save_config = input("Save email and club ID for future use? (y/n) [y]: ").strip().lower()
                    if save_config in ('', 'y', 'yes'):
                        config.save_credentials(club_id=club_id, email=email)
                
                api = SpondAPI(token, club_id)
            else:
                # Legacy bearer token authentication
                if not password_or_token:
                    print("Error: Bearer token is required")
                    return 1
                if not club_id:
                    print("Error: Club ID is required for bearer token authentication")
                    return 1
                api = SpondAPI(password_or_token, club_id)
        
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
