#!/bin/bash
set -euo pipefail
APP_DIR="$HOME/railway_detector"
mkdir -p "$APP_DIR" "$HOME/.local/share/applications" "$HOME/Desktop"
chmod +x "$APP_DIR/start_railway_dashboard.sh"
cat > "$HOME/.local/share/applications/railway-track-inspector.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Railway Track Inspector
Comment=Start the local railway defect detection dashboard
Exec=$APP_DIR/start_railway_dashboard.sh
Icon=camera-web
Terminal=false
Categories=Utility;Education;
StartupNotify=true
EOF
cp "$HOME/.local/share/applications/railway-track-inspector.desktop" "$HOME/Desktop/Railway Track Inspector.desktop"
chmod +x "$HOME/Desktop/Railway Track Inspector.desktop"
if command -v gio >/dev/null 2>&1; then gio set "$HOME/Desktop/Railway Track Inspector.desktop" metadata::trusted true 2>/dev/null || true; fi
echo "Desktop icon installed. If your desktop shows an 'Allow Launching' menu, click it once."
