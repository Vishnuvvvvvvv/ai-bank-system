from langchain_google_genai import (
    ChatGoogleGenerativeAI
)

from app.rag.policy_retriever import (
    retrieve_policy_context
)

from app.config import GOOGLE_API_KEY


llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.2
)


def answer_policy_question(
    query: str
):

    context = retrieve_policy_context(query)

    prompt = f"""
You are a banking policy assistant.

Answer the user's question ONLY using
the provided banking policy context.

If the answer is not found,
say:
"I could not find this information in the policy documents."

USER QUESTION:
{query}

POLICY CONTEXT:
{context}

ANSWER:
"""

    response = llm.invoke(prompt)

    return response.content