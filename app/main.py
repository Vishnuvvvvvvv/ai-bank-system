from fastapi import FastAPI
from fastapi import File
from fastapi import Form
from fastapi import UploadFile
from app.services.rag_service import (
    answer_policy_question
)

from sqlalchemy.orm import Session

from fastapi import Depends, HTTPException

from app.database.database import get_db

from app.models.user import User

from app.auth.schemas import (
    LoginRequest,
    TokenResponse
)

from app.auth.hashing import verify_password

from app.auth.jwt_handler import (
    create_access_token
)

from app.auth.dependencies import (
    get_current_user
)
from app.services.account_service import (
    get_account_balance
)

from app.services.transaction_service import (
    transfer_money
)

from app.services.card_service import (
    block_card
)

from app.services.loan_service import (
    get_user_loans
)
from app.models.account import Account

from app.models.account import Account

from app.services.account_service import (
    get_account_balance
)

from app.services.transaction_service import (
    transfer_money,
    get_transactions
)

from app.services.beneficiary_service import (
    add_beneficiary,
    get_beneficiaries
)

from app.services.card_service import (
    block_card,
    activate_card,
    freeze_card
)

from app.services.loan_service import (
    get_user_loans,
    calculate_emi,
    evaluate_loan_eligibility
)

from app.services.audit_service import (
    create_audit_log
)

from app.services.compliance_service import (
    validate_transfer_limit,
    fraud_check
)

from app.schemas.transaction_schema import (
    TransferRequest
)

from app.schemas.beneficiary_schema import (
    AddBeneficiaryRequest
)

from app.schemas.loan_schema import (
    LoanEligibilityRequest,
    EmiCalculationRequest
)
from app.schemas.loan_schema import (
    LoanApplicationRequest
)

from app.schemas.chat_schema import (
    ChatRequest
)


from app.services.loan_service import (
    apply_for_loan
)
from app.services.document_service import (
    get_user_documents,
    process_and_store_document
)
from app.database.database import (
    Base,
    engine
)
from app.models.document_upload import DocumentUpload
from pydantic import BaseModel

from app.agents.supervisor import (
    supervisor_router
)

from app.agents.workflow import (
    graph
)
from uuid import uuid4


app = FastAPI()


@app.on_event("startup")
def create_missing_tables():

    Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"message": "Banking AI Backend Running"}


@app.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == request.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    valid_password = verify_password(
        request.password,
        user.password_hash
    )

    if not valid_password:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(
        {
            "user_id": user.id,
            "email": user.email
        }
    )

    return {
        "access_token": token
    }


@app.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)
):

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role
    }


@app.get("/balance")
def get_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return get_account_balance(
        db,
        current_user.id
    )


@app.post("/transfer")
def transfer(
    request: TransferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    sender_account = db.query(Account).filter(
        Account.user_id == current_user.id
    ).first()

    limit_validation = validate_transfer_limit(
        request.amount
    )

    if not limit_validation["success"]:
        return limit_validation

    fraud_validation = fraud_check(
        request.amount
    )

    result = transfer_money(
        db=db,
        sender_account_number=sender_account.account_number,
        receiver_account_number=request.receiver_account,
        amount=request.amount
    )

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="TRANSFER_MONEY",
        status=result["message"]
    )

    return {
        "fraud_check": fraud_validation,
        "transaction_result": result
    }

@app.get("/transactions")
def transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    account = db.query(Account).filter(
        Account.user_id == current_user.id
    ).first()

    return get_transactions(
        db,
        account.account_number
    )


@app.post("/beneficiaries")
def create_beneficiary(
    request: AddBeneficiaryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return add_beneficiary(
        db=db,
        user_id=current_user.id,
        beneficiary_name=request.beneficiary_name,
        receiver_account=request.receiver_account,
        ifsc_code=request.ifsc_code
    )


@app.get("/beneficiaries")
def list_beneficiaries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return get_beneficiaries(
        db,
        current_user.id
    )


@app.post("/block-card")
def block_my_card(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    account = db.query(Account).filter(
        Account.user_id == current_user.id
    ).first()

    return block_card(
        db,
        account.account_number
    )



@app.post("/freeze-card")
def freeze_my_card(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    account = db.query(Account).filter(
        Account.user_id == current_user.id
    ).first()

    return freeze_card(
        db,
        account.account_number
    )



@app.post("/activate-card")
def activate_my_card(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    account = db.query(Account).filter(
        Account.user_id == current_user.id
    ).first()

    return activate_card(
        db,
        account.account_number
    )

@app.get("/loans")
def loans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return get_user_loans(
        db,
        current_user.id
    )


@app.post("/calculate-emi")
def emi_calculator(
    request: EmiCalculationRequest
):

    emi = calculate_emi(
        principal=request.principal,
        annual_rate=request.annual_rate,
        years=request.years
    )

    return {
        "emi": emi
    }


@app.post("/loan-eligibility")
def loan_eligibility(
    request: LoanEligibilityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return evaluate_loan_eligibility(
        db=db,
        user_id=current_user.id,
        loan_type=request.loan_type
    )


@app.post("/apply-loan")
def apply_loan(
    request: LoanApplicationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    result = apply_for_loan(
        db=db,
        user_id=current_user.id,
        loan_type=request.loan_type,
        requested_amount=request.requested_amount,
        annual_income=request.annual_income,
        employment_type=request.employment_type
    )

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="APPLY_LOAN",
        status=result["message"]
    )

    return result


@app.post("/documents/upload")
async def upload_document(
    document_type: str | None = Form(default=None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return await process_and_store_document(
        db=db,
        user_id=current_user.id,
        file=file,
        document_type=document_type
    )


@app.post("/documents/upload-batch")
async def upload_documents(
    document_type: str | None = Form(default=None),
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    results = []

    for file in files:
        results.append(
            await process_and_store_document(
                db=db,
                user_id=current_user.id,
                file=file,
                document_type=document_type
            )
        )

    return {
        "success": True,
        "processed_count": len(results),
        "documents": results
    }


@app.get("/documents")
def documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    uploads = get_user_documents(
        db,
        current_user.id
    )

    return [
        {
            "document_id": doc.id,
            "document_type": doc.document_type,
            "file_name": doc.file_name,
            "status": doc.status,
            "monthly_salary": doc.monthly_salary,
            "average_balance": doc.average_balance,
            "monthly_income": doc.monthly_income,
            "transaction_health": doc.transaction_health,
            "kyc_validity": doc.kyc_validity,
        }
        for doc in uploads
    ]



@app.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(
        get_current_user
    )
):

    thread_id = (
        request.thread_id
        or str(uuid4())
    )

    initial_state = {

    "user_id": current_user.id,

    "query": request.message
}

    result = await graph.ainvoke(
        initial_state,
        config={
            "configurable": {
                "thread_id": thread_id
            }
        }
    )

    return {
        "thread_id": thread_id,
        "result": result
    }



    

@app.get("/policy/query")
def query_policy(
    question: str
):

    response = answer_policy_question(
        question
    )

    return {
        "question": question,
        "response": response
    }
