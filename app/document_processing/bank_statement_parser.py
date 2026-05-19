import re


def _extract_amount(text: str, labels: list[str]) -> float | None:

    for label in labels:
        match = re.search(
            rf"{label}\s*[:=-]?\s*(?:rs\.?|inr)?\s*([0-9,]+(?:\.\d+)?)",
            text,
            flags=re.IGNORECASE,
        )

        if match:
            return float(match.group(1).replace(",", ""))

    return None


def _extract_statement_balances(text: str) -> list[float]:

    balances = []

    for line in text.splitlines():
        if not re.match(r"\s*\d{2}-\d{2}-\d{4}\b", line):
            continue

        amounts = re.findall(r"\d[\d,]*(?:\.\d+)?", line)

        if amounts:
            balances.append(float(amounts[-1].replace(",", "")))

    return balances


def _extract_salary_credits(text: str) -> list[float]:

    credits = []

    for line in text.splitlines():
        if "salary" not in line.lower() and "transfer" not in line.lower():
            continue

        amounts = re.findall(r"\d[\d,]*(?:\.\d+)?", line)

        if len(amounts) >= 2:
            credits.append(float(amounts[-2].replace(",", "")))

    return credits


def parse_bank_statement(text: str) -> dict:

    average_balance = _extract_amount(
        text,
        ["average balance", "avg balance"],
    )

    monthly_income = _extract_amount(
        text,
        ["monthly income", "salary credit", "income"],
    )

    balances = _extract_statement_balances(text)
    salary_credits = _extract_salary_credits(text)

    if average_balance is None and balances:
        average_balance = round(sum(balances) / len(balances), 2)

    if monthly_income is None and salary_credits:
        monthly_income = sum(salary_credits)

    lowered = text.lower()

    if "bounce" in lowered or "failed debit" in lowered:
        transaction_health = "UNHEALTHY"
    else:
        transaction_health = "HEALTHY"

    return {
        "average_balance": average_balance,
        "monthly_income": monthly_income,
        "transaction_health": transaction_health,
    }
