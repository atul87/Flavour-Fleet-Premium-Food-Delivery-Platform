import os
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

def test_environment():
    """Simple test to ensure pytest collects successfully for CI/CD."""
    assert True

def test_auth_imports():
    """Verify auth module can be imported without syntax errors."""
    try:
        from routes.auth import auth_bp
        assert auth_bp is not None
    except Exception as e:
        assert False, f"Failed to import auth module: {e}"
