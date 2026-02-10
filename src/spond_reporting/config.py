"""
Configuration management for Spond reporting tool
"""

import os
import json
import getpass
from typing import Optional, Dict, Any
from pathlib import Path


class Config:
    """Configuration manager for Spond credentials and settings"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.spond-reporting'
        self.config_file = self.config_dir / 'config.json'
        self.config_dir.mkdir(exist_ok=True)
    
    def save_credentials(self, club_id: str, email: Optional[str] = None,
                        bearer_token: Optional[str] = None,
                        save_token: bool = False) -> None:
        """
        Save credentials to config file
        
        Args:
            club_id (str): Club ID
            email (str, optional): Spond account email
            bearer_token (str, optional): Bearer token (legacy)
            save_token (bool): Whether to save the bearer token (default: False for security)
        """
        config_data = {
            'club_id': club_id
        }
        
        if email:
            config_data['email'] = email
        
        if save_token and bearer_token:
            config_data['bearer_token'] = bearer_token
            print("Warning: Bearer token saved to config file. Keep this file secure!")
        
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Set restrictive permissions on config file
        os.chmod(self.config_file, 0o600)
        
        print(f"Configuration saved to: {self.config_file}")
    
    def load_credentials(self) -> Dict[str, Optional[str]]:
        """
        Load credentials from config file
        
        Returns:
            Dict[str, Optional[str]]: Dictionary with email, bearer_token, and club_id
        """
        if not self.config_file.exists():
            return {'email': None, 'bearer_token': None, 'club_id': None}
        
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            return {
                'email': config_data.get('email'),
                'bearer_token': config_data.get('bearer_token'),
                'club_id': config_data.get('club_id')
            }
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config file: {e}")
            return {'email': None, 'bearer_token': None, 'club_id': None}
    
    def get_credentials_interactive(self) -> tuple:
        """
        Get credentials interactively from user input.
        
        Supports two authentication modes:
        1. Email/password login via the spond library (recommended)
        2. Legacy bearer token authentication
        
        Returns:
            tuple: (email, password, club_id) for spond auth, or
                   (None, bearer_token, club_id) for legacy auth
        """
        # Load existing config
        saved_creds = self.load_credentials()
        
        # Determine authentication method
        if saved_creds.get('bearer_token'):
            print("Legacy bearer token found in config.")
            use_legacy = input("Continue with bearer token? Enter 'n' to switch to email/password login [y]: ").strip().lower()
            if use_legacy in ('', 'y', 'yes'):
                bearer_token = saved_creds['bearer_token']
                # Get club ID
                club_id = self._get_club_id_interactive(saved_creds)
                return None, bearer_token, club_id
        
        # Email/password authentication (recommended)
        if saved_creds.get('email'):
            email_prompt = f"Enter your Spond email [{saved_creds['email']}]: "
            email = input(email_prompt).strip()
            if not email:
                email = saved_creds['email']
                print(f"Using saved email: {email}")
        else:
            email = input('Enter your Spond email: ').strip()
        
        password = getpass.getpass('Enter your Spond password: ')
        
        # Get club ID
        club_id = self._get_club_id_interactive(saved_creds)
        
        # Ask if user wants to save email and club ID
        if not saved_creds.get('club_id') or club_id != saved_creds.get('club_id') or email != saved_creds.get('email'):
            save_config = input("Save email and club ID for future use? (y/n) [y]: ").strip().lower()
            if save_config in ('', 'y', 'yes'):
                self.save_credentials(club_id=club_id, email=email)
        
        return email, password, club_id
    
    def _get_club_id_interactive(self, saved_creds: Dict) -> str:
        """
        Get club ID interactively
        
        Args:
            saved_creds (Dict): Previously saved credentials
            
        Returns:
            str: Club ID
        """
        if saved_creds.get('club_id'):
            club_id_prompt = f"Enter your Spond Club ID [{saved_creds['club_id']}]: "
            club_id = input(club_id_prompt).strip()
            if not club_id:
                club_id = saved_creds['club_id']
                print(f"Using saved club ID: {club_id}")
        else:
            club_id = input('Enter your Spond Club ID: ').strip()
        
        return club_id
