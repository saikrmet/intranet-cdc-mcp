"""
CDC Intranet MCP Client Example

This module demonstrates how to interact with the CDC Intranet MCP Server
using the FastMCP client library. It shows practical examples of:

1. Connecting to the MCP server via HTTP transport
2. Calling the search_cdc_intranet tool with queries
3. Calling the fetch_cdc_intranet tool to retrieve full page content
4. Handling responses and extracting data

Usage Examples:
- Search for AI-related content across CDC intranet
- Fetch specific pages by URL for detailed content analysis
- Integration patterns for MCP clients

This client can be used for testing the server functionality and as a 
reference for implementing MCP clients in other applications.
"""

import asyncio
from fastmcp import Client

# MCP Server Configuration
# For local development: "http://localhost:8000/mcp"
# For production deployment: Use the actual CDC internal server URL
# client = Client("http://localhost:8000/mcp")
client = Client("https://edav-prd-intranet-mcp.edav-prd-app.appserviceenvironment.net/mcp")


async def call_tool(query: str):
    """
    Demonstrate calling MCP tools for CDC intranet search and content retrieval.
    
    This function shows how to:
    1. Establish a connection to the MCP server
    2. Call the search_cdc_intranet tool with a query
    3. Process and display the results
    
    Args:
        query (str): Search query to send to CDC intranet search
        
    The function uses an async context manager to ensure proper connection
    cleanup after the operations complete.
    """
    async with client:
        # Search for content across CDC intranet
        result = await client.call_tool("search_cdc_intranet", {"query": query})
        
        # Alternative: Fetch specific page content by URL
        # result = await client.call_tool("fetch_cdc_intranet", {"id": url})
        
        print(result.data)

# Example usage
if __name__ == "__main__":
    # Search for AI-related content
    asyncio.run(call_tool("AI"))
    
    # Alternative example: Fetch specific page
    # asyncio.run(call_tool("https://intranet.cdc.gov/ai/success-stories.html"))