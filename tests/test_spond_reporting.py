"""
Tests for the Spond Payment Reporting Tool
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from spond_reporting.config import Config
from spond_reporting.api import SpondAPI, SpondAPIError, _authenticate, _SpondClub2FA, fetch_clubs
from spond_reporting.report import PaymentReportGenerator
from spond import AuthenticationError


class TestConfig:
    """Tests for configuration management"""
    
    def test_config_directory_creation(self):
        """Test that config directory is created"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('spond_reporting.config.Path.home', return_value=Path(temp_dir)):
                config = Config()
                assert config.config_dir.exists()
    
    def test_save_and_load_credentials(self):
        """Test saving and loading credentials with email"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('spond_reporting.config.Path.home', return_value=Path(temp_dir)):
                config = Config()
                
                # Save credentials with email
                config.save_credentials(club_id="test_club_id", email="test@example.com")
                
                # Load credentials
                creds = config.load_credentials()
                assert creds['email'] == "test@example.com"
                assert creds['club_id'] == "test_club_id"
                assert creds['bearer_token'] is None
    
    def test_save_and_load_legacy_credentials(self):
        """Test saving and loading legacy bearer token credentials"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('spond_reporting.config.Path.home', return_value=Path(temp_dir)):
                config = Config()
                
                # Save credentials with bearer token
                config.save_credentials(
                    club_id="test_club_id",
                    bearer_token="test_token",
                    save_token=True
                )
                
                # Load credentials
                creds = config.load_credentials()
                assert creds['bearer_token'] == "test_token"
                assert creds['club_id'] == "test_club_id"


class TestSpondAPI:
    """Tests for Spond API client"""
    
    def test_api_initialization(self):
        """Test API client initialization"""
        api = SpondAPI("test_token", "test_club_id")
        assert api.bearer_token == "test_token"
        assert api.club_id == "test_club_id"
        assert "Bearer test_token" in api.headers["authorization"]
        assert api.headers["x-spond-clubid"] == "test_club_id"
    
    def test_api_from_credentials(self):
        """Test API client creation via email/password authentication"""
        with patch('spond_reporting.api._authenticate', return_value="mocked_token") as mock_auth:
            api = SpondAPI.from_credentials("user@example.com", "password123", "club_id")
            mock_auth.assert_called_once_with("user@example.com", "password123", None)
            assert api.bearer_token == "mocked_token"
            assert api.club_id == "club_id"
            assert "Bearer mocked_token" in api.headers["authorization"]
    
    def test_api_from_credentials_with_2fa_callback(self):
        """Test API client creation with a custom 2FA callback"""
        callback = Mock(return_value="123456")
        with patch('spond_reporting.api._authenticate', return_value="mocked_token") as mock_auth:
            api = SpondAPI.from_credentials(
                "user@example.com", "password123", "club_id",
                two_factor_callback=callback
            )
            mock_auth.assert_called_once_with("user@example.com", "password123", callback)
    
    def test_authenticate_success(self):
        """Test successful authentication via spond library"""
        mock_client = MagicMock()
        mock_client.token = "test_token_123"
        mock_client.login = AsyncMock()
        mock_client.clientsession = MagicMock()
        mock_client.clientsession.close = AsyncMock()
        
        with patch('spond_reporting.api._SpondClub2FA', return_value=mock_client):
            token = _authenticate("user@example.com", "password123")
            assert token == "test_token_123"
    
    def test_authenticate_failure(self):
        """Test authentication failure raises SpondAPIError"""
        mock_client = MagicMock()
        mock_client.login = AsyncMock(side_effect=Exception("Invalid credentials"))
        mock_client.clientsession = MagicMock()
        mock_client.clientsession.close = AsyncMock()
        
        with patch('spond_reporting.api._SpondClub2FA', return_value=mock_client):
            with pytest.raises(SpondAPIError, match="Authentication failed"):
                _authenticate("user@example.com", "wrong_password")
    
    def test_authenticate_with_2fa_success(self):
        """Test successful authentication with 2FA"""
        callback = Mock(return_value="123456")
        
        # Simulate: login sets token after 2FA flow
        mock_client = MagicMock()
        mock_client.token = "authenticated_token"
        mock_client.login = AsyncMock()
        mock_client.clientsession = MagicMock()
        mock_client.clientsession.close = AsyncMock()
        
        with patch('spond_reporting.api._SpondClub2FA', return_value=mock_client):
            token = _authenticate("user@example.com", "password123", callback)
            assert token == "authenticated_token"
    
    def test_authenticate_passes_2fa_callback(self):
        """Test that 2FA callback is passed to _SpondClub2FA"""
        callback = Mock(return_value="654321")
        
        mock_client = MagicMock()
        mock_client.token = "token_2fa"
        mock_client.login = AsyncMock()
        mock_client.clientsession = MagicMock()
        mock_client.clientsession.close = AsyncMock()
        
        with patch('spond_reporting.api._SpondClub2FA', return_value=mock_client) as mock_cls:
            _authenticate("user@example.com", "password123", callback)
            mock_cls.assert_called_once_with(
                username="user@example.com",
                password="password123",
                two_factor_callback=callback,
            )


