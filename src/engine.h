#ifndef ENGINE_H
#define ENGINE_H

#include <stdint.h>

void title_init(void);
void title_update(uint8_t keys, uint8_t prev_keys);
void engine_init(void);
void engine_update(uint8_t keys, uint8_t prev_keys);

extern uint8_t app_state;

#endif
