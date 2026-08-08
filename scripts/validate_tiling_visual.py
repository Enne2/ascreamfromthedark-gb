"""Capture a deterministic post-movement screenshot for tiling regression tests."""

import argparse
import json
import re
from pathlib import Path

from pyboy import PyBoy


REQUIRED_SYMBOLS = (
    "_app_state",
    "_hint_active",
    "_hint_shown_once",
    "_fog_radius",
    "_map_size",
    "_maze",
    "_num_enemies",
    "_player_lx",
    "_player_ly",
    "_stairs_lx",
    "_stairs_ly",
    "_stamina",
)

FLOOR_FIXTURE = (
    (0, 0, 0, 0, 0, 0, 0),
    (0, 1, 0, 1, 1, 0, 0),
    (0, 1, 1, 0, 1, 0, 0),
    (0, 1, 1, 1, 1, 0, 0),
    (0, 1, 0, 1, 1, 0, 0),
    (0, 1, 1, 1, 1, 1, 0),
    (0, 0, 0, 0, 0, 0, 0),
)


def install_fixture(
    pyboy: PyBoy, symbols: dict[str, int], scenario: str
) -> tuple[tuple[int, ...], ...]:
    # Enemy placement depends on the hardware DIV seed and would make visual
    # comparisons between two ROM links nondeterministic. Disable their logic
    # and hide the sixteen enemy OAM entries (IDs 2..17).
    pyboy.memory[symbols["_num_enemies"]] = 0
    for sprite_id in range(2, 18):
        pyboy.memory[0xFE00 + sprite_id * 4] = 0

    if scenario.startswith("wrap_"):
        fixture = [
            [1 if 0 < x < 20 and 0 < y < 20 else 0 for x in range(21)]
            for y in range(21)
        ]
        pyboy.memory[symbols["_map_size"]] = 21
        pyboy.memory[symbols["_fog_radius"]] = 1
    else:
        fixture = [list(row) for row in FLOOR_FIXTURE]

    if scenario == "hatch":
        fixture[3][2] = 2
        pyboy.memory[symbols["_stairs_lx"]] = 2
        pyboy.memory[symbols["_stairs_ly"]] = 3

    maze_address = symbols["_maze"]
    for y in range(21):
        for x in range(21):
            pyboy.memory[maze_address + y * 21 + x] = 0
    for y, row in enumerate(fixture):
        for x, value in enumerate(row):
            pyboy.memory[maze_address + y * 21 + x] = value
    return tuple(tuple(row) for row in fixture)


def load_symbols(path: Path) -> dict[str, int]:
    symbols: dict[str, int] = {}
    pattern = re.compile(r"^DEF\s+(\S+)\s+0x([0-9A-Fa-f]+)$")
    for line in path.read_text().splitlines():
        match = pattern.match(line)
        if match:
            symbols[match.group(1)] = int(match.group(2), 16)

    missing = [name for name in REQUIRED_SYMBOLS if name not in symbols]
    if missing:
        raise RuntimeError(f"Missing symbols in {path}: {', '.join(missing)}")
    return symbols


def tick(pyboy: PyBoy, count: int) -> None:
    for _ in range(count):
        pyboy.tick()


def wait_for(pyboy: PyBoy, address: int, expected: int, limit: int) -> None:
    for _ in range(limit):
        pyboy.tick()
        if pyboy.memory[address] == expected:
            return
    actual = pyboy.memory[address]
    raise RuntimeError(
        f"Timeout waiting for {address:#06x} == {expected}; actual value is {actual}"
    )


def choose_move(pyboy: PyBoy, symbols: dict[str, int]) -> tuple[str, int, int]:
    player_x = pyboy.memory[symbols["_player_lx"]]
    player_y = pyboy.memory[symbols["_player_ly"]]
    map_size = pyboy.memory[symbols["_map_size"]]
    maze_address = symbols["_maze"]

    # The C array is maze[MAX_MAP_SIZE][MAX_MAP_SIZE], so its physical row
    # stride remains 21 even while the active level is only 7x7.
    candidates = (
        ("right", player_x + 1, player_y),
        ("down", player_x, player_y + 1),
        ("left", player_x - 1, player_y),
        ("up", player_x, player_y - 1),
    )
    for button, target_x, target_y in candidates:
        if not (0 <= target_x < map_size and 0 <= target_y < map_size):
            continue
        tile = pyboy.memory[maze_address + target_y * 21 + target_x]
        if tile in (1, 2):
            return button, target_x, target_y
    raise RuntimeError(f"No walkable neighbour at ({player_x}, {player_y})")


