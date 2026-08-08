# Intelligenza Artificiale (Fantasmi)

## Multi-Entity (fino a 8 fantasmi)

Il gioco supporta fino a `MAX_ENEMIES = 8` fantasmi coesistenti. Il numero attivo è `num_enemies = level` (1 al livello 1, 8 al livello 8). Lo stato di ciascun fantasma è in **array indicizzati**:

```c
uint8_t enemy_lx[8], enemy_ly[8];
uint8_t enemy_is_moving[8], enemy_move_progress[8];
int8_t  enemy_start_lx[8], enemy_start_ly[8];
int8_t  enemy_target_lx[8], enemy_target_ly[8];
int16_t enemy_start_px[8], enemy_start_py[8];
int16_t enemy_target_px[8], enemy_target_py[8];
uint8_t enemy_cooldown[8];
```

Ogni fantasma usa 2 slot OAM a partire da `2 + i*2` (il player usa 0-1). Tutti condividono la stessa tile data (ghost sprite), con palette invertita (OBP1 = 0x1B, bianco su scuro).

## Pathfinding: Greedy invece di A*

A* richiederebbe heap, nodi e calcoli pesanti — inammissibile su 4 MHz, soprattutto con 8 fantasmi. L'approccio **Greedy** è leggero:

Per ciascun fantasma, tra le 4 celle adiacenti calpestabili, sceglie quella che **minimizza la distanza al quadrato** verso il giocatore (`dx² + dy²`). No sqrt (i quadrati bastano per il confronto `A < B ⇔ A² < B²`).

**Difetto voluto**: il Greedy si incastra nei vicoli a U. In un labirinto con loop, questo diventa una dinamica di gioco — il giocatore astuto sfrutta il level design per seminare i fantasmi.

## Attivazione e Cooldown Scalabile

### Attivazione
Il fantasma insegue solo se entro il raggio di nebbia:
```c
if (dist <= fog_radius) { // inizia a inseguire }
```
`fog_radius` = 2 (5×5) ai livelli 1-6, = 1 (3×3) ai livelli 7-8.

### Cooldown
Dopo ogni passo (16 frame di LERP), il fantasma aspetta `enemy_step_cooldown` frame:
- Livello 1: 60 frame (1 secondo) — lento, gestibile.
- Livello 8: 11 frame — implacabile, quasi continuo.

I cooldown iniziali sono **sfasati** (`enemy_step_cooldown + i*8`) così i fantasmi non si muovono in sincrono.

## Hitbox Pixel-Perfect

La morte non si basa sulla coincidenza di cella logica, ma sulla **sovrapposizione dei pixel fisici** renderizzati:

```c
if (|p_px - enemy_px| < 12 && |p_py - enemy_py| < 6) {
    game_over = 1;  // sconfitta
}
```

Questo rende la morte "giusta" agli occhi del giocatore e permette scambi per il rotto della cuffia. Al primo fantasma che catcha il player, il loop si ferma (`return`).

## Culling

I fantasmi sono renderizzati solo se:
1. Entro `fog_radius` dal giocatore (Chebyshev).
2. On-screen (con wrap `& 255` + soglie fisiche `-8..168` / `-8..152`).

Altrimenti lo sprite è spostato offscreen `(0,0)`.