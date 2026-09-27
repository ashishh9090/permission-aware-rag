#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$DIR"

echo "=========================================================="
echo " Starting Permission-Aware Multi-Tenant RAG Platform     "
echo "=========================================================="

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Ensure database is seeded
python -m backend.app.seed_data

echo ""
echo "🚀 Starting Full-Stack Application on http://localhost:8000"
echo "   - Interactive Dashboard: http://localhost:8000"
echo "   - Swagger API Docs:      http://localhost:8000/docs"
echo "   - Health Check:          http://localhost:8000/health"
echo "=========================================================="

exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
