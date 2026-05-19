from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from app.database.database import Base


class DocumentUpload(Base):

    __tablename__ = "document_uploads"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), index=True)

    document_type = Column(String, index=True)

    file_name = Column(String)

    extracted_text = Column(Text)

    extracted_name = Column(String)

    employer = Column(String)

    monthly_salary = Column(Float)

    average_balance = Column(Float)

    monthly_income = Column(Float)

    transaction_health = Column(String)

    dob = Column(String)

    kyc_validity = Column(String)

    status = Column(String, default="PROCESSED")
