from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.document_processing.bank_statement_parser import parse_bank_statement
from app.document_processing.document_classifier import classify_document
from app.document_processing.llm_field_extractor import extract_document_fields_with_llm
from app.document_processing.kyc_validator import validate_kyc_document
from app.document_processing.ocr_service import extract_text_from_upload
from app.document_processing.salary_parser import parse_salary_slip
from app.models.document_upload import DocumentUpload
from app.models.employment_profile import EmploymentProfile
from app.models.user import User


def resolve_document_type(
    extracted_text: str,
    file_name: str,
    requested_type: str | None,
) -> str:
    detected_type = classify_document(
        extracted_text,
        file_name,
    )

    if not requested_type:
        return detected_type

    # Mixed uploads are common in the UI. If the user-selected type conflicts
    # with clear file content, trust the content so loan evidence is not stored
    # under the wrong document type.
    if requested_type != detected_type and _has_strong_type_signal(
        extracted_text,
        file_name,
        detected_type,
    ):
        return detected_type

    return requested_type


def _has_strong_type_signal(
    text: str,
    file_name: str,
    document_type: str,
) -> bool:
    haystack = f"{file_name} {text}".lower()

    signals = {
        "BANK_STATEMENT": [
            "bank statement",
            "account holder",
            "ifsc code",
            "date description debit credit balance",
            "upi/pos transaction",
        ],
        "SALARY_SLIP": [
            "salary slip",
            "employee name",
            "gross salary",
            "net salary",
            "basic salary",
        ],
        "AADHAAR": [
            "aadhaar",
            "aadhar",
        ],
        "PAN": [
            "pan number",
        ],
    }

    return any(signal in haystack for signal in signals.get(document_type, []))


def _clean_llm_value(value):
    if value in (None, "", []):
        return None

    if isinstance(value, (int, float)) and value == 0:
        return None

    return value


async def process_and_store_document(
    db: Session,
    user_id: int,
    file: UploadFile,
    document_type: str | None = None,
):

    extracted_text = await extract_text_from_upload(file)
    resolved_type = resolve_document_type(
        extracted_text,
        file.filename,
        document_type,
    )

    parsed = extract_document_fields_with_llm(
        extracted_text,
        resolved_type,
    )
    fallback = {}

    if resolved_type == "SALARY_SLIP":
        fallback = parse_salary_slip(extracted_text)
    elif resolved_type == "BANK_STATEMENT":
        fallback = parse_bank_statement(extracted_text)
    elif resolved_type in ["AADHAAR", "PAN"]:
        fallback = validate_kyc_document(extracted_text, resolved_type)

    parsed = {
        **fallback,
        **{
            key: value
            for key, value in parsed.items()
            if _clean_llm_value(value) is not None
        },
    }

    upload = DocumentUpload(
        user_id=user_id,
        document_type=resolved_type,
        file_name=file.filename,
        extracted_text=extracted_text,
        extracted_name=parsed.get("employee_name") or parsed.get("name"),
        employer=parsed.get("employer"),
        monthly_salary=parsed.get("salary"),
        average_balance=parsed.get("average_balance"),
        monthly_income=parsed.get("monthly_income"),
        transaction_health=parsed.get("transaction_health"),
        dob=parsed.get("dob"),
        kyc_validity=parsed.get("kyc_validity"),
        status="PROCESSED",
    )

    db.add(upload)

    if resolved_type == "SALARY_SLIP" and parsed.get("salary"):
        employment = db.query(EmploymentProfile).filter(
            EmploymentProfile.user_id == user_id
        ).first()

        if not employment:
            employment = EmploymentProfile(
                user_id=user_id,
                employment_type="SALARIED",
                experience_years=0,
            )
            db.add(employment)

        employment.monthly_income = parsed["salary"]
        employment.company_name = parsed.get("employer")

    if resolved_type in ["AADHAAR", "PAN"] and parsed.get("kyc_validity") == "VALID":
        user = db.query(User).filter(User.id == user_id).first()

        if user:
            user.kyc_status = "VERIFIED"

    db.commit()
    db.refresh(upload)

    return {
        "success": True,
        "document_id": upload.id,
        "document_type": upload.document_type,
        "file_name": upload.file_name,
        "parsed_data": parsed,
    }


def get_user_documents(db: Session, user_id: int):

    return db.query(DocumentUpload).filter(
        DocumentUpload.user_id == user_id
    ).all()
