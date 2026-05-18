from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    user_id: int,
    action: str,
    status: str,
    ip_address: str = "127.0.0.1"
):

    log = AuditLog(
        user_id=user_id,
        action=action,
        status=status,
        ip_address=ip_address
    )

    db.add(log)

    db.commit()