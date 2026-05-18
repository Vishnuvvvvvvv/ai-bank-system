from app.services.compliance_service import (
    fraud_check,
    validate_transfer_limit
)


async def compliance_check(
    intent: str,
    amount: float = 0
):

    # =====================================
    # FRAUD CHECK
    # =====================================

    fraud_result = fraud_check(amount)

    # =====================================
    # LIMIT CHECK
    # =====================================

    limit_result = validate_transfer_limit(amount)

    if not limit_result["success"]:

        return {
            "allowed": False,
            "message": limit_result["message"]
        }

    return {
        "allowed": True,
        "fraud_check": fraud_result
    }