#include "sound.h"
#include "globals.h"
#include <gb/gb.h>

/**
 * ==========================================
 * GAME BOY AUDIO HARDWARE (APU)
 * ==========================================
 * Il Game Boy ha 4 canali audio. Noi usiamo:
 * - Canale 1 (Onda quadra con sweep & envelope): Usato per gli arpeggi rapidi (es. Vittoria).
 * - Canale 2 (Onda quadra con envelope): Usato per i bassi pulsanti o le melodie tenute.
 * - Canale 4 (Rumore bianco): Usato per simulare le percussioni (crash o thud) manipolando le frequenze noise.
 */

// --- Variabili di stato interne per i timer musicali ---
static volatile uint8_t music_timer = 0;
static volatile uint8_t music_step = 0;

static volatile uint8_t gameover_music_timer = 0;
static volatile uint8_t gameover_music_step = 0;

static volatile uint8_t victory_music_timer = 0;
static volatile uint8_t victory_music_step = 0;

static volatile uint8_t title_music_timer = 0;
static volatile uint8_t title_music_step = 0;

static volatile uint8_t finale_music_timer = 0;
static volatile uint8_t finale_music_step = 0;

// Note frequencies calculation: (2048 - (131072 / frequency))
#define R 0
#define N_C2 44
#define N_E2 458
#define N_F2 547
#define N_G2 742
#define N_A2 857
#define N_AS2 907
#define N_B2 961
#define N_C3 1046
#define N_CS3 1103
#define N_D3 1155
#define N_E3 1253
#define N_F3 1298
#define N_FS3 1340
#define N_G3 1380
#define N_GS3 1417
#define N_A3 1453
#define N_AS3 1486
#define N_B3 1517
#define N_C4 1547
#define N_CS4 1575
#define N_D4 1602
#define N_E4 1651
#define N_F4 1673
#define N_FS4 1694
#define N_G4 1714
#define N_GS4 1732
#define N_A4 1751
#define N_AS4 1767
#define N_B4 1783
#define N_C5 1798
#define N_CS5 1812
#define N_D5 1825
#define N_E5 1849
#define N_F5 1860
#define N_FS5 1871
#define N_G5 1881
#define N_GS5 1890
#define N_A5 1899

// --- Sequences ---

const uint16_t ch1_seq[128] = {
    // 1 Dm
    N_D3, N_A3, N_D4, N_A3, N_D3, N_A3, N_D4, N_A3,
    // 2 A/C#
    N_CS3, N_A3, N_CS4, N_A3, N_CS3, N_A3, N_CS4, N_A3,
    // 3 F/C
    N_C3, N_A3, N_C4, N_A3, N_C3, N_A3, N_C4, N_A3,
    // 4 G/B
    N_B2, N_G3, N_B3, N_G3, N_B2, N_G3, N_B3, N_G3,
    // 5 Bb
    N_AS2, N_F3, N_AS3, N_F3, N_AS2, N_F3, N_AS3, N_F3,
    // 6 F/A
    N_A2, N_F3, N_A3, N_F3, N_A2, N_F3, N_A3, N_F3,
    // 7 Gm
    N_G2, N_D3, N_G3, N_D3, N_G2, N_D3, N_G3, N_D3,
    // 8 A7
    N_A2, N_E3, N_A3, N_CS4, N_A2, N_E3, N_A3, N_CS4,
    // 9 Dm (intensifies: higher arpeggio)
    N_D3, N_D4, N_F4, N_A4, N_D3, N_D4, N_F4, N_A4,
    // 10 A/C#
    N_CS3, N_CS4, N_E4, N_A4, N_CS3, N_CS4, N_E4, N_A4,
    // 11 F/C
    N_C3, N_C4, N_F4, N_A4, N_C3, N_C4, N_F4, N_A4,
    // 12 G/B
    N_B2, N_B3, N_D4, N_G4, N_B2, N_B3, N_D4, N_G4,
    // 13 Bb
    N_AS2, N_AS3, N_D4, N_F4, N_AS2, N_AS3, N_D4, N_F4,
    // 14 F/A
    N_A2, N_A3, N_C4, N_F4, N_A2, N_A3, N_C4, N_F4,
    // 15 Gm
    N_G2, N_G3, N_AS3, N_D4, N_G2, N_G3, N_AS3, N_D4,
    // 16 A7 -> Dm resolution
    N_A2, N_A3, N_CS4, N_E4, N_A2, R, N_D3, R
};

