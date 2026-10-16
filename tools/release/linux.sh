#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-only
#
# The Linux x86_64 release (Steam Deck and other x86_64 Linux):
#
#   build/release/Cyberbots-linux-x86_64.tar.gz    the port, on its own
#   build/release/Cyberbots-linux-x86_64.AppImage  the same port, as an AppImage
#
# RUN THIS ON x86_64 LINUX, WHERE YOUR ROM SET IS. The archives hold the game's translated code,
# which is made from a ROM set (`make`, `make explore`), so they cannot be built in CI: the same
# reason the Windows zip is made by hand (tools/release/windows.sh).
#
#   make && make launcher      # with rom/ present
#   tools/release/linux.sh
#
# It needs a compiler, cmake, ninja, make, curl, python3 and the SDL3 and zlib development
# packages:
#   Arch / SteamOS:  sudo pacman -S --needed base-devel cmake ninja sdl3 zlib
#   Debian/Ubuntu:   sudo apt install build-essential cmake ninja-build libsdl3-dev zlib1g-dev curl python3
set -eu
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

GAME=cybots
NAME=Cyberbots
OUT="$ROOT/build/release"
BUILD="$ROOT/build/release-linux"
STAGE="$BUILD/stage/$NAME"

[ -f "build/$GAME/$GAME" ] || { echo "error: build/$GAME/$GAME is missing: run 'make' first" >&2; exit 1; }
[ -f "build/$GAME/$GAME-launcher" ] || { echo "error: build/$GAME/$GAME-launcher is missing: run 'make launcher' first" >&2; exit 1; }

# 1. The tarball: the two programs, the README and the licence.
rm -rf "$BUILD/stage"
mkdir -p "$STAGE"
cp "build/$GAME/$GAME" "build/$GAME/$GAME-launcher" "$STAGE/"
cp "$ROOT/README.md" "$STAGE/README.md"
cp "$ROOT/LICENSE" "$STAGE/LICENSE"
unset STRIP 2>/dev/null || true
strip "$STAGE/$GAME" "$STAGE/$GAME-launcher" 2>/dev/null || true

mkdir -p "$OUT"
rm -f "$OUT/$NAME-linux-x86_64.tar.gz"
tar -czf "$OUT/$NAME-linux-x86_64.tar.gz" -C "$BUILD/stage" "$NAME"
echo "wrote $OUT/$NAME-linux-x86_64.tar.gz"

# 2. The AppImage: an AppDir with the programs, an icon, a desktop entry and an AppRun; the
#    libraries the programs need gathered by linuxdeploy; the archive packed by its appimage plugin.
APPDIR="$BUILD/$NAME.AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin" \
         "$APPDIR/usr/share/applications" \
         "$APPDIR/usr/share/icons/hicolor/256x256/apps"
cp "build/$GAME/$GAME" "build/$GAME/$GAME-launcher" "$APPDIR/usr/bin/"
cp "$ROOT/tools/release/$GAME.png" "$APPDIR/$GAME.png"
cp "$ROOT/tools/release/$GAME.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/$GAME.png"

cat > "$APPDIR/AppRun" <<'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/usr/bin/cybots-launcher" "$@"
EOF
chmod +x "$APPDIR/AppRun"

cat > "$APPDIR/usr/share/applications/$GAME.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Cyberbots: Fullmetal Madness
Comment=Native recomp port (needs your own cybots ROM set)
Exec=$GAME-launcher
Icon=$GAME
Categories=Game;ArcadeGame;
Terminal=false
EOF

TOOLS="$BUILD/tools"
mkdir -p "$TOOLS"
[ -x "$TOOLS/linuxdeploy" ] || curl -fsSL -o "$TOOLS/linuxdeploy" \
    https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
[ -x "$TOOLS/linuxdeploy-plugin-appimage" ] || curl -fsSL -o "$TOOLS/linuxdeploy-plugin-appimage" \
    https://github.com/linuxdeploy/linuxdeploy-plugin-appimage/releases/download/continuous/linuxdeploy-plugin-appimage-x86_64.AppImage
chmod +x "$TOOLS/linuxdeploy" "$TOOLS/linuxdeploy-plugin-appimage"

# (linuxdeploy and its plugin are themselves AppImages: extract and run, so no FUSE is needed)
export APPIMAGE_EXTRACT_AND_RUN=1
export LINUXDEPLOY_OUTPUT_VERSION="$(cat "$ROOT/VERSION" 2>/dev/null || echo 0.1.0)"
"$TOOLS/linuxdeploy" --appdir "$APPDIR" \
    --executable "$APPDIR/usr/bin/$GAME" \
    --executable "$APPDIR/usr/bin/$GAME-launcher" \
    --desktop-file "$APPDIR/usr/share/applications/$GAME.desktop" \
    --icon-file "$APPDIR/$GAME.png" \
    --plugin appimage

rm -f "$OUT/$NAME-linux-x86_64.AppImage"
for a in "$ROOT"/*.AppImage; do
    [ -f "$a" ] && mv "$a" "$OUT/$NAME-linux-x86_64.AppImage"
done
[ -f "$OUT/$NAME-linux-x86_64.AppImage" ] || { echo "error: no AppImage was written" >&2; exit 1; }
echo "wrote $OUT/$NAME-linux-x86_64.AppImage"

"$ROOT/tools/release/sums.sh"
