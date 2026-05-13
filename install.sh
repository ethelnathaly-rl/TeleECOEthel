#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "No se encontró python3. Instala Python 3.10+ y vuelve a ejecutar." >&2
  exit 1
fi

VENV_DIR=".venv"
"$PYTHON_BIN" -m venv "$VENV_DIR"
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Creado .env desde .env.example"
fi

if [ ! -f go2rtc.yaml ]; then
  cp go2rtc.example.yaml go2rtc.yaml
  echo "Creado go2rtc.yaml desde go2rtc.example.yaml"
fi

python scripts/init_db.py --demo
mkdir -p logs app/static/grabaciones

echo ""
echo "✅ TeleECOE instalado."
echo "Inicia con: ./start.sh"
