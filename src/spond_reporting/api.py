"""
Spond API client for fetching payment and member data.

Uses the spond library (https://pypi.org/project/spond/) for authentication,
with custom club API calls for endpoints not yet supported by the library.
"""

import asyncio
import requests
import json
from typing import Dict, List, Optional, Tuple

from spond.club import SpondClub


class SpondAPIError(Exception):
    """Custom exception for Spond API errors"""
    pass


def _authenticate(username: str, password: str) -> str:
    """
    Authenticate with Spond using the spond library and return a bearer token.

    Args:
        username (str): Spond account email address
        password (str): Spond account password

    Returns:
        str: Bearer token for API access

    Raises:
        SpondAPIError: If authentication fails
    """
    async def _login() -> str:
        client = SpondClub(username=username, password=password)
        try:
            await client.login()
            token = client.token
            if not token:
                raise SpondAPIError("Authentication succeeded but no token was returned")
            return token
        except Exception as e:
            raise SpondAPIError(f"Authentication failed: {e}")
        finally:
            await client.clientsession.close()

    try:
        return asyncio.run(_login())
    except SpondAPIError:
        raise
    except Exception as e:
        raise SpondAPIError(f"Authentication failed: {e}")


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
            "accept": "application/json",
            "authorization": f"Bearer {bearer_token}",
            "content-type": "application/json",
            "x-spond-clubid": club_id,
        }
    
    @classmethod
    def from_credentials(cls, username: str, password: str, club_id: str) -> "SpondAPI":
        """
        Create a SpondAPI client by authenticating with email and password
        using the spond library.
        
        Args:
            username (str): Spond account email address
            password (str): Spond account password
            club_id (str): Club ID for the Spond club
            
        Returns:
            SpondAPI: An authenticated API client instance
            
        Raises:
            SpondAPIError: If authentication fails
        """
        token = _authenticate(username, password)
        return cls(bearer_token=token, club_id=club_id)

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
        except SpondAPIError:
            raise
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
