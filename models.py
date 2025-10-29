"""
Data Models for CDC Intranet MCP Server

This module defines Pydantic models for structured data exchange between the MCP server
and clients. These models ensure consistent data formatting and validation for:

1. Search results from CDC intranet search API
2. Content items in MCP response format
3. Tool responses following MCP protocol standards

The models provide type safety, automatic serialization/deserialization, and
validation for all data flowing through the MCP server.
"""

from pydantic import BaseModel, Field
from typing import List, Literal


class SearchResult(BaseModel):
    """
    A single search result item from CDC intranet search.
    
    Represents one page or document found in the CDC intranet search results.
    Contains all the essential information needed to identify and access the content.
    
    Attributes:
        id (str): Unique identifier for the page (usually the URL)
        title (str): Page title as returned by the search API
        text (str): Content snippet or description, often with search terms highlighted
        url (str): Direct URL to access the page on CDC intranet
    """
    id: str
    title: str
    text: str
    url: str


class SearchResults(BaseModel):
    """
    Container for multiple search results.
    
    Wraps an array of SearchResult objects, typically representing
    the complete set of results returned from a single search query.
    
    Attributes:
        results (List[SearchResult]): Array of individual search result items
    """
    results: List[SearchResult]


class ContentItem(BaseModel):
    """
    A content item in the MCP response format.
    
    Follows the Model Context Protocol specification for content items.
    Currently only supports text content, but the type field allows for
    future extension to support images and other resource types.
    
    Attributes:
        type (Literal): Content type - currently only "text" is used
        text (str): The actual content data as a string
    """
    type: Literal["text", "image", "resource"]
    text: str


class SearchToolResponse(BaseModel):
    """
    The complete tool response format for MCP protocol.
    
    Represents the top-level response structure that MCP clients expect
    when calling tools. Contains an array of content items that hold
    the actual data returned by the tool.
    
    This model ensures compliance with MCP protocol requirements and
    provides validation that at least one content item is always present.
    
    Attributes:
        content (List[ContentItem]): Array of content items with minimum length of 1
    """
    content: List[ContentItem] = Field(min_length=1)