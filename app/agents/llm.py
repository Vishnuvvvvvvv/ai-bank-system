# from langchain_google_genai import (
#     ChatGoogleGenerativeAI
# )

# from app.config import GOOGLE_API_KEY

# llm = ChatGoogleGenerativeAI(
#     model="gemini-3.1-flash-lite",
#     google_api_key=GOOGLE_API_KEY,
#     temperature=0
# )

from langchain_openai import ChatOpenAI

import httpx

from app.config import (
    GENAI_API_KEY,
)




client = httpx.Client(
    verify=False
)


llm = ChatOpenAI(

    base_url="https://genailab.tcs.in",

    model="azure/genailab-maas-gpt-4o-mini",

    api_key=GENAI_API_KEY,

    http_client=client,

    temperature=0
)