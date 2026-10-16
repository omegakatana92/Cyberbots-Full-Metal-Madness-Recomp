// SPDX-License-Identifier: GPL-3.0-only
//
// Cyberbots: cheats and free play. Optional features (the launcher's Features page and the in-game menu
// switch them); they work on the game's memory after every frame. With every feature off the game runs
// exactly as the board does.
#include "cybots.h"

namespace cps2recomp {

namespace {
    using namespace cybots;

    // A round is being fought when both players' health is a sensible amount: outside a round (and in the
    // attract show) the game keeps 0 there, which is what tells the cheats not to touch it.
    bool Fighting() {
        for (int n = 0; n < 2; n++) {
            if (Ram16(Player(n) + kHealth) == 0) {
                return false;
            }
        }
        return true;
    }

    uint8_t clockAtStart = 0; // (the round's clock when it began: infinite_time)

    void Frame(Machine &) {
        // (two credits: a second player can always join. It is what the title waits for, so the attract
        // show gives way to it, as on a board with free play set.)
        if (FeatureOn("free_play") && Ram8(kCredits) < 2) {
            SetRam8(kCredits, 2);
        }
        if (!Fighting()) {
            clockAtStart = 0; // (the clock is put back when the next round begins)
            return;
        }
        static const char *const kNoDamage[2] = {"no_damage", "no_damage_2"};
        for (int n = 0; n < 2; n++) {
            if (FeatureOn(kNoDamage[n])) {
                // Put the health back where the round began, the value the game keeps for it.
                const uint16_t ceiling = Ram16(Player(n) + kHealthCeiling);
                SetRam16(Player(n) + kHealth, ceiling);
                SetRam16(Player(n) + kHealthShown, ceiling);
            }
        }
        if (FeatureOn("infinite_time")) {
            // The clock stands still: keep it at what it read when this round began.
            const uint8_t now = Ram8(kClock);
            if (clockAtStart == 0 && now > 0) {
                clockAtStart = now;
            }
            if (clockAtStart != 0) {
                SetRam8(kClock, clockAtStart);
            }
        }
        // One-hit knockouts: the opponent (player 2) is left with a single point of health, so any hit
        // ends the round. (A hit does at least one.)
        if (FeatureOn("one_hit")) {
            SetRam16(Player(1) + kHealth, 1);
            SetRam16(Player(1) + kHealthShown, 1);
        }
    }
} // namespace

void CheatsFrame(Machine &machine) {
    Frame(machine);
}

void RegisterCheats() {
    Game &game = TheGame();
    game.features.push_back({"free_play", "Game", "Free play", "Start works without a coin.", kFeatureEnhanced});
    game.features.push_back({"no_damage", "Cheats", "No damage", "Player 1's health does not go down."});
    game.features.push_back({"no_damage_2", "Cheats", "No damage, player 2", "Player 2's health does not go down (the opponent's, in a one-player game)."});
    game.features.push_back({"infinite_time", "Cheats", "Infinite time", "The round's clock stands still."});
    game.features.push_back({"one_hit", "Cheats", "One-hit knockouts", "Player 2 (the opponent, in a one-player game) goes down with the first hit."});
}

} // namespace cps2recomp
