from sqlalchemy.orm import Session

from app.models.loan import Loan
from app.models.loan_application import LoanApplication

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
    salary: float
):

    if salary >= 50000:
        return {
            "eligible": True,
            "max_loan": salary * 60
        }

    return {
        "eligible": False,
        "max_loan": 0
    }


def apply_for_loan(
    db: Session,
    user_id: int,
    loan_type: str,
    requested_amount: float,
    annual_income: float,
    employment_type: str
):

    eligibility = check_loan_eligibility(
        annual_income / 12
    )

    if not eligibility["eligible"]:

        return {
            "success": False,
            "message": "Not eligible for loan"
        }

    application = LoanApplication(
        user_id=user_id,
        loan_type=loan_type,
        requested_amount=requested_amount,
        annual_income=annual_income,
        employment_type=employment_type,
        status="PENDING"
    )

    db.add(application)

    db.commit()

    db.refresh(application)

    return {
        "success": True,
        "message": "Loan application submitted",
        "application_id": application.id,
        "status": application.status
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




