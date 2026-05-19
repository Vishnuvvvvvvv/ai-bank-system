import json
import re
from typing import Any

from app.agents.llm import llm


def extract_document_fields_with_llm(
    text: str,
    document_type: str,
) -> dict[str, Any]:
    """Extract structured fields from uploaded banking documents.

    The deterministic parsers remain the fallback because local/dev test data
    should still work if the LLM provider is unavailable.
    """

    if not text.strip():
        return {}

    prompt = f"""
Extract banking document fields as strict JSON only.

Document type: {document_type}

Return only these keys when available:
- employee_name
- name
- employer
- salary
- average_balance
- monthly_income
- transaction_health
- dob
- kyc_validity

Rules:
- salary, average_balance, and monthly_income must be numbers.
- transaction_health must be HEALTHY or UNHEALTHY.
- kyc_validity must be VALID or INVALID.
- Use null for unknown values.
- Do not include markdown fences or explanation.

Document text:
{text}
"""

    try:
        response = llm.invoke(prompt)
    except Exception:
        return {}

    content = getattr(response, "content", response)
    if isinstance(content, list):
        content = " ".join(
            item.get("text", "") if isinstance(item, dict) else str(item)
            for item in content
        )

    raw = str(content).strip()
    match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if match:
        raw = match.group(0)

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}

    if not isinstance(parsed, dict):
        return {}

    cleaned = {
        key: value
        for key, value in parsed.items()
        if value not in (None, "", [])
    }

    for amount_key in ["salary", "average_balance", "monthly_income"]:
        if amount_key in cleaned:
            cleaned[amount_key] = _coerce_float(cleaned[amount_key])

    for text_key in ["transaction_health", "kyc_validity"]:
        if text_key in cleaned and isinstance(cleaned[text_key], str):
            cleaned[text_key] = cleaned[text_key].upper()

    return {
        key: value
        for key, value in cleaned.items()
        if value is not None
    }


def _coerce_float(value: Any) -> float | None:

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        match = re.search(r"\d[\d,]*(?:\.\d+)?", value)
        if match:
            return float(match.group(0).replace(",", ""))

    return None
