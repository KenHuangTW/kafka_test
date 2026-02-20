import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def _mysql_url() -> str:
    user = os.getenv("MYSQL_USER", "app_user")
    password = os.getenv("MYSQL_PASSWORD", "app_password")
    host = os.getenv("MYSQL_HOST", "localhost")
    port = os.getenv("MYSQL_PORT", "3333")
    database = os.getenv("MYSQL_DATABASE", "kafka")
    return f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"


engine = create_engine(
    _mysql_url(),
    pool_pre_ping=True,
    pool_recycle=1800,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)


def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
