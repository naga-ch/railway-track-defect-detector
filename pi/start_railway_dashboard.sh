#!/bin/bash
set -euo pipefail
APP_DIR="$HOME/railway_detector"
VENV="$HOME/railway-venv"
MODEL="$APP_DIR/best_ncnn_model"
LOG_DIR="$APP_DIR/logs"
LOG_FILE="$LOG_DIR/dashboard.log"
mkdir -p "$LOG_DIR" "$APP_DIR/captures" "$HOME/.cache/railway-inspector-chromium"
if [[ ! -d "$VENV" ]]; then
  zenity --error --title="Railway detector" --text="Python environment not found: $VENV" 2>/dev/null || true
  exit 1
fi
if [[ ! -d "$MODEL" ]]; then
  zenity --error --title="Railway detector" --text="NCNN model not found: $MODEL" 2>/dev/null || true
  exit 1
fi
source "$VENV/bin/activate"
if ! python -c 'import flask, cv2, picamera2, ultralytics' >/dev/null 2>&1; then
  if command -v zenity >/dev/null 2>&1; then
    zenity --question --title="Railway detector setup" --text="Dashboard dependencies are missing. Install Flask in the active virtual environment now?" || exit 1
  fi
  pip install flask
fi
cd "$APP_DIR"
python "$APP_DIR/railway_dashboard.py" --host 127.0.0.1 --port 8765 >>"$LOG_FILE" 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID" > "$APP_DIR/dashboard.pid"
BROWSER_PID=""
cleanup() {
  if [[ -n "$BROWSER_PID" ]]; then kill "$BROWSER_PID" 2>/dev/null || true; fi
  kill "$SERVER_PID" 2>/dev/null || true
  rm -f "$APP_DIR/dashboard.pid" "$APP_DIR/browser.pid"
}
trap cleanup EXIT INT TERM
for _ in $(seq 1 40); do
  if curl -fsS http://127.0.0.1:8765/ >/dev/null 2>&1; then break; fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    zenity --error --title="Railway detector" --text="Dashboard failed to start. See $LOG_FILE" 2>/dev/null || true
    exit 1
  fi
  sleep 0.25
done
BROWSER=""
if command -v chromium >/dev/null 2>&1; then
  BROWSER=chromium
elif command -v chromium-browser >/dev/null 2>&1; then
  BROWSER=chromium-browser
fi
if [[ -n "$BROWSER" ]]; then
  "$BROWSER" --kiosk --noerrdialogs --disable-infobars --no-first-run \
    --user-data-dir="$HOME/.cache/railway-inspector-chromium" http://127.0.0.1:8765/ &
  BROWSER_PID=$!
  echo "$BROWSER_PID" > "$APP_DIR/browser.pid"
  wait "$BROWSER_PID" || true
else
  xdg-open http://127.0.0.1:8765/ || true
  wait "$SERVER_PID"
fi
