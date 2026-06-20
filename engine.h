#ifndef ENGINE_H
#define ENGINE_H

#include <stdint.h>

void engine_init(void);
void engine_update(uint8_t keys, uint8_t prev_keys);

#endif
