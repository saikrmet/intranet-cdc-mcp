import asyncio
import os
from fastmcp import FastMCP
from models import SearchToolResponse, SearchResults, SearchResult, ContentItem
import logging
import httpx
from urllib.parse import quote_plus
import json, ssl
from bs4 import BeautifulSoup
from httpx_ntlm import HttpNtlmAuth


# Configure structured logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class CDCSearchService:
    def __init__(self):
        logger.info("Initializing CDC Search Service with NTLM authentication")
        
        # Get service account credentials from environment variables
        username = os.getenv('CDC_SERVICE_USERNAME')
        password = os.getenv('CDC_SERVICE_PASSWORD')
        
        if not username or not password:
            logger.warning("Service account credentials not found in environment variables. Falling back to current user credentials.")
            auth = HttpNtlmAuth(None, None)  # Use current Windows credentials as fallback
        else:
            logger.info(f"Using service account: {username}")
            auth = HttpNtlmAuth(username, password)
        
        # Configure HTTP client for CDC intranet access with Windows auth
        self.http_client = httpx.AsyncClient(
            auth=auth,
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Connection": "keep-alive",
            }
        )
    
    async def close(self):
        logger.info("Closing CDC Search Service HTTP client")
        await self.http_client.aclose()
    
    def _get_text_from_highlighting(self, doc, highlighting):
        """Extract text from highlighting data with fallbacks."""
        doc_id = doc.get("id", "")
        
        # Try to get highlighted content first
        if doc_id in highlighting:
            highlight_data = highlighting[doc_id]
            content = highlight_data.get("content", [])
            if content and content[0]:
                return content[0]
        
        # Fall back to description from doc
        description = doc.get("description", [])
        if description and description[0]:
            return description[0]
        
        return "No content available"
    
    async def search_cdc_intranet(self, query: str) -> dict:
        if not query.strip():
            logger.warning("Empty search query received")
            response = SearchToolResponse(
                content=[ContentItem(type="text", text=json.dumps({"results": []}))]
            )
            return response.model_dump()
        
        logger.info(f"Searching CDC intranet: query='{query}'")
        url = f"https://intranetsearch.cdc.gov/srch/intranet/browse2-nodoc?q={quote_plus(query)}&wt=json&start=0&rows=10&fl=id,url,title,description&hl=on&hl.simple.pre=%3Cb%3E&hl.simple.post=%3C/b%3E&hl.defaultSummary=true&hl.snippets=1&hl.method=unified&hl.fragsize=300&hl.fl=content,description&echoParams=none&indent=false"
        
        try:
            response = await self.http_client.get(url)
            response.raise_for_status()
            
            data = response.json()
            docs = data.get("response", {}).get("docs", [])
            highlighting = data.get("highlighting", {})
            
            logger.info(f"Search completed successfully: found {len(docs)} results for query '{query}'")
            
            results = SearchResults(results=[
                SearchResult(
                    id=doc.get("id", ""),
                    title=doc.get("title", "Untitled"),
                    text=self._get_text_from_highlighting(doc, highlighting),
                    url=doc.get("url", "")
                )
                for doc in docs
            ])
            
            search_response = SearchToolResponse(
                content=[ContentItem(type="text", text=results.model_dump_json())]
            )
            return search_response.model_dump()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during search: status={e.response.status_code}, query='{query}', url={url}")
            error_text = f"HTTP {e.response.status_code} error while searching CDC intranet"
        except httpx.TimeoutException:
            logger.error(f"Request timeout during search: query='{query}', timeout=30s")
            error_text = "Search request timed out"
        except httpx.ConnectError as e:
            logger.error(f"Connection error during search: {str(e)}, query='{query}'")
            error_text = "Unable to connect to CDC intranet search service"
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON response from search API: query='{query}'")
            error_text = "Invalid response format from search service"
        except Exception as e:
            logger.error(f"Unexpected error during search: {type(e).__name__}={str(e)}, query='{query}'")
            error_text = f"Search service error: {type(e).__name__}"
            
        error_result = SearchResult(
            id="", 
            title="Search Error", 
            text=error_text, 
            url=""
        )
        error_response = SearchToolResponse(
            content=[ContentItem(type="text", text=error_result.model_dump_json())]
        )
        return error_response.model_dump()

    async def fetch_cdc_intranet(self, id: str) -> dict:
        """Fetch and extract content from a CDC intranet page."""
        logger.info(f"Fetching CDC intranet page: {id}")
        
        try:
            # Fetch the HTML content
            response = await self.http_client.get(id)
            response.raise_for_status()
            
            logger.debug(f"Successfully retrieved page content: status={response.status_code}, content_length={len(response.content)}")
            
            # Parse HTML with Beautiful Soup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract content from the specific main element
            main_content = soup.find('main', role='main')
            
            if main_content:
                # Extract title from the first h1 in the main content area
                h1_tag = main_content.find('h1')
                title = h1_tag.get_text(strip=True) if h1_tag else "Untitled"
                
                # Extract all text from the main content area
                text = main_content.get_text(separator=' ', strip=True)
                # Clean up excessive whitespace
                text = ' '.join(text.split())
                
                logger.info(f"Successfully extracted content: title='{title}', content_length={len(text)}")
            else:
                logger.warning(f"No main content element found on page: {id}")
                title = "No Title"
                text = "No content found."
            
            # Create SearchResult object using Pydantic model
            result = SearchResult(
                id=id,
                title=title,
                text=text,
                url=id
            )
            
            # Return in MCP format using the same pattern as search
            fetch_response = SearchToolResponse(
                content=[ContentItem(type="text", text=result.model_dump_json())]
            )
            return fetch_response.model_dump()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching page {id}: status={e.response.status_code}")
            error_text = f"HTTP {e.response.status_code} error while fetching page"
        except httpx.TimeoutException:
            logger.error(f"Timeout error fetching page {id}: timeout=30s")
            error_text = "Request timed out while fetching page"
        except httpx.ConnectError as e:
            logger.error(f"Connection error fetching page {id}: {str(e)}")
            error_text = "Unable to connect to CDC intranet"
        except Exception as e:
            logger.error(f"Unexpected error fetching page {id}: {type(e).__name__}={str(e)}")
            error_text = f"Failed to fetch content: {type(e).__name__}"
            
        error_result = SearchResult(
            id=id,
            title="Fetch Error",
            text=error_text,
            url=id
        )
        error_response = SearchToolResponse(
            content=[ContentItem(type="text", text=error_result.model_dump_json())]
        )
        return error_response.model_dump()


