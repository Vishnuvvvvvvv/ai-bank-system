from langchain_chroma import Chroma

import httpx

from langchain_openai import (
    OpenAIEmbeddings
)

from app.config import (
    GENAI_API_KEY,
)


client = httpx.Client(
    verify=False
)


embeddings = OpenAIEmbeddings(

    base_url="https://genailab.tcs.in",

    model="azure/genailab-maas-text-embedding-3-large",

    api_key=GENAI_API_KEY,

    http_client=client,

    tiktoken_enabled=False,

     check_embedding_ctx_length=False
)

vectordb = Chroma(
    persist_directory="./policy_db",
    embedding_function=embeddings
)


def retrieve_policy_context(query: str):

    docs = vectordb.similarity_search(
        query,
        k=2
    )

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    return context
