
from app.db.mongo import chunks_collection
from bson import ObjectId


def get_context(matches):

    context_chunks = []

    for match in matches:
        chunk_id = match["id"]

        doc = chunks_collection.find_one(
            {"_id": ObjectId(chunk_id)}
        )

        if doc:
            context_chunks.append(doc["text"])

    return "\n\n".join(context_chunks)