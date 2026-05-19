def is_confirmation(
    query: str
):

    normalized = query.lower().strip()

    confirmations = [
        "confirm",
        "yes",
        "proceed",
        "continue",
        "ok",
        "okay",
    ]

    return (
        normalized in confirmations
        or any(word in normalized.split() for word in confirmations)
    )
