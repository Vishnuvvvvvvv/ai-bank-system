import re
import json


def extract_transfer_details(
    query: str,
    user_context: dict,
    beneficiary_tool_output: str
):

    # ==========================================
    # EXTRACT AMOUNT
    # ==========================================

    amount_match = re.search(
        r"\d+",
        query
    )

    amount = (
        float(amount_match.group())
        if amount_match
        else 0
    )

    # ==========================================
    # LOAD BENEFICIARY JSON
    # ==========================================

    beneficiaries = json.loads(
        beneficiary_tool_output
    )

    # ==========================================
    # MATCH BENEFICIARY
    # ==========================================

    receiver_name = None
    receiver_account = None

    for beneficiary in beneficiaries:

        beneficiary_name = beneficiary[
            "beneficiary_name"
        ]

        if beneficiary_name.lower() in query.lower():

            receiver_name = beneficiary_name

            receiver_account = beneficiary[
                "receiver_account"
            ]

            break

    # ==========================================
    # PRIMARY ACCOUNT
    # ==========================================

    sender_account = user_context[
        "accounts"
    ][0]["account_number"]

    return {

        "sender_account": sender_account,

        "receiver_account": receiver_account,

        "receiver_name": receiver_name,

        "amount": amount
    }