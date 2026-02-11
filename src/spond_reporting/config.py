"""
Configuration management for Spond reporting tool
"""

import os
import json
from typing import Optional, Dict
from pathlib import Path


class Config:
    """Configuration manager for Spond credentials and settings"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.spond-reporting'
        self.config_file = self.config_dir / 'config.json'
        self.config_dir.mkdir(exist_ok=True)
    
    def save_credentials(self, club_id: str,
                        bearer_token: Optional[str] = None,
                        save_token: bool = False) -> None:
        """
        Save credentials to config file
        
        Args:
            club_id (str): Club ID
            bearer_token (str, optional): Bearer token
            save_token (bool): Whether to save the bearer token
        """
        # Load existing config to preserve fields not being updated
        existing = {}
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    existing = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        if club_id:
            existing['club_id'] = club_id

        if save_token and bearer_token:
            existing['bearer_token'] = bearer_token
        
        with open(self.config_file, 'w') as f:
            json.dump(existing, f, indent=2)
        
        # Set restrictive permissions on config file (user-only access)
        try:
            import sys
            if sys.platform == "win32":
                import subprocess
                # On Windows, use icacls to restrict to current user only
                subprocess.run(
                    ["icacls", str(self.config_file), "/inheritance:r",
                     "/grant:r", f"{os.environ.get('USERNAME', '')}:(R,W)"],
                    capture_output=True, timeout=5,
                )
            else:
                os.chmod(self.config_file, 0o600)
        except Exception:
            pass  # Best-effort permission restriction
        
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

    @staticmethod
    def select_club_interactive(clubs: list) -> str:
        """
        Display available clubs and let the user select one.

        Args:
            clubs (list): List of club dicts with 'id' and 'name' keys

        Returns:
            str: Selected club ID

        Raises:
            ValueError: If no clubs are available or selection is invalid
        """
        if not clubs:
            raise ValueError("No clubs found for this account")

        if len(clubs) == 1:
            selected = clubs[0]
            print(f"\nUsing club: {selected.get('name', 'Unknown')}")
            return selected['id']

        print("\nAvailable clubs:")
        for i, club in enumerate(clubs, 1):
            name = club.get('name', 'Unknown')
            club_id = club.get('id', '')
            print(f"  {i}. {name} ({club_id})")

        while True:
            selection = input(f"\nSelect a club (1-{len(clubs)}): ").strip()
            try:
                index = int(selection)
                if 1 <= index <= len(clubs):
                    selected = clubs[index - 1]
                    print(f"Selected: {selected.get('name', 'Unknown')}")
                    return selected['id']
                else:
                    print(f"Please enter a number between 1 and {len(clubs)}")
            except ValueError:
                print(f"Please enter a valid number between 1 and {len(clubs)}")
