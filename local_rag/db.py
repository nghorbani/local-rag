"""
Database module for the local_rag package.

This module provides functions for creating a database engine and session,
as well as bootstrapping the database with the necessary tables and extensions.
"""

import contextlib
from typing import Any, Dict, Generator, Optional

from sqlalchemy import Column, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.sql import text

from local_rag.config import Settings, get_settings

__all__ = ["get_engine", "get_session", "bootstrap", "Document", "Chunk", "Base"]

# Create a base class for declarative models
Base = declarative_base()


class Document(Base):
    """
    Document model representing a scanned document.
    
    This model stores metadata about a document, including its path,
    status flags for OCR and embedding, and other relevant information.
    """
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    path = Column(String(255), nullable=False, unique=True)
    status_ocr = Column(Integer, default=0, nullable=False)  # 0=pending, 1=success, 2=error
    status_embed = Column(Integer, default=0, nullable=False)  # 0=pending, 1=success, 2=error
    md_path = Column(String(255), nullable=True)  # Path to the markdown file
    
    def __repr__(self) -> str:
        return f"<Document(id={self.id}, path='{self.path}', status_ocr={self.status_ocr}, status_embed={self.status_embed})>"


class Chunk(Base):
    """
    Chunk model representing a text chunk from a document.
    
    This model stores a chunk of text from a document, along with its
    embedding vector and other relevant information.
    """
    __tablename__ = "chunks"
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    sequence = Column(Integer, nullable=False)  # Order of chunk within document
    text = Column(Text, nullable=False)
    embedding = Column("embedding", None, nullable=True)  # Will be pgvector type
    
    def __repr__(self) -> str:
        return f"<Chunk(id={self.id}, document_id={self.document_id}, sequence={self.sequence})>"


def get_engine(settings: Optional[Settings] = None) -> Engine:
    """
    Create a SQLAlchemy engine for the database.
    
    Args:
        settings: Optional settings object. If not provided, it will be loaded.
        
    Returns:
        Engine: A SQLAlchemy engine.
    """
    if settings is None:
        settings = get_settings()
    
    return create_engine(
        settings.pg_connection_string,
        echo=False,  # Set to True for debugging
        future=True,
    )


def get_session(engine: Optional[Engine] = None) -> sessionmaker:
    """
    Create a SQLAlchemy session factory.
    
    Args:
        engine: Optional engine. If not provided, it will be created.
        
    Returns:
        sessionmaker: A SQLAlchemy session factory.
    """
    if engine is None:
        engine = get_engine()
    
    return sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
    )


@contextlib.contextmanager
def session_scope(session_factory: Optional[sessionmaker] = None) -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    This context manager creates a session, handles commits and rollbacks,
    and ensures the session is closed when the context exits.
    
    Args:
        session_factory: Optional session factory. If not provided, it will be created.
        
    Yields:
        Session: A SQLAlchemy session.
    """
    if session_factory is None:
        session_factory = get_session()
    
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def bootstrap(engine: Optional[Engine] = None, settings: Optional[Settings] = None) -> None:
    """
    Bootstrap the database with the necessary tables and extensions.
    
    This function creates the pgvector extension and the tables for the
    Document and Chunk models.
    
    Args:
        engine: Optional engine. If not provided, it will be created.
        settings: Optional settings object. If not provided, it will be loaded.
    """
    if settings is None:
        settings = get_settings()
    
    if engine is None:
        engine = get_engine(settings)
    
    # Create the pgvector extension
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    
    # Create the tables
    Base.metadata.create_all(engine)
    
    # Create the HNSW index on the embedding column
    with engine.connect() as conn:
        # Check if the index already exists
        result = conn.execute(text(
            "SELECT 1 FROM pg_indexes WHERE indexname = 'chunks_embedding_idx'"
        ))
        if not result.fetchone():
            # Create the index with the specified parameters
            conn.execute(text(
                f"CREATE INDEX chunks_embedding_idx ON chunks USING hnsw "
                f"(embedding vector_l2_ops) WITH (m = {settings.hnsw_m}, "
                f"ef_construction = {settings.hnsw_ef_construction})"
            ))
            conn.commit()
