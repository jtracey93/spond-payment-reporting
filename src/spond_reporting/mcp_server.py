#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Server for Spond Payment Reporting

This module implements an MCP server that exposes Spond payment functionality
to AI assistants and VS Code extensions.
"""

import json
import sys
import os
from typing import Dict, List, Any, Optional
import asyncio
from dataclasses import dataclass

from .api import SpondAPI, SpondAPIError
from .config import Config
from .report import PaymentReportGenerator


@dataclass
class MCPTool:
    """Represents an MCP tool/function"""
    name: str
    description: str
    parameters: Dict[str, Any]


class SpondMCPServer:
    """MCP Server for Spond Payment Reporting"""
    
    def __init__(self):
        self.config = Config()
        self.api = None
        self.report_generator = PaymentReportGenerator()
        self.tools = self._define_tools()
    
    def _define_tools(self) -> List[MCPTool]:
        """Define available MCP tools"""
        return [
            MCPTool(
                name="get_member_payment_summary",
                description="Get payment summary for a specific club member",
                parameters={
                    "type": "object",
                    "properties": {
                        "member_name": {
                            "type": "string",
                            "description": "Name of the member to look up (case-insensitive partial match)"
                        }
                    },
                    "required": ["member_name"]
                }
            ),
            MCPTool(
                name="get_all_outstanding_payments",
                description="Get all outstanding payments for the club",
                parameters={
                    "type": "object",
                    "properties": {
                        "title_filter": {
                            "type": "string",
                            "description": "Optional filter for payment titles (e.g., 'Match Fee', '2025')"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 50
                        }
                    }
                }
            ),
            MCPTool(
                name="get_payment_statistics",
                description="Get statistics about outstanding payments",
                parameters={
                    "type": "object",
                    "properties": {
                        "title_filter": {
                            "type": "string",
                            "description": "Optional filter for payment titles"
                        }
                    }
                }
            ),
            MCPTool(
                name="search_members",
                description="Search for club members by name",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for member names"
                        }
                    },
                    "required": ["query"]
                }
            )
        ]
    
    async def initialize_api(self, bearer_token: str = None, club_id: str = None) -> bool:
        """Initialize the Spond API connection"""
        try:
            # Try to load from config if not provided
            if not bearer_token or not club_id:
                creds = self.config.load_credentials()
                bearer_token = bearer_token or creds.get('bearer_token')
                club_id = club_id or creds.get('club_id')
            
            if not bearer_token or not club_id:
                return False
            
            self.api = SpondAPI(bearer_token, club_id)
            return True
            
        except Exception:
            return False
    
    async def get_member_payment_summary(self, member_name: str) -> Dict[str, Any]:
        """Get payment summary for a specific member"""
        if not self.api:
            return {"error": "API not initialized. Please provide bearer_token and club_id."}
        
        try:
            # Get members and payments
            members, member_map = self.api.get_members()
            payments = self.api.get_payments()
            
            # Find matching members (case-insensitive partial match)
            matching_members = []
            member_name_lower = member_name.lower()
            
            for member_id, name in member_map.items():
                if member_name_lower in name.lower():
                    matching_members.append((member_id, name))
            
            if not matching_members:
                return {
                    "error": f"No members found matching '{member_name}'",
                    "available_members": list(member_map.values())[:10]  # Show first 10 as examples
                }
            
            if len(matching_members) > 1:
                return {
                    "error": f"Multiple members found matching '{member_name}'. Please be more specific.",
                    "matching_members": [name for _, name in matching_members]
                }
            
            member_id, full_name = matching_members[0]
            
            # Process payments for this member
            granular_rows, stats = self.report_generator.process_payment_data(payments, member_map, self.api)
            
            # Filter for this specific member
            member_payments = [row for row in granular_rows if row.get('Member ID') == member_id]
            
            if not member_payments:
                return {
                    "member_name": full_name,
                    "total_owed": 0,
                    "outstanding_payments": [],
                    "message": f"{full_name} has no outstanding payments"
                }
            
            # Calculate totals
            total_owed = sum(float(payment.get('Amount', 0)) for payment in member_payments)
            
            # Group by payment type
            payment_types = {}
            for payment in member_payments:
                payment_type = payment.get('Payment Title', 'Unknown')
                if payment_type not in payment_types:
                    payment_types[payment_type] = {
                        'count': 0,
                        'total_amount': 0,
                        'payments': []
                    }
                payment_types[payment_type]['count'] += 1
                payment_types[payment_type]['total_amount'] += float(payment.get('Amount', 0))
                payment_types[payment_type]['payments'].append({
                    'title': payment.get('Payment Title'),
                    'amount': payment.get('Amount'),
                    'due_date': payment.get('Due Date'),
                    'description': payment.get('Description', '')
                })
            
            return {
                "member_name": full_name,
                "total_owed": round(total_owed, 2),
                "outstanding_payments_count": len(member_payments),
                "payment_types": payment_types
            }
            
        except SpondAPIError as e:
            return {"error": f"Spond API Error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    async def get_all_outstanding_payments(self, title_filter: str = None, limit: int = 50) -> Dict[str, Any]:
        """Get all outstanding payments"""
        if not self.api:
            return {"error": "API not initialized. Please provide bearer_token and club_id."}
        
        try:
            members, member_map = self.api.get_members()
            payments = self.api.get_payments()
            
            # Process payments
            granular_rows, stats = self.report_generator.process_payment_data(payments, member_map, self.api)
            
            # Apply title filter if provided
            if title_filter:
                title_filter_lower = title_filter.lower()
                granular_rows = [
                    row for row in granular_rows 
                    if title_filter_lower in row.get('Payment Title', '').lower()
                ]
            
            # Limit results
            if limit and len(granular_rows) > limit:
                granular_rows = granular_rows[:limit]
                truncated = True
            else:
                truncated = False
            
            # Format results
            formatted_payments = []
            for row in granular_rows:
                formatted_payments.append({
                    'member_name': row.get('Member Name'),
                    'payment_title': row.get('Payment Title'),
                    'amount': row.get('Amount'),
                    'due_date': row.get('Due Date'),
                    'description': row.get('Description', '')
                })
            
            return {
                "outstanding_payments": formatted_payments,
                "total_count": len(formatted_payments),
                "truncated": truncated,
                "filter_applied": title_filter,
                "statistics": stats
            }
            
        except SpondAPIError as e:
            return {"error": f"Spond API Error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    async def get_payment_statistics(self, title_filter: str = None) -> Dict[str, Any]:
        """Get payment statistics"""
        if not self.api:
            return {"error": "API not initialized. Please provide bearer_token and club_id."}
        
        try:
            members, member_map = self.api.get_members()
            payments = self.api.get_payments()
            
            # Process payments
            granular_rows, stats = self.report_generator.process_payment_data(payments, member_map, self.api)
            
            # Apply title filter if provided
            if title_filter:
                title_filter_lower = title_filter.lower()
                filtered_rows = [
                    row for row in granular_rows 
                    if title_filter_lower in row.get('Payment Title', '').lower()
                ]
            else:
                filtered_rows = granular_rows
            
            # Calculate statistics
            if not filtered_rows:
                return {
                    "total_outstanding_payments": 0,
                    "total_amount_owed": 0,
                    "unique_members_with_debt": 0,
                    "payment_types": {},
                    "filter_applied": title_filter
                }
            
            total_amount = sum(float(row.get('Amount', 0)) for row in filtered_rows)
            unique_members = len(set(row.get('Member ID') for row in filtered_rows))
            
            # Group by payment type
            payment_types = {}
            for row in filtered_rows:
                payment_type = row.get('Payment Title', 'Unknown')
                if payment_type not in payment_types:
                    payment_types[payment_type] = {
                        'count': 0,
                        'total_amount': 0
                    }
                payment_types[payment_type]['count'] += 1
                payment_types[payment_type]['total_amount'] += float(row.get('Amount', 0))
            
            # Round amounts
            for pt in payment_types.values():
                pt['total_amount'] = round(pt['total_amount'], 2)
            
            return {
                "total_outstanding_payments": len(filtered_rows),
                "total_amount_owed": round(total_amount, 2),
                "unique_members_with_debt": unique_members,
                "payment_types": payment_types,
                "filter_applied": title_filter,
                "club_statistics": stats
            }
            
        except SpondAPIError as e:
            return {"error": f"Spond API Error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    async def search_members(self, query: str) -> Dict[str, Any]:
        """Search for members by name"""
        if not self.api:
            return {"error": "API not initialized. Please provide bearer_token and club_id."}
        
        try:
            members, member_map = self.api.get_members()
            
            # Search members (case-insensitive partial match)
            query_lower = query.lower()
            matching_members = []
            
            for member_id, name in member_map.items():
                if query_lower in name.lower():
                    matching_members.append({
                        'id': member_id,
                        'name': name
                    })
            
            return {
                "query": query,
                "matching_members": matching_members,
                "total_matches": len(matching_members)
            }
            
        except SpondAPIError as e:
            return {"error": f"Spond API Error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    async def handle_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a tool call"""
        if tool_name == "get_member_payment_summary":
            return await self.get_member_payment_summary(parameters.get("member_name"))
        elif tool_name == "get_all_outstanding_payments":
            return await self.get_all_outstanding_payments(
                parameters.get("title_filter"),
                parameters.get("limit", 50)
            )
        elif tool_name == "get_payment_statistics":
            return await self.get_payment_statistics(parameters.get("title_filter"))
        elif tool_name == "search_members":
            return await self.search_members(parameters.get("query"))
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    async def handle_mcp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP request"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                # Initialize the MCP server
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "spond-payment-reporting",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                # List available tools
                tools_list = []
                for tool in self.tools:
                    tools_list.append({
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.parameters
                    })
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": tools_list
                    }
                }
            
            elif method == "tools/call":
                # Call a tool
                tool_name = params.get("name")
                tool_params = params.get("arguments", {})
                
                # Initialize API with provided credentials if available
                bearer_token = tool_params.pop("bearer_token", None)
                club_id = tool_params.pop("club_id", None)
                
                if bearer_token and club_id:
                    await self.initialize_api(bearer_token, club_id)
                elif not self.api:
                    await self.initialize_api()
                
                result = await self.handle_tool_call(tool_name, tool_params)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def run_stdio(self):
        """Run the MCP server using stdio transport"""
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    response = await self.handle_mcp_request(request)
                    print(json.dumps(response), flush=True)
                except json.JSONDecodeError as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": f"Parse error: {str(e)}"
                        }
                    }
                    print(json.dumps(error_response), flush=True)
                    
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)


def main():
    """Main entry point for the MCP server"""
    server = SpondMCPServer()
    asyncio.run(server.run_stdio())


if __name__ == "__main__":
    main()