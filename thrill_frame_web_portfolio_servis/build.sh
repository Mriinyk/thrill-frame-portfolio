#!/usr/bin/env bash
set -o errexit

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

python -m pip install -r ../requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
