from fastapi import APIRouter
from app.db.postgres import SessionLocal
from sqlalchemy import text

router = APIRouter(prefix="/history", tags=["History"])


@router.get("/{user_id}")
def get_history(user_id: int):

    db = SessionLocal()

    rows = db.execute(
        text("""
        SELECT question, answer, created_at
        FROM chat_history
        WHERE user_id=:uid
        ORDER BY created_at DESC
        """),
        {"uid": user_id}
    ).fetchall()

    return rows