#!/usr/bin/env python3
"""
Command-line interface for Spond Payment Reporting Tool
"""

import argparse
import sys

from .config import Config
from .api import SpondAPI, SpondAPIError
from .report import PaymentReportGenerator


def main():
    """Main entry point for the CLI application"""
    parser = argparse.ArgumentParser(
        description="Generate payment reports from Spond club management system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  spond-report                          # Interactive mode with prompts
  spond-report --auto-credentials       # Automated credential gathering (experimental)
  spond-report -o my_report.xlsx        # Specify output file
  spond-report --title-filter "2025"    # Filter for payments containing "2025"
  spond-report --title-filter "Match Fee" --title-filter "2025"  # Filter for payments containing BOTH
  spond-report --title-filter "Match Fee" --output matches.xlsx  # Filter match fees only
  spond-report --bearer-token TOKEN --club-id ID  # Provide credentials directly
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
        help='Spond Club ID'
    )
    
    parser.add_argument(
        '--auto-credentials',
        action='store_true',
        help='Use automated credential gathering (experimental, requires Spond login)'
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
        
        # Get credentials
        if args.bearer_token and args.club_id:
            bearer_token = args.bearer_token
            club_id = args.club_id
            if args.verbose:
                print("Using credentials from command line arguments")
        else:
            print("Spond Payment Reporting Tool v1.0.0")
            print("=====================================")
            print()
            
            if args.auto_credentials:
                print("🤖 Using automated credential gathering mode")
                print()
            
            bearer_token, club_id = config.get_credentials_interactive(auto_mode=args.auto_credentials)
        
        if not bearer_token or not club_id:
            print("Error: Bearer token and club ID are required")
            return 1
        
        # Initialize API client
        if args.verbose:
            print(f"Connecting to Spond API for club: {club_id}")
        
        api = SpondAPI(bearer_token, club_id)
        
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
