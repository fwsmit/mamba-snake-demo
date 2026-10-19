"""
Word-command socket client for voice-controlled snake.

Connects to the KWS Word Socket (see socket_docs.md): a small TCP server on
localhost (tcp://127.0.0.1:8765 by default) that pushes each guessed keyword
as a single line terminated by a newline ("left\\n", "up\\n", ...). The server
only sends data, it never expects any bytes back from clients.

The WordCommandClient class runs a daemon thread that keeps the connection
alive (reconnecting while the server is unavailable) and exposes the received
words through a thread-safe queue, so the game loop never blocks on I/O.
"""

import socket
import threading
import queue

from config import (
    SOCKET_HOST,
    SOCKET_PORT,
    SOCKET_RECONNECT_DELAY,
    UP,
    DOWN,
    LEFT,
    RIGHT,
)

# Words that map to snake directions (subset of the SpeechCommands labels
# documented in socket_docs.md).
DIRECTION_WORDS = {
    "up": UP,
    "down": DOWN,
    "left": LEFT,
    "right": RIGHT,
}

# Simple game-flow words
START_WORDS = frozenset({"disabled"})
STOP_WORDS = frozenset({"disabled"})


class WordCommandClient:
    """
    Client for the KWS word socket.

    A daemon thread maintains the connection (reconnecting with a delay while
    the server is down) and pushes each received word onto an internal queue.
    The game loop drains the queue with get_command().
    """

    def __init__(self, host=SOCKET_HOST, port=SOCKET_PORT, reconnect_delay=SOCKET_RECONNECT_DELAY):
        """
        Args:
            host (str): Server host (default from config).
            port (int): Server port (default from config).
            reconnect_delay (float): Seconds to wait between attempts.
        """
        self.host = host
        self.port = port
        self.reconnect_delay = reconnect_delay
        self._queue = queue.Queue()
        self._stop_event = threading.Event()
        self._thread = None
        self.connected = False

    def start(self):
        """Start the background reader thread (idempotent)."""
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="word-socket")
        self._thread.start()

    def stop(self):
        """Stop the background thread and close the socket (idempotent)."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        self.connected = False

    def get_command(self):
        """
        Return the next received word, or None if none are waiting.

        Returns:
            str or None: Stripped word label.
        """
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    def _run(self):
        """Thread entry point: keep (re)connecting until stopped."""
        while not self._stop_event.is_set():
            try:
                self._connect_and_read()
            except Exception as exc:  # pragma: no cover - defensive safety net
                print(f"[word-socket] error: {exc}")
            if not self._stop_event.is_set():
                self._stop_event.wait(self.reconnect_delay)

    def _connect_and_read(self):
        """Connect once and read words until the server drops the connection."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)  # low timeout so stop() is honoured promptly
        try:
            sock.connect((self.host, self.port))
        except Exception as exc:
            sock.close()
            print(f"[word-socket] cannot connect to {self.host}:{self.port} ({exc})")
            return

        self.connected = True
        print(f"[word-socket] connected to {self.host}:{self.port}")
        buf = b""
        try:
            while not self._stop_event.is_set():
                try:
                    data = sock.recv(4096)
                except socket.timeout:
                    continue  # no data yet; loop again so stop() is checked
                if not data:
                    break  # server closed the connection
                buf += data
                # Split complete lines out of the buffer (words end with \n)
                while b"\n" in buf:
                    raw, buf = buf.split(b"\n", 1)
                    word = raw.decode("utf-8", errors="ignore").strip()
                    if word:
                        self._queue.put(word)
        finally:
            sock.close()
            self.connected = False
            print("[word-socket] disconnected")