def execute_move(
    pyboy: PyBoy, symbols: dict[str, int], button: str, target_x: int, target_y: int
) -> None:
    pyboy.button(button, 2)
    for _ in range(120):
        pyboy.tick()
        current = (
            pyboy.memory[symbols["_player_lx"]],
            pyboy.memory[symbols["_player_ly"]],
        )
        if current == (target_x, target_y):
            return
    raise RuntimeError(
        f"Player did not complete move {button} to ({target_x}, {target_y})"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("rom", type=Path)
    parser.add_argument("noi", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--trace-dir",
        type=Path,
        help="Optional directory for a screenshot after every completed move",
    )
    parser.add_argument(
        "--stamina",
        type=int,
        choices=range(101),
        metavar="0..100",
        help="Override stamina before the movement-triggered redraw",
    )
    parser.add_argument(
        "--scenario",
        choices=("floor", "hatch", "wrap_x", "wrap_y"),
        default="floor",
    )
    args = parser.parse_args()

    symbols = load_symbols(args.noi)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.trace_dir:
        args.trace_dir.mkdir(parents=True, exist_ok=True)

    pyboy = PyBoy(str(args.rom), window="null", cgb=False)
    try:
        tick(pyboy, 180)

        # Title -> intro. Static screen copies are intentionally given enough
        # time to finish before the next input edge is sent.
        pyboy.button("start", 2)
        tick(pyboy, 220)

        # Intro -> gameplay -> first-run instructions.
        pyboy.button("a", 2)
        wait_for(pyboy, symbols["_app_state"], 1, 360)
        tick(pyboy, 220)

        # Close instructions and wait until gameplay is active.
        pyboy.button("b", 2)
        wait_for(pyboy, symbols["_hint_active"], 0, 360)
        tick(pyboy, 30)

        fixture = install_fixture(pyboy, symbols, args.scenario)
        if args.stamina is not None:
            pyboy.memory[symbols["_stamina"]] = args.stamina

        start_x = pyboy.memory[symbols["_player_lx"]]
        start_y = pyboy.memory[symbols["_player_ly"]]
        if args.scenario.startswith("wrap_"):
            moves = []
            current_x, current_y = start_x, start_y
            while current_x < 15:
                current_x += 1
                moves.append(("right", current_x, current_y))
            if args.scenario == "wrap_y":
                while current_y < 15:
                    current_y += 1
                    moves.append(("down", current_x, current_y))
        else:
            moves = [choose_move(pyboy, symbols)]

        trace = []
        for index, (button, target_x, target_y) in enumerate(moves, start=1):
            execute_move(pyboy, symbols, button, target_x, target_y)
            # Give the engine a neutral input edge before the next scripted
            # step; otherwise two identical directions can merge under DAS.
            tick(pyboy, 3)
            if args.trace_dir:
                trace_path = args.trace_dir / f"{index:02d}_{target_x:02d}_{target_y:02d}.png"
                pyboy.screen.image.save(trace_path)
                trace.append(str(trace_path))

        tick(pyboy, 4)
        pyboy.screen.image.save(args.output)

        map_size = pyboy.memory[symbols["_map_size"]]
        maze_address = symbols["_maze"]
        maze = [
            [
                pyboy.memory[maze_address + y * 21 + x]
                for x in range(map_size)
            ]
            for y in range(map_size)
        ]
        fixture_matches = maze == [list(row) for row in fixture]
        if not fixture_matches:
            raise RuntimeError("Injected maze fixture changed during the test")
        final_position = [
            pyboy.memory[symbols["_player_lx"]],
            pyboy.memory[symbols["_player_ly"]],
        ]
        if final_position != [target_x, target_y]:
            raise RuntimeError(
                f"Unexpected final position {final_position}; expected "
                f"{[target_x, target_y]}"
            )
        state = {
            "rom": str(args.rom),
            "scenario": args.scenario,
            "start": [start_x, start_y],
            "moves": [button for button, _, _ in moves],
            "target": [target_x, target_y],
            "final": final_position,
            "map_size": map_size,
            "maze": maze,
            "fixture_matches": fixture_matches,
            "hint_shown_once": pyboy.memory[symbols["_hint_shown_once"]],
            "stamina": pyboy.memory[symbols["_stamina"]],
            "trace": trace,
        }
        args.output.with_suffix(".json").write_text(
            json.dumps(state, indent=2) + "\n"
        )
        print(
            json.dumps(
                {
                    "final": state["final"],
                    "fixture_matches": state["fixture_matches"],
                    "moves": len(state["moves"]),
                    "scenario": state["scenario"],
                    "stamina": state["stamina"],
                },
                sort_keys=True,
            )
        )
    finally:
        pyboy.stop()


if __name__ == "__main__":
    main()
