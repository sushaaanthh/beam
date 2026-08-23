from __future__ import annotations

import logging
import socket
from collections.abc import Generator

import dns.resolver
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# Ensure Neon PostgreSQL host resolution succeeds across Windows DNS resolvers
_orig_getaddrinfo = socket.getaddrinfo

def _neon_dns_getaddrinfo(host, port, *args, **kwargs):
    try:
        return _orig_getaddrinfo(host, port, *args, **kwargs)
    except socket.gaierror:
        if host and "neon.tech" in str(host):
            try:
                resolver = dns.resolver.Resolver()
                resolver.nameservers = ["8.8.8.8", "1.1.1.1"]
                answers = resolver.resolve(str(host), "A")
                ip = str(answers[0])
                return _orig_getaddrinfo(ip, port, *args, **kwargs)
            except Exception as e:
                logger.warning("DNS resolution via fallback failed: %s", e)
        raise

socket.getaddrinfo = _neon_dns_getaddrinfo


def _build_db_engine() -> Engine:
    db_uri = settings.SQLALCHEMY_DATABASE_URI
    connect_args = {}
    if "sqlite" in db_uri:
        connect_args = {"check_same_thread": False}

    try:
        eng = create_engine(db_uri, pool_pre_ping=True, connect_args=connect_args)
        # Test connection
        with eng.connect() as conn:
            logger.info("Connected to primary database: %s", db_uri.split("@")[-1] if "@" in db_uri else db_uri)
        return eng
    except Exception as e:
        logger.warning("Failed to connect to primary database (%s). Falling back to SQLite.", e)
        return create_engine("sqlite:///./beam.db", connect_args={"check_same_thread": False})


engine: Engine = _build_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
