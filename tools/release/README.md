# Release builds

The port is released as three downloads:

| Build | File | Made by |
| --- | --- | --- |
| Windows x64 | `Cyberbots-windows-x64.zip` | `tools/release/windows.sh` (in an MSYS2 MinGW64 shell) |
| Linux x86_64 | `Cyberbots-linux-x86_64.tar.gz` | `tools/release/linux.sh` (on x86_64 Linux) |
| Linux x86_64 (AppImage) | `Cyberbots-linux-x86_64.AppImage` | `tools/release/linux.sh` (on x86_64 Linux) |

Each script also rewrites `build/release/SHA256SUMS.txt` (`tools/release/sums.sh`).

## Why these are built by hand and not in CI

The archives hold **the game's translated code**, which is made from a ROM set, so a build needs a
machine that has one. CI has no ROM set (and should not), so it never builds or holds a release
archive. The same is true of the toolkit this port is built with, by design.

None of the archives contains a ROM set or a BIOS: the player brings their own. What they contain
is the port — the translated program and the toolkit's machine — plus the DLLs or libraries the
programs need at run time.

## Windows

In an **MSYS2 MinGW64** shell, with `rom/` in place:

```sh
make
make launcher
tools/release/windows.sh
```

This writes `build/release/Cyberbots-windows-x64.zip`: the two `.exe`s, the DLLs they need
(`SDL3.dll`, `zlib1.dll`, the MinGW-w64/GCC runtimes), their licences and a `README.txt`. The
script checks with `objdump` that nothing else is needed, and stops if it is.

## Linux / Steam Deck

On **x86_64 Linux**, with `rom/` in place, and the SDL3 development package installed:

```sh
# Arch / SteamOS
sudo pacman -S --needed base-devel cmake ninja sdl3 zlib
# Debian / Ubuntu
sudo apt install build-essential cmake ninja-build libsdl3-dev zlib1g-dev curl python3

make
make launcher
tools/release/linux.sh
```

This writes both the `.tar.gz` (the two programs, self-contained) and the `.AppImage` (the same
programs in an AppDir, their libraries gathered by [linuxdeploy] and packed by its appimage
plugin; the icon is `tools/release/cybots.png`, a placeholder to replace). `APPIMAGE_EXTRACT_AND_RUN`
is set, so the AppImage tools need no FUSE.

On a Steam Deck the `.tar.gz` unpacks and runs as-is; the `.AppImage` can be added to Steam as a
non-Steam game (both open the launcher, which asks for your ROM set the first time).

## Uploading

```sh
gh release create v0.1.0-beta.1 --target main --prerelease \
    --title "0.1.0-beta.1" --notes-file notes.md \
    build/release/Cyberbots-windows-x64.zip \
    build/release/Cyberbots-linux-x86_64.tar.gz \
    build/release/Cyberbots-linux-x86_64.AppImage \
    build/release/SHA256SUMS.txt
```

[linuxdeploy]: https://github.com/linuxdeploy/linuxdeploy
