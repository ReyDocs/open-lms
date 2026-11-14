import pytest
import pytest_asyncio
import os
import sys
from uuid import uuid4
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.infrastructure.database.connection import Base, get_db
from app.infrastructure.database.models import UserModel
from app.main import create_app
from app.infrastructure.security.jwt_handler import JWTHandler

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    app = create_app()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_admin(db_session):
    now = datetime.now(timezone.utc)
    user = UserModel(
        id=uuid4(),
        email="test_admin@openlms.edu",
        full_name="Admin Test",
        role="admin",
        created_at=now,
        updated_at=now,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def sample_teacher(db_session):
    now = datetime.now(timezone.utc)
    user = UserModel(
        id=uuid4(),
        email="test_teacher@openlms.edu",
        full_name="Teacher Test",
        role="teacher",
        created_at=now,
        updated_at=now,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def sample_student(db_session):
    now = datetime.now(timezone.utc)
    user = UserModel(
        id=uuid4(),
        email="test_student@openlms.edu",
        full_name="Student Test",
        role="student",
        student_id="STU999",
        created_at=now,
        updated_at=now,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
def auth_headers():
    jwt_handler = JWTHandler()

    def _get_headers(user: UserModel):
        token = jwt_handler.create_access_token(user.id, user.email, user.role)
        return {"Authorization": f"Bearer {token}"}

    return _get_headers
