import re

# from app.agents.intent_classifier import (
#     classify_intent
# )

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

from app.agents.context_builder import (
    build_user_context
)
from app.agents.confirmation import (
    is_confirmation
)
from app.agents.workflow_extractors import (
    extract_transfer_details
)
from app.models.account import Account
from app.models.beneficiary import Beneficiary
from app.models.loan_application import LoanApplication
from app.services.audit_service import create_audit_log
from app.services.loan_service import (
    apply_for_loan,
    evaluate_loan_eligibility,
    infer_loan_type_from_query,
)
from app.services.transaction_service import transfer_money

from app.agents.tool_registry import (
    get_all_tools
)

from app.agents.rag_agent import (
    rag_agent
)



async def supervisor_router(
         db,
    query: str,
    user_id: int,
     intent: str,
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

        result = transfer_money(
            db=db,
            sender_account_number=pending_transfer["sender_account"],
            receiver_account_number=pending_transfer["receiver_account"],
            amount=pending_transfer["amount"],
        )

        create_audit_log(
            db=db,
            user_id=user_id,
            action="TRANSFER_MONEY",
            status=result["message"],
        )

        workflow_data.clear()

        return {
            "intent": "MONEY_TRANSFER",
            "response": _format_transfer_result(result)
        }

    if (
        workflow_data.get("awaiting_loan_submission_confirmation")
        and is_confirmation(query)
    ):

        loan_type = workflow_data.get(
            "pending_loan_type"
        ) or infer_loan_type_from_query(query)

        result = apply_for_loan(
            db=db,
            user_id=user_id,
            loan_type=loan_type,
            requested_amount=workflow_data.get("requested_loan_amount", 0),
            annual_income=0,
            employment_type="",
        )

        workflow_data.pop("awaiting_loan_submission_confirmation", None)
        workflow_data.pop("pending_loan_application", None)

        if not result.get("awaiting_document_upload"):
            workflow_data.pop("awaiting_document_upload", None)
            workflow_data.pop("missing_documents", None)

        return {
            "intent": "APPLY_LOAN",
            "response": result,
            "workflow_data": workflow_data,
        }

    # intent = classify_intent(query)

    document_followup = _handle_pending_loan_document_followup(
        db=db,
        user_id=user_id,
        query=query,
        workflow_data=workflow_data,
    )

    if document_followup:
        return document_followup

    loan_amount_update = _try_update_pending_loan_amount(
        db=db,
        user_id=user_id,
        query=query,
    )

    if loan_amount_update:
        return {
            "intent": "LOAN_APPLICATION",
            "response": loan_amount_update,
            "workflow_data": workflow_data,
        }

    transfer_response = _handle_transfer_state(
        db=db,
        user_id=user_id,
        query=query,
        intent=intent,
        workflow_data=workflow_data,
    )

    if transfer_response:
        return transfer_response


    # =========================================
# FAQ / POLICY QUERIES
# =========================================

    # =========================================
# FAQ / POLICY QUERIES
# =========================================

    if intent in [
        "FAQ_QUERY",
        "POLICY_QUERY"
    ]:

        response = await rag_agent(
            query=query
        )

        return {
            "intent": intent,
            "response": response,
            "workflow_data": workflow_data
        }

    # ==========================================
    # DETERMINISTIC LOAN WORKFLOWS
    # ==========================================

    if intent in [
        "LOAN_ELIGIBILITY",
        "APPLY_LOAN",
        "LOAN_APPLICATION",
    ]:

        loan_type = workflow_data.get(
            "pending_loan_type"
        ) or infer_loan_type_from_query(query)
        requested_amount = _extract_money_amount(query) or workflow_data.get(
            "requested_loan_amount",
            0,
        )

        if requested_amount:
            workflow_data["requested_loan_amount"] = requested_amount

        eligibility = evaluate_loan_eligibility(
            db=db,
            user_id=user_id,
            loan_type=loan_type,
        )

        if intent == "LOAN_ELIGIBILITY":

            workflow_data["pending_loan_type"] = loan_type

            if eligibility["awaiting_documents"]:
                workflow_data["awaiting_document_upload"] = True
                workflow_data["missing_documents"] = eligibility[
                    "missing_documents"
                ]

            return {
                "intent": intent,
                "response": eligibility,
                "workflow_data": workflow_data,
            }

        if eligibility["eligible"]:
            workflow_data["pending_loan_type"] = loan_type
            workflow_data["requested_loan_amount"] = requested_amount
            workflow_data["pending_loan_application"] = True
            workflow_data["awaiting_loan_submission_confirmation"] = True
            workflow_data.pop("awaiting_document_upload", None)
            workflow_data.pop("missing_documents", None)

            return {
                "intent": "APPLY_LOAN",
                "response": {
                    "success": True,
                    "message": (
                        "Your uploaded documents satisfy the loan checks. "
                        "Should we proceed with submitting the loan application?"
                    ),
                    "requires_confirmation": True,
                    "eligibility": eligibility,
                },
                "workflow_data": workflow_data,
            }

        result = apply_for_loan(
            db=db,
            user_id=user_id,
            loan_type=loan_type,
            requested_amount=requested_amount,
            annual_income=0,
            employment_type="",
        )

        if result.get("awaiting_document_upload"):
            workflow_data["awaiting_document_upload"] = True
            workflow_data["pending_loan_type"] = loan_type
            workflow_data["missing_documents"] = result[
                "missing_documents"
            ]
            workflow_data["pending_loan_application"] = True

        else:
            workflow_data.pop("awaiting_document_upload", None)
            workflow_data.pop("missing_documents", None)
            workflow_data.pop("pending_loan_application", None)

        return {
            "intent": "APPLY_LOAN",
            "response": result,
            "workflow_data": workflow_data,
        }
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

    assistant_response = _extract_final_ai_message(response)

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
        "response": assistant_response,
         "workflow_data": workflow_data
    }


