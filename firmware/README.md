# Prebuilt ESP32-S3 firmware

These binaries are the demo firmware built from `esp-dl/main/apps/demo` with
the bundled `demo.espdl` model. They let you flash the board without installing
ESP-IDF or compiling anything:

```bash
python run-demo.py --flash
```

`manifest.json` records the flash offsets, flash settings and the SHA-256 of
the model that the firmware was built with. `run-demo.py --flash` only uses
this bundle when the requested model matches that hash. If you pass a
different model, it automatically falls back to a source build (ESP-IDF
required).

## Refreshing the bundle

After changing the C++ app or the bundled model, rebuild from source and
re-run the packaging script:

```bash
source ~/.espressif/tools/activate_idf_v6.0.1.sh
cd esp-dl
idf.py -D ACTIVE_APP=demo build
cd ..
python tools/package-firmware.py
```

Commit the updated `firmware/` files together with the source/model change.
