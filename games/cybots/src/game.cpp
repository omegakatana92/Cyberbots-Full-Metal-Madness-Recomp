// SPDX-License-Identifier: GPL-3.0-only
//
// Cyberbots: what the game's own sources add to the port (see PROGRESS.md).
#include "game.h"

namespace cps2recomp {

void RegisterCheats();             // cheats.cpp
void CheatsFrame(Machine &machine);

void RegisterGame() {
    RegisterCheats();
    // (the cheats see what a frame did, after it)
    TheGame().frame = [](Machine &machine) {
        CheatsFrame(machine);
    };
}

} // namespace cps2recomp
