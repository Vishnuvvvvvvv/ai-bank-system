from langchain_google_genai import (
    ChatGoogleGenerativeAI
)

from app.config import GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    google_api_key=GOOGLE_API_KEY,
    temperature=0
)