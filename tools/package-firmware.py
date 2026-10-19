#!/usr/bin/env python3
"""Copy the current ESP-DL build into firmware/ for prebuilt flashing.

Run this after building the demo from source (for example with
`python run-demo.py --build`, or `idf.py -D ACTIVE_APP=demo build` in
esp-dl/). The resulting firmware/ directory is what `run-demo.py --flash`
uses by default, so it does not need ESP-IDF or a compiler.
"""

import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "esp-dl/build"
FLASH_ARGS = BUILD_DIR / "flasher_args.json"
BUILT_MODEL = ROOT / "esp-dl/main/model/model.espdl"
DEFAULT_MODEL = ROOT / "demo.espdl"
FIRMWARE_DIR = ROOT / "firmware"
MANIFEST = FIRMWARE_DIR / "manifest.json"


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    if not FLASH_ARGS.is_file():
        print(f"Error: build output not found: {FLASH_ARGS}", file=sys.stderr)
        print("Build the demo first, then re-run this script.", file=sys.stderr)
        return 1

    model_hash = sha256_file(DEFAULT_MODEL)
    if BUILT_MODEL.is_file() and sha256_file(BUILT_MODEL) != model_hash:
        print("Error: the build does not use demo.espdl.", file=sys.stderr)
        print("Rebuild with the bundled model before packaging.", file=sys.stderr)
        return 1

    flash_args = json.loads(FLASH_ARGS.read_text())
    settings = flash_args.get("flash_settings", {})
    flash_files = flash_args.get("flash_files", {})
    if not flash_files:
        print("Error: no flash files listed in flasher_args.json", file=sys.stderr)
        return 1

    FIRMWARE_DIR.mkdir(exist_ok=True)
    parts = []
    for offset, rel_path in sorted(flash_files.items(),
                                   key=lambda item: int(item[0], 16)):
        src = BUILD_DIR / rel_path
        if not src.is_file():
            print(f"Error: missing build artifact: {src}", file=sys.stderr)
            return 1
        dst = FIRMWARE_DIR / Path(rel_path).name
        shutil.copy2(src, dst)
        parts.append({
            "offset": offset,
            "file": dst.name,
            "sha256": sha256_file(dst),
        })

    manifest = {
        "chip": flash_args.get("extra_esptool_args", {}).get("chip", "esp32s3"),
        "flash_mode": settings.get("flash_mode", "dio"),
        "flash_freq": settings.get("flash_freq", "80m"),
        "flash_size": settings.get("flash_size", "16MB"),
        "model": DEFAULT_MODEL.name,
        "model_sha256": model_hash,
        "parts": parts,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Packaged {len(parts)} files into {FIRMWARE_DIR}")
    for part in parts:
        print(f"  {part['offset']}: {part['file']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
