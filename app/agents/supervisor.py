from app.agents.intent_classifier import (
    classify_intent
)

from app.agents.account_agent import (
    build_account_agent
)

from app.agents.transfer_agent import (
    build_transfer_agent
)

from app.agents.card_agent import (
    build_card_agent
)

from app.agents.loan_agent import (
    build_loan_agent
)

from app.agents.rag_agent import (
    rag_agent
)
from app.agents.context_builder import (
    build_user_context
)
from app.agents.confirmation import (
    is_confirmation
)
from app.agents.workflow_extractors import (
    extract_transfer_details
)

from app.agents.tool_registry import (
    get_all_tools
)

async def supervisor_router(
         db,
    query: str,
    user_id: int,
    workflow_data: dict
):

    # ==========================================
# RESUME PENDING WORKFLOW
# ==========================================

    if (
        workflow_data.get("awaiting_transfer_confirmation")
        and is_confirmation(query)
    ):

        pending_transfer = workflow_data[
            "pending_transfer"
        ]

        tools = await get_all_tools()

        transfer_tool = next(
            tool
            for tool in tools
            if tool.name == "transfer"
        )

        transfer_payload = {

        "sender_account": pending_transfer[
            "sender_account"
        ],

        "receiver_account": pending_transfer[
            "receiver_account"
        ],

        "amount": pending_transfer[
            "amount"
        ]
    }

        result = await transfer_tool.ainvoke(
            transfer_payload
        )   

        workflow_data.clear()

        return {
            "intent": "MONEY_TRANSFER",
            "response": result
        }

    intent = classify_intent(query)

    # ==========================================
    # ACCOUNT DOMAIN
    # ==========================================

    if intent in [
        "BALANCE_INQUIRY",
        "ACCOUNT_DETAILS",
        "PROFILE_DETAILS",
        "ACCOUNT_CREATION"
    ]:

        agent = await build_account_agent()

    # ==========================================
    # TRANSFER DOMAIN
    # ==========================================

    elif intent in [
        "MONEY_TRANSFER",
        "TRANSACTION_HISTORY",
        "ADD_BENEFICIARY",
        "LIST_BENEFICIARIES"
    ]:

        agent = await build_transfer_agent()

    # ==========================================
    # CARD DOMAIN
    # ==========================================

    elif intent in [
        "BLOCK_CARD",
        "ACTIVATE_CARD",
        "FREEZE_CARD"
    ]:

        agent = await build_card_agent()

    # ==========================================
    # LOAN DOMAIN
    # ==========================================

    elif intent in [
        "LOAN_ELIGIBILITY",
        "EMI_CALCULATION",
        "APPLY_LOAN",
        "LOAN_DETAILS"
    ]:

        agent = await build_loan_agent()

    # ==========================================
    # FAQ DOMAIN
    # ==========================================

    else:

        response = await rag_agent(query)

        return {
            "intent": intent,
            "response": response
        }

    user_context = build_user_context(
    db,
    user_id
)
    
    # ==========================================
    # REAL AGENT EXECUTION
    # ==========================================

    response = await agent.ainvoke(
    {
        "messages": [
            {
                "role": "system",
                "content": f"""
Authenticated Banking Context:

{user_context}

Rules:
- NEVER ask user for already available account information
- Use provided accounts automatically
- Use MCP tools whenever needed
- Use primary account for transfers unless specified
- Never hallucinate balances
- Maintain banking safety
"""
            },
            {
                "role": "user",
                "content": query
            }
        ]
    }
)

    if intent == "MONEY_TRANSFER":

        beneficiary_tool_output = None

        # ==========================================
        # FIND BENEFICIARY TOOL RESULT
        # ==========================================

        for message in response["messages"]:

            if getattr(message, "type", None) == "tool":

                if message.name == "beneficiaries":

                    if isinstance(message.content, list):

                        beneficiary_tool_output = (
                            message.content[0]["text"]
                        )

                    else:

                        beneficiary_tool_output = (
                            message.content
                        )

        # ==========================================
        # BUILD TRANSFER DETAILS
        # ==========================================

        if beneficiary_tool_output:

            transfer_details = extract_transfer_details(
                query=query,
                user_context=user_context,
                beneficiary_tool_output=beneficiary_tool_output
            )

            workflow_data[
                "awaiting_transfer_confirmation"
            ] = True

            workflow_data[
                "pending_transfer"
            ] = transfer_details

        
    return {
        "intent": intent,
        "response": response,
         "workflow_data": workflow_data
    }