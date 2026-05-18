from fastmcp import FastMCP

from app.database.database import SessionLocal

# =========================================================
# ACCOUNT SERVICES
# =========================================================

from app.services.account_service import (
    get_account_balance,
    get_user_accounts,
    create_new_account,
    get_user_profile
)

# =========================================================
# TRANSACTION SERVICES
# =========================================================

from app.services.transaction_service import (
    transfer_money,
    get_transactions
)

# =========================================================
# CARD SERVICES
# =========================================================

from app.services.card_service import (
    block_card,
    activate_card,
    freeze_card
)

# =========================================================
# LOAN SERVICES
# =========================================================

from app.services.loan_service import (
    get_user_loans,
    calculate_emi,
    check_loan_eligibility,
    apply_for_loan,
    get_user_loan_applications
)

# =========================================================
# BENEFICIARY SERVICES
# =========================================================

from app.services.beneficiary_service import (
    add_beneficiary,
    get_beneficiaries
)

# =========================================================
# AUDIT SERVICES
# =========================================================

from app.services.audit_service import (
    create_audit_log
)

# =========================================================
# MCP SERVER
# =========================================================

mcp = FastMCP("Unified Banking MCP Server")

# =========================================================
# ACCOUNT TOOLS
# =========================================================


@mcp.tool()
def get_balance(user_id: int):
    """
    Retrieve the current bank account balance for a user.

    Use this tool when:
    - user asks for account balance
    - user asks available funds
    - user asks savings balance
    - user asks current balance

    Parameters:
    - user_id: authenticated banking user ID

    Example Queries:
    - What is my balance?
    - Show my account balance
    - How much money do I have?
    """

    db = SessionLocal()

    result = get_account_balance(
        db,
        user_id
    )

    db.close()

    return result


@mcp.tool()
def get_accounts(user_id: int):
    """
    Retrieve all bank accounts associated with a user.

    Use this tool when:
    - user asks account details
    - user wants account list
    - user asks linked accounts

    Parameters:
    - user_id: authenticated banking user ID

    Example Queries:
    - Show all my accounts
    - List my bank accounts
    - What accounts do I have?
    """

    db = SessionLocal()

    result = get_user_accounts(
        db,
        user_id
    )

    db.close()

    return [
        {
            "account_number": acc.account_number,
            "balance": acc.balance,
            "account_type": acc.account_type,
            "status": acc.status
        }
        for acc in result
    ]


@mcp.tool()
def create_account(
    user_id: int,
    account_type: str
):
    """
    Create a new bank account for a user.

    Use this tool when:
    - user wants to open new account
    - user requests savings/current account

    Parameters:
    - user_id: authenticated banking user ID
    - account_type: SAVINGS or CURRENT

    Example Queries:
    - Open a savings account
    - Create a new bank account
    - I want a current account
    """

    db = SessionLocal()

    result = create_new_account(
        db,
        user_id,
        account_type
    )

    db.close()

    return {
        "account_number": result.account_number,
        "account_type": result.account_type,
        "status": result.status
    }


@mcp.tool()
def profile(user_id: int):
    """
    Retrieve customer profile information.

    Use this tool when:
    - user asks profile details
    - user asks KYC information
    - user asks personal banking details

    Parameters:
    - user_id: authenticated banking user ID

    Example Queries:
    - Show my profile
    - What is my KYC status?
    - Show my account details
    """

    db = SessionLocal()

    user = get_user_profile(
        db,
        user_id
    )

    db.close()

    return {
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "kyc_status": user.kyc_status
    }


# =========================================================
# TRANSACTION TOOLS
# =========================================================


@mcp.tool()
def transfer(
    sender_account: str,
    receiver_account: str,
    amount: float
):
    """
    Transfer money between bank accounts.

    Use this tool when:
    - user wants to send money
    - transfer funds
    - pay another user
    - move money

    Parameters:
    - sender_account: sender bank account number
    - receiver_account: receiver bank account number
    - amount: transfer amount

    Example Queries:
    - Transfer 5000 to Rahul
    - Send money to SB10002
    - Pay 1000 to John
    """

    db = SessionLocal()

    result = transfer_money(
        db,
        sender_account,
        receiver_account,
        amount
    )

    create_audit_log(
        db=db,
        user_id=1,
        action="TRANSFER_MONEY",
        status=result["message"]
    )

    db.close()

    return result


@mcp.tool()
def transactions(account_number: str):
    """
    Retrieve transaction history for a bank account.

    Use this tool when:
    - user asks recent transactions
    - user asks payment history
    - user asks transfer history

    Parameters:
    - account_number: bank account number

    Example Queries:
    - Show my last transactions
    - Transaction history
    - Recent payments
    """

    db = SessionLocal()

    result = get_transactions(
        db,
        account_number
    )

    db.close()

    return [
        {
            "sender": txn.sender_account,
            "receiver": txn.receiver_account,
            "amount": txn.amount,
            "status": txn.status,
            "remarks": txn.remarks
        }
        for txn in result
    ]


# =========================================================
# BENEFICIARY TOOLS
# =========================================================


@mcp.tool()
def add_beneficiary_tool(
    user_id: int,
    beneficiary_name: str,
    receiver_account: str,
    ifsc_code: str
):
    """
    Add a beneficiary/payee for future money transfers.

    Use this tool when:
    - user wants to save payee
    - user adds beneficiary
    - user stores receiver details

    Parameters:
    - user_id: authenticated banking user ID
    - beneficiary_name: saved beneficiary nickname
    - receiver_account: receiver account number
    - ifsc_code: bank IFSC code

    Example Queries:
    - Add Rahul as beneficiary
    - Save a payee
    - Add new transfer recipient
    """

    db = SessionLocal()

    result = add_beneficiary(
        db,
        user_id,
        beneficiary_name,
        receiver_account,
        ifsc_code
    )

    db.close()

    return result


