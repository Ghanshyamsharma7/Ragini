from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os

DATABASE_URL = os.getenv("NEON_DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,           # max persistent connections
    max_overflow=2,        # extra connections allowed under load
    pool_timeout=30,       # seconds to wait for a connection
    pool_recycle=300,      # recycle connections every 5 min (before Neon kills them)
    pool_pre_ping=True,    # test connection before using it — auto-reconnects if dead
    connect_args={
        "sslmode": "require",
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)