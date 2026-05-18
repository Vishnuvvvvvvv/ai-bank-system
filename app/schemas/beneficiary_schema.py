from pydantic import BaseModel


class AddBeneficiaryRequest(BaseModel):

    beneficiary_name: str

    receiver_account: str

    ifsc_code: str