@mcp.tool()
def beneficiaries(user_id: int):
    """
    Retrieve saved beneficiaries/payees for a user.

    Use this tool when:
    - user asks saved payees
    - user asks beneficiaries
    - user asks transfer recipients

    Parameters:
    - user_id: authenticated banking user ID

    Example Queries:
    - Show my beneficiaries
    - List my payees
    - Saved recipients
    """

    db = SessionLocal()

    result = get_beneficiaries(
        db,
        user_id
    )

    db.close()

    return [
        {
            "beneficiary_name": b.beneficiary_name,
            "receiver_account": b.receiver_account,
            "ifsc_code": b.ifsc_code
        }
        for b in result
    ]


# =========================================================
# CARD TOOLS
# =========================================================


@mcp.tool()
def block(account_number: str):
    """
    Block or disable a debit/ATM card.

    Use this tool when:
    - card is lost
    - suspicious activity detected
    - user wants to disable card

    Parameters:
    - account_number: customer account number

    Example Queries:
    - Block my ATM card
    - Disable my debit card
    - My card is lost
    """

    db = SessionLocal()

    result = block_card(
        db,
        account_number
    )

    db.close()

    return result


@mcp.tool()
def activate(account_number: str):
    """
    Activate a debit or ATM card.

    Use this tool when:
    - user activates new card
    - user reactivates card

    Parameters:
    - account_number: customer account number

    Example Queries:
    - Activate my card
    - Enable my ATM card
    - Start my debit card
    """

    db = SessionLocal()

    result = activate_card(
        db,
        account_number
    )

    db.close()

    return result


@mcp.tool()
def freeze(account_number: str):
    """
    Temporarily freeze a debit or ATM card.

    Use this tool when:
    - user wants temporary freeze
    - suspicious activity detected
    - user traveling internationally

    Parameters:
    - account_number: customer account number

    Example Queries:
    - Freeze my card
    - Temporarily disable my debit card
    - Pause my ATM card
    """

    db = SessionLocal()

    result = freeze_card(
        db,
        account_number
    )

    db.close()

    return result


# =========================================================
# LOAN TOOLS
# =========================================================


@mcp.tool()
def loans(user_id: int):
    """
    Retrieve all approved loans associated with a user.

    Use this tool when:
    - user asks active loans
    - user asks loan details
    - user asks EMI information

    Parameters:
    - user_id: authenticated banking user ID

    Example Queries:
    - Show my loans
    - Active loan details
    - My EMI information
    """

    db = SessionLocal()

    result = get_user_loans(
        db,
        user_id
    )

    db.close()

    return [
        {
            "loan_type": loan.loan_type,
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "emi": loan.emi,
            "status": loan.status
        }
        for loan in result
    ]


@mcp.tool()
def emi(
    principal: float,
    annual_rate: float,
    years: int
):
    """
    Calculate EMI for a loan.

    Use this tool when:
    - user asks EMI calculation
    - user estimates loan repayment
    - user compares loan plans

    Parameters:
    - principal: loan amount
    - annual_rate: yearly interest rate
    - years: loan duration

    Example Queries:
    - Calculate EMI for 10 lakh loan
    - EMI for home loan
    - Monthly payment estimate
    """

    return calculate_emi(
        principal,
        annual_rate,
        years
    )


@mcp.tool()
def eligibility(salary: float):
    """
    Check loan eligibility based on salary.

    Use this tool when:
    - user asks loan eligibility
    - user checks borrowing capacity
    - user asks maximum loan amount

    Parameters:
    - salary: monthly salary

    Example Queries:
    - Am I eligible for loan?
    - Maximum loan amount for my salary
    - Can I get a home loan?
    """

    return check_loan_eligibility(
        salary
    )


@mcp.tool()
def apply_loan(
    user_id: int,
    loan_type: str,
    requested_amount: float,
    annual_income: float,
    employment_type: str
):
    """
    Submit a new loan application.

    Supported loan types:
    - HOME_LOAN
    - PERSONAL_LOAN
    - VEHICLE_LOAN
    - EDUCATION_LOAN
    - BUSINESS_LOAN
    - GOLD_LOAN

    Use this tool when:
    - user wants loan application
    - user applies for loan
    - user requests financing

    Parameters:
    - user_id: authenticated banking user ID
    - loan_type: category of loan
    - requested_amount: requested loan amount
    - annual_income: yearly income
    - employment_type: SALARIED or SELF_EMPLOYED

    Example Queries:
    - Apply for home loan
    - I need personal loan
    - Apply for car loan
    """

    db = SessionLocal()

    result = apply_for_loan(
        db,
        user_id,
        loan_type,
        requested_amount,
        annual_income,
        employment_type
    )

    create_audit_log(
        db=db,
        user_id=user_id,
        action="APPLY_LOAN",
        status=result["message"]
    )

    db.close()

    return result



@mcp.tool()
def loan_applications(user_id: int):
    """
    Retrieve all loan applications submitted by a user.

    Includes:
    - pending applications
    - approved applications
    - rejected applications
    - under review applications

    Use this tool when:
    - user asks applied loans
    - user asks pending loans
    - user asks rejected loans
    - user asks loan application status
    """

    db = SessionLocal()

    result = get_user_loan_applications(
        db,
        user_id
    )

    db.close()

    return [
        {
            "application_id": app.id,
            "loan_type": app.loan_type,
            "requested_amount": app.requested_amount,
            "status": app.status,
            "annual_income": app.annual_income,
            "employment_type": app.employment_type
        }
        for app in result
    ]

if __name__ == "__main__":
    mcp.run()