from langchain.agents import create_agent

from app.agents.llm import llm

from app.agents.tool_registry import (
    get_all_tools
)


ACCOUNT_TOOLS = [
    "get_balance",
    "get_accounts",
    "profile",
    "create_account"
]


async def build_account_agent():

    tools = await get_all_tools()

    filtered_tools = [
        tool
        for tool in tools
        if tool.name in ACCOUNT_TOOLS
    ]

    SYSTEM_PROMPT = """
You are an enterprise banking account assistant.

Responsibilities:
- balance inquiries
- account details
- profile details
- account creation

Rules:
- never hallucinate balances
- always use tools
- provide professional banking responses
"""

    agent = create_agent(
        model=llm,
        tools=filtered_tools,
        system_prompt=SYSTEM_PROMPT
    )

    return agent