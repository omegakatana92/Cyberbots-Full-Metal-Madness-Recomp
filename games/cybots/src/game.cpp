// SPDX-License-Identifier: GPL-3.0-only
//
// Cyberbots: what the game's own sources add to the port (see PROGRESS.md).
#include "game.h"

namespace cps2recomp {

void RegisterCheats();   // cheats.cpp
void CheatsFrame(Machine &machine);
void RegisterTraining(); // training.cpp
void TrainingBeforeFrame(Machine &machine);
void TrainingFrame(Machine &machine);

namespace {
    void BeforeFrame(Machine &machine) {
        TrainingBeforeFrame(machine);
    }

    // (the cheats see what a frame did, after it; the training aids show what was just read)
    void Frame(Machine &machine) {
        CheatsFrame(machine);
        TrainingFrame(machine);
    }
} // namespace

void RegisterGame() {
    RegisterCheats();
    RegisterTraining();
    TheGame().beforeFrame = BeforeFrame;
    TheGame().frame = Frame;
}

} // namespace cps2recomp
