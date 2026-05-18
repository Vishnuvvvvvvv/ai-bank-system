from sqlalchemy.orm import Session

from app.models.user import User

from app.models.account import Account

from app.models.card import Card


def build_user_context(
    db: Session,
    user_id: int
):

    # ==========================================
    # USER
    # ==========================================

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    # ==========================================
    # ACCOUNTS
    # ==========================================

    accounts = db.query(Account).filter(
        Account.user_id == user_id
    ).all()

    # ==========================================
    # CARDS
    # ==========================================

    cards = db.query(Card).join(
        Account,
        Card.account_id == Account.id
    ).filter(
        Account.user_id == user_id
    ).all()

    return {

        "user": {
            "id": user.id,
            "name": user.name,
            "kyc_status": user.kyc_status
        },

        "accounts": [
            {
                "account_number": acc.account_number,
                "account_type": acc.account_type,
                "balance": acc.balance,
                "status": acc.status
            }
            for acc in accounts
        ],

        "cards": [
            {
                "card_number": card.card_number[-4:],
                "status": card.status
            }
            for card in cards
        ]
    }