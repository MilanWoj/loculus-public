#!/usr/bin/env bash
# Author: MilanWoj
set -euo pipefail

APP_NAME="Loculus"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/build-macos"
APP_BUNDLE="$BUILD_DIR/$APP_NAME.app"

rm -rf "$APP_BUNDLE"
mkdir -p "$APP_BUNDLE/Contents/MacOS" "$APP_BUNDLE/Contents/Resources"

swiftc -O \
  "$SCRIPT_DIR/main.swift" "$SCRIPT_DIR/AppDelegate.swift" \
  -o "$APP_BUNDLE/Contents/MacOS/$APP_NAME"

cp "$SCRIPT_DIR/Info.plist" "$APP_BUNDLE/Contents/Info.plist"
echo "$PROJECT_ROOT" > "$APP_BUNDLE/Contents/Resources/project_root.txt"

echo "Built $APP_BUNDLE"
