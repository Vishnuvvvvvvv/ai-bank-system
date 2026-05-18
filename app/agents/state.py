from typing import TypedDict
from typing import Optional
from typing import Dict
from typing import Any


class BankingState(
    TypedDict,
    total=False
):

    user_id: int

    query: str

    intent: Optional[str]

    response: Optional[Any]

    authenticated: bool

    awaiting_confirmation: bool

    confirmed: bool

    workflow_data: Dict[str, Any]