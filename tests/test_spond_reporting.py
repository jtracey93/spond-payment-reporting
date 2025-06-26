"""
Tests for the Spond Payment Reporting Tool
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from spond_reporting.config import Config
from spond_reporting.api import SpondAPI
from spond_reporting.report import PaymentReportGenerator
from spond_reporting.auth import SpondAuthenticator, SpondAPIError


class TestSpondAuthenticator:
    """Tests for automated authentication"""
    
    def test_authenticator_initialization(self):
        """Test authenticator initialization"""
        auth = SpondAuthenticator()
        assert auth.base_url == "https://api.spond.com"
        assert "authorization" not in auth.headers  # Should not have auth initially
        assert auth.headers["content-type"] == "application/json"
    
    @patch('spond_reporting.auth.getpass.getpass')
    @patch('builtins.input')
    @patch('spond_reporting.auth.requests.Session')
    def test_get_credentials_automated_single_club(self, mock_session_class, mock_input, mock_getpass):
        """Test automated credential gathering with single club"""
        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_input.side_effect = [
            'test@example.com',  # email
        ]
        mock_getpass.return_value = 'test_password'
        
        # Mock successful login response
        login_response = Mock()
        login_response.status_code = 200
        login_response.json.return_value = {'token': 'test_bearer_token'}
        
        # Mock profile response (first try)
        profile_response = Mock()
        profile_response.status_code = 200
        profile_response.json.return_value = {'clubs': [{'id': 'test_club_id', 'name': 'Test Club'}]}
        
        # Configure session to return different responses for different URLs
        def mock_request_side_effect(url, **kwargs):
            if 'auth/login' in url:
                return login_response
            elif 'user/profile' in url:
                return profile_response
            else:
                return Mock(status_code=404)
        
        mock_session.post.side_effect = mock_request_side_effect
        mock_session.get.side_effect = mock_request_side_effect
        
        auth = SpondAuthenticator()
        bearer_token, club_id = auth.get_credentials_automated()
        
        assert bearer_token == 'test_bearer_token'
        assert club_id == 'test_club_id'
    
    @patch('spond_reporting.auth.requests.Session')
    def test_authenticate_invalid_credentials(self, mock_session_class):
        """Test authentication with invalid credentials"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Mock 401 response
        login_response = Mock()
        login_response.status_code = 401
        mock_session.post.return_value = login_response
        
        auth = SpondAuthenticator()
        
        with pytest.raises(SpondAPIError, match="Invalid email or password"):
            auth.authenticate('invalid@example.com', 'wrong_password')


class TestConfig:
    """Tests for configuration management"""
    
    def test_config_directory_creation(self):
        """Test that config directory is created"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('spond_reporting.config.Path.home', return_value=Path(temp_dir)):
                config = Config()
                assert config.config_dir.exists()
    
    def test_save_and_load_credentials(self):
        """Test saving and loading credentials"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('spond_reporting.config.Path.home', return_value=Path(temp_dir)):
                config = Config()
                
                # Save credentials
                config.save_credentials("test_token", "test_club_id", save_token=True)
                
                # Load credentials
                creds = config.load_credentials()
    def test_get_credentials_interactive_manual_mode(self):
        """Test interactive credentials in manual mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('spond_reporting.config.Path.home', return_value=Path(temp_dir)):
                config = Config()
                
                with patch('builtins.input', side_effect=['test_token', 'test_club_id', 'y', 'n']):
                    bearer_token, club_id = config.get_credentials_interactive(auto_mode=False)
                    
                    assert bearer_token == 'test_token'
                    assert club_id == 'test_club_id'
    
    @patch('spond_reporting.config.SpondAuthenticator')
    def test_get_credentials_automated_mode(self, mock_auth_class):
        """Test automated credentials mode"""
        mock_auth = MagicMock()
        mock_auth_class.return_value = mock_auth
        mock_auth.get_credentials_automated.return_value = ('auto_token', 'auto_club_id')
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('spond_reporting.config.Path.home', return_value=Path(temp_dir)):
                config = Config()
                
                with patch('builtins.input', side_effect=['y', 'n']):  # save config responses
                    bearer_token, club_id = config.get_credentials_automated()
                    
                    assert bearer_token == 'auto_token'
                    assert club_id == 'auto_club_id'
                    mock_auth.get_credentials_automated.assert_called_once()


class TestSpondAPI:
    """Tests for Spond API client"""
    
    def test_api_initialization(self):
        """Test API client initialization"""
        api = SpondAPI("test_token", "test_club_id")
        assert api.bearer_token == "test_token"
        assert api.club_id == "test_club_id"
        assert "Bearer test_token" in api.headers["authorization"]
        assert api.headers["x-spond-clubid"] == "test_club_id"


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


if __name__ == '__main__':
    pytest.main([__file__])
