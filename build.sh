#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "=== [Step 1/3] Building Vue 3 Frontend ==="
cd frontend
npm install
npm run build
cd ..

echo "=== [Step 2/3] Installing Python Dependencies ==="
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "=== [Step 3/3] Preparing Django Staticfiles, DB Migrations & Seed Data ==="
cd backend
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py seed_data
cd ..

echo "=== HR System Build Completed Successfully! ==="