def create_server():
    search_service = CDCSearchService()
    instructions = """
    This MCP server provides search capabilities for the CDC internal web (intranet).
    Use the search_cdc_intranet tool to find relevant pages and sites across CDC's 
    intranet infrastructure. Returns structured results with titles, descriptions, 
    and URLs from CDC internal websites.
    """
    logger.info("Initializing FastMCP server for CDC intranet search")
    mcp = FastMCP(name="CDC Intranet MCP Server", instructions=instructions)

    @mcp.tool
    async def search_cdc_intranet(query: str) -> dict:
        """Search engine for sites on the CDC internal web (intranet).

        This tool searches through the CDC's intranet websites to find relevant pages and sites.
        Returns a list of search results with basic information including site titles, text descriptions
        and URLs from the CDC intranet web.

        Args:
            query: Search query string. Natural language queries work best for finding relevant CDC intranet sites.

        Returns:
            Dictionary with 'content' key containing search results:
            - content: array of content items with search data
            - Each search result includes:
              - id: unique identifier for the CDC intranet page
              - title: page title from CDC intranet
              - text: description/snippet from the page
              - url: direct URL to the CDC intranet page
        """
        logger.info(f"Received search request via MCP tool: query='{query}'")
        return await search_service.search_cdc_intranet(query)
    
    @mcp.tool
    async def fetch_cdc_intranet(id: str) -> dict:
        """Fetch the full contents of a CDC intranet document by its unique identifier.

        This tool retrieves the complete content of a specific CDC intranet page that was 
        found through search_cdc_intranet. Use this after searching to get the full site 
        content of a particular search result for further analysis.

        Args:
            id: The unique identifier from a search result (obtained from search_cdc_intranet).

        Returns:
            Dictionary with 'content' key containing document data:
            - content: array of content items with full document information
            - Document object includes:
              - id: unique identifier for the document
              - title: document title
              - text: full text content of the CDC intranet page
              - url: direct URL to the original CDC intranet page for citation
              - metadata: additional document information (source, etc.)
        """
        logger.info(f"Received fetch request via MCP tool: id='{id}'")
        return await search_service.fetch_cdc_intranet(id)

    return mcp, search_service


async def main():
    logger.info("Starting CDC Intranet MCP Server")
    server, search_service = create_server()
    try:
        logger.info("Server starting on host=0.0.0.0, port=8000")
        await server.run_async(transport="http", host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Server error: {type(e).__name__}={str(e)}")
        raise
    finally:
        logger.info("Shutting down CDC Search Service")
        await search_service.close()
        logger.info("Server shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())