def _extract_final_ai_message(response):

    if not isinstance(response, dict):
        return response

    messages = response.get("messages")

    if not isinstance(messages, list):
        return response

    for message in reversed(messages):
        message_type = getattr(message, "type", None)

        if message_type != "ai":
            continue

        content = getattr(message, "content", "")

        if content:
            return _content_to_text(content)

    return "I completed the request, but could not format the final response."


def _content_to_text(content):

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, dict):
                parts.append(item.get("text", ""))
            else:
                parts.append(str(item))

        return "\n".join(part for part in parts if part)

    return str(content)


def _handle_transfer_state(
    db,
    user_id: int,
    query: str,
    intent: str,
    workflow_data: dict,
):
    lowered = query.lower()
    pending = workflow_data.get("pending_transfer")
    transfer_words = ["transfer", "send", "fund"]

    if not pending and intent != "MONEY_TRANSFER" and not any(
        word in lowered for word in transfer_words
    ):
        return None

    transfer = dict(pending or {})
    amount = _extract_money_amount(query)
    sender_account = _extract_sender_account(query)
    beneficiary = (
        _find_named_beneficiary(db, user_id, query)
        or _find_beneficiary_by_account(db, user_id, query)
        or _infer_single_beneficiary(db, user_id, query)
    )

    if amount:
        transfer["amount"] = amount

    if sender_account:
        transfer["sender_account"] = sender_account

    if beneficiary:
        transfer["receiver_name"] = beneficiary.beneficiary_name
        transfer["receiver_account"] = beneficiary.receiver_account
        transfer["ifsc_code"] = beneficiary.ifsc_code

    if not transfer.get("sender_account"):
        primary_account = _primary_account(db, user_id)
        if primary_account:
            transfer["sender_account"] = primary_account.account_number

    workflow_data["pending_transfer"] = transfer

    balance_line = ""
    if "balance" in lowered:
        account = _account_by_number(
            db,
            user_id,
            transfer.get("sender_account"),
        ) or _primary_account(db, user_id)

        if account:
            balance_line = (
                f"Your current balance in account {account.account_number} "
                f"is INR {account.balance:,.2f}.\n\n"
            )

    missing = []
    if not transfer.get("receiver_account"):
        missing.append("beneficiary")
    if not transfer.get("amount"):
        missing.append("amount")
    if not transfer.get("sender_account"):
        missing.append("source account")

    if missing:
        workflow_data.pop("awaiting_transfer_confirmation", None)
        return {
            "intent": "MONEY_TRANSFER",
            "response": balance_line + _transfer_missing_message(missing, transfer),
            "workflow_data": workflow_data,
        }

    workflow_data["awaiting_transfer_confirmation"] = True

    return {
        "intent": "MONEY_TRANSFER",
        "response": (
            balance_line
            + "Please confirm this transfer:\n\n"
            + f"- From: {transfer['sender_account']}\n"
            + f"- To: {transfer.get('receiver_name', 'beneficiary')} "
            + f"({transfer['receiver_account']})\n"
            + f"- Amount: INR {transfer['amount']:,.2f}\n\n"
            + "Reply `confirm` to proceed."
        ),
        "workflow_data": workflow_data,
    }


def _transfer_missing_message(missing: list[str], transfer: dict) -> str:
    if missing == ["amount"] and transfer.get("receiver_name"):
        return (
            f"I found {transfer['receiver_name']} as your saved beneficiary. "
            "How much would you like to transfer?"
        )

    if missing == ["beneficiary"] and transfer.get("amount"):
        return (
            f"I have the amount as INR {transfer['amount']:,.2f}. "
            "Which saved beneficiary should receive it?"
        )

    return "Please provide the " + ", ".join(missing) + " for the transfer."


def _format_transfer_result(result: dict) -> str:
    if result.get("success"):
        return (
            f"{result.get('message', 'Transfer successful')}.\n\n"
            f"Remaining balance: INR {result.get('remaining_balance', 0):,.2f}"
        )

    return result.get("message", "Transfer failed")


