"""
Tests for the MCP Server functionality
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
import asyncio

from spond_reporting.mcp_server import SpondMCPServer, MCPTool


class TestSpondMCPServer:
    """Tests for Spond MCP Server"""
    
    def test_mcp_tools_definition(self):
        """Test that MCP tools are properly defined"""
        server = SpondMCPServer()
        
        assert len(server.tools) == 4
        tool_names = [tool.name for tool in server.tools]
        
        expected_tools = [
            "get_member_payment_summary",
            "get_all_outstanding_payments", 
            "get_payment_statistics",
            "search_members"
        ]
        
        for tool_name in expected_tools:
            assert tool_name in tool_names
        
        # Check that each tool has required fields
        for tool in server.tools:
            assert isinstance(tool, MCPTool)
            assert tool.name
            assert tool.description
            assert tool.parameters
            assert "type" in tool.parameters
            assert tool.parameters["type"] == "object"
    
    @pytest.mark.asyncio
    async def test_initialize_api_with_credentials(self):
        """Test API initialization with provided credentials"""
        server = SpondMCPServer()
        
        with patch('spond_reporting.mcp_server.SpondAPI') as mock_api:
            result = await server.initialize_api("test_token", "test_club_id")
            
            assert result is True
            assert server.api is not None
            mock_api.assert_called_once_with("test_token", "test_club_id")
    
    @pytest.mark.asyncio
    async def test_initialize_api_from_config(self):
        """Test API initialization from config"""
        server = SpondMCPServer()
        
        with patch.object(server.config, 'load_credentials') as mock_load:
            mock_load.return_value = {
                'bearer_token': 'config_token',
                'club_id': 'config_club_id'
            }
            
            with patch('spond_reporting.mcp_server.SpondAPI') as mock_api:
                result = await server.initialize_api()
                
                assert result is True
                assert server.api is not None
                mock_api.assert_called_once_with("config_token", "config_club_id")
    
    @pytest.mark.asyncio
    async def test_initialize_api_missing_credentials(self):
        """Test API initialization with missing credentials"""
        server = SpondMCPServer()
        
        with patch.object(server.config, 'load_credentials') as mock_load:
            mock_load.return_value = {}
            
            result = await server.initialize_api()
            assert result is False
            assert server.api is None
    
    @pytest.mark.asyncio
    async def test_get_member_payment_summary_no_api(self):
        """Test member payment summary without API initialization"""
        server = SpondMCPServer()
        
        result = await server.get_member_payment_summary("John Smith")
        
        assert "error" in result
        assert "API not initialized" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_member_payment_summary_member_not_found(self):
        """Test member payment summary with member not found"""
        server = SpondMCPServer()
        server.api = Mock()
        
        # Mock API responses
        server.api.get_members.return_value = ([], {"123": "Jane Doe", "456": "Bob Wilson"})
        server.api.get_payments.return_value = []
        
        result = await server.get_member_payment_summary("John Smith")
        
        assert "error" in result
        assert "No members found matching" in result["error"]
        assert "available_members" in result
    
    @pytest.mark.asyncio
    async def test_get_member_payment_summary_multiple_matches(self):
        """Test member payment summary with multiple matches"""
        server = SpondMCPServer()
        server.api = Mock()
        
        # Mock API responses
        server.api.get_members.return_value = ([], {
            "123": "John Smith", 
            "456": "John Wilson",
            "789": "Johnny Smith"
        })
        server.api.get_payments.return_value = []
        
        result = await server.get_member_payment_summary("John")
        
        assert "error" in result
        assert "Multiple members found" in result["error"]
        assert "matching_members" in result
        assert len(result["matching_members"]) == 3
    
    @pytest.mark.asyncio
    async def test_get_member_payment_summary_success(self):
        """Test successful member payment summary"""
        server = SpondMCPServer()
        server.api = Mock()
        
        # Mock API responses
        server.api.get_members.return_value = ([], {"123": "John Smith"})
        server.api.get_payments.return_value = []
        
        # Mock report generator
        server.report_generator.process_payment_data = Mock(return_value=(
            [
                {
                    'Member ID': '123',
                    'Member Name': 'John Smith',
                    'Payment Title': 'Match Fee 2025',
                    'Amount': 25.0,
                    'Due Date': '2025-01-15',
                    'Description': 'Home vs Away Team'
                }
            ],
            {'total_payments_processed': 1}
        ))
        
        result = await server.get_member_payment_summary("John Smith")
        
        assert "error" not in result
        assert result["member_name"] == "John Smith"
        assert result["total_owed"] == 25.0
        assert result["outstanding_payments_count"] == 1
        assert "payment_types" in result
        assert "Match Fee 2025" in result["payment_types"]
    
    @pytest.mark.asyncio
    async def test_get_member_payment_summary_no_payments(self):
        """Test member payment summary with no outstanding payments"""
        server = SpondMCPServer()
        server.api = Mock()
        
        # Mock API responses
        server.api.get_members.return_value = ([], {"123": "John Smith"})
        server.api.get_payments.return_value = []
        
        # Mock report generator
        server.report_generator.process_payment_data = Mock(return_value=([], {}))
        
        result = await server.get_member_payment_summary("John Smith")
        
        assert "error" not in result
        assert result["member_name"] == "John Smith"
        assert result["total_owed"] == 0
        assert result["outstanding_payments"] == []
        assert "no outstanding payments" in result["message"]
    
    @pytest.mark.asyncio
    async def test_get_all_outstanding_payments_no_api(self):
        """Test get all outstanding payments without API"""
        server = SpondMCPServer()
        
        result = await server.get_all_outstanding_payments()
        
        assert "error" in result
        assert "API not initialized" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_all_outstanding_payments_success(self):
        """Test successful get all outstanding payments"""
        server = SpondMCPServer()
        server.api = Mock()
        
        # Mock API responses
        server.api.get_members.return_value = ([], {"123": "John Smith"})
        server.api.get_payments.return_value = []
        
        # Mock report generator
        server.report_generator.process_payment_data = Mock(return_value=(
            [
                {
                    'Member Name': 'John Smith',
                    'Payment Title': 'Match Fee 2025',
                    'Amount': 25.0,
                    'Due Date': '2025-01-15',
                    'Description': 'Home vs Away Team'
                }
            ],
            {'total_payments_processed': 1}
        ))
        
        result = await server.get_all_outstanding_payments()
        
        assert "error" not in result
        assert "outstanding_payments" in result
        assert len(result["outstanding_payments"]) == 1
        assert result["total_count"] == 1
        assert result["truncated"] is False
        assert "statistics" in result
    
    @pytest.mark.asyncio
    async def test_get_all_outstanding_payments_with_filter(self):
        """Test get all outstanding payments with title filter"""
        server = SpondMCPServer()
        server.api = Mock()
        
        # Mock API responses
        server.api.get_members.return_value = ([], {"123": "John Smith"})
        server.api.get_payments.return_value = []
        
        # Mock report generator
        server.report_generator.process_payment_data = Mock(return_value=(
            [
                {
                    'Member Name': 'John Smith',
                    'Payment Title': 'Match Fee 2025',
                    'Amount': 25.0,
                    'Due Date': '2025-01-15',
                    'Description': 'Home vs Away Team'
                },
                {
                    'Member Name': 'Jane Doe',
                    'Payment Title': 'Membership 2025',
                    'Amount': 100.0,
                    'Due Date': '2025-01-01',
                    'Description': 'Annual membership'
                }
            ],
            {'total_payments_processed': 2}
        ))
        
        result = await server.get_all_outstanding_payments(title_filter="Match Fee")
        
        assert "error" not in result
        assert "outstanding_payments" in result
        assert len(result["outstanding_payments"]) == 1
        assert result["outstanding_payments"][0]["payment_title"] == "Match Fee 2025"
        assert result["filter_applied"] == "Match Fee"
    
    @pytest.mark.asyncio
    async def test_search_members_success(self):
        """Test successful member search"""
        server = SpondMCPServer()
        server.api = Mock()
        
        # Mock API responses
        server.api.get_members.return_value = ([], {
            "123": "John Smith",
            "456": "Jane Smith", 
            "789": "Bob Wilson"
        })
        
        result = await server.search_members("Smith")
        
        assert "error" not in result
        assert result["query"] == "Smith"
        assert result["total_matches"] == 2
        assert len(result["matching_members"]) == 2
        
        member_names = [m["name"] for m in result["matching_members"]]
        assert "John Smith" in member_names
        assert "Jane Smith" in member_names
    
    @pytest.mark.asyncio
    async def test_handle_tool_call_unknown_tool(self):
        """Test handling unknown tool calls"""
        server = SpondMCPServer()
        
        result = await server.handle_tool_call("unknown_tool", {})
        
        assert "error" in result
        assert "Unknown tool" in result["error"]
    
    @pytest.mark.asyncio
    async def test_handle_mcp_request_initialize(self):
        """Test MCP initialize request"""
        server = SpondMCPServer()
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        
        response = await server.handle_mcp_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        assert response["result"]["protocolVersion"] == "2024-11-05"
        assert "capabilities" in response["result"]
        assert "serverInfo" in response["result"]
    
    @pytest.mark.asyncio
    async def test_handle_mcp_request_tools_list(self):
        """Test MCP tools/list request"""
        server = SpondMCPServer()
        
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = await server.handle_mcp_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 2
        assert "result" in response
        assert "tools" in response["result"]
        assert len(response["result"]["tools"]) == 4
        
        # Check tool structure
        tool = response["result"]["tools"][0]
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool
    
    @pytest.mark.asyncio
    async def test_handle_mcp_request_unknown_method(self):
        """Test MCP request with unknown method"""
        server = SpondMCPServer()
        
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "unknown/method",
            "params": {}
        }
        
        response = await server.handle_mcp_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 3
        assert "error" in response
        assert response["error"]["code"] == -32601
        assert "Method not found" in response["error"]["message"]


if __name__ == '__main__':
    pytest.main([__file__])