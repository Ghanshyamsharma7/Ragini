from app.db.mongo import chunks_collection
from datetime import datetime


def store_chunk_document(class_name, subject, chapter, chunk_id, text):

    doc = {
        "class": class_name,
        "subject": subject,
        "chapter": chapter,
        "chunk_id": chunk_id,
        "text": text,
        "created_at": datetime.utcnow()
    }

    result = chunks_collection.insert_one(doc)

    return str(result.inserted_id)