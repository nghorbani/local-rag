"""
Tests for the db module.

This module tests the database functionality, including the engine factory,
session helper, and bootstrap function.
"""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from local_rag.config import Settings
from local_rag.db import Chunk, Document, bootstrap, get_engine, get_session, session_scope


def test_document_model():
    """Test that the Document model has the expected attributes."""
    document = Document(
        path="/test/path/to/document.jpg",
        status_ocr=0,
        status_embed=0,
        md_path="/test/path/to/document.md",
    )
    
    assert document.path == "/test/path/to/document.jpg"
    assert document.status_ocr == 0
    assert document.status_embed == 0
    assert document.md_path == "/test/path/to/document.md"
    assert repr(document).startswith("<Document(")


def test_chunk_model():
    """Test that the Chunk model has the expected attributes."""
    chunk = Chunk(
        document_id=1,
        sequence=0,
        text="Test chunk text",
        embedding=None,
    )
    
    assert chunk.document_id == 1
    assert chunk.sequence == 0
    assert chunk.text == "Test chunk text"
    assert chunk.embedding is None
    assert repr(chunk).startswith("<Chunk(")


@patch("local_rag.db.create_engine")
@patch("local_rag.db.get_settings")
def test_get_engine(mock_get_settings, mock_create_engine):
    """Test that get_engine creates an engine with the correct connection string."""
    # Set up mocks
    mock_settings = MagicMock(spec=Settings)
    mock_settings.pg_connection_string = "postgresql://test-user:test-password@test-host:5432/test-db"
    mock_get_settings.return_value = mock_settings
    mock_engine = MagicMock(spec=Engine)
    mock_create_engine.return_value = mock_engine
    
    # Call the function
    engine = get_engine()
    
    # Check that create_engine was called with the correct arguments
    mock_create_engine.assert_called_once_with(
        "postgresql://test-user:test-password@test-host:5432/test-db",
        echo=False,
        future=True,
    )
    
    # Check that the function returns the engine
    assert engine is mock_engine


@patch("local_rag.db.sessionmaker")
@patch("local_rag.db.get_engine")
def test_get_session(mock_get_engine, mock_sessionmaker):
    """Test that get_session creates a session factory with the correct engine."""
    # Set up mocks
    mock_engine = MagicMock(spec=Engine)
    mock_get_engine.return_value = mock_engine
    mock_session_factory = MagicMock(spec=sessionmaker)
    mock_sessionmaker.return_value = mock_session_factory
    
    # Call the function
    session_factory = get_session()
    
    # Check that sessionmaker was called with the correct arguments
    mock_sessionmaker.assert_called_once_with(
        bind=mock_engine,
        autocommit=False,
        autoflush=False,
    )
    
    # Check that the function returns the session factory
    assert session_factory is mock_session_factory


@patch("local_rag.db.get_session")
def test_session_scope(mock_get_session):
    """Test that session_scope creates a session and handles commits and rollbacks."""
    # Set up mocks
    mock_session = MagicMock(spec=Session)
    mock_session_factory = MagicMock(spec=sessionmaker)
    mock_session_factory.return_value = mock_session
    mock_get_session.return_value = mock_session_factory
    
    # Test normal case (no exception)
    with session_scope() as session:
        assert session is mock_session
    
    # Check that the session was committed and closed
    mock_session.commit.assert_called_once()
    mock_session.close.assert_called_once()
    
    # Reset mocks
    mock_session.reset_mock()
    
    # Test exception case
    with pytest.raises(ValueError):
        with session_scope() as session:
            assert session is mock_session
            raise ValueError("Test exception")
    
    # Check that the session was rolled back and closed
    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()


@patch("local_rag.db.Base")
@patch("local_rag.db.text")
def test_bootstrap(mock_text, mock_base):
    """Test that bootstrap creates the pgvector extension and tables."""
    # Set up mocks
    mock_engine = MagicMock(spec=Engine)
    mock_conn = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None
    mock_conn.execute.return_value = mock_result
    mock_settings = MagicMock(spec=Settings)
    mock_settings.hnsw_m = 16
    mock_settings.hnsw_ef_construction = 64
    
    # Call the function
    bootstrap(mock_engine, mock_settings)
    
    # Check that the pgvector extension was created
    mock_text.assert_any_call("CREATE EXTENSION IF NOT EXISTS vector")
    mock_conn.execute.assert_any_call(mock_text.return_value)
    mock_conn.commit.assert_called()
    
    # Check that the tables were created
    mock_base.metadata.create_all.assert_called_once_with(mock_engine)
    
    # Check that the index was created
    mock_text.assert_any_call("SELECT 1 FROM pg_indexes WHERE indexname = 'chunks_embedding_idx'")
    mock_text.assert_any_call(
        "CREATE INDEX chunks_embedding_idx ON chunks USING hnsw "
        "(embedding vector_l2_ops) WITH (m = 16, ef_construction = 64)"
    )
