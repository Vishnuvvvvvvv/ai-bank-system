from pydantic import BaseModel


class LoanEligibilityRequest(BaseModel):

    salary: float


class EmiCalculationRequest(BaseModel):

    principal: float

    annual_rate: float

    years: int


class LoanApplicationRequest(BaseModel):

    loan_type: str

    requested_amount: float

    annual_income: float

    employment_type: str