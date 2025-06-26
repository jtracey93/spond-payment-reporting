"""
Tests for the Spond Payment Reporting Tool
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

from spond_reporting.config import Config
from spond_reporting.api import SpondAPI
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
        """Test saving and loading credentials"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('spond_reporting.config.Path.home', return_value=Path(temp_dir)):
                config = Config()
                
                # Save credentials
                config.save_credentials("test_token", "test_club_id", save_token=True)
                
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
