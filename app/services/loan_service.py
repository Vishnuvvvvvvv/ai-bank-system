from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.document_upload import DocumentUpload
from app.models.employment_profile import EmploymentProfile
from app.models.loan import Loan
from app.models.loan_application import LoanApplication
from app.models.transaction import Transaction
from app.models.user import User


LOAN_RULES = {
    "HOME_LOAN": {
        "minimum_salary": 30000,
        "minimum_balance": 50000,
        "kyc_required": True,
        "healthy_transactions_required": False,
        "required_documents": [
            "SALARY_SLIP",
            "BANK_STATEMENT",
            "KYC",
        ],
    },
    "BIKE_LOAN": {
        "minimum_salary": 20000,
        "minimum_balance": 0,
        "kyc_required": True,
        "healthy_transactions_required": False,
        "required_documents": [
            "SALARY_SLIP",
            "KYC",
        ],
    },
    "PERSONAL_LOAN": {
        "minimum_salary": 25000,
        "minimum_balance": 0,
        "kyc_required": True,
        "healthy_transactions_required": True,
        "required_documents": [
            "SALARY_SLIP",
            "BANK_STATEMENT",
            "KYC",
        ],
    },
    "CAR_LOAN": {
        "minimum_salary": 30000,
        "minimum_balance": 25000,
        "kyc_required": True,
        "healthy_transactions_required": False,
        "required_documents": [
            "SALARY_SLIP",
            "BANK_STATEMENT",
            "KYC",
        ],
    },
}


def normalize_loan_type(loan_type: str | None):

    text = (loan_type or "").upper().replace(" ", "_")

    aliases = {
        "HOME": "HOME_LOAN",
        "HOME_LOAN": "HOME_LOAN",
        "HOUSE_LOAN": "HOME_LOAN",
        "HOUSING_LOAN": "HOME_LOAN",
        "BIKE": "BIKE_LOAN",
        "BIKE_LOAN": "BIKE_LOAN",
        "TWO_WHEELER_LOAN": "BIKE_LOAN",
        "PERSONAL": "PERSONAL_LOAN",
        "PERSONAL_LOAN": "PERSONAL_LOAN",
        "CAR": "CAR_LOAN",
        "CAR_LOAN": "CAR_LOAN",
        "VEHICLE_LOAN": "CAR_LOAN",
    }

    return aliases.get(text, text if text in LOAN_RULES else "PERSONAL_LOAN")


def infer_loan_type_from_query(query: str):

    lowered = query.lower()

    if "home" in lowered or "house" in lowered or "housing" in lowered:
        return "HOME_LOAN"

    if "bike" in lowered or "two wheeler" in lowered:
        return "BIKE_LOAN"

    if "car" in lowered or "vehicle" in lowered:
        return "CAR_LOAN"

    return "PERSONAL_LOAN"

def get_user_loans(
    db: Session,
    user_id: int
):

    return db.query(Loan).filter(
        Loan.user_id == user_id
    ).all()


def calculate_emi(
    principal: float,
    annual_rate: float,
    years: int
):

    monthly_rate = annual_rate / 12 / 100

    months = years * 12

    emi = (
        principal
        * monthly_rate
        * ((1 + monthly_rate) ** months)
    ) / (
        ((1 + monthly_rate) ** months) - 1
    )

    return round(emi, 2)


def check_loan_eligibility(
    salary: float,
    loan_type: str = "PERSONAL_LOAN"
):

    normalized_type = normalize_loan_type(loan_type)
    rule = LOAN_RULES[normalized_type]

    if salary >= rule["minimum_salary"]:
        return {
            "eligible": True,
            "loan_type": normalized_type,
            "max_loan": salary * 60,
            "rule": rule,
        }

    return {
        "eligible": False,
        "loan_type": normalized_type,
        "max_loan": 0,
        "rule": rule,
        "reason": (
            f"Minimum monthly salary for {normalized_type} "
            f"is {rule['minimum_salary']}"
        ),
    }


def _latest_document(db: Session, user_id: int, document_types: list[str]):

    return db.query(DocumentUpload).filter(
        DocumentUpload.user_id == user_id,
        DocumentUpload.document_type.in_(document_types),
    ).order_by(
        DocumentUpload.id.desc()
    ).first()


def _latest_bank_statement(db: Session, user_id: int):
    statement_doc = _latest_document(db, user_id, ["BANK_STATEMENT"])

    if statement_doc:
        return statement_doc

    return db.query(DocumentUpload).filter(
        DocumentUpload.user_id == user_id,
        DocumentUpload.file_name.ilike("%statement%"),
    ).order_by(
        DocumentUpload.id.desc()
    ).first()


