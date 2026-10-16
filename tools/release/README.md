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

Build on an **old base**: Ubuntu 22.04 (glibc 2.35) rather than a current release. The programs take
glibc from the machine that runs them, so the older the glibc they are built against, the more
machines can run them. The same sources built on Ubuntu 24.04 come out asking for `GLIBC_2.38` —
glibc's C23 `strtol` redirect, which libstdc++ turns on — and then refuse to start on SteamOS 3.5
and on Debian 12. Built on 22.04 they ask for `GLIBC_2.34`, which is every SteamOS from 3.4 on (the
Steam Deck, Game Mode included) and every desktop Linux since 2022.

A chroot is enough; no containers are needed.

```sh
# 1. An old base.
sudo apt-get install -y debootstrap
sudo debootstrap --variant=minbase --components=main,universe jammy /srv/jammy \
     http://archive.ubuntu.com/ubuntu
sudo mkdir -p /srv/jammy/tmp && sudo chmod 1777 /srv/jammy/tmp
sudo cp /etc/resolv.conf /srv/jammy/etc/resolv.conf
for m in proc sys dev dev/pts; do sudo mount --bind /$m /srv/jammy/$m; done

# 2. The compiler and the development packages SDL 3 is built against. CMake comes from Kitware's
#    own tarball because the toolkit's CMake asks for 3.28+ and 22.04 ships 3.22; it is only a build
#    tool, so it does not touch the programs' glibc.
sudo chroot /srv/jammy /bin/bash -c '
  apt-get update -qq && apt-get install -y -qq --no-install-recommends \
    build-essential ninja-build python3 curl file ca-certificates zlib1g-dev \
    libx11-dev libxext-dev libxrandr-dev libxcursor-dev libxi-dev libxss-dev libxtst-dev \
    libxkbcommon-dev libwayland-dev libdecor-0-dev libegl-dev libgl-dev \
    libpulse-dev libasound2-dev libudev-dev libdbus-1-dev libpipewire-0.3-dev
  curl -fsSL -o /tmp/cmake.tar.gz \
    https://github.com/Kitware/CMake/releases/download/v3.31.6/cmake-3.31.6-linux-x86_64.tar.gz
  mkdir -p /opt/cmake && tar -xzf /tmp/cmake.tar.gz --strip-components=1 -C /opt/cmake'

# 3. Build, with the project bind-mounted so the archives land in this tree. work/cybots/gen (the
#    translated code, from `make` and one `make explore` on a fresh tree) and rom/ have to be there.
sudo mount --bind "$PWD" /srv/jammy/build
sudo chroot /srv/jammy /bin/bash -c '
  export PATH=/opt/cmake/bin:$PATH
  cd /build && tools/release/linux.sh'
```

`lib.sh` builds **SDL 3 3.4.16 statically** from a checksum-checked source into
`build/deps/sdl-linux` — Ubuntu 22.04 ships no SDL 3 — then the game and the launcher against it with
`-static-libstdc++ -static-libgcc`, so the programs need only the system's usual X11/Wayland, sound
and zlib libraries. It writes both:

- `Cyberbots-linux-x86_64.tar.gz` — the two programs, self-contained;
- `Cyberbots-linux-x86_64.AppImage` — the same programs in an AppDir, their libraries gathered by
  [linuxdeploy] and packed by its appimage plugin (`tools/release/cybots.png`, drawn by
  `tools/release/make-icon.py` — original artwork, no game art). `APPIMAGE_EXTRACT_AND_RUN` is set, so
  no FUSE is needed.

To see what an archive asks for:

```sh
objdump -p build/release-linux/game/cybots | sed -n 's/^ *NEEDED *//p' | sort -u
objdump -T build/release-linux/game/cybots | grep -o 'GLIBC_[0-9.]*' | sort -uV | tail -n 1
```

On a Steam Deck the `.tar.gz` unpacks and runs as-is; the `.AppImage` can be added to Steam as a
non-Steam game. Both open the launcher, which asks for your ROM set the first time.

### On Windows, in WSL

The Linux build runs in WSL 2 (the chroot above and all), so a Linux machine is not needed. If
`wsl --install` is refused (it wants an administrator), a distribution can be imported without one:

```sh
curl -fsSL -o ubuntu-base.tar.gz \
  https://cdimage.ubuntu.com/ubuntu-base/releases/24.04/release/ubuntu-base-24.04.5-base-amd64.tar.gz
wsl --import cyberbots-wsl "%USERPROFILE%\wsl\cyberbots-wsl" ubuntu-base.tar.gz --version 2
wsl -d cyberbots-wsl -u root -- bash -c "apt-get update && apt-get install -y debootstrap"
```

Keep the distribution's folder outside temporary directories, or a disk cleanup may take it with it.
Build inside the distribution's own filesystem (a build under `/mnt/c` is slow): copy the repository
in — `rom/`, `work/` and all — and run the steps above there. WSL is what this project's own Linux and
AppImage builds were made in.

## Uploading

```sh
gh release create v1.0.0 --target main \
    --title "Cyberbots Fullmetal Madness v1.0.0" --notes-file notes.md \
    build/release/Cyberbots-windows-x64.zip \
    build/release/Cyberbots-linux-x86_64.tar.gz \
    build/release/Cyberbots-linux-x86_64.AppImage \
    build/release/SHA256SUMS.txt
```

[linuxdeploy]: https://github.com/linuxdeploy/linuxdeploy