class TestSpondClub2FA:
    """Tests for the 2FA-aware SpondClub subclass"""

    @staticmethod
    def _make_client(callback=None):
        """Create a _SpondClub2FA with mocked aiohttp to avoid event loop requirement."""
        with patch('spond.base.aiohttp.CookieJar'), \
             patch('spond.base.aiohttp.ClientSession', return_value=MagicMock()):
            client = _SpondClub2FA("user@example.com", "pass123", callback)
        client.clientsession = MagicMock()
        return client

    def test_login_no_2fa(self):
        """Test login succeeds without 2FA when loginToken is returned"""
        client = self._make_client()
        
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={"loginToken": "direct_token"})
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)
        
        client.clientsession.post = MagicMock(return_value=mock_response)
        
        asyncio.run(client.login())
        assert client.token == "direct_token"

    def test_login_with_2fa(self):
        """Test login triggers 2FA flow and completes successfully"""
        callback = Mock(return_value="123456")
        client = self._make_client(callback)
        
        # First response: 2FA required
        first_response = AsyncMock()
        first_response.json = AsyncMock(return_value={
            "token": "temp_token",
            "phoneNumber": "+47****89",
        })
        first_response.__aenter__ = AsyncMock(return_value=first_response)
        first_response.__aexit__ = AsyncMock(return_value=False)
        
        # Second response: verification success
        second_response = AsyncMock()
        second_response.json = AsyncMock(return_value={
            "loginToken": "final_token",
        })
        second_response.__aenter__ = AsyncMock(return_value=second_response)
        second_response.__aexit__ = AsyncMock(return_value=False)
        
        client.clientsession.post = MagicMock(
            side_effect=[first_response, second_response]
        )
        
        asyncio.run(client.login())
        assert client.token == "final_token"
        callback.assert_called_once_with("+47****89")

    def test_login_2fa_no_callback_raises(self):
        """Test that 2FA without a callback raises an error"""
        client = self._make_client(callback=None)
        
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={
            "token": "temp_token",
            "phoneNumber": "+47****89",
        })
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)
        
        client.clientsession.post = MagicMock(return_value=mock_response)
        
        with pytest.raises(SpondAPIError, match="Two-factor authentication is required"):
            asyncio.run(client.login())

    def test_login_2fa_empty_code_raises(self):
        """Test that an empty 2FA code raises an error"""
        callback = Mock(return_value="")
        client = self._make_client(callback)
        
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={
            "token": "temp_token",
            "phoneNumber": "+47****89",
        })
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)
        
        client.clientsession.post = MagicMock(return_value=mock_response)
        
        with pytest.raises(SpondAPIError, match="SMS verification code cannot be empty"):
            asyncio.run(client.login())

    def test_login_2fa_verification_failure(self):
        """Test that 2FA verification failure raises an error"""
        callback = Mock(return_value="wrong_code")
        client = self._make_client(callback)
        
        # First response: 2FA required
        first_response = AsyncMock()
        first_response.json = AsyncMock(return_value={
            "token": "temp_token",
            "phoneNumber": "+47****89",
        })
        first_response.__aenter__ = AsyncMock(return_value=first_response)
        first_response.__aexit__ = AsyncMock(return_value=False)
        
        # Second response: verification fails
        second_response = AsyncMock()
        second_response.json = AsyncMock(return_value={
            "message": "Invalid code",
        })
        second_response.__aenter__ = AsyncMock(return_value=second_response)
        second_response.__aexit__ = AsyncMock(return_value=False)
        
        client.clientsession.post = MagicMock(
            side_effect=[first_response, second_response]
        )
        
        with pytest.raises(AuthenticationError, match="Two-factor verification failed"):
            asyncio.run(client.login())


