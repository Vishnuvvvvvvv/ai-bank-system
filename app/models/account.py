from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.database.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    account_number = Column(String, unique=True)

    account_type = Column(String)

    balance = Column(Float, default=0.0)

    ifsc_code = Column(String)

    status = Column(String, default="ACTIVE")