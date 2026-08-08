"""Capture deterministic static-screen regression fixtures from a linked ROM."""

import argparse
import json
import re
from pathlib import Path

from pyboy import PyBoy


REQUIRED_SYMBOLS = (
    "_app_state",
    "_credits_active",
    "_game_over",
    "_game_over_timer",
    "_hint_active",
    "_intro_active",
    "_level",
    "_map_buffer",
)


def load_symbols(path: Path) -> dict[str, int]:
    symbols: dict[str, int] = {}
    pattern = re.compile(r"^DEF\s+(\S+)\s+0x([0-9A-Fa-f]+)$")
    for line in path.read_text().splitlines():
        match = pattern.match(line)
        if match:
            symbols[match.group(1)] = int(match.group(2), 16)
    missing = [name for name in REQUIRED_SYMBOLS if name not in symbols]
    if missing:
        raise RuntimeError(f"Missing symbols: {', '.join(missing)}")
    return symbols


def tick(pyboy: PyBoy, count: int) -> None:
    for _ in range(count):
        pyboy.tick()


def wait_for(pyboy: PyBoy, address: int, expected: int, limit: int = 360) -> None:
    for _ in range(limit):
        pyboy.tick()
        if pyboy.memory[address] == expected:
            return
    raise RuntimeError(f"Timeout waiting for {address:#06x} == {expected}")


def enter_gameplay(pyboy: PyBoy, symbols: dict[str, int]) -> None:
    pyboy.button("start", 2)
    tick(pyboy, 220)
    pyboy.button("a", 2)
    wait_for(pyboy, symbols["_app_state"], 1)
    tick(pyboy, 220)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("rom", type=Path)
    parser.add_argument("noi", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--screen",
        required=True,
        choices=("title", "intro", "credits", "instructions", "death", "deeper", "finale"),
    )
    args = parser.parse_args()

    symbols = load_symbols(args.noi)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pyboy = PyBoy(str(args.rom), window="null", cgb=False)
    try:
        tick(pyboy, 180)
        if args.screen == "intro":
            pyboy.button("start", 2)
            wait_for(pyboy, symbols["_intro_active"], 1)
            tick(pyboy, 180)
        elif args.screen == "credits":
            pyboy.button("select", 2)
            wait_for(pyboy, symbols["_credits_active"], 1)
            tick(pyboy, 120)
        elif args.screen != "title":
            enter_gameplay(pyboy, symbols)
            if args.screen == "instructions":
                wait_for(pyboy, symbols["_hint_active"], 1)
                tick(pyboy, 120)
            else:
                pyboy.button("b", 2)
                wait_for(pyboy, symbols["_hint_active"], 0)
                tick(pyboy, 30)
                state = {"death": 1, "deeper": 2, "finale": 3}[args.screen]
                if args.screen == "finale":
                    pyboy.memory[symbols["_level"]] = 8
                pyboy.memory[symbols["_game_over"]] = state
                pyboy.memory[symbols["_game_over_timer"]] = 1
                wait_for(pyboy, symbols["_game_over_timer"], 0)
                # font_load() and a tilemap transfer may span multiple frames;
                # timer==0 is set before show_*() has necessarily returned.
                tick(pyboy, 180)

        pyboy.screen.image.save(args.output)
        state = {
            "rom": str(args.rom),
            "screen": args.screen,
            "app_state": pyboy.memory[symbols["_app_state"]],
            "game_over": pyboy.memory[symbols["_game_over"]],
            "level": pyboy.memory[symbols["_level"]],
            "buffer_nonzero": sum(
                pyboy.memory[symbols["_map_buffer"] + index] != 0
                for index in range(32 * 32)
            ),
            "bg_map_nonzero": sum(
                pyboy.memory[0x9800 + index] != 0 for index in range(32 * 32)
            ),
            "alt_map_nonzero": sum(
                pyboy.memory[0x9C00 + index] != 0 for index in range(32 * 32)
            ),
        }
        args.output.with_suffix(".json").write_text(json.dumps(state, indent=2) + "\n")
        print(json.dumps(state, sort_keys=True))
    finally:
        pyboy.stop()


if __name__ == "__main__":
    main()
