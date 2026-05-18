from sqlalchemy.orm import Session

from app.models.account import Account


def get_primary_account(
    db: Session,
    user_id: int
):

    account = db.query(Account).filter(
        Account.user_id == user_id
    ).first()

    return account