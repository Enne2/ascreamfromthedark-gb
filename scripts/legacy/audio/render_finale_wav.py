#!/usr/bin/env python3
"""
Renderizza la musica del finale di "A Scream from the Dark" in un file WAV.
Estrae le sequenze CH1 (melodia), CH2 (basso) e CH4 (rintocchi) dal sorgente
sound.c e le sintetizza in un file audio.

Uso: python3 render_finale_wav.py [output.wav]
Output di default: /tmp/finale_music.wav
"""

import re
import struct
import wave
import sys
import math

# === Costanti delle note (dal sound.c) ===
# Valore Game Boy -> frequenza: freq = 131072 / (2048 - value)
R = 0  # rest (silenzio)
NOTES = {
    'N_C2': 44, 'N_E2': 458, 'N_F2': 547, 'N_G2': 742, 'N_A2': 857,
    'N_AS2': 907, 'N_B2': 961,
    'N_C3': 1046, 'N_CS3': 1103, 'N_D3': 1155, 'N_E3': 1253,
    'N_F3': 1298, 'N_FS3': 1340, 'N_G3': 1380, 'N_GS3': 1417,
    'N_A3': 1453, 'N_AS3': 1486, 'N_B3': 1517,
    'N_C4': 1547, 'N_CS4': 1575, 'N_D4': 1602, 'N_E4': 1651,
    'N_F4': 1673, 'N_FS4': 1694, 'N_G4': 1714, 'N_GS4': 1732,
    'N_A4': 1751, 'N_AS4': 1767, 'N_B4': 1783,
    'N_C5': 1798, 'N_CS5': 1812, 'N_D5': 1825, 'N_E5': 1849,
    'N_F5': 1860, 'N_FS5': 1871, 'N_G5': 1881, 'N_GS5': 1890,
    'N_A5': 1899,
    'R': 0,
}

def gb_freq(value):
    """Converte un valore Game Boy in frequenza Hz."""
    if value == 0:
        return 0
    return 131072.0 / (2048 - value)

# === Estrai le sequenze dal sound.c ===
def extract_array(filename, array_name):
    with open(filename) as f:
        text = f.read()
    pattern = rf'const uint16_t {array_name}\[192\] = \{{(.*?)\}};'
    m = re.search(pattern, text, re.DOTALL)
    if not m:
        raise ValueError(f"Array {array_name} not found in {filename}")
    body = m.group(1)
    tokens = re.findall(r'N_\w+|R\b', body)
    values = []
    for tok in tokens:
        values.append(NOTES.get(tok, 0))
    return values

SOUND_C = 'src/sound.c'
ch1_seq = extract_array(SOUND_C, 'finale_ch1_seq')
ch2_seq = extract_array(SOUND_C, 'finale_ch2_seq')
print(f"CH1: {len(ch1_seq)} steps, CH2: {len(ch2_seq)} steps")

# === Parametri audio ===
SAMPLE_RATE = 22050  # Hz
FRAMES_PER_NOTE = 14  # 14 frame/nota a 60fps -> ~0.233s/nota
NOTE_DURATION = FRAMES_PER_NOTE / 60.0  # secondi per nota
SAMPLES_PER_NOTE = int(SAMPLE_RATE * NOTE_DURATION)
TOTAL_STEPS = 192  # un loop completo

# Envelope del Game Boy (semplificato): volume con fade
# CH1: NR12=0xA2 -> volume iniziale 10 (0xA), fade down (sweep -2)
# CH2: NR22=0xD1 -> volume iniziale 13 (0xD), fade down (sweep -1)
# CH4: NR42=0xB2 -> volume iniziale 11 (0xB), fade down (sweep -2)

def generate_tone(freq, duration, sample_rate, volume=0.5, waveform='square',
                  envelope_init=15, envelope_sweep=-2):
    """Genera un'onda quadra con envelope del Game Boy."""
    if freq == 0 or volume == 0:
        return [0.0] * int(sample_rate * duration)
    
    n_samples = int(sample_rate * duration)
    samples = []
    
    # Game Boy envelope: parte da envelope_init, cambia di envelope_sweep
    # ogni 1/64 secondo. sweep negativo = fade out.
    env_step_samples = sample_rate / 64.0  # campioni per step di envelope
    for i in range(n_samples):
        # Calcola envelope corrente (0-15, mappa a 0.0-1.0)
        env_steps_elapsed = i / env_step_samples
        env_val = envelope_init + envelope_sweep * env_steps_elapsed
        env_val = max(0, min(15, env_val))
        amp = (env_val / 15.0) * volume
        
        # Onda quadra (50% duty cycle come NR11=0x80 / NR21=0x80)
        phase = (i * freq / sample_rate) % 1.0
        if waveform == 'square':
            val = amp if phase < 0.5 else -amp
        elif waveform == 'sine':
            val = amp * math.sin(2 * math.pi * phase)
        samples.append(val)
    
    return samples

