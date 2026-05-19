from app.rag.policy_qa import (
    answer_policy_question
)


async def rag_agent(
    query: str
):

    response = answer_policy_question(
        query=query
    )

    return {
        "intent": "POLICY_QUERY",
        "message": response
    }