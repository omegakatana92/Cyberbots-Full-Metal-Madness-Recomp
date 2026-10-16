# Release builds

The port is released as three downloads:

| Build | File | Made by |
| --- | --- | --- |
| Windows x64 | `Cyberbots-windows-x64.zip` | `tools/release/windows.sh` (in an MSYS2 MinGW64 shell) |
| Linux x86_64 | `Cyberbots-linux-x86_64.tar.gz` | `tools/release/linux.sh` (on x86_64 Linux) |
| Linux x86_64 (AppImage) | `Cyberbots-linux-x86_64.AppImage` | `tools/release/linux.sh` (on x86_64 Linux) |

Each script also rewrites `build/release/SHA256SUMS.txt` (`tools/release/sums.sh`).

## Why these are built by hand and not in CI

The archives hold **the game's translated code** (`work/cybots/gen`), which is made from a ROM set,
so a build needs a machine that has one. CI has no ROM set (and should not), so it never builds or
holds a release archive — the same choice the toolkit's own releases make, by design.

None of the archives contains a ROM set or a BIOS: the player brings their own. What they contain is
the port — the translated program and the toolkit's machine — plus what the programs need at run
time.

## Windows

In an **MSYS2 MinGW64** shell, with `rom/` in place:

```sh
make
make launcher
tools/release/windows.sh
```

This writes `build/release/Cyberbots-windows-x64.zip`: the two `.exe`s, the DLLs they need
(`SDL3.dll`, `zlib1.dll`, the MinGW-w64/GCC runtimes), their licences and a `README.txt`. The script
checks with `objdump` that nothing else is needed, and stops if it is.

## Linux / Steam Deck

On **x86_64 Linux**, with `rom/` in place. Install the build packages once (Ubuntu 24.04 and the
like):

```sh
sudo apt install build-essential cmake ninja-build python3 curl zlib1g-dev \
  libx11-dev libxext-dev libxrandr-dev libxcursor-dev libxi-dev libxss-dev libxtst-dev \
  libxkbcommon-dev libwayland-dev wayland-protocols libdecor-0-dev libegl-dev libgl-dev \
  libpulse-dev libasound2-dev libudev-dev libdbus-1-dev libpipewire-0.3-dev
```

Then, from the repository root:

```sh
make            # translate the game's code with your ROM set (make explore once, on a fresh tree)
tools/release/linux.sh
```

`linux.sh` (`lib.sh`) builds **SDL 3 3.4.16 statically** from a checksum-checked source into
`build/deps/sdl-linux` — Ubuntu 24.04 ships no SDL 3 — then the game and the launcher against it with
`-static-libstdc++ -static-libgcc`, so the programs need only the system's usual X11/Wayland, sound
and zlib libraries. It writes both:

- `Cyberbots-linux-x86_64.tar.gz` — the two programs, self-contained;
- `Cyberbots-linux-x86_64.AppImage` — the same programs in an AppDir, their libraries gathered by
  [linuxdeploy] and packed by its appimage plugin (`tools/release/cybots.png` is a placeholder icon,
  replace it with your own). `APPIMAGE_EXTRACT_AND_RUN` is set, so no FUSE is needed.

On a Steam Deck the `.tar.gz` unpacks and runs as-is; the `.AppImage` can be added to Steam as a
non-Steam game. Both open the launcher, which asks for your ROM set the first time.

### On Windows, in WSL

The Linux build runs in WSL 2, so a Linux machine is not needed. If `wsl --install` is refused (it
wants an administrator), a distribution can be imported without one:

```sh
curl -fsSL -o ubuntu-base.tar.gz \
  https://cdimage.ubuntu.com/ubuntu-base/releases/24.04/release/ubuntu-base-24.04.5-base-amd64.tar.gz
wsl --import cyberbots-wsl "%USERPROFILE%\wsl\cyberbots-wsl" ubuntu-base.tar.gz --version 2
wsl -d cyberbots-wsl -u root -- bash -c "apt-get update && apt-get install -y <the packages above>"
```

Keep the distribution's folder outside temporary directories, or a disk cleanup may take it with it.
Build inside the distribution's own filesystem (a build under `/mnt/c` is slow): copy the repository
in — `rom/`, `work/` and all — and run `tools/release/linux.sh` there. WSL is what this project's
own Linux and AppImage builds were made in.

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
