from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.database import Base


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)

    account_id = Column(Integer, ForeignKey("accounts.id"))

    card_number = Column(String, unique=True)

    card_type = Column(String)

    expiry_date = Column(String)

    status = Column(String, default="ACTIVE")