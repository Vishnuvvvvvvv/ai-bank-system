from langchain.agents import create_agent

from app.agents.llm import llm

from app.agents.tool_registry import (
    get_all_tools
)


TRANSFER_TOOLS = [
    "transfer",
    "transactions",
    "beneficiaries",
    "add_beneficiary_tool"
]


async def build_transfer_agent():

    tools = await get_all_tools()

    filtered_tools = [
        tool
        for tool in tools
        if tool.name in TRANSFER_TOOLS
    ]

    SYSTEM_PROMPT = """
You are an enterprise banking transfer AI agent.

Responsibilities:
- money transfer
- transaction history
- beneficiary management

Rules:
- ALWAYS use available account context
- ALWAYS validate beneficiary
- NEVER execute transfers immediately
- FIRST prepare transfer details
- ASK for confirmation
- After confirmation transfer can execute
"""

    agent = create_agent(
        model=llm,
        tools=filtered_tools,
        system_prompt=SYSTEM_PROMPT
    )

    return agent