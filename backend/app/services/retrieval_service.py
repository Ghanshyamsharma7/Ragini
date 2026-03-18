from app.services.embedding_service import generate_embedding
from app.services.pinecone_service import search_vectors


def search_chunks(question: str, class_name: str, subject: str):
    """
    Generates embedding for question and searches
    only within the class+subject namespace in Pinecone.
    """
    query_embedding = generate_embedding(question)
    matches = search_vectors(query_embedding, class_name, subject, top_k=5)
    return matches