from fastapi import APIRouter
from datetime import datetime
from app.services.ocr_service import process_pdf_from_supabase, list_all_pdfs
from app.services.chunk_service import semantic_chunk_text
from app.services.mongo_service import store_chunk_document
from app.services.embedding_service import generate_embedding
from app.services.pinecone_service import upsert_vectors
from app.utils.path_parser import parse_supabase_path
from app.db.mongo import ingested_files_collection, chunks_collection
from bson import ObjectId
import time

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


def is_already_ingested(file_path: str) -> bool:
    return ingested_files_collection.find_one({"file_path": file_path}) is not None


def mark_as_ingested(file_path: str, chunk_count: int):
    ingested_files_collection.insert_one({
        "file_path": file_path,
        "chunk_count": chunk_count,
        "ingested_at": datetime.utcnow()
    })


@router.post("/ingest-all")
def ingest_all():
    bucket = "CBSE_BOOKS"
    all_files = list_all_pdfs(bucket)

    total_chunks = 0
    skipped = 0
    processed = 0
    failed = 0

    for file_path in all_files:

        if is_already_ingested(file_path):
            print(f"   Skipping: {file_path}")
            skipped += 1
            continue

        class_name, subject, chapter = parse_supabase_path(file_path)

        print("\n" + "="*60)
        print(f"FILE    : {file_path}")
        print(f"CLASS   : {class_name} | SUBJECT: {subject} | CHAPTER: {chapter}")
        print("="*60)

        try:
            text = process_pdf_from_supabase(bucket, file_path)
            if not text.strip():
                print(f"   Empty text — skipping")
                failed += 1
                continue

            chunks = semantic_chunk_text(text)
            print(f"   Created {len(chunks)} chunks")

            vectors = []
            for i, chunk in enumerate(chunks):
                mongo_id = store_chunk_document(
                    class_name, subject, chapter, i, chunk
                )
                total_chunks += 1
                embedding = generate_embedding(chunk)
                vectors.append({
                    "id": mongo_id,
                    "values": embedding,
                    "metadata": {"chapter": chapter, "chunk_index": i}
                })
                print(f"  Embedded {i+1}/{len(chunks)}", end="\r")

                if len(vectors) >= 100:
                    upsert_vectors(vectors, class_name, subject)
                    vectors = []

            if vectors:
                upsert_vectors(vectors, class_name, subject)

            mark_as_ingested(file_path, len(chunks))
            processed += 1
            print(f"\n  ✓ Done: {len(chunks)} chunks → MongoDB + Pinecone")

        except Exception as e:
            print(f"   ERROR on {file_path}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
            continue

    print(f"\nINGESTION COMPLETE — Processed: {processed} | Skipped: {skipped} | Failed: {failed} | Chunks: {total_chunks}")
    return {"status": "done", "processed": processed, "skipped": skipped, "failed": failed, "total_chunks": total_chunks}


def embed_existing():
    """
    Embeds existing MongoDB chunks into Pinecone.
    Skips chunks already embedded — safe to restart anytime.
    """
    from app.services.pinecone_service import index as pinecone_index

    total = 0
    skipped = 0
    failed = 0

    # Get all unique class+subject combinations
    pipeline = [{"$group": {"_id": {"class": "$class", "subject": "$subject"}}}]
    combos = list(chunks_collection.aggregate(pipeline))
    print(f"Found {len(combos)} class+subject combinations\n")

    for combo in combos:
        class_name = combo["_id"]["class"]
        subject = combo["_id"]["subject"]
        namespace = f"{class_name}__{subject}"

        print(f"Processing: {class_name} / {subject}")

        # Check which IDs already exist in this Pinecone namespace
        docs = list(chunks_collection.find({"class": class_name, "subject": subject}))
        all_ids = [str(doc["_id"]) for doc in docs]

        # Fetch existing vectors from Pinecone in batches of 100
        existing_ids = set()
        for i in range(0, len(all_ids), 100):
            batch_ids = all_ids[i:i+100]
            try:
                fetch_result = pinecone_index.fetch(ids=batch_ids, namespace=namespace)
                existing_ids.update(fetch_result.vectors.keys())
            except Exception:
                pass

        # Filter to only unembedded chunks
        pending_docs = [doc for doc in docs if str(doc["_id"]) not in existing_ids]

        print(f"  Total: {len(docs)} | Already embedded: {len(existing_ids)} | Pending: {len(pending_docs)}")

        if not pending_docs:
            print(f"   All chunks already embedded — skipping")
            skipped += len(docs)
            continue

        vectors = []
        for i, doc in enumerate(pending_docs):
            try:
                embedding = generate_embedding(doc["text"])
                vectors.append({
                    "id": str(doc["_id"]),
                    "values": embedding,
                    "metadata": {
                        "chapter": doc.get("chapter", ""),
                        "chunk_index": doc.get("chunk_id", i)
                    }
                })
                total += 1
                print(f"  Embedding {i+1}/{len(pending_docs)}", end="\r")

                # Upsert in batches of 100
                if len(vectors) >= 100:
                    upsert_vectors(vectors, class_name, subject)
                    vectors = []
                    time.sleep(1)  # avoid rate limiting

            except Exception as e:
                print(f"\n   Error on chunk {doc['_id']}: {e}")
                failed += 1
                continue

        if vectors:
            upsert_vectors(vectors, class_name, subject)

        print(f"\n   Done: {class_name}/{subject}\n")

    print(f"\n{'='*60}")
    print(f"EMBEDDING COMPLETE")
    print(f"Newly embedded : {total}")
    print(f"Already existed: {skipped}")
    print(f"Failed         : {failed}")
    print(f"{'='*60}")
    return {"embedded": total, "skipped": skipped, "failed": failed}


@router.post("/embed-existing")
def embed_existing_endpoint():
    return embed_existing()


@router.get("/status")
def ingestion_status():
    ingested = list(ingested_files_collection.find(
        {}, {"_id": 0, "file_path": 1, "chunk_count": 1, "ingested_at": 1}
    ))
    return {"total_ingested": len(ingested), "files": ingested}