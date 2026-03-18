from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse
from app.auth.oauth import oauth
from app.db.postgres import SessionLocal
from sqlalchemy import text
import os

router = APIRouter(prefix="/auth", tags=["Auth"])

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def auth_callback(request: Request):

    token = await oauth.google.authorize_access_token(request)
    user_info = token["userinfo"]

    google_id = user_info["sub"]
    email = user_info["email"]
    name = user_info["name"]
    picture = user_info["picture"]

    db = SessionLocal()

    user = db.execute(
        text("SELECT * FROM users WHERE google_id=:gid"),
        {"gid": google_id}
    ).fetchone()

    if not user:
        result = db.execute(
            text("""
            INSERT INTO users (google_id,email,name,picture)
            VALUES (:gid,:email,:name,:pic)
            RETURNING id
            """),
            {
                "gid": google_id,
                "email": email,
                "name": name,
                "pic": picture
            }
        )
        user_id = result.fetchone()[0]
        db.commit()
    else:
        user_id = user.id

    # redirect to frontend
    response = RedirectResponse(url=f"{FRONTEND_URL}/chat")

    # set cookie for authentication
    response.set_cookie(
        key="user_id",
        value=str(user_id),
        httponly=True,
        samesite="lax",
        secure=False # Set to True in production with HTTPS
    )

    return response


@router.get("/me")
def get_current_user(request: Request):

    user_id = request.cookies.get("user_id")

    if not user_id:
        return None

    db = SessionLocal()

    user = db.execute(
        text("SELECT id,name,email,picture FROM users WHERE id=:uid"),
        {"uid": user_id}
    ).fetchone()

    if not user:
        return None

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "picture": user.picture
    }


@router.get("/logout")
def logout():

    response = RedirectResponse(url=FRONTEND_URL)

    response.delete_cookie("user_id")

    return response

