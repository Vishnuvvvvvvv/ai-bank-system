# Sample Test Flows

## Loan Application Pauses For Missing Documents

1. Login as `vishnu@test.com` with password `password123`.
2. Call `POST /chat` with:

```json
{
  "message": "Apply for home loan"
}
```

Expected result:
- Intent resolves to `APPLY_LOAN`.
- No loan application is created.
- Response includes `awaiting_document_upload: true`.
- Response includes missing documents such as `SALARY_SLIP` and `BANK_STATEMENT`.

## Upload Salary Slip

1. Call `POST /documents/upload` as multipart form-data.
2. Set `document_type` to `SALARY_SLIP`.
3. Upload a text file containing:

```text
Employee Name: Vishnu
Employer: Infosys
Net Salary: 85000
```

Expected result:
- Document is stored as `SALARY_SLIP`.
- Monthly salary is extracted as `85000`.
- Employment profile is updated deterministically.

## Upload Bank Statement

1. Call `POST /documents/upload` as multipart form-data.
2. Set `document_type` to `BANK_STATEMENT`.
3. Upload a text file containing:

```text
Average Balance: 74400
Monthly Income: 85000
Transaction Health: Healthy
```

Expected result:
- Document is stored as `BANK_STATEMENT`.
- Average balance and monthly income are extracted.
- Transaction health is `HEALTHY`.

## Continue Loan Application

1. Call `POST /chat` with the same `thread_id` from the first chat response.
2. Send:

```json
{
  "message": "Apply for home loan",
  "thread_id": "<same-thread-id>"
}
```

Expected result:
- Eligibility is evaluated by `loan_service.py`.
- If salary, balance, KYC, and documents pass, the assistant asks whether to proceed with submitting the loan application.
- If a rule fails, the response includes deterministic rejection reasons.

## Confirm Loan Submission

1. Call `POST /chat` with the same `thread_id`.
2. Send:

```json
{
  "message": "yes",
  "thread_id": "<same-thread-id>"
}
```

Expected result:
- A `loan_applications` row is created only after this confirmation.
- The response includes the submitted application id and status.

## FAQ And Policy RAG

1. Call `POST /chat` with `What documents are needed for KYC?`.
2. Call `POST /chat` with `What are bike loan rules?`.

Expected result:
- RAG answers from Chroma policy documents.
- RAG explains policy only and does not approve or reject loans.
