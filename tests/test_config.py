"""
Tests for the config module.

This module tests the Settings class and get_settings function.
"""

import os
from unittest.mock import patch

import pytest

from local_rag.config import Settings, get_settings


def test_settings_dataclass():
    """Test that the Settings dataclass can be instantiated."""
    settings = Settings(
        ocr_model_name="test-model",
        ocr_api_url="http://test-url",
        embed_model_name="test-embed-model",
        embed_api_url="http://test-embed-url",
        embed_batch_size=32,
        chat_model_name="test-chat-model",
        chat_api_url="http://test-chat-url",
        pg_host="localhost",
        pg_port=5432,
        pg_user="test-user",
        pg_password="test-password",
        pg_database="test-db",
        app_host="localhost",
        app_port=5000,
        doc_root="/test/path",
        hnsw_m=16,
        hnsw_ef_construction=64,
    )
    
    assert settings.ocr_model_name == "test-model"
    assert settings.ocr_api_url == "http://test-url"
    assert settings.embed_model_name == "test-embed-model"
    assert settings.embed_api_url == "http://test-embed-url"
    assert settings.embed_batch_size == 32
    assert settings.chat_model_name == "test-chat-model"
    assert settings.chat_api_url == "http://test-chat-url"
    assert settings.pg_host == "localhost"
    assert settings.pg_port == 5432
    assert settings.pg_user == "test-user"
    assert settings.pg_password == "test-password"
    assert settings.pg_database == "test-db"
    assert settings.app_host == "localhost"
    assert settings.app_port == 5000
    assert settings.doc_root == "/test/path"
    assert settings.hnsw_m == 16
    assert settings.hnsw_ef_construction == 64


def test_pg_connection_string():
    """Test that the pg_connection_string property works correctly."""
    settings = Settings(
        ocr_model_name="test-model",
        ocr_api_url="http://test-url",
        embed_model_name="test-embed-model",
        embed_api_url="http://test-embed-url",
        embed_batch_size=32,
        chat_model_name="test-chat-model",
        chat_api_url="http://test-chat-url",
        pg_host="test-host",
        pg_port=5432,
        pg_user="test-user",
        pg_password="test-password",
        pg_database="test-db",
        app_host="localhost",
        app_port=5000,
        doc_root="/test/path",
        hnsw_m=16,
        hnsw_ef_construction=64,
    )
    
    assert settings.pg_connection_string == "postgresql://test-user:test-password@test-host:5432/test-db"


@patch.dict(os.environ, {
    "OCR_MODEL_NAME": "test-model",
    "OCR_API_URL": "http://test-url",
    "EMBED_MODEL_NAME": "test-embed-model",
    "EMBED_API_URL": "http://test-embed-url",
    "EMBED_BATCH_SIZE": "32",
    "CHAT_MODEL_NAME": "test-chat-model",
    "CHAT_API_URL": "http://test-chat-url",
    "PG_HOST": "test-host",
    "PG_PORT": "5432",
    "PG_USER": "test-user",
    "PG_PASSWORD": "test-password",
    "PG_DATABASE": "test-db",
    "APP_HOST": "localhost",
    "APP_PORT": "5000",
    "DOC_ROOT": "/test/path",
    "HNSW_M": "16",
    "HNSW_EF_CONSTRUCTION": "64",
})
def test_get_settings():
    """Test that get_settings loads settings from environment variables."""
    settings = get_settings()
    
    assert settings.ocr_model_name == "test-model"
    assert settings.ocr_api_url == "http://test-url"
    assert settings.embed_model_name == "test-embed-model"
    assert settings.embed_api_url == "http://test-embed-url"
    assert settings.embed_batch_size == 32
    assert settings.chat_model_name == "test-chat-model"
    assert settings.chat_api_url == "http://test-chat-url"
    assert settings.pg_host == "test-host"
    assert settings.pg_port == 5432
    assert settings.pg_user == "test-user"
    assert settings.pg_password == "test-password"
    assert settings.pg_database == "test-db"
    assert settings.app_host == "localhost"
    assert settings.app_port == 5000
    assert settings.doc_root == "/test/path"
    assert settings.hnsw_m == 16
    assert settings.hnsw_ef_construction == 64


@patch.dict(os.environ, {})
def test_get_settings_missing_required():
    """Test that get_settings raises an error when required variables are missing."""
    with pytest.raises(ValueError):
        get_settings()


@patch.dict(os.environ, {
    "OCR_MODEL_NAME": "test-model",
    "OCR_API_URL": "http://test-url",
    "EMBED_MODEL_NAME": "test-embed-model",
    "EMBED_API_URL": "http://test-embed-url",
    "EMBED_BATCH_SIZE": "not-an-integer",
    "CHAT_MODEL_NAME": "test-chat-model",
    "CHAT_API_URL": "http://test-chat-url",
    "PG_HOST": "test-host",
    "PG_PORT": "5432",
    "PG_USER": "test-user",
    "PG_PASSWORD": "test-password",
    "PG_DATABASE": "test-db",
    "APP_HOST": "localhost",
    "APP_PORT": "5000",
    "DOC_ROOT": "/test/path",
    "HNSW_M": "16",
    "HNSW_EF_CONSTRUCTION": "64",
})
def test_get_settings_invalid_integer():
    """Test that get_settings raises an error when integer variables are invalid."""
    with pytest.raises(ValueError):
        get_settings()
