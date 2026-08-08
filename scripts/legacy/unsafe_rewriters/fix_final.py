import re

with open("src/engine.c", "r") as f:
    content = f.read()

content = re.sub(r'// SPAWN DEL NEMICO.*?enemy_cooldown = 60;', 'init_enemies();', content, flags=re.DOTALL)
content = re.sub(r'enemy_lx\s*=\s*rx;\s*enemy_ly\s*=\s*ry;\s*enemy_target_lx\s*=\s*rx;\s*enemy_target_ly\s*=\s*ry;', '', content)
content = re.sub(r'enemy_start_lx\s*=\s*rx;\s*enemy_start_ly\s*=\s*ry;', '', content)

with open("src/engine.c", "w") as f:
    f.write(content)

with open("src/enemy_logic.c", "r") as f:
    content = f.read()

if '#include <rand.h>' not in content:
    content = content.replace('#include "enemy_logic.h"', '#include "enemy_logic.h"\n#include <rand.h>')

with open("src/enemy_logic.c", "w") as f:
    f.write(content)
