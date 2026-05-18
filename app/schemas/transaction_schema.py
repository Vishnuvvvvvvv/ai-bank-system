from pydantic import BaseModel


class TransferRequest(BaseModel):

    receiver_account: str

    amount: float