"""
local_rag package initializer

This file exports the public API of the local_rag package.
"""

from local_rag.config import Settings, get_settings
from local_rag.db import Base, Chunk, Document, bootstrap, get_engine, get_session, session_scope

__all__ = [
    "__version__",
    "Settings",
    "get_settings",
    "Base",
    "Document",
    "Chunk",
    "bootstrap",
    "get_engine",
    "get_session",
    "session_scope",
]
__version__ = "0.1.0"