// "Going Deeper" mysterious melody (96 steps)
const uint16_t next_level_seq[96] = {
    // 1. Am (Relief but somewhat somber)
    N_A3, N_C4, N_E4, N_A4, N_E4, N_C4, N_A3, R,
    N_A3, N_C4, N_E4, N_A4, N_E4, N_C4, N_A3, R,
    // 2. Fmaj7 (Mystery and opening up)
    N_F3, N_A3, N_C4, N_E4, N_C4, N_A3, N_F3, R,
    N_F3, N_A3, N_C4, N_E4, N_C4, N_A3, N_F3, R,
    // 3. Dm (Getting darker)
    N_D3, N_F3, N_A3, N_D4, N_A3, N_F3, N_D3, R,
    N_D3, N_F3, N_A3, N_D4, N_A3, N_F3, N_D3, R,
    // 4. E7 (Tension, unresolved)
    N_E3, N_GS3, N_B3, N_D4, N_B3, N_GS3, N_E3, R,
    N_E3, N_GS3, N_B3, N_D4, N_B3, N_GS3, N_E3, R,
    // 5. C augmented (Eerie, strange descent)
    N_C3, N_E3, N_GS3, N_C4, N_GS3, N_E3, N_C3, R,
    N_C3, N_E3, N_GS3, N_C4, N_GS3, N_E3, N_C3, R,
    // 6. Deep descending finish (Fading into the abyss)
    N_G2, N_E3, N_C3, R, N_E2, N_C3, N_G2, R,
    N_C2, R, R, R, R, R, R, R
};

const uint16_t ch2_seq[128] = {
    // 1 Dm
    N_F4, R, R, R, N_E4, R, R, R,
    // 2 A/C#
    N_E4, R, R, R, N_D4, R, R, R,
    // 3 F/C
    N_C4, R, R, R, N_D4, R, N_E4, R,
    // 4 G/B
    N_D4, R, R, R, N_F4, R, R, R,
    // 5 Bb
    N_D4, R, R, R, N_C4, R, R, R,
    // 6 F/A
    N_C4, R, R, R, N_AS3, R, R, R,
    // 7 Gm
    N_AS3, R, N_A3, N_AS3, N_C4, R, N_AS3, R,
    // 8 A7
    N_A3, R, R, R, R, R, R, R,
    // 9 Dm
    N_A4, R, R, R, N_G4, R, N_F4, N_E4,
    // 10 A/C#
    N_G4, R, R, R, N_F4, R, N_E4, N_D4,
    // 11 F/C
    N_F4, R, R, R, N_E4, R, N_C4, R,
    // 12 G/B
    N_D4, R, R, R, N_G4, R, R, R,
    // 13 Bb
    N_F4, R, R, R, N_E4, R, N_D4, N_CS4,
    // 14 F/A
    N_E4, R, R, R, N_D4, R, N_C4, N_B3,
    // 15 Gm
    N_D4, R, R, R, N_C4, R, N_AS3, R,
    // 16 A7 -> Dm resolution
    N_A3, R, R, R, R, R, N_D4, R
};

