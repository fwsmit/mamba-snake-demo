# Standalone ESP32-S3 KWS demo

This is a demo of a voice-powered snake game running on the ESP32-S3. The voice recognition model is powered by Mamba and is fully running on the MCU.

## Setup

Python 3.10+ is required. The dashboard uses Tkinter, which is included with
most Python installers. On Debian/Ubuntu install it with
`sudo apt install python3-tk`.

Create a virtual environment and install the Python dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The prebuilt ESP32-S3 firmware is committed under `firmware/`, so flashing does
not require ESP-IDF or a compiler. ESP-IDF is only needed if you rebuild the
firmware from source.

## Run

```bash
# Flash the prebuilt firmware, then monitor and launch the snake game
python run-demo.py --flash

# Rebuild the firmware from source and flash it (requires ESP-IDF v6.0.1)
python run-demo.py --build

# Monitor already-flashed firmware and launch the snake game
python run-demo.py
```

By default `--flash` uses `firmware/` together with the bundled `demo.espdl`.
Passing a different model automatically falls back to a source build:

```bash
python run-demo.py --flash path/to/model.espdl
```

On Linux, serial output and flashing use `/dev/ttyACM0`. The dashboard
publishes recognized keywords on `tcp://127.0.0.1:8765` for the snake game;
use `--port N` to change the port.

## Rebuilding the prebuilt firmware

After changing the C++ app or bundled model, rebuild and refresh the checked-in
firmware bundle:

```bash
source ~/.espressif/tools/activate_idf_v6.0.1.sh
cd esp-dl
idf.py -D ACTIVE_APP=demo build
cd ..
python tools/package-firmware.py
```

See `firmware/README.md` for details about the generated manifest.

## Tests

```bash
python Python-Snake-Game/test_snake.py

# Optional Python test dependencies
python -m pip install -r requirements-dev.txt
```
