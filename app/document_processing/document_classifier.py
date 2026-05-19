from typing import Literal

DocumentType = Literal[
    "SALARY_SLIP",
    "AADHAAR",
    "PAN",
    "BANK_STATEMENT",
]


def classify_document(text: str, file_name: str = "") -> DocumentType:

    haystack = f"{file_name} {text}".lower()

    if (
        "bank statement" in haystack
        or "account holder" in haystack
        or "ifsc code" in haystack
        or "date description debit credit balance" in haystack
        or "upi/pos transaction" in haystack
        or "statement" in haystack
        or "transaction" in haystack
    ):
        return "BANK_STATEMENT"

    if "salary" in haystack or "payslip" in haystack:
        return "SALARY_SLIP"

    if "aadhaar" in haystack or "aadhar" in haystack:
        return "AADHAAR"

    if "pan" in haystack:
        return "PAN"

    return "BANK_STATEMENT"
