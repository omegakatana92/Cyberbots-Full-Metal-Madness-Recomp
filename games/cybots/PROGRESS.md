# Cyberbots: progress

What is known of *Cyberbots: Fullmetal Madness* (Europe 950424)'s memory, and what has been built on it.
Every address here was found by experiment on the running board with the toolkit's own tools
(`docs/FEATURES.md`); nothing is a dump of the game's data, and no game data is written down.

## How each was found

The tools used, in the order they were reached for:

- `--menu FRAME:KEYS` drives the in-game menu with no window: at `FRAME` it opens the menu and presses the
  keys' buttons (`d` down, `a` confirm). "Insert coin" is the seventh `d` (Save, Load, Slot, *Game*,
  *Display*, Speed, Sound, **Insert coin**, …), which is how a coin goes in without a hand.
- `--dump-ram FRAME:FILE` writes the 64 KiB of work RAM after a frame; `--poke ADDR=BYTE` writes a byte
  every frame (a guess, to be checked); `--trace LOW-HIGH:FILE` appends a stretch of work RAM after every
  frame; `--shot-every N:PFX` writes pictures of the board.
- With free play on, a **real match** can be driven with no hand: the menu's "Player 2 joins" (the ninth
  `d`: the pages moved down by one each time a feature category was added) presses player 2's Start, and
  the character select's own timer then picks two characters and the round begins with its clock running.
  The attract show's demo fights do **not** run the clock, which is why the first traces missed it.
- `cps2recomp/tools/ramfind.py` lists the addresses that held a known value in each of several dumps;
  `cps2recomp/tools/tracechanges.py` prints a trace where it changes.

The board's own attract show **plays demo fights** (a two-player demo runs around frames 1300-2350 on a
cold boot), so a round can be watched with no coin in.

## The memory so far

| Address | Size | What | How it was found |
| --- | --- | --- | --- |
| `FF80B6` | byte | **Credits**: the value the title shows as `CREDIT(S)=n`; 0 in the attract show | Dumped work RAM with and without one coin (inserted through the menu), then `ramfind.py` for a byte that was 0 in the control and 1 after the coin. `--poke FF80B6=2` made the title show `CREDIT(S)=2`, which fixed it. This game's coinage is one coin, one credit. |
| `FFEBA0` | byte (BCD) | **The round's clock**: the board's two digits (`0x99` reads as "99"); it steps down by one about every second (every 60 frames) while a round is fought, and is 0 outside one | Drove a real match (free play + "Player 2 joins"), then took two `--dump-ram`s 60 frames apart and looked for a byte that had fallen by one: it read `0x78` where the picture at that frame showed "78". |
| `FF81E4` (+`FF85E4`) | word | **Player 1 (player 2) health** | Watched the attract demo fight: a word that steps down as hits land and is 0 at the round's end. A `--poke` to 0x10 emptied that player's bar. The two records are 0x400 apart. |
| `FF81E6` (+`FF85E6`) | word | The same health again (what the bars are drawn from) | The same trace: it moves with the health word. |
| `FF831E` (+`FF871E`) | word | The full value the health is put back to (the ceiling), held while a round is fought and 0 outside one | Found with the health words; used by the no-damage cheats. |

The health words are 0 outside a round (and in the attract show), which is what the cheats use to tell a
round from everything else.

## Features built on it (`src/`)

| Feature | Category | What it does |
| --- | --- | --- |
| `free_play` | Game (Enhanced) | Holds two credits, so Start works without a coin. It is what the title waits for, so the attract show gives way to the title. |
| `no_damage` | Cheats | Puts player 1's health back to the round's full value every frame. |
| `no_damage_2` | Cheats | The same for player 2 (the opponent's, in a one-player game). |
| `infinite_time` | Cheats | Holds the round's clock where it stood when the round began, so it never runs out. |
| `one_hit` | Cheats | Leaves the opponent (player 2) a single point of health, so any hit ends the round. |
| `input_display` | Training | What each player holds, and for how long, at their side of the picture. The first training aid: it is the toolkit's `fight::InputHistory` (the notation, the hold counts) fed from the port's own panel bits, so it needed no new address. The game's facing byte is still unknown, so the notation is not yet turned to the player's side. |

Each was checked with no window: `free_play` against the title (`CREDIT(S)=2`), the no-damage cheats
against the attract demo fight (the bar stays full, and the health word stays at the ceiling).

## Next

- The **rest of the player record**: positions, facing and the state that says a move is out are not yet
  picked out of the values that move every frame (the record from `+0x000` to `+0x33F` is busy with
  animation, the generator at `FF80B4`, and the like). They are what the training aids (a hit box, the
  input display) are built from.
- The **gauge** (the POWER bars) for `full_gauge`: it was not among the values that grow over an idle
  round, which suggests it is spent and refilled by attacking rather than filling on its own.
- A **rewrite of the damage rule** (`docs/READABLE.md`) for a cleaner `one_hit` than holding the health at
  one point.
