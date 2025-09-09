import asyncio
from fastmcp import Client

client = Client("http://localhost:8000/mcp")

async def call_tool(query: str):
    async with client:
        result = await client.call_tool("search_cdc_intranet", {"query": query})
        # result = await client.call_tool("fetch_cdc_intranet", {"id": id})
        print(result.data)

asyncio.run(call_tool("AI"))
# asyncio.run(call_tool("https://intranet.cdc.gov/ai/success-stories.html"))