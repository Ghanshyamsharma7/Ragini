import os
import uuid
import numpy as np
from redisvl.index import SearchIndex
from redisvl.schema import IndexSchema
from redisvl.query import VectorQuery
from redis import Redis
from dotenv import load_dotenv
from app.services.embedding_service import generate_embedding

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
SIM_THRESHOLD = float(os.getenv("CACHE_SIM_THRESHOLD", 0.2))

redis_client = Redis.from_url(REDIS_URL)

schema = IndexSchema.from_dict({
    "index": {"name": "ragini_semantic_cache", "prefix": "cache"},
    "fields": [
        {"name": "question", "type": "text"},
        {"name": "answer", "type": "text"},
        {"name": "class_name", "type": "tag"},
        {"name": "subject", "type": "tag"},
        {
            "name": "embedding",
            "type": "vector",
            "attrs": {
                "dims": 3072,
                "distance_metric": "cosine",
                "algorithm": "flat"
            }
        }
    ]
})

index = SearchIndex(schema, redis_client)
index.create(overwrite=True)


def search_cache(question: str, class_name: str, subject: str):

    query_embedding = generate_embedding(question)
    query_vector = np.array(query_embedding, dtype=np.float32).tobytes()

    vq = VectorQuery(
        query_vector,
        "embedding",
        num_results=5,   # retrieve few candidates
        return_fields=["question", "answer", "class_name", "subject", "vector_distance"]
    )

    results = index.query(vq)

    if not results:
        return None

    for result in results:

        # filter by class and subject
        if result.get("class_name") != class_name:
            continue

        if result.get("subject") != subject:
            continue

        distance = float(result.get("vector_distance", 1))

        if distance <= SIM_THRESHOLD:
            return result.get("answer")

    return None


def store_cache(question: str, answer: str, class_name: str, subject: str):

    embedding = generate_embedding(question)
    embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()

    doc = {
        "id": str(uuid.uuid4()),
        "question": question,
        "answer": answer,
        "class_name": class_name,
        "subject": subject,
        "embedding": embedding_bytes
    }

    index.load([doc])