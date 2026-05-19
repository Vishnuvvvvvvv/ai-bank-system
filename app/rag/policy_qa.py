from app.rag.policy_retriever import (
    retrieve_policy_context
)

from app.agents.llm import llm


def answer_policy_question(
    query: str
):

    # =========================================
    # RETRIEVE RELEVANT POLICY CONTEXT
    # =========================================

    context = retrieve_policy_context(
        query
    )

    # =========================================
    # RAG PROMPT
    # =========================================

    prompt = f"""
You are a banking policy assistant.

Answer the user's question ONLY
using the provided banking policy context.

If the answer is not found
in the context, say:

"I could not find this information
in the banking policy documents."

USER QUESTION:
{query}

POLICY CONTEXT:
{context}

ANSWER:
"""

    response = llm.invoke(
        prompt
    )

    return response.content