from pydantic import BaseModel, Field
from typing import List, Literal


class SearchResult(BaseModel):
    """A single search result item."""
    id: str
    title: str
    text: str
    url: str


class SearchResults(BaseModel):
    """Container for search results array."""
    results: List[SearchResult]


class ContentItem(BaseModel):
    """A content item in the MCP response."""
    type: Literal["text", "image", "resource"]
    text: str


class SearchToolResponse(BaseModel):
    """The complete search tool response for MCP."""
    content: List[ContentItem] = Field(min_length=1)