from sqlalchemy import Column, Integer, Float, String, ForeignKey
from app.database.database import Base


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    loan_type = Column(String)

    loan_amount = Column(Float)

    interest_rate = Column(Float)

    emi = Column(Float)

    status = Column(String, default="ACTIVE")