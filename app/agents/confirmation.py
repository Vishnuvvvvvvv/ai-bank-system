def is_confirmation(
    query: str
):

    confirmations = [
        "confirm",
        "yes",
        "proceed",
        "continue",
        "ok"
    ]

    return query.lower().strip() in confirmations