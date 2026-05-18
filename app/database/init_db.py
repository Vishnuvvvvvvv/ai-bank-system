from app.database.database import engine

from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.card import Card
from app.models.beneficiary import Beneficiary
from app.models.loan import Loan
from app.models.audit_log import AuditLog
from app.models.loan_application import LoanApplication
from app.models.employment_profile import EmploymentProfile

User.metadata.create_all(bind=engine)
Account.metadata.create_all(bind=engine)
Transaction.metadata.create_all(bind=engine)
Card.metadata.create_all(bind=engine)
Beneficiary.metadata.create_all(bind=engine)
Loan.metadata.create_all(bind=engine)
LoanApplication.metadata.create_all(bind=engine)
EmploymentProfile.metadata.create_all(bind=engine)
AuditLog.metadata.create_all(bind=engine)

print("All tables created successfully.")