// Eerie pulse note frequencies (96-note sequence for normal gameplay)
const uint16_t eerie_reg_vals[] = {
    // Pattern 1 (A minor)
    1453, 1546, 1650, 1733, 1754, 1733, 1650, 1546,
    1453, 1546, 1650, 1733, 1754, 1733, 1650, 1546,
    1453, 1546, 1650, 1733, 1754, 1733, 1650, 1546,
    1453, 1546, 1650, 1733, 1754, 1733, 1650, 1546,
    
    // Pattern 2 (D minor)
    1303, 1453, 1546, 1650, 1678, 1650, 1546, 1453,
    1303, 1453, 1546, 1650, 1678, 1650, 1546, 1453,
    1303, 1453, 1546, 1650, 1678, 1650, 1546, 1453,
    1303, 1453, 1546, 1650, 1678, 1650, 1546, 1453,
    
    // Pattern 3 (E7 tension)
    1369, 1497, 1589, 1709, 1733, 1709, 1589, 1497,
    1369, 1497, 1589, 1709, 1733, 1709, 1589, 1497,
    1369, 1497, 1589, 1709, 1733, 1709, 1589, 1497,
    1369, 1497, 1589, 1709, 1733, 1709, 1589, 1497
};

const uint16_t title_melody[32] = {
    N_A2, N_E3, N_A3, N_E3, N_C4, N_A3, N_E3, N_A2, // Am
    N_G2, N_D3, N_G3, N_D3, N_B3, N_G3, N_D3, N_G2, // G
    N_F2, N_C3, N_F3, N_C3, N_A3, N_F3, N_C3, N_F2, // F
    N_E2, N_B2, N_E3, N_B2, N_GS3, N_E3, N_B2, N_E2  // E
};

const uint16_t finale_ch1_seq[192] = {
    N_A4, R, N_F4, R, N_D4, R, N_A3, R,
    N_A4, N_F4, N_D4, N_A3, N_F4, N_D4, N_A3, R,
    N_G4, R, N_E4, R, N_C4, R, N_G3, R,
    N_F4, R, N_D4, R, N_AS3, R, N_F3, R,
    N_E4, R, N_CS4, R, N_A3, R, N_E3, R,
    N_A4, N_F4, N_D4, N_A3, N_A4, N_F4, N_D4, R,
    N_A4, N_A4, N_G4, N_F4, N_E4, N_F4, N_D4, R,
    N_G4, N_F4, N_E4, N_D4, N_C4, N_D4, N_E4, R,
    N_F4, N_F4, N_E4, N_D4, N_C4, N_AS3, N_A3, R,
    N_E4, N_E4, N_D4, N_CS4, N_B3, N_CS4, N_E4, R,
    N_A5, R, N_A5, N_G5, N_F5, N_E5, N_D5, R,
    N_A5, N_F5, N_D5, N_A4, N_F5, N_D5, N_A4, R,
    N_G5, R, N_G5, N_F5, N_E5, N_D5, N_C5, R,
    N_F5, R, N_F5, N_E5, N_D5, N_C5, N_AS4, R,
    N_E5, N_E5, N_F5, N_E5, N_CS5, N_A4, N_CS5, R,
    N_D5, N_C5, N_B4, N_A4, N_G4, N_F4, N_E4, R,
    N_A4, N_G4, N_F4, N_E4, N_D4, N_C4, N_AS3, N_A3,
    N_D4, R, N_C4, R, N_AS3, R, N_A3, R,
    N_D4, R, N_C4, R, N_AS3, R, N_A3, R,
    N_E3, R, R, R, N_A3, R, R, R,
    N_D3, R, R, R, R, R, R, R,
    N_D3, R, R, R, N_C2, R, R, R,
    N_C2, R, R, R, R, R, R, R,
    R, R, R, R, R, R, R, R
};

