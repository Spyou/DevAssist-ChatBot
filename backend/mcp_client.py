"""
MCP Client for integrating MCP tools into the chatbot
"""

import json
import asyncio
from typing import Optional, Dict, Any
from web_research import WebResearchService

class MCPClient:
    """
    Client to interact with MCP tools
    """
    
    def __init__(self):
        self.research_service = WebResearchService()
        self.tools = {
            "queryProgrammingWeb": self.query_programming_web
        }
    
    async def query_programming_web(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Execute queryProgrammingWeb tool
        """
        # Validate query
        if not self.research_service.is_programming_query(query):
            return {
                "error": "Query must be programming-related",
                "query": query,
                "results": []
            }
        
        # Perform search
        self.research_service.max_results = max_results
        results = await self.research_service.search_web(query)
        
        return {
            "query": query,
            "results": results,
            "count": len(results),
            "sources": [{"title": r["title"], "url": r["url"]} for r in results]
        }
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool by name
        """
        if tool_name in self.tools:
            return await self.tools[tool_name](**arguments)
        
        return {"error": f"Unknown tool: {tool_name}"}
    
    def list_tools(self) -> list:
        """
        List available MCP tools
        """
        return [
            {
                "name": "queryProgrammingWeb",
                "description": "Search the web for programming information",
                "parameters": {
                    "query": "string (required)",
                    "max_results": "integer (optional, default: 5)"
                }
            }
        ]
