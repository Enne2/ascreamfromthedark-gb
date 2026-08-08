"""Validate the release-relevant fields and checksums of a Game Boy ROM."""

import argparse
from pathlib import Path


NINTENDO_LOGO = bytes.fromhex(
    "CEED6666CC0D000B03730083000C000D"
    "0008111F8889000EDCCC6EE6DDDDD999"
    "BBBB67636E0EECCCDDDC999FBBB9333E"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("rom", type=Path)
    parser.add_argument("--title", required=True)
    args = parser.parse_args()

    rom = args.rom.read_bytes()
    if len(rom) < 0x150:
        raise RuntimeError(f"ROM too short: {len(rom)} bytes")
    if rom[0x104:0x134] != NINTENDO_LOGO:
        raise RuntimeError("Invalid Nintendo logo")

    title = rom[0x134:0x144].split(b"\0", 1)[0].decode("ascii")
    if title != args.title:
        raise RuntimeError(f"Title is {title!r}, expected {args.title!r}")
    if rom[0x143] not in (0x00, 0x80, 0xC0):
        raise RuntimeError(f"Invalid CGB flag {rom[0x143]:#04x}")
    if rom[0x14A] != 0x01:
        raise RuntimeError(f"Destination is not non-Japanese: {rom[0x14A]:#04x}")

    header_checksum = 0
    for value in rom[0x134:0x14D]:
        header_checksum = (header_checksum - value - 1) & 0xFF
    if header_checksum != rom[0x14D]:
        raise RuntimeError(
            f"Header checksum {rom[0x14D]:#04x}, expected {header_checksum:#04x}"
        )

    stored_global = (rom[0x14E] << 8) | rom[0x14F]
    computed_global = (sum(rom) - rom[0x14E] - rom[0x14F]) & 0xFFFF
    if stored_global != computed_global:
        raise RuntimeError(
            f"Global checksum {stored_global:#06x}, expected {computed_global:#06x}"
        )

    print(
        f"header ok: title={title!r}, destination=non-Japanese, "
        f"cartridge_type={rom[0x147]:#04x}, rom_size={len(rom)}, "
        f"header_checksum={header_checksum:#04x}, global_checksum={stored_global:#06x}"
    )


if __name__ == "__main__":
    main()
