from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.database import Base


class Beneficiary(Base):
    __tablename__ = "beneficiaries"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    beneficiary_name = Column(String)

    receiver_account = Column(String)

    ifsc_code = Column(String)

    verified = Column(String, default="YES")