const uint16_t finale_ch2_seq[192] = {
    N_D3, R, R, R, R, R, R, R,
    N_A2, R, R, R, R, R, R, R,
    N_C3, R, R, R, R, R, R, R,
    N_AS2, R, R, R, R, R, R, R,
    N_A2, R, R, R, N_E3, R, R, R,
    N_D3, R, R, R, R, R, R, R,
    N_D3, R, N_A2, R, N_D3, R, N_A2, R,
    N_C3, R, N_G2, R, N_C3, R, N_G2, R,
    N_AS2, R, N_F2, R, N_AS2, R, N_F2, R,
    N_A2, R, N_E3, R, N_A2, R, N_E3, R,
    N_D3, R, R, R, N_A2, R, R, R,
    N_D3, R, N_A2, R, N_D3, R, N_A2, R,
    N_C3, R, N_G2, R, N_C3, R, N_G2, R,
    N_AS2, R, N_F2, R, N_AS2, R, N_F2, R,
    N_A2, R, N_E3, R, N_A2, R, N_E3, R,
    N_D3, N_C3, N_AS2, N_A2, N_G2, N_F2, N_E2, R,
    N_A2, N_G2, N_F2, N_E2, N_D3, N_C3, N_AS2, N_A2,
    N_D3, R, N_C3, R, N_AS2, R, N_A2, R,
    N_D3, R, N_C3, R, N_AS2, R, N_A2, R,
    N_A2, R, R, R, N_E3, R, R, R,
    N_D3, R, R, R, R, R, R, R,
    N_D3, R, R, R, N_C2, R, R, R,
    N_C2, R, R, R, R, R, R, R,
    R, R, R, R, R, R, R, R
};

void sound_reset_music_state(void) {
    music_timer = 0;
    music_step = 0;
    gameover_music_timer = 0;
    gameover_music_step = 0;
    victory_music_timer = 0;
    victory_music_step = 0;
    title_music_timer = 0;
    title_music_step = 0;
    finale_music_timer = 0;
    finale_music_step = 0;
}

static void play_note(uint16_t reg_val) {
    NR21_REG = 0x80; // 50% duty cycle
    NR22_REG = 0x73; // volume 7, fade envelope
    NR23_REG = reg_val & 0xFF;
    NR24_REG = (reg_val >> 8) | 0x80; // trigger note
}

void play_gameover_step(uint8_t step) {
    if (step < 128) {
        uint16_t n1 = ch1_seq[step];
        if (n1 != R) {
            NR10_REG = 0x00; // No sweep
            NR11_REG = 0x80; // 50% duty
            NR12_REG = 0x73; // volume 7, fast fade for arpeggio pluck
            NR13_REG = n1 & 0xFF;
            NR14_REG = (n1 >> 8) | 0x80; // trigger note
        }

        uint16_t n2 = ch2_seq[step];
        if (n2 != R) {
            NR21_REG = 0x80; // 50% duty
            NR22_REG = 0xA7; // volume 10, long fade for melody sustain
            NR23_REG = n2 & 0xFF;
            NR24_REG = (n2 >> 8) | 0x80;
        }

        // Add dramatic percussion on the first beat of each chord (every 8 steps) using Channel 4 (Noise)
        if (step % 8 == 0) {
            NR41_REG = 0x01;
            NR42_REG = 0xB2; // Volume 11, quick fade
            // step < 64 gets a lower tympani, step >= 64 gets a crash
            if (step < 64) {
                NR43_REG = 0x68; // Low thud freq
            } else {
                NR43_REG = 0x42; // Crash freq
            }
            NR44_REG = 0x80; // trigger noise
        }
    }
}

void play_finale_step(uint8_t step) {
    if (step < 192) {
        uint16_t n1 = finale_ch1_seq[step];
        if (n1 != R) {
            NR10_REG = 0x00;
            NR11_REG = 0x80;
            NR12_REG = 0xA2; // soft, long fade: somber melody
            NR13_REG = n1 & 0xFF;
            NR14_REG = (n1 >> 8) | 0x80;
        }
        uint16_t n2 = finale_ch2_seq[step];
        if (n2 != R) {
            NR21_REG = 0x80;
            NR22_REG = 0xD1; // deep bass, slow fade
            NR23_REG = n2 & 0xFF;
            NR24_REG = (n2 >> 8) | 0x80;
        }
        // CH4 noise toll at the start of each chord (every 8 steps):
        // mid toll by default, crash at the scream climax, deep toll in the abyss.
        if (step % 8 == 0) {
            NR41_REG = 0x01;
            NR42_REG = 0xB2;
            if (step >= 160) {
                NR43_REG = 0x70; // deep toll (abyss)
            } else if (step == 80 || step == 88 || step == 112) {
                NR43_REG = 0x42; // crash (climax)
            } else {
                NR43_REG = 0x68; // mid toll
            }
            NR44_REG = 0x80;
        }
    }
}

