# ============================================
# FLAVOUR FLEET — WSGI Entry Point
# Used by gunicorn for production deployments:
#   gunicorn --worker-class eventlet -w 1 wsgi:app
# ============================================

import os
from dotenv import load_dotenv

# Load .env from the same directory as this file
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from app import app, socketio  # noqa: E402

if __name__ == "__main__":
    socketio.run(app)
