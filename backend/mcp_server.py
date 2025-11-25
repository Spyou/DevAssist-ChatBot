"""
MCP Server for DevAssist Chatbot
Provides web research tool via Model Context Protocol
"""

import asyncio
import json
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
from web_research import WebResearchService

# Initialize MCP Server
mcp_server = Server("devassist-web-research")
research_service = WebResearchService()

@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """
    List available MCP tools
    """
    return [
        Tool(
            name="queryProgrammingWeb",
            description=(
                "Search the web for programming-related information. "
                "Returns titles, URLs, and snippets from top search results. "
                "Only works with programming queries (Python, JavaScript, APIs, frameworks, etc.)"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Programming-related search query"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        )
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Execute MCP tool and return results
    """
    if name == "queryProgrammingWeb":
        query = arguments.get("query", "")
        max_results = arguments.get("max_results", 5)
        
        # Validate programming query
        if not research_service.is_programming_query(query):
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Query must be programming-related. Include keywords like: code, python, javascript, api, etc.",
                    "query": query,
                    "results": []
                }, indent=2)
            )]
        
        # Perform web search
        research_service.max_results = max_results
        results = await research_service.search_web(query)
        
        # Format response
        response = {
            "query": query,
            "results": results,
            "count": len(results),
            "sources": [{"title": r["title"], "url": r["url"]} for r in results]
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]
    
    return [TextContent(
        type="text",
        text=json.dumps({"error": f"Unknown tool: {name}"})
    )]

async def run_mcp_server():
    """
    Run MCP server with stdio transport
    """
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options()
        )

if __name__ == "__main__":
    print("Starting MCP Server: devassist-web-research")
    asyncio.run(run_mcp_server())
