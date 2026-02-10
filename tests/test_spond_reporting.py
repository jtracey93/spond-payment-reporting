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
from spond_reporting.api import SpondAPI, SpondAPIError, _authenticate
from spond_reporting.report import PaymentReportGenerator


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
            mock_auth.assert_called_once_with("user@example.com", "password123")
            assert api.bearer_token == "mocked_token"
            assert api.club_id == "club_id"
            assert "Bearer mocked_token" in api.headers["authorization"]
    
    def test_authenticate_success(self):
        """Test successful authentication via spond library"""
        mock_client = MagicMock()
        mock_client.token = "test_token_123"
        mock_client.login = AsyncMock()
        mock_client.clientsession = MagicMock()
        mock_client.clientsession.close = AsyncMock()
        
        with patch('spond_reporting.api.SpondClub', return_value=mock_client):
            token = _authenticate("user@example.com", "password123")
            assert token == "test_token_123"
    
    def test_authenticate_failure(self):
        """Test authentication failure raises SpondAPIError"""
        mock_client = MagicMock()
        mock_client.login = AsyncMock(side_effect=Exception("Invalid credentials"))
        mock_client.clientsession = MagicMock()
        mock_client.clientsession.close = AsyncMock()
        
        with patch('spond_reporting.api.SpondClub', return_value=mock_client):
            with pytest.raises(SpondAPIError, match="Authentication failed"):
                _authenticate("user@example.com", "wrong_password")


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
