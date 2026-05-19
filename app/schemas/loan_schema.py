from pydantic import BaseModel


class LoanEligibilityRequest(BaseModel):

    loan_type: str


class EmiCalculationRequest(BaseModel):

    principal: float

    annual_rate: float

    years: int


class LoanApplicationRequest(BaseModel):

    loan_type: str

    requested_amount: float = 0

    annual_income: float = 0

    employment_type: str = ""
