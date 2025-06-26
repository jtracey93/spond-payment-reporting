"""
Spond API client for fetching payment and member data
"""

import requests
import json
from typing import Dict, List, Optional, Tuple


class SpondAPIError(Exception):
    """Custom exception for Spond API errors"""
    pass


class SpondAPI:
    """Client for interacting with Spond API"""
    
    def __init__(self, bearer_token: str, club_id: str):
        """
        Initialize Spond API client
        
        Args:
            bearer_token (str): Bearer token for authentication
            club_id (str): Club ID for the Spond club
        """
        self.bearer_token = bearer_token
        self.club_id = club_id
        self.session = requests.Session()
        self.base_url = "https://api.spond.com"
        
        # Set up default headers
        self.headers = {
            "authority": "api.spond.com",
            "accept": "application/json",
            "accept-language": "en-GB,en;q=0.9,en-US;q=0.8",
            "api-level": "4.72.0",
            "authorization": f"Bearer {bearer_token}",
            "cache-control": "no-cache",
            "origin": "https://club.spond.com",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://club.spond.com/",
            "sec-ch-ua": '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "x-spond-clubid": club_id,
            "x-spond-membershipauth": "undefined",
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0"
        }
    
    def _make_request(self, url: str, method: str = "GET") -> Dict:
        """
        Make an API request with error handling
        
        Args:
            url (str): The URL to request
            method (str): HTTP method (default: GET)
            
        Returns:
            Dict: JSON response data
            
        Raises:
            SpondAPIError: If the request fails
        """
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type:
                raise SpondAPIError(f"Expected JSON but got content-type: {content_type}")
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            raise SpondAPIError(f"HTTP Error: {e}. Response: {response.text}")
        except json.JSONDecodeError as e:
            raise SpondAPIError(f"JSON Decode Error: {e}. Response: {response.text}")
        except Exception as e:
            raise SpondAPIError(f"Unexpected error: {e}")
    
    def get_members(self) -> Tuple[List[Dict], Dict[str, str]]:
        """
        Fetch all club members
        
        Returns:
            Tuple[List[Dict], Dict[str, str]]: (members list, member_id -> name mapping)
        """
        url = f"{self.base_url}/club/v1/members?"
        members = self._make_request(url)
        
        # Build member ID to name mapping
        member_map = {}
        for member in members:
            member_id = member.get('id')
            name = member.get('name') or f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
            if member_id and name:
                member_map[member_id] = name
        
        return members, member_map
    
    def get_payments(self) -> List[Dict]:
        """
        Fetch all payments
        
        Returns:
            List[Dict]: List of payment objects
        """
        url = f"{self.base_url}/club/v1/payments/?"
        return self._make_request(url)
    
    def get_payment_details(self, payment_id: str) -> Dict:
        """
        Fetch detailed payment information
        
        Args:
            payment_id (str): Payment ID
            
        Returns:
            Dict: Detailed payment information
        """
        url = f"{self.base_url}/club/v1/payments/{payment_id}?includeSignupRequestRecipients=false"
        return self._make_request(url)
