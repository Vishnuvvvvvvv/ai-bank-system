from sqlalchemy.orm import Session

from app.models.account import Account

from app.models.user import User


def get_user_accounts(
    db: Session,
    user_id: int
):

    return db.query(Account).filter(
        Account.user_id == user_id
    ).all()


def get_account_balance(
    db: Session,
    user_id: int
):

    account = db.query(Account).filter(
        Account.user_id == user_id
    ).first()

    if not account:
        return None

    return {
        "account_number": account.account_number,
        "balance": account.balance,
        "account_type": account.account_type
    }


def create_new_account(
    db: Session,
    user_id: int,
    account_type: str
):

    account = Account(
        user_id=user_id,
        account_number=f"SB{user_id}000",
        account_type=account_type,
        balance=0,
        ifsc_code="BANK0001",
        status="ACTIVE"
    )

    db.add(account)

    db.commit()

    db.refresh(account)

    return account


def get_user_profile(
    db: Session,
    user_id: int
):

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    return user