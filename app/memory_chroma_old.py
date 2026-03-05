import os
import uuid
from typing import List

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings


def _get_vs() -> Chroma:
    """
    Returns a persistent Chroma vector store.
    Uses OpenAI embeddings, stored locally in CHROMA_DIR.
    """
    chroma_dir = os.getenv("CHROMA_DIR", "./chroma_db")
    collection_name = os.getenv("CHROMA_COLLECTION", "cfo_memory")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY. Memory needs embeddings, set it in .env")

    embeddings = OpenAIEmbeddings(api_key=api_key)
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=chroma_dir,
    )


def add_memory(business_id: str, kind: str, question: str, answer: str) -> None:
    """
    Stores a single interaction in the vector DB.
    """
    vs = _get_vs()

    doc = (
        f"[{kind.upper()}]\n"
        f"Business: {business_id}\n"
        f"Question: {question}\n"
        f"Answer: {answer}"
    )

    vs.add_texts(
        texts=[doc],
        metadatas=[{"business_id": business_id, "kind": kind}],
        ids=[str(uuid.uuid4())],
    )
    vs.persist()


def retrieve_memory(business_id: str, query: str, k: int = 5) -> List[str]:
    """
    Retrieves up to k relevant past memories for this business.
    """
    vs = _get_vs()
    docs = vs.similarity_search(
        query=query,
        k=k,
        filter={"business_id": business_id},
    )
    return [d.page_content for d in docs]