def build_financial_profile(db: Session, user_id: int):

    user = db.query(User).filter(User.id == user_id).first()
    account = db.query(Account).filter(Account.user_id == user_id).first()
    employment = db.query(EmploymentProfile).filter(
        EmploymentProfile.user_id == user_id
    ).first()

    salary_doc = _latest_document(db, user_id, ["SALARY_SLIP"])
    statement_doc = _latest_bank_statement(db, user_id)
    kyc_doc = _latest_document(db, user_id, ["AADHAAR", "PAN"])

    account_number = account.account_number if account else None
    transactions = []

    if account_number:
        transactions = db.query(Transaction).filter(
            Transaction.sender_account == account_number
        ).all()

    monthly_salary = None

    if salary_doc and salary_doc.monthly_salary:
        monthly_salary = salary_doc.monthly_salary
    elif employment and employment.monthly_income:
        monthly_salary = employment.monthly_income
    elif statement_doc and statement_doc.monthly_income:
        monthly_salary = statement_doc.monthly_income

    average_balance = None

    if statement_doc and statement_doc.average_balance:
        average_balance = statement_doc.average_balance
    elif account:
        average_balance = account.balance

    failed_transactions = [
        txn
        for txn in transactions
        if txn.status and txn.status.upper() != "SUCCESS"
    ]

    transaction_health = (
        statement_doc.transaction_health
        if statement_doc and statement_doc.transaction_health
        else "UNHEALTHY"
        if failed_transactions
        else "HEALTHY"
    )

    kyc_verified = bool(user and user.kyc_status == "VERIFIED") or bool(
        kyc_doc and kyc_doc.kyc_validity == "VALID"
    )

    return {
        "monthly_salary": monthly_salary or 0,
        "average_balance": average_balance or 0,
        "kyc_verified": kyc_verified,
        "transaction_health": transaction_health,
        "has_salary_document": salary_doc is not None,
        "has_bank_statement": statement_doc is not None,
        "has_kyc_document": kyc_doc is not None,
        "employment_type": (
            employment.employment_type
            if employment and employment.employment_type
            else "SALARIED"
        ),
    }


def evaluate_loan_eligibility(
    db: Session,
    user_id: int,
    loan_type: str,
):

    normalized_type = normalize_loan_type(loan_type)
    rule = LOAN_RULES[normalized_type]
    profile = build_financial_profile(db, user_id)

    missing_documents = []
    rejection_reasons = []

    if "SALARY_SLIP" in rule["required_documents"] and not profile[
        "has_salary_document"
    ]:
        missing_documents.append("SALARY_SLIP")

    if "BANK_STATEMENT" in rule["required_documents"] and not profile[
        "has_bank_statement"
    ]:
        missing_documents.append("BANK_STATEMENT")

    if "KYC" in rule["required_documents"] and not (
        profile["has_kyc_document"] or profile["kyc_verified"]
    ):
        missing_documents.append("AADHAAR_OR_PAN")

    if profile["monthly_salary"] < rule["minimum_salary"]:
        rejection_reasons.append(
            f"Monthly salary must be at least {rule['minimum_salary']}"
        )

    if profile["average_balance"] < rule["minimum_balance"]:
        rejection_reasons.append(
            f"Average balance must be at least {rule['minimum_balance']}"
        )

    if rule["kyc_required"] and not profile["kyc_verified"]:
        rejection_reasons.append("KYC verification is mandatory")

    if (
        rule["healthy_transactions_required"]
        and profile["transaction_health"] != "HEALTHY"
    ):
        rejection_reasons.append("Healthy transaction history is required")

    return {
        "loan_type": normalized_type,
        "eligible": not missing_documents and not rejection_reasons,
        "awaiting_documents": bool(missing_documents),
        "missing_documents": missing_documents,
        "rejection_reasons": rejection_reasons,
        "profile": profile,
        "rules": rule,
    }


def apply_for_loan(
    db: Session,
    user_id: int,
    loan_type: str,
    requested_amount: float,
    annual_income: float,
    employment_type: str
):

    eligibility = evaluate_loan_eligibility(
        db=db,
        user_id=user_id,
        loan_type=loan_type,
    )

    if eligibility["awaiting_documents"]:

        return {
            "success": False,
            "message": "Additional documents are required before applying",
            "awaiting_document_upload": True,
            "missing_documents": eligibility["missing_documents"],
            "eligibility": eligibility,
        }

    if not eligibility["eligible"]:

        return {
            "success": False,
            "message": "Not eligible for loan",
            "rejection_reasons": eligibility["rejection_reasons"],
            "eligibility": eligibility,
        }

    normalized_type = eligibility["loan_type"]
    monthly_salary = eligibility["profile"]["monthly_salary"]
    resolved_income = annual_income or monthly_salary * 12
    resolved_employment_type = (
        employment_type or eligibility["profile"]["employment_type"]
    )

    application = LoanApplication(
        user_id=user_id,
        loan_type=normalized_type,
        requested_amount=requested_amount,
        annual_income=resolved_income,
        employment_type=resolved_employment_type,
        status="PENDING"
    )

    db.add(application)

    db.commit()

    db.refresh(application)

    return {
        "success": True,
        "message": "Loan application submitted",
        "application_id": application.id,
        "status": application.status,
        "eligibility": eligibility,
    }



def get_user_loan_applications(
    db: Session,
    user_id: int
):

    return db.query(
        LoanApplication
    ).filter(
        LoanApplication.user_id == user_id
    ).all()




