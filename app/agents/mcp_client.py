from langchain_mcp_adapters.client import (
    MultiServerMCPClient
)

client = MultiServerMCPClient(
    {
        "banking": {
            "command": "python",
            "args": [
                "-m",
                "app.mcp.banking_mcp_server"
            ],
            "transport": "stdio"
        }
    }
)