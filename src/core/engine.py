# -*- coding: utf-8 -*-
# @Time: 2025/12/13
# @Author: Administrator
# @File: engine.py
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from .constants import appConstants

engine = create_engine(
    appConstants.dbUrl,
    echo=False,
    logging_name="SQLAlchemy",
    pool_size=50,
    max_overflow=100,
    pool_timeout=30,
    pool_recycle=1800,
    connect_args={"check_same_thread": False},
)
print(f"{appConstants.dbUrl}")
SessionLocal = scoped_session(sessionmaker(bind=engine))


@contextmanager
def get_db():
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        SessionLocal.remove()


def dispose():
    engine.dispose()


__all__ = ["get_db", "dispose"]
