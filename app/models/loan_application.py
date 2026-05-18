from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import ForeignKey

from app.database.database import Base


class LoanApplication(Base):

    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    loan_type = Column(String)

    requested_amount = Column(Float)

    annual_income = Column(Float)

    employment_type = Column(String)

    status = Column(String, default="PENDING")