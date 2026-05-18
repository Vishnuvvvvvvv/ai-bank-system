def validate_transfer_limit(
    amount: float
):

    DAILY_LIMIT = 100000

    if amount > DAILY_LIMIT:

        return {
            "success": False,
            "message": "Transfer exceeds limit"
        }

    return {
        "success": True
    }


def fraud_check(
    amount: float
):

    if amount > 50000:

        return {
            "flagged": True,
            "message": "High value transaction"
        }

    return {
        "flagged": False
    }