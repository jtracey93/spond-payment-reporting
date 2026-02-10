"""
Spond API client for fetching payment and member data.

Uses the spond library (https://pypi.org/project/spond/) for authentication,
with custom club API calls for endpoints not yet supported by the library.
Includes support for SMS-based two-factor authentication (2FA).
"""

import asyncio
import requests
import json
from typing import Callable, Dict, List, Optional, Tuple

from spond import AuthenticationError
from spond.club import SpondClub


class SpondAPIError(Exception):
    """Custom exception for Spond API errors"""
    pass


class _SpondClub2FA(SpondClub):
    """Extended SpondClub that supports SMS-based two-factor authentication."""

    def __init__(
        self,
        username: str,
        password: str,
        two_factor_callback: Optional[Callable[[str], str]] = None,
    ) -> None:
        super().__init__(username=username, password=password)
        self._two_factor_callback = two_factor_callback

    async def login(self) -> None:
        login_url = f"{self.api_url}login"
        data = {"email": self.username, "password": self.password}
        async with self.clientsession.post(login_url, json=data) as r:
            login_result = await r.json()
            self.token = login_result.get("loginToken")

            if self.token is not None:
                return

            # Check if 2FA is required
            temp_token = login_result.get("token")
            phone_number = login_result.get("phoneNumber")
            if temp_token and phone_number:
                await self._handle_2fa(temp_token, phone_number)
                return

            err_msg = f"Login failed. Response received: {login_result}"
            raise AuthenticationError(err_msg)

    async def _handle_2fa(self, temp_token: str, phone_number: str) -> None:
        """Handle SMS-based two-factor authentication."""
        if self._two_factor_callback is None:
            raise SpondAPIError(
                f"Two-factor authentication is required (SMS sent to "
                f"{phone_number}) but no 2FA handler is available. "
                f"Use --bearer-token as a fallback."
            )

        sms_code = self._two_factor_callback(phone_number)
        if not sms_code:
            raise SpondAPIError("SMS verification code cannot be empty")

        login_url = f"{self.api_url}login"
        data = {
            "email": self.username,
            "password": self.password,
            "code": sms_code,
            "token": temp_token,
        }
        async with self.clientsession.post(login_url, json=data) as r:
            verify_result = await r.json()
            self.token = verify_result.get("loginToken")
            if self.token is None:
                err_msg = (
                    f"Two-factor verification failed. "
                    f"Response received: {verify_result}"
                )
                raise AuthenticationError(err_msg)


def _default_2fa_callback(phone_number: str) -> str:
    """Default interactive callback that prompts the user for the SMS 2FA code."""
    print(f"\nTwo-factor authentication required!")
    print(f"An SMS verification code has been sent to: {phone_number}")
    return input("Enter SMS verification code: ").strip()


def _authenticate(
    username: str,
    password: str,
    two_factor_callback: Optional[Callable[[str], str]] = None,
) -> str:
    """
    Authenticate with Spond using the spond library and return a bearer token.
    Supports SMS-based two-factor authentication (2FA).

    Args:
        username (str): Spond account email address
        password (str): Spond account password
        two_factor_callback: Optional callback that receives a phone number
            and returns the SMS verification code. If None, an interactive
            prompt is used.

    Returns:
        str: Bearer token for API access

    Raises:
        SpondAPIError: If authentication fails
    """
    if two_factor_callback is None:
        two_factor_callback = _default_2fa_callback

    async def _login() -> str:
        client = _SpondClub2FA(
            username=username,
            password=password,
            two_factor_callback=two_factor_callback,
        )
        try:
            await client.login()
            token = client.token
            if not token:
                raise SpondAPIError("Authentication succeeded but no token was returned")
            return token
        except SpondAPIError:
            raise
        except AuthenticationError as e:
            raise SpondAPIError(f"Authentication failed: {e}")
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


def fetch_clubs(bearer_token: str) -> List[Dict]:
    """
    Fetch available clubs for the authenticated user.

    This calls the Spond club API without a club ID header to retrieve
    the list of clubs the user has access to.

    Args:
        bearer_token (str): Bearer token from authentication

    Returns:
        List[Dict]: List of club objects with 'id' and 'name' keys

    Raises:
        SpondAPIError: If the request fails
    """
    url = "https://api.spond.com/club/v1/clubs"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {bearer_token}",
        "content-type": "application/json",
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        raise SpondAPIError(f"Failed to fetch clubs: {e}")
    except Exception as e:
        raise SpondAPIError(f"Failed to fetch clubs: {e}")


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
    def from_credentials(
        cls,
        username: str,
        password: str,
        club_id: str,
        two_factor_callback: Optional[Callable[[str], str]] = None,
    ) -> "SpondAPI":
        """
        Create a SpondAPI client by authenticating with email and password
        using the spond library. Supports SMS-based 2FA.
        
        Args:
            username (str): Spond account email address
            password (str): Spond account password
            club_id (str): Club ID for the Spond club
            two_factor_callback: Optional callback that receives a phone number
                and returns the SMS verification code. If None, an interactive
                prompt is used when 2FA is required.
            
        Returns:
            SpondAPI: An authenticated API client instance
            
        Raises:
            SpondAPIError: If authentication fails
        """
        token = _authenticate(username, password, two_factor_callback)
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
