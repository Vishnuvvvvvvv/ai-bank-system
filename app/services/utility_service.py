from sqlalchemy.orm import Session

from app.models.account import Account


def validate_account(
    db: Session,
    account_number: str
):

    account = db.query(Account).filter(
        Account.account_number == account_number
    ).first()

    return account is not None