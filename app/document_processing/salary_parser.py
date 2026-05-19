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


def _extract_company_name(text: str) -> str | None:

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for line in lines:
        lowered = line.lower()

        if any(
            marker in lowered
            for marker in ["pvt", "ltd", "limited", "technologies", "solutions"]
        ):
            return line

    return None


def _extract_value(text: str, labels: list[str]) -> str | None:

    for label in labels:
        match = re.search(
            rf"{label}\s*[:=-]?\s*([A-Za-z .&]+)",
            text,
            flags=re.IGNORECASE,
        )

        if match:
            return match.group(1).strip()

    return None


def parse_salary_slip(text: str) -> dict:

    return {
        "salary": _extract_amount(
            text,
            ["net salary", "gross salary", "monthly salary", "basic salary", "salary"],
        ),
        "employer": _extract_value(
            text,
            ["employer", "company", "organization"],
        ) or _extract_company_name(text),
        "employee_name": _extract_value(
            text,
            ["employee name", "name"],
        ),
    }
