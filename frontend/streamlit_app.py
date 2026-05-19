from __future__ import annotations

import json
from typing import Any

import pandas as pd
import streamlit as st

from api_client import BankingApiClient
from api_client import BankingApiError


DEFAULT_API_URL = "http://127.0.0.1:8000"
DOCUMENT_TYPES = {
    "Auto detect": None,
    "Salary slip": "SALARY_SLIP",
    "Aadhaar": "AADHAAR",
    "PAN": "PAN",
    "Bank statement": "BANK_STATEMENT",
}
LOAN_TYPES = {
    "Home loan": "HOME_LOAN",
    "Bike loan": "BIKE_LOAN",
    "Personal loan": "PERSONAL_LOAN",
    "Car loan": "CAR_LOAN",
}


def configure_page() -> None:
    st.set_page_config(
        page_title="Agentic Banking AI",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #f8fafc 0%, #eef6f3 52%, #f7f4ef 100%);
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #102826 0%, #1c403a 100%);
            border-right: 1px solid rgba(255,255,255,.08);
        }
        [data-testid="stSidebar"] * {
            color: #f6fbfa;
        }
        .block-container {
            padding-top: 2rem;
            max-width: 1180px;
        }
        h1, h2, h3 {
            letter-spacing: 0;
            color: #17312e;
        }
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #dce7e4;
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 12px 28px rgba(15, 40, 38, .07);
        }
        [data-testid="stChatMessage"] {
            background: rgba(255,255,255,.94);
            border: 1px solid #dbe7e4;
            border-radius: 8px;
            padding: .8rem 1rem;
            box-shadow: 0 10px 24px rgba(15, 40, 38, .06);
        }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            background: #f0f7ff;
            border-color: #cfe2f7;
        }
        [data-testid="stChatMessage"] p {
            line-height: 1.55;
        }
        [data-testid="stChatInput"] {
            border: 1px solid #cbdcd8;
            border-radius: 8px;
        }
        .bank-panel {
            background: rgba(255,255,255,.92);
            border: 1px solid #dce7e4;
            border-radius: 8px;
            padding: 1rem 1.15rem;
            box-shadow: 0 12px 28px rgba(15, 40, 38, .06);
        }
        .status-chip {
            display: inline-block;
            padding: .25rem .55rem;
            border-radius: 999px;
            background: #dff4ed;
            color: #0d513f;
            font-size: .82rem;
            font-weight: 700;
        }
        .risk-chip {
            display: inline-block;
            padding: .25rem .55rem;
            border-radius: 999px;
            background: #fff0d9;
            color: #755116;
            font-size: .82rem;
            font-weight: 700;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid #dce7e4;
            border-radius: 8px;
            overflow: hidden;
        }
        .stButton button, .stFormSubmitButton button {
            border-radius: 8px;
            border: 1px solid #1f6f63;
            background: #1f6f63;
            color: #ffffff;
            font-weight: 700;
        }
        .stButton button:hover, .stFormSubmitButton button:hover {
            border-color: #174f48;
            background: #174f48;
            color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    defaults = {
        "api_url": DEFAULT_API_URL,
        "token": None,
        "user": None,
        "thread_id": None,
        "chat_history": [],
        "workflow_state": {},
        "uploaded_documents": [],
        "last_eligibility": None,
        "pending_actions": [],
    }

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def client() -> BankingApiClient:
    return BankingApiClient(
        base_url=st.session_state.api_url,
        token=st.session_state.token,
    )


def render_login() -> None:
    left, right = st.columns([1.05, 1])

    with left:
        st.markdown("## Enterprise Agentic Banking AI")
        st.write(
            "Secure customer banking workspace for conversational service, "
            "loan workflows, document intake, and policy-grounded assistance."
        )
        st.markdown(
            """
            <div class="bank-panel">
                <span class="status-chip">JWT secured</span>
                <span class="status-chip">LangGraph stateful workflows</span>
                <span class="status-chip">RAG policy answers</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        with st.form("login_form"):
            st.subheader("Sign in")
            st.session_state.api_url = st.text_input(
                "FastAPI base URL",
                value=st.session_state.api_url,
            )
            email = st.text_input("Email", value="vishnu@test.com")
            password = st.text_input(
                "Password",
                value="password123",
                type="password",
            )
            submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            try:
                api = BankingApiClient(st.session_state.api_url)
                token = api.login(email, password)
                st.session_state.token = token
                st.session_state.user = BankingApiClient(
                    st.session_state.api_url,
                    token,
                ).me()
                st.rerun()
            except BankingApiError as exc:
                st.error(f"Login failed: {exc}")
            except requests_error_tuple() as exc:
                st.error(f"Could not reach backend: {exc}")


def requests_error_tuple():
    import requests

    return (
        requests.ConnectionError,
        requests.Timeout,
        requests.RequestException,
    )


def render_sidebar() -> str:
    st.sidebar.markdown("## SecureBank AI")
    user = st.session_state.user or {}
    st.sidebar.caption(st.session_state.api_url)
    st.sidebar.markdown(f"**{user.get('name', 'Customer')}**")
    st.sidebar.caption(user.get("email", ""))

    page = st.sidebar.radio(
        "Workspace",
        [
            "Dashboard",
            "Assistant",
            "Documents",
            "Loans",
        ],
    )

    st.sidebar.divider()
    st.sidebar.markdown("### Conversation")
    st.sidebar.caption(f"Thread: `{st.session_state.thread_id or 'new'}`")

    workflow_state = st.session_state.workflow_state
    if workflow_state.get("awaiting_document_upload"):
        st.sidebar.warning("Document upload pending")

    if st.sidebar.button("New conversation", use_container_width=True):
        st.session_state.thread_id = None
        st.session_state.chat_history = []
        st.session_state.workflow_state = {}
        st.session_state.pending_actions = []
        st.rerun()

    if st.sidebar.button("Logout", use_container_width=True):
        for key in [
            "token",
            "user",
            "thread_id",
            "chat_history",
            "workflow_state",
            "uploaded_documents",
            "last_eligibility",
            "pending_actions",
        ]:
            st.session_state.pop(key, None)
        init_state()
        st.rerun()

    return page


def extract_assistant_text(payload: dict[str, Any]) -> str:
    result = payload.get("result", payload)

    if isinstance(result, dict):
        response = result.get("response", result)
    else:
        response = result

    if isinstance(response, dict):
        if "eligible" in response:
            return format_eligibility_response(response)

        if "message" in response:
            return format_response_dict(response)

        if "response" in response:
            return extract_from_response_value(response["response"])

        if response.get("awaiting_document_upload"):
            missing = ", ".join(response.get("missing_documents", []))
            return f"Please upload the required documents before we continue: {missing}."

        if "eligible" in response:
            if response.get("eligible"):
                return "You meet the deterministic eligibility checks for this loan."

            reasons = response.get("rejection_reasons") or []
            missing = response.get("missing_documents") or []
            details = reasons or [f"Missing documents: {', '.join(missing)}"]
            return "Eligibility is not complete yet. " + " ".join(details)

    return extract_from_response_value(response)


def extract_from_response_value(value: Any) -> str:
    if isinstance(value, str):
        return value

    if isinstance(value, dict):
        if "messages" in value:
            return extract_final_message_text(value["messages"])

        if "message" in value:
            return format_response_dict(value)

        return json.dumps(value, indent=2, default=str)

    if isinstance(value, list):
        return json.dumps(value, indent=2, default=str)

    return str(value)


def extract_final_message_text(messages: Any) -> str:
    if not isinstance(messages, list):
        return extract_from_response_value(messages)

    for message in reversed(messages):
        if not isinstance(message, dict):
            continue

        if message.get("type") != "ai":
            continue

        content = message.get("content")
        if content:
            return content_to_markdown(content)

    return "I completed the request, but could not format the final response."


def content_to_markdown(content: Any) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, dict):
                parts.append(str(item.get("text", "")))
            else:
                parts.append(str(item))

        return "\n".join(part for part in parts if part)

    return str(content)


def format_response_dict(response: dict[str, Any]) -> str:
    lines = [str(response.get("message", "")).strip()]

    eligibility = response.get("eligibility")
    if isinstance(eligibility, dict):
        profile = eligibility.get("profile", {})
        if eligibility.get("eligible"):
            lines.append("")
            lines.append("Eligibility checks passed.")
        elif eligibility.get("awaiting_documents"):
            missing = ", ".join(eligibility.get("missing_documents", []))
            lines.append("")
            lines.append(f"Documents still needed: {missing}.")
        elif eligibility.get("rejection_reasons"):
            lines.append("")
            lines.append("Reasons:")
            for reason in eligibility.get("rejection_reasons", []):
                lines.append(f"- {reason}")

        if profile:
            lines.append("")
            lines.append("Extracted profile:")
            lines.append(
                f"- Monthly salary: INR {profile.get('monthly_salary', 0):,.0f}"
            )
            lines.append(
                f"- Average balance: INR {profile.get('average_balance', 0):,.0f}"
            )
            lines.append(
                f"- Transaction health: {profile.get('transaction_health', 'N/A')}"
            )

    if response.get("application_id"):
        lines.append("")
        lines.append(f"Application ID: `{response['application_id']}`")

    return "\n".join(line for line in lines if line is not None).strip()


def format_eligibility_response(eligibility: dict[str, Any]) -> str:
    if eligibility.get("eligible"):
        heading = "You are eligible based on the current checks."
    elif eligibility.get("awaiting_documents"):
        heading = "Eligibility is almost ready, but documents are still pending."
    else:
        heading = "You are not eligible under the current rules."

    lines = [
        heading,
        "",
        f"Loan type: `{eligibility.get('loan_type', 'N/A')}`",
    ]

    missing = eligibility.get("missing_documents") or []
    if missing:
        lines.append("Missing documents: " + ", ".join(missing))

    reasons = eligibility.get("rejection_reasons") or []
    if reasons:
        lines.append("")
        lines.append("Reasons:")
        lines.extend(f"- {reason}" for reason in reasons)

    profile = eligibility.get("profile") or {}
    if profile:
        lines.append("")
        lines.append("Current profile:")
        lines.append(f"- Monthly salary: INR {profile.get('monthly_salary', 0):,.0f}")
        lines.append(f"- Average balance: INR {profile.get('average_balance', 0):,.0f}")
        lines.append(f"- KYC verified: {profile.get('kyc_verified')}")
        lines.append(f"- Salary slip uploaded: {profile.get('has_salary_document')}")
        lines.append(f"- Bank statement uploaded: {profile.get('has_bank_statement')}")

    return "\n".join(lines)


def update_workflow_state(payload: dict[str, Any]) -> None:
    result = payload.get("result")

    if not isinstance(result, dict):
        return

    workflow_data = result.get("workflow_data") or {}
    st.session_state.workflow_state = workflow_data

    response = result.get("response")
    if isinstance(response, dict):
        if "eligibility" in response:
            st.session_state.last_eligibility = response["eligibility"]
        elif "eligible" in response:
            st.session_state.last_eligibility = response

        if response.get("awaiting_document_upload"):
            missing = response.get("missing_documents", [])
            st.session_state.pending_actions = [
                f"Upload {doc.replace('_', ' ').title()}"
                for doc in missing
            ]


def render_dashboard() -> None:
    api = client()
    st.title("Banking Dashboard")

    try:
        balance = api.balance() or {}
        transactions = api.transactions()
        loans = api.loans()
        documents = api.documents()
    except Exception as exc:
        st.error(f"Could not load dashboard: {exc}")
        return

    cols = st.columns(4)
    cols[0].metric("Balance", f"INR {balance.get('balance', 0):,.2f}")
    cols[1].metric("Account", balance.get("account_type", "N/A"))
    cols[2].metric("Recent Transactions", len(transactions))
    cols[3].metric("Documents", len(documents))

    st.divider()
    left, right = st.columns([1.25, 1])

    with left:
        st.subheader("Recent Transactions")
        if transactions:
            st.dataframe(pd.DataFrame(transactions), use_container_width=True)
        else:
            st.info("No transactions found.")

    with right:
        st.subheader("Active Loans")
        if loans:
            st.dataframe(pd.DataFrame(loans), use_container_width=True)
        else:
            st.info("No active loans found.")

        st.subheader("Workflow Status")
        pending = st.session_state.pending_actions
        if pending:
            for item in pending:
                st.warning(item)
        else:
            st.success("No pending customer actions.")


def render_chat() -> None:
    st.title("Banking Assistant")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.workflow_state.get("awaiting_document_upload"):
        render_inline_upload_panel()

    prompt = st.chat_input("Ask about accounts, transfers, cards, loans, or policies")

    if not prompt:
        return

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("Thinking through your banking workflow...")

        try:
            payload = client().chat(prompt, st.session_state.thread_id)
            st.session_state.thread_id = payload.get(
                "thread_id",
                st.session_state.thread_id,
            )
            update_workflow_state(payload)
            assistant_text = extract_assistant_text(payload)

            placeholder.markdown(assistant_text)

            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": assistant_text,
                }
            )
        except Exception as exc:
            placeholder.error(f"Assistant request failed: {exc}")


def render_inline_upload_panel() -> None:
    missing = st.session_state.workflow_state.get("missing_documents", [])

    with st.expander("Upload required documents", expanded=True):
        st.info(
            "Upload the required files here. Choose `Auto detect` when uploading "
            "more than one document type together."
        )
        if missing:
            st.warning("Required now: " + ", ".join(missing))
        render_upload_form("chat_upload")


def render_documents() -> None:
    st.title("Document Center")
    render_upload_form("documents_page")

    st.subheader("Uploaded Documents")
    try:
        docs = client().documents()
    except Exception as exc:
        st.error(f"Could not load documents: {exc}")
        return

    st.session_state.uploaded_documents = docs

    if docs:
        st.dataframe(
            build_documents_dataframe(docs),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Upload a salary slip, Aadhaar, PAN, or bank statement to begin.")


def render_upload_form(key_prefix: str) -> None:
    with st.form(f"{key_prefix}_form", clear_on_submit=True):
        label = st.selectbox(
            "Document type",
            list(DOCUMENT_TYPES.keys()),
            key=f"{key_prefix}_document_type",
            help="Use Auto detect for mixed uploads like salary slip + bank statement.",
        )
        uploaded = st.file_uploader(
            "Choose documents",
            type=["txt", "pdf", "png", "jpg", "jpeg"],
            key=f"{key_prefix}_file",
            accept_multiple_files=True,
        )
        submitted = st.form_submit_button("Process document")

    if not submitted:
        return

    if not uploaded:
        st.warning("Select at least one file first.")
        return

    try:
        if len(uploaded) > 1 and DOCUMENT_TYPES[label]:
            st.warning(
                "Multiple files were uploaded with one selected type. The backend "
                "will still auto-correct clear mismatches, but Auto detect is safest "
                "for mixed documents."
            )

        uploads = [
            (
                file.name,
                file.getvalue(),
                file.type,
            )
            for file in uploaded
        ]
        result = client().upload_documents(
            uploads=uploads,
            document_type=DOCUMENT_TYPES[label],
        )
        st.success(f"Processed {result.get('processed_count', len(uploads))} document(s).")
        st.dataframe(
            build_upload_result_dataframe(result),
            use_container_width=True,
            hide_index=True,
        )
        st.session_state.uploaded_documents = client().documents()

        pending_loan = st.session_state.workflow_state.get("pending_loan_type")
        if pending_loan:
            st.session_state.last_eligibility = client().loan_eligibility(
                pending_loan
            )
            sync_workflow_from_eligibility(st.session_state.last_eligibility)

            if st.session_state.last_eligibility.get("eligible"):
                st.info(
                    "Documents look good for the pending loan. Go back to the assistant "
                    "and confirm if you want to submit the application."
                )
            else:
                missing = st.session_state.last_eligibility.get("missing_documents", [])
                if missing:
                    st.warning("Still needed: " + ", ".join(missing))
    except Exception as exc:
        st.error(f"Upload failed: {exc}")


def sync_workflow_from_eligibility(eligibility: dict[str, Any]) -> None:
    if eligibility.get("awaiting_documents"):
        st.session_state.workflow_state["awaiting_document_upload"] = True
        st.session_state.workflow_state["missing_documents"] = eligibility.get(
            "missing_documents",
            [],
        )
        st.session_state.pending_actions = [
            f"Upload {doc.replace('_', ' ').title()}"
            for doc in eligibility.get("missing_documents", [])
        ]
        return

    st.session_state.workflow_state.pop("awaiting_document_upload", None)
    st.session_state.workflow_state.pop("missing_documents", None)
    st.session_state.pending_actions = []


def build_upload_result_dataframe(result: dict[str, Any]) -> pd.DataFrame:
    rows = []

    for document in result.get("documents", []):
        parsed = document.get("parsed_data", {})
        rows.append(
            {
                "File": document.get("file_name", "-"),
                "Detected Type": document.get("document_type", "-"),
                "Name": parsed.get("employee_name") or parsed.get("name") or "-",
                "Employer": parsed.get("employer") or "-",
                "Salary": parsed.get("salary"),
                "Average Balance": parsed.get("average_balance"),
                "Monthly Income": parsed.get("monthly_income"),
                "KYC": parsed.get("kyc_validity") or "-",
            }
        )

    return pd.DataFrame(rows)


def build_documents_dataframe(docs: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []

    for doc in docs:
        rows.append(
            {
                "ID": doc.get("document_id"),
                "Type": doc.get("document_type"),
                "File": doc.get("file_name"),
                "Status": doc.get("status"),
                "Salary": doc.get("monthly_salary"),
                "Average Balance": doc.get("average_balance"),
                "Monthly Income": doc.get("monthly_income"),
                "Health": doc.get("transaction_health"),
                "KYC": doc.get("kyc_validity"),
            }
        )

    return pd.DataFrame(rows)


def format_eligibility_summary(eligibility: dict[str, Any]) -> str:
    profile = eligibility.get("profile", {})
    lines = [
        f"**Loan type:** `{eligibility.get('loan_type', 'N/A')}`",
        f"**Decision:** {'Eligible' if eligibility.get('eligible') else 'Needs attention'}",
    ]

    missing = eligibility.get("missing_documents") or []
    if missing:
        lines.append("**Missing documents:** " + ", ".join(missing))

    reasons = eligibility.get("rejection_reasons") or []
    if reasons:
        lines.append("**Reasons:**")
        lines.extend(f"- {reason}" for reason in reasons)

    if profile:
        lines.extend(
            [
                "**Extracted profile:**",
                f"- Monthly salary: INR {profile.get('monthly_salary', 0):,.0f}",
                f"- Average balance: INR {profile.get('average_balance', 0):,.0f}",
                f"- KYC verified: {profile.get('kyc_verified')}",
                f"- Transaction health: {profile.get('transaction_health', 'N/A')}",
            ]
        )

    return "\n".join(lines)


def render_loans() -> None:
    st.title("Loan Workspace")

    left, right = st.columns([1, 1])

    with left:
        st.subheader("Eligibility Check")
        selected = st.selectbox("Loan type", list(LOAN_TYPES.keys()))

        if st.button("Check eligibility", use_container_width=True):
            try:
                st.session_state.last_eligibility = client().loan_eligibility(
                    LOAN_TYPES[selected]
                )
            except Exception as exc:
                st.error(f"Eligibility check failed: {exc}")

        eligibility = st.session_state.last_eligibility
        if eligibility:
            if eligibility.get("eligible"):
                st.success("Eligible based on deterministic banking checks.")
            elif eligibility.get("awaiting_documents"):
                st.warning(
                    "Documents required: "
                    + ", ".join(eligibility.get("missing_documents", []))
                )
            else:
                st.error("Not eligible under current rules.")

            st.markdown(format_eligibility_summary(eligibility))
            with st.expander("Raw eligibility details"):
                st.json(eligibility)

    with right:
        st.subheader("Document Evidence")
        render_upload_form("loan_page")

    st.divider()
    st.subheader("Active Loans")
    try:
        loans = client().loans()
        if loans:
            st.dataframe(pd.DataFrame(loans), use_container_width=True)
        else:
            st.info("No active loans found.")
    except Exception as exc:
        st.error(f"Could not load loans: {exc}")


def main() -> None:
    configure_page()
    init_state()

    if not st.session_state.token:
        render_login()
        return

    page = render_sidebar()

    if page == "Dashboard":
        render_dashboard()
    elif page == "Assistant":
        render_chat()
    elif page == "Documents":
        render_documents()
    elif page == "Loans":
        render_loans()


if __name__ == "__main__":
    main()
