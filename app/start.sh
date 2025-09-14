#!/bin/bash
set -e

# DB migrate
alembic upgrade head

# FastAPI başlat
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
