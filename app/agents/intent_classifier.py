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
- POLICY_QUERY


INTENT RULES:

1. FAQ_QUERY
General banking FAQs.

Examples:
- How to open account?
- What is FD?
- What is savings account?

2. POLICY_QUERY
Banking rules, KYC,
interest rates, eligibility rules,
loan policies.

Examples:
- Home loan interest rate
- KYC requirements
- Minimum salary for loan

3. BALANCE_INQUIRY
Balance/account money questions.

4. MONEY_TRANSFER
Sending money.

5. LOAN_ELIGIBILITY
Personalized eligibility.

Example:
- Am I eligible for home loan?

6. APPLY_LOAN
Applying for loan.

Example:
- Apply for home loan

7. BLOCK_CARD / ACTIVATE_CARD / FREEZE_CARD
Block/freeze/activate card.

8. TRANSACTION_HISTORY
Transaction statements/history.

9. ACCOUNT_DETAILS / PROFILE_DETAILS / ACCOUNT_CREATION
Profile/account updates.

Return ONLY the intent name.


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
