from app.database.database import SessionLocal

from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.card import Card
from app.models.beneficiary import Beneficiary
from app.models.loan import Loan
from app.auth.hashing import hash_password
from app.models.employment_profile import EmploymentProfile


db = SessionLocal()

# =========================
# USERS
# =========================

user1 = User(
    name="Vishnu",
    email="vishnu@test.com",
    phone="9999999999",
    password_hash=hash_password("password123"),
    kyc_status="VERIFIED"
)

user2 = User(
    name="Rahul",
    email="rahul@test.com",
    phone="8888888888",
    password_hash=hash_password("password123"),
    kyc_status="VERIFIED"
)

db.add(user1)
db.add(user2)

db.commit()

db.refresh(user1)
db.refresh(user2)

# =========================
# ACCOUNTS
# =========================

account1 = Account(
    user_id=user1.id,
    account_number="SB10001",
    account_type="SAVINGS",
    balance=75000,
    ifsc_code="BANK0001"
)

account2 = Account(
    user_id=user2.id,
    account_number="SB10002",
    account_type="SAVINGS",
    balance=45000,
    ifsc_code="BANK0001"
)

db.add(account1)
db.add(account2)

db.commit()

db.refresh(account1)
db.refresh(account2)

# =========================
# TRANSACTIONS
# =========================

txn1 = Transaction(
    sender_account="SB10001",
    receiver_account="SB10002",
    amount=5000,
    txn_type="TRANSFER",
    status="SUCCESS",
    remarks="Rent Payment"
)

txn2 = Transaction(
    sender_account="SB10002",
    receiver_account="SB10001",
    amount=2000,
    txn_type="TRANSFER",
    status="SUCCESS",
    remarks="Food Split"
)

db.add(txn1)
db.add(txn2)

# =========================
# CARDS
# =========================

card1 = Card(
    account_id=account1.id,
    card_number="4111111111111111",
    card_type="DEBIT",
    expiry_date="12/30",
    status="ACTIVE"
)

db.add(card1)

# =========================
# BENEFICIARIES
# =========================

beneficiary1 = Beneficiary(
    user_id=user1.id,
    beneficiary_name="Rahul",
    receiver_account="SB10002",
    ifsc_code="BANK0001"
)

db.add(beneficiary1)

# =========================
# LOANS
# =========================

loan1 = Loan(
    user_id=user1.id,
    loan_type="HOME_LOAN",
    loan_amount=2500000,
    interest_rate=8.5,
    emi=24500,
    status="ACTIVE"
)

db.add(loan1)

employment1 = EmploymentProfile(
    user_id=user1.id,
    company_name="Infosys",
    employment_type="SALARIED",
    monthly_income=85000,
    experience_years=4
)

db.add(employment1)

db.commit()

print("Seed data inserted successfully.")