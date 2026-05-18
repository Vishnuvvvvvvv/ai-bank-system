from sqlalchemy import Column, Integer, String, Float
from app.database.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    sender_account = Column(String)

    receiver_account = Column(String)

    amount = Column(Float)

    txn_type = Column(String)

    status = Column(String)

    remarks = Column(String)