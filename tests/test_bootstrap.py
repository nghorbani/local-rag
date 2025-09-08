"""
Smoke test for the local_rag package.

This test ensures that the package can be imported and that the
version is defined.
"""

import pytest


def test_package_imports():
    """Test that the package can be imported."""
    import local_rag
    assert hasattr(local_rag, "__version__")
    assert local_rag.__version__ is not None


def test_config_imports():
    """Test that the config module can be imported."""
    try:
        from local_rag import config
        assert True  # If we get here, the import succeeded
    except ImportError:
        pytest.fail("Failed to import local_rag.config")
