#ifndef SOUND_H
#define SOUND_H

#include <stdint.h>

/**
 * ==========================================
 * AUDIO SYNTHESIS & SEQUENCING
 * ==========================================
 * This module manages all sound generation via the Game Boy APU registers.
 */

// Resets internal music state variables
void sound_reset_music_state(void);

// Callbacks to be hooked into the Game Boy VBL (Vertical Blanking) interrupt
void play_music_tick(void);

// Call to manually play a note from the game over / victory sequences 
void play_gameover_step(uint8_t step);
void play_victory_step(uint8_t step);

#endif
