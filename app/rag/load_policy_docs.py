from langchain_community.document_loaders import TextLoader

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from langchain_chroma import Chroma

def load_documents():

    files = [
        "data/policies/home_loan_policy.txt",
        "data/policies/personal_loan_policy.txt",
        "data/policies/kyc_policy.txt",
        "data/policies/savings_account_policy.txt",
        "data/policies/loan_products.txt",
        "data/policies/bike_loan_policy.txt",
        "data/policies/debit_card_policy.txt",
        "data/policies/transaction_policy.txt",
        "data/policies/loan_eligibility_rules.txt",
    ]

    docs = []

    for file in files:

        print(f"Loading file: {file}")

        loader = TextLoader(
            file,
            encoding="utf-8"
        )

        loaded_docs = loader.load()

        print(f"Loaded docs count: {len(loaded_docs)}")

        docs.extend(loaded_docs)

    return docs


def create_vector_db():

    docs = load_documents()

    print(f"Total docs loaded: {len(docs)}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    split_docs = splitter.split_documents(docs)

    print(f"Total chunks created: {len(split_docs)}")

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

    vectordb = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings,
        persist_directory="./policy_db"
    )

    print("Vector DB created successfully.")

if __name__ == "__main__":
    create_vector_db()
