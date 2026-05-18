from sqlalchemy.orm import Session

from app.models.account import Account

from app.models.transaction import Transaction


def transfer_money(
    db: Session,
    sender_account_number: str,
    receiver_account_number: str,
    amount: float
):

    sender = db.query(Account).filter(
        Account.account_number == sender_account_number
    ).first()

    receiver = db.query(Account).filter(
        Account.account_number == receiver_account_number
    ).first()

    if not sender:
        return {
            "success": False,
            "message": "Sender account not found"
        }

    if not receiver:
        return {
            "success": False,
            "message": "Receiver account not found"
        }

    if sender.balance < amount:
        return {
            "success": False,
            "message": "Insufficient balance"
        }

    sender.balance -= amount

    receiver.balance += amount

    transaction = Transaction(
        sender_account=sender.account_number,
        receiver_account=receiver.account_number,
        amount=amount,
        txn_type="TRANSFER",
        status="SUCCESS",
        remarks="AI Banking Transfer"
    )

    db.add(transaction)

    db.commit()

    return {
        "success": True,
        "message": "Transfer successful",
        "remaining_balance": sender.balance
    }


def get_transactions(
    db: Session,
    account_number: str
):

    return db.query(Transaction).filter(
        Transaction.sender_account == account_number
    ).all()