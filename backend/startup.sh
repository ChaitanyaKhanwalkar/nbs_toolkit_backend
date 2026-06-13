#!/usr/bin/env bash
set -e

APP_ROOT=/home/site/wwwroot
RUN_DIR=/tmp/nbsrun

echo "NbS backend startup: preparing runtime directory"
rm -rf "$RUN_DIR"
mkdir -p "$RUN_DIR"

if [ -f "$APP_ROOT/output.tar.zst" ]; then
  echo "Found Oryx output package; extracting to $RUN_DIR"
  tar --zstd -xf "$APP_ROOT/output.tar.zst" -C "$RUN_DIR"
  cd "$RUN_DIR"
else
  echo "No Oryx output package found; running from $APP_ROOT"
  cd "$APP_ROOT"
fi

echo "Startup working directory:"
pwd
echo "Startup directory contents:"
ls -la

if [ -f app/main.py ]; then
  echo "Detected app/main.py. First lines:"
  sed -n '1,40p' app/main.py
  echo "Route keyword check:"
  grep -En "health|api/v1|FastAPI|include_router" app/main.py || true
else
  echo "ERROR: app/main.py was not found in the startup directory."
  exit 1
fi

export PYTHONPATH="$PWD:${PYTHONPATH:-}"

exec python -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
