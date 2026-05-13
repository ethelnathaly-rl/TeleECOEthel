#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  echo "No existe .venv. Ejecuta primero: ./install.sh" >&2
  exit 1
fi
# shellcheck disable=SC1091
source .venv/bin/activate

if [ ! -f evaluaciones.db ]; then
  python scripts/init_db.py --demo
fi

mkdir -p logs app/static/grabaciones

echo "Iniciando TeleECOE..."
echo "PC maestra: http://localhost:5000"
python run.py
