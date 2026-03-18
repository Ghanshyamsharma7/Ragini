from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.api import ingest, query, auth, history, session
from app.api.config import router as config_router
import os

app = FastAPI(title="RAGINI")

# Required for Google OAuth
# Use environment variable for secret key in production
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "super-secret-session-key")
)

# Allow both local dev and production frontend URLs
origins = [
    "http://localhost:5173",
    os.getenv("FRONTEND_URL", ""),  # e.g. https://ragini.vercel.app
]
# Filter empty strings
origins = [o for o in origins if o]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
app.include_router(query.router)
app.include_router(auth.router)
app.include_router(history.router)
app.include_router(session.router)
app.include_router(config_router)

@app.get("/")
def root():
    return {"message": "RAGINI Backend Running"}