import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_short_term_factory
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.memory.short_term import InMemoryShortTermMemory


@pytest.fixture
def client() -> TestClient:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_short_term_factory] = lambda: (
        lambda session_id: InMemoryShortTermMemory(session_id)
    )

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)
