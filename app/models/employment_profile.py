from sqlalchemy import Column, Integer, String, Float, ForeignKey

from app.database.database import Base


class EmploymentProfile(Base):

    __tablename__ = "employment_profiles"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    company_name = Column(String)

    employment_type = Column(String)

    monthly_income = Column(Float)

    experience_years = Column(Integer)