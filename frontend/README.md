# Streamlit Frontend

Professional Streamlit UI for the Agentic Banking AI backend.

## Run Backend

```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Run Frontend

Install the Streamlit frontend dependencies in the same virtual environment:

```powershell
.\venv\Scripts\python.exe -m pip install -r frontend\requirements.txt
```

Start the UI:

```powershell
.\venv\Scripts\streamlit.exe run frontend\streamlit_app.py
```

Default seed login:

- Email: `vishnu@test.com`
- Password: `password123`

The frontend integrates with these backend routes:

- `POST /login`
- `GET /me`
- `POST /chat`
- `POST /documents/upload`
- `GET /documents`
- `POST /loan-eligibility`
- `GET /balance`
- `GET /transactions`
- `GET /loans`
