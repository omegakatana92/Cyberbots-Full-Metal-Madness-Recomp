# Cyberbots: Fullmetal Madness — recomp

A native PC port of *Cyberbots: Fullmetal Madness* (Capcom, 1995, CPS-2), made with
[tmcleroy's cps2recomp](https://github.com/tmcleroy/cps2recomp) by static recompilation: the game's
68000 program is translated to C++ ahead of time and runs on the toolkit's own machine. No emulator is
part of the port.

Not affiliated with or endorsed by Capcom. No game data is in this repository: the port reads the ROM
set of a board its player owns.

## Features

With every feature off the port runs exactly as the board does. From the toolkit (no game-specific work):

- The **launcher**: choose the ROM set (checked file by file by CRC-32), set the controls, Play.
- The **in-game menu** (Esc or `F1`; a stick's click, or Start+Select): save states (nine slots),
  Reset, Insert coin, Player 2 joins, Quit game.
- **Stop, step, slow** (`P`, `O`, `-`/`=`).
- **Run-ahead** and the **Display** options (scaling, picture shape, window size, full screen).
- Every key and button **remappable**, for each player.

From the game's own sources (`games/cybots/src/`; the addresses behind them, and how each was found, are
in [games/cybots/PROGRESS.md](games/cybots/PROGRESS.md)):

- **Free play** — Start works without a coin.
- **No damage** and **No damage, player 2** — a player's health does not go down.
- **Infinite time** — the round's clock stands still.
- **One-hit knockouts** — the opponent goes down with the first hit.
- **Input display** (training aid) — what each player holds, and for how long.

`--list-features` prints the whole list. Training mode, widescreen, custom colours and the other
"alternative modes" are still to come — see [ROADMAP.md](ROADMAP.md) for what each needs and the order
to build them.

## Layout

| Path | What |
| --- | --- |
| `cps2recomp/` | A copy of the toolkit (`v0.3.0`), made by its `tools/sync-toolkit.sh`. Never change it here. |
| `games/cybots/game.cfg` | The ROM set's files and CRC-32s, the launcher's words, and the game's features. |
| `games/cybots/src/` | The game's own C++: the optional features on top of the board (`cybots.h`, `cheats.cpp`, `training.cpp`, `game.cpp`). |
| `games/cybots/PROGRESS.md` | The game's memory as it has been found (credits, health, the round's clock), and how each address was found. |
| `ROADMAP.md` | The features still to build (training mode, widescreen, modes) and what each needs. |
| `rom/` | Your ROM set: a folder of its files or the set's zip. Not committed. |
| `build/`, `work/` | Build output and generated code. Not committed. |

## Prerequisites (MSYS2, MinGW64)

Run all commands from an **MSYS2 MinGW64** shell (so `gcc`/`g++`, SDL3 and zlib are found). Install
what is missing once:

```sh
pacman -S --needed base-devel make git diffutils \
  mingw-w64-x86_64-toolchain mingw-w64-x86_64-cmake mingw-w64-x86_64-ninja \
  mingw-w64-x86_64-SDL3 mingw-w64-x86_64-zlib
```

Python 3 comes with MSYS2. CMake must be on `PATH` (`which cmake` must succeed); the MinGW64 package
above puts it in `/mingw64/bin`. `make check` also needs `git` (the repository must be a git working
tree, since `check-common` asks git for the top level) and `diffutils` (for `cmp`).

## The ROM set

`ROM` points at a folder holding the set's files or at the set's zip. The default is `rom`, so put the
set's zip at `rom/cybots.zip` (or the loose files in `rom/`). Files inside a zip are found by CRC-32,
whatever they are named, so they may sit in a subfolder. The set is only read, never changed.

The set this port is made from is MAME's `cybots` (Europe 950424); `games/cybots/game.cfg` lists its
files and checksums. **Only this revision works**: the port is made from its program, and the
training features will use addresses found in it. Other regions and revisions are refused.

## Building

```sh
make            # translate the game's code to C++ and link build/cybots/cybots.exe
make launcher   # build the launcher: build/cybots/cybots-launcher.exe
```

`make` reads the board's program out of the ROM set (above) and translates it, so the set must be in place
first. A fresh tree also needs `make explore` once, because it starts out knowing almost none of the game's
code:

```sh
make explore    # find the game's code by made-up play, in rounds (once; about ten minutes)
make            # translate again, now that the code is known
```

`make explore` plays the game headless with made-up input across several runs, records every place the code
was reached by a computed jump, and translates what it found before the next round. Its progress is in the
final run's log line, `instructions had no translation` — as low as possible is what you want (this port
reports `0`).

## Running it

The build makes two programs in `build/cybots/`: the game, `cybots.exe`, and the launcher,
`cybots-launcher.exe`. Keep them beside each other.

- **The launcher** is the way in for a player: choose the ROM set (every file checked by CRC-32), set the
  controls, choose features, Play. Where the set is kept is remembered in the launcher's own folder and
  reused next time.
- **Double-clicking `cybots.exe`** starts the launcher beside it — straight into the game if a ROM set was
  chosen before, otherwise at the launcher's first page.
- **From a shell:** `make run` runs the port windowed, with `rom/` and the settings file the Makefile
  names; pass options through with `ARGS=`, e.g. `make run ARGS=--fullscreen`.

Feature choices come from `work/cybots/settings.ini`; the eprom and the save states (`state0.bin` …) sit
beside it. `--help` lists every option (`--headless`, `--frames`, `--movie`, `--poke`, `--trace`,
`--dump-ram`, `--list-features`, `--cpu`, `--sound`, …).

**On Windows the two programs need `SDL3.dll`.** It comes from MSYS2's `mingw-w64-x86_64-SDL3` and lives in
`/mingw64/bin`, so launch from an **MSYS2 MinGW64** shell (which has it on `PATH`), or copy `SDL3.dll`
beside the two `.exe` files.

## Troubleshooting

- **"SDL3.dll was not found"** — you are not in an MSYS2 MinGW64 shell. Use one, or put MSYS2's
  `mingw64\bin` on `PATH`, or copy `SDL3.dll` beside `cybots.exe`.
- **`cmake: command not found`** — install `mingw-w64-x86_64-cmake` (Prerequisites); it lands in
  `/mingw64/bin`, which the MinGW64 shell has on `PATH`.
- **The launcher refuses the ROM set** — it checks every file by CRC-32. This port wants MAME's `cybots`
  (Europe 950424); other regions and revisions are refused on purpose.
- **Slow, or the log reports instructions left to the interpreter** — run `make explore` once, then
  `make` again.
- **No sound** — the sound program runs like the rest of the game; check the launcher's Sound row and that
  the set has its `sound_program` files (`cyb.01`, `cyb.02`).

## Checking

```sh
make check          # translated code against the interpreter, by state hash; two runs alike
make check-blocks   # every translated block beside the interpreter (registers, cycles, writes)
make check-toolkit  # cps2recomp/ is what its tools/sync-toolkit.sh recorded
make check-common   # recomp-common/ is what its tools/sync-common.sh recorded
```

See `cps2recomp/build.mk` for the full list of targets.
