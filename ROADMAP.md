# Cyberbots — features and roadmap

Where this port stands against a finished one, and what each missing piece needs. The reference is
the toolkit's own complete example, [vampire-savior-recomp](https://github.com/tmcleroy/vampire-savior-recomp)
(`games/vampire_savior/src/`), and the toolkit's documents `docs/FEATURES.md` and `docs/FIGHT.md`.

Everything below is an **optional feature**: with every feature off, the port must run exactly as the
board does. Nothing from the game (no ROM, no RAM dump, no ripped art/text) may ever be committed —
each thing found is recorded in `PROGRESS.md` as *how* it was found (a RAM diff, a write watch, a
trace), never as the data itself.

## What works today, with no game work

These come from the toolkit and already run in `build/cybots/cybots.exe`:

- The **launcher**: chooses the ROM set, checks every file by CRC-32, sets the controls, Play.
- The **in-game menu** (Esc, `F1`, a stick's click, or Start+Select): save states (9 slots), Reset,
  Insert coin, Player 2 joins, Quit game.
- **Stop, step, slow** (P, O, `-`/`=`).
- **Run-ahead** and the **Display** options (scaling, picture shape, window size, full screen).
- Every key and button **remappable**, for each player.

`--list-features` shows these; today they are the only ones.

## What a finished port adds (this is the work)

### 0. Foundation — know the game's memory

Nearly every feature below reads the game's memory or hooks a routine, so the first job is a **RAM map**
for Cyberbots: credits, each player's health, the round timer, each player's state (grounded, in the
air, in hitstun, facing), attack flags and boxes, the gauge/meter, positions, the stage id, the
character ids, and the round/match state. The names go in a new `games/cybots/src/cybots.h`, the way
`vsav.h` does.

How the toolkit finds these (all documented in `docs/FEATURES.md`):

- `--dump-ram F:FILE` + `tools/ramfind.py DUMP=VALUE ...` — addresses that held a known value across
  several dumps (this is how a credit counter, a clock and health words are found).
- `--trace LOW-HIGH:FILE` with a movie that does known things at known frames (this is how positions
  and an attack flag are found).
- `--watch LOW[-HIGH]` — every write to an address and the instruction that made it, read against
  `work/cybots/program.lst` (this is how a damage routine and a clock tick are found).
- `--poke ADDR=BYTE,...` to try a guess; `--shot-every N:PFX` + `tools/sheet.sh` to see a run.

Deliverable: `cybots.h` (names) and a `board.cpp` that reads the EEPROM's operator settings.

### 1. The Features page (the game's own switches)

Registered from `games/cybots/src/`; they then appear on the launcher's Features page and the in-game
menu, and are kept in `settings.ini`.

| Feature | Kind | Needs |
| --- | --- | --- |
| `free_play` (Enhanced) | on/off | the credit word |
| `no_damage`, `one_hit` | on/off | the damage routine (hook) or the health words |
| `infinite_time` | on/off | the timer word |
| `full_gauge` | on/off | the gauge word |
| Board/operator settings (difficulty, damage, timer speed, game speed) | choices | reading the EEPROM settings |
| "The game's own test menu" | command | a routine address to jump to |

Quick wins: these prove the RAM map and populate the menu.

### 2. Training mode (the headline feature)

The toolkit's `fight/` code is shared and game-independent; the game says, from its own memory, what
the players are doing. Vampire Savior's `src/training.cpp`, `frames.cpp`, `fight.cpp`, `boxes.cpp`,
`input.cpp` are the model. What to build:

- **Hit boxes / spacing boxes** — the game's own hit test boxes read and drawn (`SetBoxes`).
- **Frame data + frame meter** — startup/active/recovery and advantage per move (`fight::Frames`,
  `MoveLog` writing `frame_data.csv`).
- **Input display + notation** — what each player holds, the stick as a keypad number
  (`InputHistory`, `Notation`).
- **Combo readout** — hits, damage, what comes back, the round's best (`Combos`).
- **Health refills.**
- **The dummy** — stand/crouch/jump, guard (always / after a hit / at random, high or low), record and
  replay (three slots or random), get up rolled or in place (`Dummy`, `RegisterDummy`).
- **Start over** — the round as it began, middle or corner, sides swapped (a command).
- **Stage** — any of Cyberbots' stages, or the game's own choice.

Needs: the RAM map, hooks into the fight (hit tests, the players' state, move start), and a
"Training mode" command that sets up a clock-less fight nobody loses.

### 3. Alternative modes

Each is a command with a page of its own. Ordered by value and cost:

| Mode | What it adds | Needs |
| --- | --- | --- |
| Attract mode | the game's own show on a loop, no coin | a way to reach and keep the game's attract sequence |
| Stage viewer | a stage alone, scrolling, with its music | rewrites of the camera/stage drawing + `spare.h` |
| Model viewer | one character, on a stage or plain ground, any animation, any size | the character's animation lists, the model/picture code |
| Survival | one opponent after another on the health left | the round/match state |
| Endless battle | two computer fighters, no bars/clock, stages fading | `spare.h` (next fight readied while the last ends) |
| Ring out | no health; knock the opponent off the stage end | rewrites of the ring logic |
| Colour editor | see §4 | the palette tables |

### 4. Custom colours + the colour editor

`fight/colours.h` gives a game the players' own colours and an editor to make them. Needs: the ROM
image's palette ranges (character sets and effect lines), the character/set names, `showSet` (the
buffer the board shows from), and a model viewer for the editor to work in.

### 5. Widescreen

A switch on the launcher's first page, off in every preset (it can change how the game plays). Fights
are shown in 16:9, 512 columns where the board's 384, at the same height and scale — a third more of
the stage, drawn from what the game already has (nothing is stretched). The toolkit's `widescreen.cpp` in
Vampire Savior is the example. Needs rewrites of the camera (stop 64 short), the scroll screens
(`scroll[n]`, `tile`), the objects (`object`), and the edges/pieces that must be kept while they are in
the wide picture. An **Invisible walls** option keeps the wide picture but plays exactly as the board
does (checked frame-for-frame by `make check-widescreen`).

### 6. Readable rewrites (correctness, and what the above builds on)

Rewrite the fight's key routines by hand as named C++ (`docs/READABLE.md`): a frame's hit tests,
pushing apart, damage, the round frame and clock, guard range, whether a hit is guarded, reading the
panel. Vampire Savior has 123 routines rewritten; each is checked call by call with
`make check-rewrites`. This is what makes training mode and widescreen possible, and it is the part
most worth doing carefully.

## Recommended order

1. **Foundation** (`cybots.h` RAM map + `board.cpp`) — everything depends on it.
2. **Free play + cheats** — small, proves the map, fills the Features page.
3. **Readable rewrites** of the fight routines — needed by 4 and 5, and correctness.
4. **Training mode.**
5. **Widescreen.**
6. **Alternative modes** (stage → model → survival → endless → ring out).
7. **Colour editor.**

**Done so far:** the RAM map has begun — the credits, both players' health, and the round's clock, each
found and checked (`games/cybots/PROGRESS.md`) — and features are in: free play, no damage for either
player, infinite time, one-hit knockouts, and the first training aid, the input display
(`games/cybots/src/`). Next: the rest of a player's record (positions, facing, whether a move is out) for
the other training aids, and the gauge for `full_gauge`.

## Before uploading: a checklist

- [ ] `README.md` states the exact ROM set (`cybots`, Europe 950424) and that **only that revision**
      works, with the Capcom disclaimer.
- [ ] `rom/`, `build/`, `work/` are ignored and **absent** from the repository; no game data, keys or
      dumps anywhere; no screenshots beyond the few needed for the README.
- [ ] `PROGRESS.md` records how each finding was made (a RAM diff, a watch, a trace), not the data.
- [ ] `make check`, `make check-toolkit`, `make check-common` all pass.
- [ ] `LICENSE` (GPL-3.0-only) and `THIRD_PARTY_NOTICES.md` (the cipher is MAME's, BSD-3-Clause).
- [ ] Repo description set (see README's title line / the About field).
- [ ] First commit made; the repository builds from a fresh clone with the player's own ROM set.