def _extract_money_amount(query: str) -> float | None:
    currency_patterns = [
        r"(?:inr|rs\.?|rupees|₹)\s*([0-9][0-9,]*(?:\.\d+)?)",
        r"([0-9][0-9,]*(?:\.\d+)?)\s*(?:inr|rs\.?|rupees|₹)",
    ]

    for pattern in currency_patterns:
        match = re.search(pattern, query, flags=re.IGNORECASE)
        if match:
            return float(match.group(1).replace(",", ""))

    matches = re.findall(r"\b[0-9][0-9,]*(?:\.\d+)?\b", query)
    values = [
        float(match.replace(",", ""))
        for match in matches
        if len(match.replace(",", "")) < 8
    ]

    if len(values) == 1:
        return values[0]

    return None


def _extract_sender_account(query: str) -> str | None:
    match = re.search(
        r"(?:from|source|my)\s+(?:account\s*(?:number)?\s*[:#-]?\s*)?([A-Z]{2}\d{3,})",
        query,
        flags=re.IGNORECASE,
    )

    if match:
        return match.group(1).upper()

    return None


def _find_named_beneficiary(db, user_id: int, query: str):
    beneficiaries = db.query(Beneficiary).filter(
        Beneficiary.user_id == user_id
    ).all()

    lowered = query.lower()

    for beneficiary in beneficiaries:
        if beneficiary.beneficiary_name.lower() in lowered:
            return beneficiary

    return None


def _find_beneficiary_by_account(db, user_id: int, query: str):
    account_matches = re.findall(r"\b[A-Z]{2}\d{3,}\b", query, flags=re.IGNORECASE)

    if not account_matches:
        return None

    return db.query(Beneficiary).filter(
        Beneficiary.user_id == user_id,
        Beneficiary.receiver_account.in_(
            [account.upper() for account in account_matches]
        ),
    ).first()


def _infer_single_beneficiary(db, user_id: int, query: str):
    lowered = query.lower()

    if not any(word in lowered for word in ["him", "his", "her", "beneficiary"]):
        return None

    beneficiaries = db.query(Beneficiary).filter(
        Beneficiary.user_id == user_id
    ).all()

    if len(beneficiaries) == 1:
        return beneficiaries[0]

    return None


def _primary_account(db, user_id: int):
    return db.query(Account).filter(
        Account.user_id == user_id,
        Account.status == "ACTIVE",
    ).order_by(Account.id.asc()).first()


def _account_by_number(db, user_id: int, account_number: str | None):
    if not account_number:
        return None

    return db.query(Account).filter(
        Account.user_id == user_id,
        Account.account_number == account_number,
    ).first()


def _try_update_pending_loan_amount(
    db,
    user_id: int,
    query: str,
) -> str | None:
    lowered = query.lower()

    if "requested amount" not in lowered and "loan amount" not in lowered:
        return None

    amount = _extract_money_amount(query)
    if not amount:
        return None

    application = db.query(LoanApplication).filter(
        LoanApplication.user_id == user_id,
        LoanApplication.status == "PENDING",
    ).order_by(LoanApplication.id.desc()).first()

    if not application:
        return None

    application.requested_amount = amount
    db.commit()

    return (
        "Updated your pending loan application requested amount to "
        f"INR {amount:,.2f}."
    )


def _handle_pending_loan_document_followup(
    db,
    user_id: int,
    query: str,
    workflow_data: dict,
):
    loan_type = workflow_data.get("pending_loan_type")

    if not loan_type:
        return None

    lowered = query.lower()
    trigger_words = [
        "uploaded",
        "upload",
        "document",
        "documents",
        "proceed",
        "continue",
        "where",
    ]

    if not any(word in lowered for word in trigger_words):
        return None

    eligibility = evaluate_loan_eligibility(
        db=db,
        user_id=user_id,
        loan_type=loan_type,
    )

    if eligibility["awaiting_documents"]:
        workflow_data["awaiting_document_upload"] = True
        workflow_data["missing_documents"] = eligibility["missing_documents"]

        return {
            "intent": "APPLY_LOAN",
            "response": {
                "success": False,
                "message": (
                    "I checked the uploaded documents again. Please upload the "
                    "remaining required documents in the upload panel below."
                ),
                "awaiting_document_upload": True,
                "missing_documents": eligibility["missing_documents"],
                "eligibility": eligibility,
            },
            "workflow_data": workflow_data,
        }

    workflow_data.pop("awaiting_document_upload", None)
    workflow_data.pop("missing_documents", None)
    workflow_data["awaiting_loan_submission_confirmation"] = True
    workflow_data["pending_loan_application"] = True

    return {
        "intent": "APPLY_LOAN",
        "response": {
            "success": True,
            "message": (
                "Your uploaded documents now satisfy the loan checks. "
                "Should we proceed with submitting the loan application?"
            ),
            "requires_confirmation": True,
            "eligibility": eligibility,
        },
        "workflow_data": workflow_data,
    }
