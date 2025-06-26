"""
Report generator for Spond payment data
"""

import pandas as pd
from typing import Dict, List, Optional
import os


class PaymentReportGenerator:
    """Generates Excel reports from Spond payment data"""
    
    def __init__(self):
        pass
    
    def process_payment_data(self, payments: List[Dict], member_map: Dict[str, str], 
                           api_client, title_filters: Optional[List[str]] = None) -> tuple:
        """
        Process payment data to extract unpaid amounts
        
        Args:
            payments (List[Dict]): List of payments
            member_map (Dict[str, str]): Mapping of member IDs to names
            api_client: Spond API client instance
            title_filters (Optional[List[str]]): Filter payments by title containing ALL these strings
            
        Returns:
            tuple: (granular_rows, summary_stats)
        """
        granular_rows = []
        total_payments_processed = 0
        payments_with_unpaid = 0
        filtered_payments = 0
        
        print(f"Processing {len(payments)} payments...")
        if title_filters:
            print(f"Filtering for payments containing ALL of: {title_filters}")
        
        for payment in payments:
            payment_id = payment.get('id')
            payment_name = payment.get('title', 'Unnamed Payment')
            
            # Apply title filters if specified - ALL filters must match
            if title_filters:
                payment_name_lower = payment_name.lower()
                if not all(filter_term.lower() in payment_name_lower for filter_term in title_filters):
                    filtered_payments += 1
                    continue
            
            try:
                details = api_client.get_payment_details(payment_id)
                recipients = details.get('recipients', [])
                
                total_payments_processed += 1
                unpaid_count = 0
                
                for recipient in recipients:
                    status = recipient.get('status', '')
                    # Filter at recipient level - only process unpaid recipients
                    # ANSWERED = paid, UNANSWERED = not paid
                    if status == 'UNANSWERED':
                        unpaid_count += 1
                        member_id = recipient.get('memberId')
                        name = member_map.get(member_id, f"Unknown ({member_id})")
                        
                        # Extract amount from the correct path: recipients[*].claims[0].products[0].price
                        amount_pence = 0
                        claims = recipient.get('claims', [])
                        if claims and len(claims) > 0:
                            products = claims[0].get('products', [])
                            if products and len(products) > 0:
                                amount_pence = products[0].get('price', 0)
                        
                        amount = amount_pence / 100.0  # Convert from pence to pounds
                        currency = recipient.get('currency', 'GBP')  # Default to GBP
                        
                        granular_rows.append({
                            'Member Name': name,
                            'Member ID': member_id,
                            'Payment Name': payment_name,
                            'Payment ID': payment_id,
                            'Amount Owed': amount,
                            'Currency': currency,
                            'Status': status
                        })
                
                if unpaid_count > 0:
                    payments_with_unpaid += 1
                    print(f"Payment '{payment_name}' has {unpaid_count} unpaid recipients")
                    
            except Exception as e:
                print(f"Warning: Failed to process payment '{payment_name}': {e}")
                continue
        
        summary_stats = {
            'total_payments_found': len(payments),
            'filtered_payments': filtered_payments,
            'total_payments_processed': total_payments_processed,
            'payments_with_unpaid': payments_with_unpaid,
            'total_unpaid_items': len(granular_rows),
            'title_filters': title_filters
        }
        
        return granular_rows, summary_stats
    
    def generate_excel_report(self, granular_rows: List[Dict], 
                            output_path: Optional[str] = None) -> str:
        """
        Generate Excel report from granular payment data
        
        Args:
            granular_rows (List[Dict]): List of unpaid payment records
            output_path (Optional[str]): Path for output file
            
        Returns:
            str: Path to generated Excel file
        """
        if output_path is None:
            output_path = 'spond_payment_report.xlsx'
        
        # Create DataFrame for granular details
        df_details = pd.DataFrame(granular_rows)
        
        if df_details.empty:
            print("No outstanding payments found.")
            return None
        
        # Aggregate by member
        summary = df_details.groupby(['Member Name', 'Member ID', 'Currency'], 
                                   as_index=False)['Amount Owed'].sum()
        summary = summary.sort_values(by='Amount Owed', ascending=False)
        
        # Export to Excel
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            summary.to_excel(writer, sheet_name='Summary', index=False)
            df_details.to_excel(writer, sheet_name='Granular Details', index=False)
        
        return output_path
    
    def print_summary(self, granular_rows: List[Dict], summary_stats: Dict):
        """
        Print summary statistics
        
        Args:
            granular_rows (List[Dict]): List of unpaid payment records
            summary_stats (Dict): Summary statistics
        """
        print(f"\n--- Payment Report Summary ---")
        print(f"Found {summary_stats['total_payments_found']} total payments")
        if summary_stats.get('title_filters'):
            print(f"Filtered out {summary_stats['filtered_payments']} payments not containing ALL of: {summary_stats['title_filters']}")
        print(f"Processed {summary_stats['total_payments_processed']} payments")
        print(f"{summary_stats['payments_with_unpaid']} payments have unpaid recipients")
        print(f"Total unpaid items found: {summary_stats['total_unpaid_items']}")
        
        if granular_rows:
            df_details = pd.DataFrame(granular_rows)
            summary = df_details.groupby(['Member Name', 'Member ID', 'Currency'], 
                                       as_index=False)['Amount Owed'].sum()
            summary = summary.sort_values(by='Amount Owed', ascending=False)
            
            print("\nTop owing members:")
            print(summary.head(10).to_string(index=False))
        else:
            print("No outstanding payments found.")
