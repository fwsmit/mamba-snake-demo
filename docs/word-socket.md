# KWS Word Socket

While `run-demo.py` is monitoring the demo firmware, it also runs a small TCP
server on localhost that publishes the keywords guessed by the KWS model. Other
applications on the same machine can connect to it to react to spoken commands.

## Connection

- **Address:** `tcp://127.0.0.1:8765` (change with `--port N`)
- **Direction:** server → client only. The server never reads or expects any
  data from the client; clients may disconnect at any time.
- Multiple simultaneous clients are supported. If a client dies, it is
  silently dropped from the fan-out.

## Message format

Each guessed keyword is sent as a single message:

```
<word>\n
```

- `word` is the predicted class label as plain UTF-8 text, terminated by a
  single newline (`0x0A`).
- Possible values are the SpeechCommands labels used by the model:
  `down`, `go`, `left`, `no`, `off`, `on`, `right`, `stop`, `up`, `yes`,
  `silence`, `unknown`.
- A word is only sent when it **differs from the previously sent word** —
  repeating the same command does not produce repeat messages. Repeating a word
  after any other word in between does send it again.
- Words are sent regardless of the dashboard's minimum-confidence slider; the
  socket always carries the raw model prediction (2 predictions per second, so
  at most 2 messages per second).

## Example

```console
$ nc 127.0.0.1 8765
yes
left
silence
```

Minimal Python client:

```python
import socket

s = socket.create_connection(("127.0.0.1", 8765))
f = s.makefile("r", encoding="utf-8")
for word in f:
    print("heard:", word.strip())
```