class TestPaymentReportGenerator:
    """Tests for report generation"""
    
    def test_process_empty_payments(self):
        """Test processing empty payment list"""
        generator = PaymentReportGenerator()
        mock_api = Mock()
        
        granular_rows, stats = generator.process_payment_data([], {}, mock_api)
        
        assert granular_rows == []
        assert stats['total_payments_processed'] == 0
        assert stats['payments_with_unpaid'] == 0
        assert stats['total_unpaid_items'] == 0
    
    def test_generate_excel_report_empty_data(self):
        """Test Excel generation with empty data"""
        generator = PaymentReportGenerator()
        
        result = generator.generate_excel_report([])
        assert result is None


class TestFetchClubs:
    """Tests for fetching available clubs"""

    def test_fetch_clubs_success(self):
        """Test successful fetching of clubs"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(return_value=[
            {"id": "club1", "name": "Test Club 1"},
            {"id": "club2", "name": "Test Club 2"},
        ])

        with patch('spond_reporting.api.requests.get', return_value=mock_response):
            clubs = fetch_clubs("test_token")
            assert len(clubs) == 2
            assert clubs[0]['id'] == "club1"
            assert clubs[1]['name'] == "Test Club 2"

    def test_fetch_clubs_http_error(self):
        """Test fetch clubs raises SpondAPIError on HTTP error"""
        mock_response = Mock()
        mock_response.raise_for_status = Mock(
            side_effect=Exception("401 Unauthorized")
        )

        with patch('spond_reporting.api.requests.get', return_value=mock_response):
            with pytest.raises(SpondAPIError, match="Failed to fetch clubs"):
                fetch_clubs("bad_token")


class TestSelectClubInteractive:
    """Tests for interactive club selection"""

    def test_select_single_club(self):
        """Test selecting from a single club"""
        clubs = [{"id": "club1", "name": "My Club"}]
        with patch('builtins.input', return_value="1"):
            result = Config.select_club_interactive(clubs)
            assert result == "club1"

    def test_select_second_club(self):
        """Test selecting the second club from a list"""
        clubs = [
            {"id": "club1", "name": "Club A"},
            {"id": "club2", "name": "Club B"},
            {"id": "club3", "name": "Club C"},
        ]
        with patch('builtins.input', return_value="2"):
            result = Config.select_club_interactive(clubs)
            assert result == "club2"

    def test_empty_clubs_raises(self):
        """Test that empty club list raises ValueError"""
        with pytest.raises(ValueError, match="No clubs found"):
            Config.select_club_interactive([])

    def test_invalid_then_valid_selection(self):
        """Test recovery from invalid input"""
        clubs = [
            {"id": "club1", "name": "Club A"},
            {"id": "club2", "name": "Club B"},
        ]
        with patch('builtins.input', side_effect=["abc", "0", "3", "1"]):
            result = Config.select_club_interactive(clubs)
            assert result == "club1"


if __name__ == '__main__':
    pytest.main([__file__])
