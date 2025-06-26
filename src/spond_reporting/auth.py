"""
Automated authentication module for Spond API
"""

import requests
import json
import getpass
from typing import Dict, List, Tuple
from .api import SpondAPIError


class SpondAuthenticator:
    """Handles automated authentication with Spond"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://api.spond.com"
        
        # Set up default headers to mimic browser requests
        self.headers = {
            "authority": "api.spond.com",
            "accept": "application/json",
            "accept-language": "en-GB,en;q=0.9,en-US;q=0.8",
            "api-level": "4.72.0",
            "cache-control": "no-cache",
            "origin": "https://club.spond.com",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://club.spond.com/",
            "sec-ch-ua": '"Not;A=Brand";v="99", "Microsoft Edge";v="139", '
                        '"Chromium";v="139"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0"
        }
    
    def authenticate(self, email: str, password: str) -> str:
        """
        Authenticate with Spond and get bearer token
        
        Args:
            email (str): User's email
            password (str): User's password
            
        Returns:
            str: Bearer token
            
        Raises:
            SpondAPIError: If authentication fails
        """
        # WARNING: This is reverse-engineered and may break if Spond changes
        print("⚠️  Warning: Automated authentication is experimental and "
              "unofficial.")
        print("⚠️  This feature may break if Spond changes their "
              "authentication system.")
        print("⚠️  Your password will not be stored, but use at your own "
              "risk.")
        print()
        
        login_data = {
            "email": email,
            "password": password
        }
        
        try:
            # Attempt login - NOTE: This endpoint is a guess and may not be correct
            # Real Spond login endpoints need to be discovered through browser dev tools
            response = self.session.post(
                f"{self.base_url}/auth/login",
                headers=self.headers,
                json=login_data
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                bearer_token = (auth_data.get('token') or 
                               auth_data.get('access_token') or 
                               auth_data.get('bearerToken'))
                
                if bearer_token:
                    return bearer_token
                else:
                    raise SpondAPIError("Authentication succeeded but no token "
                                        "found in response")
            elif response.status_code == 401:
                raise SpondAPIError("Invalid email or password")
            elif response.status_code == 404:
                raise SpondAPIError("Authentication endpoint not found - "
                                    "Spond may have changed their API")
            else:
                raise SpondAPIError(f"Authentication failed: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise SpondAPIError(f"Network error during authentication: {e}")
        except json.JSONDecodeError as e:
            raise SpondAPIError(f"Invalid response from authentication server: {e}")
    
    def get_user_clubs(self, bearer_token: str) -> List[Dict]:
        """
        Get list of clubs the user has access to
        
        Args:
            bearer_token (str): Bearer token from authentication
            
        Returns:
            List[Dict]: List of club information
            
        Raises:
            SpondAPIError: If fetching clubs fails
        """
        headers = self.headers.copy()
        headers["authorization"] = f"Bearer {bearer_token}"
        
        try:
            # Try to get user profile which may include clubs
            # NOTE: This endpoint is also a guess - real endpoints need discovery
            response = self.session.get(
                f"{self.base_url}/user/profile",
                headers=headers
            )
            
            if response.status_code == 200:
                profile_data = response.json()
                clubs = profile_data.get('clubs', [])
                
                if clubs:
                    return clubs
                
                # If no clubs in profile, try alternative endpoint
                response = self.session.get(
                    f"{self.base_url}/clubs",
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise SpondAPIError(f"Failed to fetch clubs: HTTP {response.status_code}")
            elif response.status_code == 404:
                raise SpondAPIError("Clubs endpoint not found - "
                                    "Spond may have changed their API")
            else:
                raise SpondAPIError(f"Failed to fetch user profile: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise SpondAPIError(f"Network error while fetching clubs: {e}")
        except json.JSONDecodeError as e:
            raise SpondAPIError(f"Invalid response when fetching clubs: {e}")
    
    def get_credentials_automated(self) -> Tuple[str, str]:
        """
        Get credentials through automated authentication
        
        Returns:
            Tuple[str, str]: (bearer_token, club_id)
        """
        print("🤖 Automated Credential Gathering")
        print("=" * 40)
        print()
        
        # Get user credentials
        email = input("Enter your Spond email: ").strip()
        if not email:
            raise SpondAPIError("Email is required")
        
        password = getpass.getpass("Enter your Spond password: ")
        if not password:
            raise SpondAPIError("Password is required")
        
        print("\n🔐 Authenticating with Spond...")
        
        try:
            # Authenticate and get bearer token
            bearer_token = self.authenticate(email, password)
            print("✅ Authentication successful!")
            
            # Get available clubs
            print("🏢 Fetching your clubs...")
            clubs = self.get_user_clubs(bearer_token)
            
            if not clubs:
                raise SpondAPIError("No clubs found for your account")
            
            # If only one club, use it automatically
            if len(clubs) == 1:
                club = clubs[0]
                club_id = club.get('id') or club.get('clubId')
                club_name = club.get('name') or club.get('clubName', 'Unknown Club')
                
                if not club_id:
                    raise SpondAPIError("Club ID not found in club data")
                
                print(f"✅ Using club: {club_name} (ID: {club_id})")
                return bearer_token, club_id
            
            # Multiple clubs - let user choose
            print("\nMultiple clubs found. Please select one:")
            for i, club in enumerate(clubs, 1):
                club_name = (club.get('name') or 
                            club.get('clubName', f'Club {i}'))
                print(f"  {i}. {club_name}")
            
            while True:
                try:
                    choice = input(f"\nSelect club (1-{len(clubs)}): ").strip()
                    club_index = int(choice) - 1
                    
                    if 0 <= club_index < len(clubs):
                        selected_club = clubs[club_index]
                        club_id = selected_club.get('id') or selected_club.get('clubId')
                        club_name = (selected_club.get('name') or 
                                    selected_club.get('clubName', 
                                                     'Selected Club'))
                        
                        if not club_id:
                            raise SpondAPIError("Club ID not found in selected club data")
                        
                        print(f"✅ Selected club: {club_name} (ID: {club_id})")
                        return bearer_token, club_id
                    else:
                        print("Invalid selection. Please try again.")
                        
                except ValueError:
                    print("Please enter a valid number.")
                    
        except SpondAPIError:
            # Re-raise SpondAPIError as-is
            raise
        except Exception as e:
            raise SpondAPIError(f"Unexpected error during automated "
                                f"authentication: {e}")
