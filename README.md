# Standalone ESP32-S3 KWS demo

This is a demo of a voice-powered snake game running on the ESP32-S3. The voice recognition model is powered by Mamba and is fully running on the MCU.

## Setup

This demo requires pygame and idf.py

## Run

```bash
# Build and flash the bundled model, then monitor and launch the snake game
python run-demo.py --flash

# Monitor already-flashed firmware and launch the snake game
python run-demo.py
```
