from collections.abc import Generator
import logging
import socket
from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.base import Base

logger = logging.getLogger(__name__)

db_url = get_settings().database_url
engine = None

if db_url.startswith("postgresql"):
    try:
        # Quick socket check first to avoid blocking for a long time on connect
        parsed = urlparse(db_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 5432
        with socket.create_connection((host, port), timeout=1.0):
            pass

        temp_engine = create_engine(db_url, pool_pre_ping=True)
        with temp_engine.connect() as conn:
            pass
        engine = temp_engine
        logger.info("Successfully connected to PostgreSQL database.")
    except Exception as e:
        logger.warning(
            f"Failed to connect to PostgreSQL at {db_url} ({e}). "
            "Falling back to local SQLite database: sqlite:///./life_os.db"
        )
        db_url = "sqlite:///./life_os.db"

if engine is None:
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
    )
    if "sqlite" in db_url:
        Base.metadata.create_all(bind=engine)
        logger.info("Created tables in SQLite database.")

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
