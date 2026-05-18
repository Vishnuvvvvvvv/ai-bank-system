from sqlalchemy.orm import Session

from app.models.card import Card

from app.models.account import Account


def block_card(
    db: Session,
    account_number: str
):

    account = db.query(Account).filter(
        Account.account_number == account_number
    ).first()

    if not account:
        return {
            "success": False,
            "message": "Account not found"
        }

    card = db.query(Card).filter(
        Card.account_id == account.id
    ).first()

    if not card:
        return {
            "success": False,
            "message": "Card not found"
        }

    card.status = "BLOCKED"

    db.commit()

    return {
        "success": True,
        "message": "Card blocked"
    }


def activate_card(
    db: Session,
    account_number: str
):

    account = db.query(Account).filter(
        Account.account_number == account_number
    ).first()

    card = db.query(Card).filter(
        Card.account_id == account.id
    ).first()

    card.status = "ACTIVE"

    db.commit()

    return {
        "success": True,
        "message": "Card activated"
    }


def freeze_card(
    db: Session,
    account_number: str
):

    account = db.query(Account).filter(
        Account.account_number == account_number
    ).first()

    card = db.query(Card).filter(
        Card.account_id == account.id
    ).first()

    card.status = "FROZEN"

    db.commit()

    return {
        "success": True,
        "message": "Card frozen"
    }