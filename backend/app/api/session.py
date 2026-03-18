# backend/app/api/session.py
from fastapi import APIRouter, Request, HTTPException
from sqlalchemy import text
from app.db.postgres import SessionLocal
from pydantic import BaseModel

router = APIRouter(prefix="/session", tags=["Session"])

class CreateSessionBody(BaseModel):
    class_name: str = ""
    subject: str = ""

@router.get("/list")
def list_sessions(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return []
    try:
        db = SessionLocal()
        sessions = db.execute(
            text("""
            SELECT id, title, class_name, subject, created_at
            FROM chat_sessions
            WHERE user_id=:uid
            ORDER BY created_at DESC
            """),
            {"uid": user_id}
        ).mappings().all()
        return [dict(s) for s in sessions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")
    finally:
        db.close()

@router.post("/create")
def create_session(request: Request, body: CreateSessionBody):
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        db = SessionLocal()
        result = db.execute(
            text("""
            INSERT INTO chat_sessions (user_id, title, class_name, subject)
            VALUES (:uid, '', :class, :subject)
            RETURNING id, title, class_name, subject, created_at
            """),
            {"uid": user_id, "class": body.class_name, "subject": body.subject}
        )
        row = dict(result.mappings().first())
        db.commit()
        return row
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")
    finally:
        db.close()

@router.get("/{session_id}/history")
def get_session_history(session_id: int, request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        db = SessionLocal()
        rows = db.execute(
            text("""
            SELECT question, answer, created_at
            FROM chat_history
            WHERE user_id=:uid AND session_id=:sid
            ORDER BY created_at
            """),
            {"uid": user_id, "sid": session_id}
        ).mappings().all()
        return [dict(r) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load history: {str(e)}")
    finally:
        db.close()

@router.delete("/{session_id}")
def delete_session(session_id: int, request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        db = SessionLocal()
        # Must delete chat_history first due to foreign key constraint
        db.execute(
            text("""
            DELETE FROM chat_history
            WHERE session_id=:sid AND user_id=:uid
            """),
            {"sid": session_id, "uid": user_id}
        )
        db.execute(
            text("""
            DELETE FROM chat_sessions
            WHERE id=:sid AND user_id=:uid
            """),
            {"sid": session_id, "uid": user_id}
        )
        db.commit()
        return {"message": "Session deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")
    finally:
        db.close()