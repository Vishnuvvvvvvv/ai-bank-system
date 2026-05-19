import re


def _extract_value(text: str, labels: list[str]) -> str | None:

    for label in labels:
        match = re.search(
            rf"{label}\s*[:=-]?\s*([A-Za-z0-9 /.-]+)",
            text,
            flags=re.IGNORECASE,
        )

        if match:
            return match.group(1).strip()

    return None


def validate_kyc_document(text: str, document_type: str) -> dict:

    lowered = text.lower()
    has_identifier = (
        document_type == "AADHAAR"
        and bool(re.search(r"\d{4}\s?\d{4}\s?\d{4}", text))
    ) or (
        document_type == "PAN"
        and bool(re.search(r"[A-Z]{5}\d{4}[A-Z]", text.upper()))
    )

    is_valid = has_identifier or "valid" in lowered

    return {
        "name": _extract_value(text, ["name", "customer name"]),
        "dob": _extract_value(text, ["dob", "date of birth"]),
        "kyc_validity": "VALID" if is_valid else "REVIEW_REQUIRED",
    }