def generate_noise(duration, sample_rate, volume=0.3, envelope_init=11, envelope_sweep=-2,
                   noise_type='mid'):
    """Genera rumore per i rintocchi di campana (CH4)."""
    n_samples = int(sample_rate * duration)
    samples = []
    env_step_samples = sample_rate / 64.0
    
    # Game Boy noise: clock_divider + shift
    # mid toll: NR43=0x68 -> shift=13, divider=1 -> ~500Hz
    # crash: NR43=0x42 -> shift=8, divider=2 -> ~4kHz
    # deep toll: NR43=0x70 -> shift=14, divider=1 -> ~250Hz
    noise_params = {
        'mid': (13, 1, 0.3),
        'crash': (8, 2, 0.4),
        'deep': (14, 1, 0.25),
    }
    shift, div, vol_mult = noise_params.get(noise_type, noise_params['mid'])
    
    # Frequenza approssimativa del rumore
    base_freq = 262144.0 / (div * (1 << (shift + 1)))
    
    # LFSR (Linear Feedback Shift Register) del Game Boy per rumore autentico
    lfsr = 0x7FFF  # 15-bit LFSR
    samples_per_noise = max(1, int(sample_rate / base_freq))
    
    for i in range(n_samples):
        env_steps_elapsed = i / env_step_samples
        env_val = envelope_init + envelope_sweep * env_steps_elapsed
        env_val = max(0, min(15, env_val))
        amp = (env_val / 15.0) * volume * vol_mult
        
        # Aggiorna LFSR
        if i % samples_per_noise == 0:
            bit = ((lfsr >> 0) ^ (lfsr >> 1)) & 1
            lfsr = (lfsr >> 1) | (bit << 14)
        
        val = amp if (lfsr & 1) else -amp
        samples.append(val)
    
    return samples

# === Genera le tracce audio ===
print("Generando CH1 (melodia)...")
ch1_audio = []
for step in range(TOTAL_STEPS):
    note_val = ch1_seq[step % len(ch1_seq)]
    freq = gb_freq(note_val)
    if freq > 0:
        # CH1: NR12=0xA2 (vol 10, fade -2), duty 50%
        tone = generate_tone(freq, NOTE_DURATION, SAMPLE_RATE, volume=0.4,
                             envelope_init=10, envelope_sweep=-2)
    else:
        tone = [0.0] * SAMPLES_PER_NOTE
    ch1_audio.extend(tone)

print("Generando CH2 (basso)...")
ch2_audio = []
for step in range(TOTAL_STEPS):
    note_val = ch2_seq[step % len(ch2_seq)]
    freq = gb_freq(note_val)
    if freq > 0:
        # CH2: NR22=0xD1 (vol 13, fade -1), duty 50%
        tone = generate_tone(freq, NOTE_DURATION, SAMPLE_RATE, volume=0.3,
                             envelope_init=13, envelope_sweep=-1)
    else:
        tone = [0.0] * SAMPLES_PER_NOTE
    ch2_audio.extend(tone)

print("Generando CH4 (rintocchi)...")
ch4_audio = [0.0] * len(ch1_audio)  # traccia silenziosa di base
for step in range(TOTAL_STEPS):
    if step % 8 == 0:  # rintocco ogni 8 step
        if step >= 160:
            noise_type = 'deep'
        elif step == 80 or step == 88 or step == 112:
            noise_type = 'crash'
        else:
            noise_type = 'mid'
        
        noise = generate_noise(NOTE_DURATION, SAMPLE_RATE, volume=0.2,
                               envelope_init=11, envelope_sweep=-2,
                               noise_type=noise_type)
        start = step * SAMPLES_PER_NOTE
        for j, s in enumerate(noise):
            if start + j < len(ch4_audio):
                ch4_audio[start + j] += s

# === Mix delle tracce ===
print("Mixing...")
n_total = len(ch1_audio)
mixed = []
for i in range(n_total):
    val = ch1_audio[i] * 0.5 + ch2_audio[i] * 0.4 + ch4_audio[i] * 0.3
    # Clamping a [-1, 1]
    val = max(-1.0, min(1.0, val))
    mixed.append(val)

# === Scrivi il WAV ===
output_file = sys.argv[1] if len(sys.argv) > 1 else '/tmp/finale_music.wav'
print(f"Scrivendo {output_file}...")
duration = n_total / SAMPLE_RATE
print(f"  Durata: {duration:.1f}s ({TOTAL_STEPS} step x {NOTE_DURATION:.3f}s)")

with wave.open(output_file, 'w') as wav:
    wav.setnchannels(1)  # mono
    wav.setsampwidth(2)  # 16-bit
    wav.setframerate(SAMPLE_RATE)
    
    for val in mixed:
        # Converti a 16-bit signed
        sample = int(val * 32767)
        wav.writeframes(struct.pack('<h', sample))

print(f"Done! {output_file} ({duration:.1f}s, {SAMPLE_RATE}Hz, 16-bit mono)")