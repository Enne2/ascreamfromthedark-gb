import re

# 1. Fix main.c
with open("src/main.c", "r") as f:
    content = f.read()
if '#include "globals.h"' not in content:
    content = content.replace('#include "engine.h"', '#include "engine.h"\n#include "globals.h"')
with open("src/main.c", "w") as f:
    f.write(content)

# 2. Fix engine.c
with open("src/engine.c", "r") as f:
    content = f.read()
if '#include "enemy_logic.h"' not in content:
    content = content.replace('#include "enemy.h"', '#include "enemy.h"\n#include "enemy_logic.h"')

# Remove any remaining enemy_lx = rx lines!
content = re.sub(r'enemy_lx\s*=\s*rx;\s*enemy_ly\s*=\s*ry;\s*enemy_target_lx\s*=\s*rx;\s*enemy_target_ly\s*=\s*ry;', '', content)
content = re.sub(r'enemy_start_lx\s*=\s*rx;\s*enemy_start_ly\s*=\s*ry;', '', content)

with open("src/engine.c", "w") as f:
    f.write(content)

# 3. Fix enemy_logic.c
with open("src/enemy_logic.c", "r") as f:
    content = f.read()
if '#include <stdlib.h>' not in content:
    content = content.replace('#include "enemy_logic.h"', '#include "enemy_logic.h"\n#include <stdlib.h>')
with open("src/enemy_logic.c", "w") as f:
    f.write(content)
