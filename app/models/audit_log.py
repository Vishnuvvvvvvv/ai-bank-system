from sqlalchemy import Column, Integer, String
from app.database.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer)

    action = Column(String)

    status = Column(String)

    ip_address = Column(String)