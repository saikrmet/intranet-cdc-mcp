# CDC Intranet MCP Server

A Model Context Protocol (MCP) server that provides secure search and content retrieval capabilities for the CDC (Centers for Disease Control and Prevention) internal intranet. This server demonstrates how government agencies can leverage MCP to make internal knowledge bases accessible to AI assistants while maintaining security and authentication requirements.

## Overview

This MCP server provides two primary tools for interacting with CDC's internal intranet:

- **Search CDC Intranet**: Search across CDC's internal websites and documents
- **Fetch CDC Content**: Retrieve full content from specific CDC intranet pages

The server uses NTLM authentication to access CDC's internal search infrastructure and returns structured data that can be consumed by local and remote MCP client agents.

## Architecture

### Components

1. **FastMCP Server** (`main.py`): The core MCP server implementation using FastMCP framework
2. **Data Models** (`models.py`): Pydantic models for structured data exchange
3. **Client Example** (`client.py`): Demonstration of how to consume the MCP server
4. **Docker Container** (`Dockerfile`): Production deployment configuration

### How It Works

1. **Authentication**: Uses NTLM authentication to access CDC's internal network
2. **Search Integration**: Connects to CDC's Solr-based intranet search API
3. **Content Extraction**: Parses HTML content using BeautifulSoup to extract clean text
4. **MCP Protocol**: Exposes functionality through standardized MCP tool interface
5. **HTTP Transport**: Serves MCP over HTTP for easy integration with clients

## Features

### Search Capabilities

- Natural language search queries across CDC intranet
- Structured results with titles, descriptions, and URLs
- Highlighted search terms in content snippets
- Configurable result limits and filtering

### Content Retrieval

- Full page content extraction from CDC intranet URLs
- Clean text extraction from HTML content
- Preservation of document structure and metadata
- Error handling for inaccessible or malformed content

### Security & Authentication

- NTLM authentication for secure intranet access
- Service account or current user credential support
- Configurable through environment variables
- Network-level security (must be deployed within CDC network)

## Installation & Setup

### Prerequisites

- Python 3.11 or higher
- Access to CDC internal network
- Valid CDC credentials for NTLM authentication

### Local Development

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd intranet-cdc-mcp
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables** (optional):

   ```bash
   export CDC_SERVICE_USERNAME="your-username"
   export CDC_SERVICE_PASSWORD="your-password"
   ```

4. **Run the server**:

   ```bash
   python main.py
   ```

The server will start on `http://localhost:8000` and expose the MCP interface at `/mcp`.

### Docker Deployment

1. **Build the container**:

   ```bash
   docker build -t cdc-intranet-mcp .
   ```

2. **Run with environment variables**:

   ```bash
   docker run -p 8000:8000 \
     -e CDC_SERVICE_USERNAME="service-account" \
     -e CDC_SERVICE_PASSWORD="service-password" \
     cdc-intranet-mcp
   ```

## Usage Examples

### MCP Client Integration

The server uses **HTTP transport** for the MCP protocol, making it compatible with various MCP clients. Because the transport is streamable HTTP, the server can be deployed as a **remote MCP server** and connected to multiple MCP clients simultaneously within an agency's network. This allows for centralized deployment while serving distributed teams and applications.

#### Remote Deployment Benefits

- **Centralized Management**: Single server instance serves multiple clients
- **Shared Authentication**: One set of service credentials for all users
- **Scalable Architecture**: Horizontal scaling to handle multiple concurrent clients
- **Network Efficiency**: Reduced individual authentication overhead

#### Claude Desktop Configuration

Add to your Claude Desktop MCP settings:

```json
{
  "mcpServers": {
    "cdc-intranet": {
      "command": "fastmcp",
      "args": ["client", "http://your-cdc-server:8000/mcp"],
      "env": {}
    }
  }
}
```

### Available Tools

#### `search_cdc_intranet`

Search CDC's internal websites and documents.

**Parameters:**

- `query` (string): Natural language search query

**Returns:**

```json
{
  "content": [{
    "type": "text",
    "text": "{\"results\": [{\"id\": \"page-id\", \"title\": \"Page Title\", \"text\": \"Content snippet...\", \"url\": \"https://intranet.cdc.gov/...\"}]}"
  }]
}
```

#### `fetch_cdc_intranet`

Retrieve full content from a specific CDC intranet page.

**Parameters:**

- `id` (string): URL or identifier of the CDC intranet page

**Returns:**

```json
{
  "content": [{
    "type": "text", 
    "text": "{\"id\": \"page-url\", \"title\": \"Full Page Title\", \"text\": \"Complete page content...\", \"url\": \"https://intranet.cdc.gov/...\"}"
  }]
}
```

## Deployment Considerations

### Network Requirements

- **Must be deployed within CDC's internal network** to access intranet resources
- Requires connectivity to `intranetsearch.cdc.gov` and CDC intranet domains
- Firewall rules may need configuration for outbound HTTP/HTTPS

### Authentication Options

1. **Service Account** (Recommended for production):
   - Set `CDC_SERVICE_USERNAME` and `CDC_SERVICE_PASSWORD`
   - Use dedicated service account with appropriate permissions

2. **Current User Credentials** (Development):
   - Omit environment variables to use current Windows user
   - Suitable for development on domain-joined machines

### Scaling & Performance

- Stateless design allows horizontal scaling
- HTTP client connection pooling for efficient resource usage
- Configurable timeouts and retry policies
- Structured logging for monitoring and debugging

## Extending for Other Agencies

This implementation serves as a reference for other government agencies looking to create similar MCP servers for their internal knowledge bases:

### Key Adaptation Points

1. **Authentication Method**: Replace NTLM with your organization's auth (SAML, OAuth, etc.)
2. **Search Backend**: Modify search URLs and API calls for your search infrastructure
3. **Content Parsing**: Adjust HTML parsing for your intranet's structure
4. **Network Configuration**: Update firewall and network access requirements

### Performance & Scalability Optimizations

**ASGI Integration via FastAPI**: For high-performance production deployments, consider migrating from FastMCP's built-in HTTP server to a full ASGI implementation using FastAPI. This provides:

- **Higher Concurrency**: Better handling of simultaneous client connections
- **Advanced Middleware**: Built-in support for CORS, rate limiting, and request/response processing
- **Production-Ready Features**: Automatic OpenAPI documentation, request validation, and error handling
- **Deployment Flexibility**: Compatible with ASGI servers like Uvicorn, Gunicorn, and cloud platforms

### Extension Opportunities

The current implementation provides a solid foundation with several areas for enhancement:

**Document Handling Extension**: The current server searches and fetches web pages from CDC intranet but does not handle documents (PDFs, Word docs, PowerPoints, etc.). Future enhancements could include:

- Integration with document parsing libraries (PyPDF2, python-docx, python-pptx)
- Support for SharePoint document libraries and file systems
- Optical Character Recognition (OCR) for scanned documents
- Full-text search across document content

**JavaScript-Heavy Page Support**: The current BeautifulSoup-based parsing works well for server-rendered HTML but cannot handle JavaScript-heavy pages or Single Page Applications (SPAs). Advanced implementations could incorporate:

- Selenium WebDriver for full browser automation
- Playwright for modern web app interactions
- Headless Chrome/Firefox for JavaScript execution
- API-first approaches where available (REST/GraphQL endpoints)

