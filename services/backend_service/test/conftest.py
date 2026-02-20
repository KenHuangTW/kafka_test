from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from alembic import command
from alembic.config import Config
from dotenv import dotenv_values
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def _load_test_settings() -> dict[str, str]:
    env_path = Path(__file__).resolve().parent.parent / "test.env"
    values = {k: v for k, v in dotenv_values(env_path).items() if v is not None}
    return {
        "host": values.get("MYSQL_HOST", "localhost"),
        "port": values.get("MYSQL_PORT", "3333"),
        "root_user": values.get("MYSQL_ROOT_USER", "root"),
        "root_password": values.get("MYSQL_ROOT_PASSWORD", "root"),
        "db_name": values.get("MYSQL_TEST_DATABASE", "kafka_test"),
    }


def _admin_execute(settings: dict[str, str], sql: str) -> None:
    import mysql.connector

    conn = mysql.connector.connect(
        host=settings["host"],
        port=int(settings["port"]),
        user=settings["root_user"],
        password=settings["root_password"],
        autocommit=True,
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
    finally:
        conn.close()


def _admin_ping(settings: dict[str, str]) -> bool:
    try:
        import mysql.connector

        conn = mysql.connector.connect(
            host=settings["host"],
            port=int(settings["port"]),
            user=settings["root_user"],
            password=settings["root_password"],
            autocommit=True,
        )
        conn.close()
        return True
    except Exception:
        return False


@pytest.fixture
def db_session_factory() -> Generator[sessionmaker, None, None]:
    settings = _load_test_settings()
    db_name = settings["db_name"]

    if not _admin_ping(settings):
        pytest.skip(
            "Integration DB unavailable. Start MySQL first (docker compose up -d) "
            "or set services/backend_service/test.env."
        )

    _admin_execute(settings, f"DROP DATABASE IF EXISTS `{db_name}`")
    _admin_execute(settings, f"CREATE DATABASE `{db_name}`")

    os.environ["MYSQL_HOST"] = settings["host"]
    os.environ["MYSQL_PORT"] = settings["port"]
    os.environ["MYSQL_USER"] = settings["root_user"]
    os.environ["MYSQL_PASSWORD"] = settings["root_password"]
    os.environ["MYSQL_DATABASE"] = db_name

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(
        f"mysql+mysqlconnector://{settings['root_user']}:{settings['root_password']}@"
        f"{settings['host']}:{settings['port']}/{db_name}",
        pool_pre_ping=True,
    )
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)

    try:
        yield SessionLocal
    finally:
        engine.dispose()
        _admin_execute(settings, f"DROP DATABASE IF EXISTS `{db_name}`")


@pytest.fixture
def test_client(monkeypatch: pytest.MonkeyPatch, db_session_factory: sessionmaker) -> Generator[TestClient, None, None]:
    from services.backend_service.app.main import app, kafka
    from services.backend_service.database.mysql import get_db_session

    monkeypatch.setattr(kafka, "start", AsyncMock(return_value=None))
    monkeypatch.setattr(kafka, "consume_forever", AsyncMock(return_value=None))
    monkeypatch.setattr(kafka, "stop", AsyncMock(return_value=None))

    def override_db() -> Generator[Session, None, None]:
        db = db_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db_session] = override_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def db_session(db_session_factory: sessionmaker) -> Generator[Session, None, None]:
    session = db_session_factory()
    try:
        yield session
    finally:
        session.close()
