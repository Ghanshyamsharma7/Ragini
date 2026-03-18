import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = os.getenv("PINECONE_INDEX")
index = pc.Index(index_name)


def make_namespace(class_name: str, subject: str) -> str:
    """
    Creates consistent namespace string.
    e.g. class_09 + hindi kshitij -> class_09__hindi kshitij
    """
    return f"{class_name}__{subject}"


def upsert_vectors(vectors: list, class_name: str, subject: str):
    """
    Upsert vectors into class+subject specific namespace.
    """
    namespace = make_namespace(class_name, subject)
    index.upsert(vectors=vectors, namespace=namespace)


def search_vectors(query_embedding: list, class_name: str, subject: str, top_k: int = 5):
    """
    Search only within the specific class+subject namespace.
    Fast — no cross-namespace scanning.
    """
    namespace = make_namespace(class_name, subject)
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        namespace=namespace
    )
    return results["matches"]