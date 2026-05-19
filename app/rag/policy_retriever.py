from langchain_chroma import Chroma

from langchain_huggingface import HuggingFaceEmbeddings


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
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