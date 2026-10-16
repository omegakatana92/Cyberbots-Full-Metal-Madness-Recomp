// SPDX-License-Identifier: GPL-3.0-only
//
// Cyberbots: Fullmetal Madness (Europe 950424): names for what is known of the game's memory. Found by
// experiment on the running board; PROGRESS.md says how each one was found.
#pragma once

#include "game.h"

#include <cstdint>

namespace cybots {

// The credits the game is holding, a byte: the title shows it as CREDIT(S)=n, and a coin adds one (this
// game's coinage is one coin, one credit). 0 while the board is in its attract show.
constexpr uint32_t kCredits = 0xFF80B6;

// The round's clock, one byte in BCD: the board shows it as its two digits (0x99 is "99"), and it steps
// down by one about every second (every 60 frames) while a round is fought. 0 outside a round.
constexpr uint32_t kClock = 0xFFEBA0;
constexpr uint8_t kClockFull = 0x99; // (BCD: ninety-nine)

// A player's record: the two are 0x400 apart, player 1's first.
//   +0x1E4  the health, a word (0x31E is the same value again: what the bars are drawn from)
//   +0x31E  a word that holds the full value while a round is fought (the ceiling a restored health is put
//           back to). Both health words are 0 outside a round, and in attract mode.
constexpr uint32_t kPlayer0 = 0xFF8000, kPlayerStride = 0x400;
constexpr uint32_t kHealth = 0x1E4, kHealthShown = 0x1E6, kHealthCeiling = 0x31E;
inline constexpr uint32_t Player(int n) { return kPlayer0 + static_cast<uint32_t>(n) * kPlayerStride; }

} // namespace cybots
