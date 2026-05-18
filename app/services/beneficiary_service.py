from sqlalchemy.orm import Session

from app.models.beneficiary import Beneficiary


def add_beneficiary(
    db: Session,
    user_id: int,
    beneficiary_name: str,
    receiver_account: str,
    ifsc_code: str
):

    beneficiary = Beneficiary(
        user_id=user_id,
        beneficiary_name=beneficiary_name,
        receiver_account=receiver_account,
        ifsc_code=ifsc_code
    )

    db.add(beneficiary)

    db.commit()

    return {
        "success": True,
        "message": "Beneficiary added"
    }


def get_beneficiaries(
    db: Session,
    user_id: int
):

    return db.query(Beneficiary).filter(
        Beneficiary.user_id == user_id
    ).all()