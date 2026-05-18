from app.agents.mcp_client import client


async def get_all_tools():

    tools = await client.get_tools()

    return tools