from app.agents.llm import llm


INTENT_PROMPT = """
You are an enterprise banking AI intent classifier.

Classify the query into EXACTLY ONE intent:

- BALANCE_INQUIRY
- ACCOUNT_DETAILS
- PROFILE_DETAILS
- ACCOUNT_CREATION
- MONEY_TRANSFER
- TRANSACTION_HISTORY
- BLOCK_CARD
- ACTIVATE_CARD
- FREEZE_CARD
- ADD_BENEFICIARY
- LIST_BENEFICIARIES
- LOAN_ELIGIBILITY
- EMI_CALCULATION
- APPLY_LOAN
- LOAN_DETAILS
- FAQ_QUERY

Only return the intent name.
"""


def classify_intent(query: str):

    prompt = f"""
    {INTENT_PROMPT}

    User Query:
    {query}
    """

    response = llm.invoke(prompt)

    
    content = response.content

# ==========================================
# HANDLE LIST RESPONSE
# ==========================================

    if isinstance(content, list):

        text_parts = []

        for item in content:

            if isinstance(item, dict):

                if item.get("type") == "text":

                    text_parts.append(
                        item.get("text", "")
                    )

            else:

                text_parts.append(str(item))

        content = " ".join(text_parts)

# ==========================================
# RETURN CLEAN INTENT
# ==========================================

    return str(content).strip()