void play_victory_step(uint8_t step) {
    if (step < 96) {
        uint16_t n1 = next_level_seq[step];
        if (n1 != R) {
            NR10_REG = 0x00;
            NR11_REG = 0x80; // 50% duty
            NR12_REG = 0xC5; // louder, slightly longer fade
            NR13_REG = n1 & 0xFF;
            NR14_REG = (n1 >> 8) | 0x80;
            
            // Add a bass note on the first beat of each chord (every 16 steps)
            if (step % 16 == 0) {
                NR21_REG = 0x80;
                NR22_REG = 0xC7; // louder bass, long fade
                uint16_t bn = n1 / 2; // octave lower
                NR23_REG = bn & 0xFF;
                NR24_REG = (bn >> 8) | 0x80;
            }
        }
    }
}

/**
 * Questo interrupt scatta ogni VBL (Vertical Blanking), ovvero ~60 volte al secondo.
 * Funziona come un mini "sequencer" audio: in base allo stato del gioco, controlla il timer
 * e riproduce la nota corrispondente all'interno dell'array della traccia.
 */
void play_music_tick(void) {
    if (app_state == 0) { // TITLE SCREEN
        title_music_timer++;
        if (title_music_timer >= 30) { // 30 frames per note
            title_music_timer = 0;
            uint16_t n = title_melody[title_music_step];
            NR10_REG = 0; 
            NR11_REG = 0x80;
            NR12_REG = 0x63; // soft fade
            NR13_REG = n & 0xFF;
            NR14_REG = (n >> 8) | 0x80;
            
            // Add a slow bass note every 4 steps
            if (title_music_step % 4 == 0) {
                NR21_REG = 0x80;
                NR22_REG = 0x77;
                uint16_t bn = n / 2; // Octave lower (divide frequency logic)
                NR23_REG = bn & 0xFF;
                NR24_REG = (bn >> 8) | 0x80;
            }

            title_music_step++;
            if (title_music_step >= 32) title_music_step = 0;
        }
        return;
    }

    if (game_over) { // ENDGAME
        if (game_over_timer == 0) { // Se il ritardo di fine partita è terminato
            if (game_over == 1) { // Defeat (Ghost)
                gameover_music_timer++;
                if (gameover_music_timer >= 10) { // 10 frames per note (~6 notes/sec)
                    gameover_music_timer = 0;
                    if (gameover_music_step < 128) {
                        play_gameover_step(gameover_music_step);
                        gameover_music_step++;
                    }
                }
            } else if (game_over == 3) { // Finale tragico (brano dedicato, piu' lento)
                finale_music_timer++;
                if (finale_music_timer >= 14) { // 14 frames per note (~4 notes/sec, somber)
                    finale_music_timer = 0;
                    if (finale_music_step < 192) {
                        play_finale_step(finale_music_step);
                        finale_music_step++;
                    }
                }
            } else if (game_over == 2) { // Next Level (Going Deeper)
                victory_music_timer++;
                if (victory_music_timer >= 15) { // 15 frames per note = 4 notes/sec
                    victory_music_timer = 0;
                    if (victory_music_step < 96) {
                        play_victory_step(victory_music_step);
                        victory_music_step++;
                    }
                }
            }
        }
        return;
    }
    
    // GAMEPLAY
    music_timer++;
    if (music_timer >= 20) {
        music_timer = 0;
        play_note(eerie_reg_vals[music_step]);
        music_step++;
        if (music_step >= 96) {
            music_step = 0;
        }
    }
}
