from app.agents.llm import llm


async def rag_agent(
    query: str
):

    prompt = f"""
You are a banking knowledge assistant.

Answer banking FAQ queries professionally.

User Query:
{query}
"""

    response = llm.invoke(prompt)

    return response.content