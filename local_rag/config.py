"""
Configuration module for the local_rag package.

This module provides a Settings class for loading and validating
configuration from environment variables, and a get_settings function
for retrieving the settings.
"""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

__all__ = ["Settings", "get_settings"]


@dataclass
class Settings:
    """
    Application settings loaded from environment variables.
    
    This class validates and stores all configuration settings for the application.
    """
    # OCR Configuration
    ocr_model_name: str
    ocr_api_url: str
    
    # Embedding Configuration
    embed_model_name: str
    embed_api_url: str
    embed_batch_size: int
    
    # Chat Configuration
    chat_model_name: str
    chat_api_url: str
    
    # PostgreSQL Configuration
    pg_host: str
    pg_port: int
    pg_user: str
    pg_password: str
    pg_database: str
    
    # Application Configuration
    app_host: str
    app_port: int
    doc_root: str
    
    # HNSW Index Configuration
    hnsw_m: int
    hnsw_ef_construction: int
    
    @property
    def pg_connection_string(self) -> str:
        """
        Get the PostgreSQL connection string.
        
        Returns:
            str: The connection string for SQLAlchemy.
        """
        return (
            f"postgresql://{self.pg_user}:{self.pg_password}@"
            f"{self.pg_host}:{self.pg_port}/{self.pg_database}"
        )


def get_settings() -> Settings:
    """
    Load settings from environment variables.
    
    This function loads the .env file if it exists and then creates a Settings
    object with the values from the environment variables.
    
    Returns:
        Settings: The application settings.
        
    Raises:
        ValueError: If a required environment variable is missing or invalid.
    """
    # Load .env file if it exists
    load_dotenv()
    
    # Helper function to get and validate environment variables
    def get_env(key: str, default: Optional[str] = None, required: bool = True) -> str:
        value = os.environ.get(key, default)
        if required and value is None:
            raise ValueError(f"Environment variable {key} is required but not set")
        return value
    
    # Helper function to get and validate integer environment variables
    def get_int_env(key: str, default: Optional[int] = None, required: bool = True) -> int:
        value = get_env(key, str(default) if default is not None else None, required)
        try:
            return int(value) if value is not None else None
        except ValueError:
            raise ValueError(f"Environment variable {key} must be an integer")
    
    # Create and return the Settings object
    return Settings(
        # OCR Configuration
        ocr_model_name=get_env("OCR_MODEL_NAME"),
        ocr_api_url=get_env("OCR_API_URL"),
        
        # Embedding Configuration
        embed_model_name=get_env("EMBED_MODEL_NAME"),
        embed_api_url=get_env("EMBED_API_URL"),
        embed_batch_size=get_int_env("EMBED_BATCH_SIZE", 32),
        
        # Chat Configuration
        chat_model_name=get_env("CHAT_MODEL_NAME"),
        chat_api_url=get_env("CHAT_API_URL"),
        
        # PostgreSQL Configuration
        pg_host=get_env("PG_HOST", "localhost"),
        pg_port=get_int_env("PG_PORT", 5432),
        pg_user=get_env("PG_USER"),
        pg_password=get_env("PG_PASSWORD"),
        pg_database=get_env("PG_DATABASE"),
        
        # Application Configuration
        app_host=get_env("APP_HOST", "localhost"),
        app_port=get_int_env("APP_PORT", 5000),
        doc_root=get_env("DOC_ROOT"),
        
        # HNSW Index Configuration
        hnsw_m=get_int_env("HNSW_M", 16),
        hnsw_ef_construction=get_int_env("HNSW_EF_CONSTRUCTION", 64),
    )
