"""
Configuration management for Spond reporting tool
"""

import os
import json
from typing import Optional, Dict, Any
from pathlib import Path
from .auth import SpondAuthenticator, SpondAPIError


class Config:
    """Configuration manager for Spond credentials and settings"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.spond-reporting'
        self.config_file = self.config_dir / 'config.json'
        self.config_dir.mkdir(exist_ok=True)
    
    def save_credentials(self, bearer_token: str, club_id: str, 
                        save_token: bool = False) -> None:
        """
        Save credentials to config file
        
        Args:
            bearer_token (str): Bearer token
            club_id (str): Club ID
            save_token (bool): Whether to save the bearer token (default: False for security)
        """
        config_data = {
            'club_id': club_id
        }
        
        if save_token:
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
            Dict[str, Optional[str]]: Dictionary with bearer_token and club_id
        """
        if not self.config_file.exists():
            return {'bearer_token': None, 'club_id': None}
        
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            return {
                'bearer_token': config_data.get('bearer_token'),
                'club_id': config_data.get('club_id')
            }
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config file: {e}")
            return {'bearer_token': None, 'club_id': None}
    
    def get_credentials_interactive(self, auto_mode: bool = False) -> tuple:
        """
        Get credentials interactively from user input
        
        Args:
            auto_mode (bool): Whether to use automated credential gathering
        
        Returns:
            tuple: (bearer_token, club_id)
        """
        if auto_mode:
            return self.get_credentials_automated()
        
        # Load existing config
        saved_creds = self.load_credentials()
        
        # Get bearer token
        if saved_creds['bearer_token']:
            use_saved = input(f"Use saved bearer token? (y/n) [y]: ").strip().lower()
            if use_saved in ('', 'y', 'yes'):
                bearer_token = saved_creds['bearer_token']
                print("Using saved bearer token")
            else:
                bearer_token = input('Enter your Spond Bearer Token: ').strip()
        else:
            bearer_token = input('Enter your Spond Bearer Token: ').strip()
        
        # Get club ID
        if saved_creds['club_id']:
            club_id_prompt = f"Enter your Spond Club ID [{saved_creds['club_id']}]: "
            club_id = input(club_id_prompt).strip()
            if not club_id:
                club_id = saved_creds['club_id']
                print(f"Using saved club ID: {club_id}")
        else:
            club_id = input('Enter your Spond Club ID: ').strip()
        
        # Ask if user wants to save credentials
        if not saved_creds['club_id'] or club_id != saved_creds['club_id']:
            save_config = input("Save club ID for future use? (y/n) [y]: ").strip().lower()
            if save_config in ('', 'y', 'yes'):
                save_token = input("Save bearer token too? (NOT recommended for security) (y/n) [n]: ").strip().lower()
                self.save_credentials(bearer_token, club_id, save_token in ('y', 'yes'))
        
        return bearer_token, club_id
    
    def get_credentials_automated(self) -> tuple:
        """
        Get credentials using automated authentication
        
        Returns:
            tuple: (bearer_token, club_id)
        """
        authenticator = SpondAuthenticator()
        try:
            bearer_token, club_id = authenticator.get_credentials_automated()
            
            # Ask if user wants to save the credentials
            print()
            save_config = input("Save club ID for future use? (y/n) [y]: ").strip().lower()
            if save_config in ('', 'y', 'yes'):
                save_token = input("Save bearer token too? (NOT recommended for security) (y/n) [n]: ").strip().lower()
                self.save_credentials(bearer_token, club_id, save_token in ('y', 'yes'))
            
            return bearer_token, club_id
            
        except SpondAPIError as e:
            print(f"❌ Automated authentication failed: {e}")
            print("📝 You can still use manual mode by extracting credentials from browser developer tools.")
            print("   See README.md for detailed instructions.")
            raise
