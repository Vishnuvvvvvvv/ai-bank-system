from langchain.agents import create_agent

from app.agents.llm import llm

from app.agents.tool_registry import (
    get_all_tools
)


CARD_TOOLS = [
    "block",
    "activate",
    "freeze"
]


async def build_card_agent():

    tools = await get_all_tools()

    filtered_tools = [
        tool
        for tool in tools
        if tool.name in CARD_TOOLS
    ]

    SYSTEM_PROMPT = """
You are a banking card management AI agent.

Responsibilities:
- block cards
- activate cards
- freeze cards

Rules:
- prioritize banking safety
- always use tools
- explain actions clearly
"""

    agent = create_agent(
        model=llm,
        tools=filtered_tools,
        system_prompt=SYSTEM_PROMPT
    )

    return agent