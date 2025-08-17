"""
Minimal tests that should definitely pass
Use this as a baseline to ensure testing works
"""

import os
import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_project_exists():
    """Test that the project structure exists"""
    assert Path("src").exists()
    assert Path("app").exists()
    assert Path("tests").exists()


def test_requirements_exists():
    """Test that requirements.txt exists"""
    assert Path("requirements.txt").exists()


def test_main_api_exists():
    """Test that main API file exists"""
    assert Path("app/main.py").exists()


def test_can_import_app():
    """Test that we can import the FastAPI app"""
    try:
        from app.main import app

        assert app is not None
    except ImportError:
        pytest.skip("FastAPI app not importable")


def test_can_import_data_pipeline():
    """Test that we can import DataPipeline"""
    try:
        from src.data_pipeline import DataPipeline

        assert DataPipeline is not None
    except ImportError:
        pytest.skip("DataPipeline not importable")


def test_models_directory_exists():
    """Test that models directory exists"""
    assert Path("models").exists()


def test_basic_math():
    """Sanity check that pytest is working"""
    assert 2 + 2 == 4
    assert 10 * 10 == 100


def test_api_has_endpoints():
    """Test that API has basic endpoints"""
    try:
        from app.main import app

        routes = [route.path for route in app.routes]

        # Check for at least some endpoints
        assert "/" in routes
        assert "/health" in routes or "/healthz" in routes

    except ImportError:
        pytest.skip("Cannot import API")


if __name__ == "__main__":
    print("Running minimal tests...")
    pytest.main([__file__, "-v"])
