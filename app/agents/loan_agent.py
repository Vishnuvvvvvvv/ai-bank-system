from langchain.agents import create_agent

from app.agents.llm import llm

from app.agents.tool_registry import (
    get_all_tools
)


LOAN_TOOLS = [
    "emi",
    "eligibility",
    "apply_loan",
    "loans",
    "loan_applications"
]


async def build_loan_agent():

    tools = await get_all_tools()

    filtered_tools = [
        tool
        for tool in tools
        if tool.name in LOAN_TOOLS
    ]

    SYSTEM_PROMPT = """
You are an enterprise banking loan AI agent.

Responsibilities:
- loan eligibility
- EMI calculations
- loan applications
- loan details

Rules:
- always use tools
- provide financially safe responses
- explain loan details clearly
"""

    agent = create_agent(
        model=llm,
        tools=filtered_tools,
        system_prompt=SYSTEM_PROMPT
    )

    return agent