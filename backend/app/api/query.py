# backend/app/api/query.py
from typing import Optional
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from app.db.postgres import SessionLocal
from app.services.retrieval_service import search_chunks
from app.services.context_service import get_context
from app.services.llm_service import generate_answer
from app.services.semantic_cache_service import search_cache, store_cache

router = APIRouter(prefix="/query", tags=["Query"])


class AskRequest(BaseModel):
    class_name: str = ""
    subject: str = ""
    question: str
    session_id: Optional[int] = None


@router.post("/ask")
def ask_question(req: AskRequest, request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # class_name from frontend is already "class_09" format — use directly
    class_name = req.class_name
    subject = req.subject

    # Step 1: Check semantic cache first
    cached_answer = search_cache(req.question, class_name, subject)
    if cached_answer:
        print(f"  Cache hit for: {req.question[:50]}")
        _save_to_history(req, user_id, cached_answer)
        return {
            "question": req.question,
            "answer": cached_answer,
            "source": "cache",
        }

    # Step 2: Search Pinecone namespace for this class+subject
    matches = search_chunks(req.question, class_name, subject)

    # Step 3: Fetch chunk texts from MongoDB
    context = get_context(matches)

    print(f"  Matches: {len(matches)} | Context length: {len(context)}")

    # Step 4: Generate answer from LLM
    answer = generate_answer(context, req.question)

    # Step 5: Save to history + update session title
    _save_to_history(req, user_id, answer)

    # Step 6: Cache for future similar questions
    store_cache(req.question, answer, class_name, subject)

    return {"question": req.question, "answer": answer}


def _save_to_history(req: AskRequest, user_id: str, answer: str):
    """Save Q&A to chat history and update session title if first message."""
    try:
        db = SessionLocal()
        db.execute(
            text("""
            INSERT INTO chat_history
                (user_id, session_id, question, answer, class_name, subject)
            VALUES (:uid, :sid, :q, :a, :c, :s)
            """),
            {
                "uid": user_id,
                "sid": req.session_id,
                "q": req.question,
                "a": answer,
                "c": req.class_name,
                "s": req.subject,
            },
        )
        if req.session_id:
            title = req.question.strip()[:50]
            if len(req.question.strip()) > 50:
                title += "..."
            db.execute(
                text("""
                UPDATE chat_sessions
                SET title = :title
                WHERE id = :sid AND user_id = :uid
                AND (title = '' OR title IS NULL)
                """),
                {"title": title, "sid": req.session_id, "uid": user_id},
            )
        db.commit()
    except Exception as e:
        print(f"   History save error: {e}")
    finally:
        db.close()