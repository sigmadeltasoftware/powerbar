#!/usr/bin/env python3
"""pbrun — run a command, stream its output, and publish live progress to
``~/.claude/progress.json`` so powerbar can show a status-line bar.

Turns a silent multi-minute build/verify into a glance: instead of "is it stuck or working?",
powerbar renders ``⚙ verify hydra-core ●●●●●○○○ 7/11 12s`` (determinate, from ``[i/N]`` markers
that e.g. ``synapse verify-proofs`` emits) or ``⚙ build 42s`` (indeterminate — elapsed only —
for tools like ``cargo`` that don't emit a count).

    pbrun --label "verify hydra-core" -- synapse verify-proofs --flow hydra-core --jobs 6
    pbrun -- cargo test -p hydra-core            # no [i/N] -> label + ticking elapsed

A background heartbeat re-stamps the file every second, so the bar stays alive (and the elapsed
keeps ticking) even while the wrapped command is silent — e.g. a long cargo compile with no
output. The file is written atomically and removed on exit; powerbar also ignores any file
older than its TTL, so a crashed run never leaves a phantom bar.

NOTE: for the bar to update live *during* a long command, the powerbar status-line needs
``"refreshInterval": 1000`` (Claude Code >= 2.1.97), set by powerbar's install.sh — otherwise
the status line only re-renders on events and freezes for the duration of the command.
"""
import json
import os
import re
import subprocess
import sys
import threading
import time

PROGRESS_FILE = os.path.expanduser("~/.claude/progress.json")
MARKER = re.compile(rb"\[(\d+)/(\d+)\]")  # e.g. [7/11]


class Progress:
    def __init__(self, label):
        self._lock = threading.Lock()
        now = time.time()
        self._state = {"label": label, "done": 0, "total": 0, "started": now, "ts": now}
        self._alive = True

    def flush(self):
        with self._lock:
            self._state["ts"] = time.time()
            data = dict(self._state)
        tmp = PROGRESS_FILE + ".tmp"
        try:
            os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
            with open(tmp, "w") as f:
                json.dump(data, f)
            os.replace(tmp, PROGRESS_FILE)  # atomic — powerbar never reads a half-written file
        except OSError:
            pass

    def update(self, done, total):
        with self._lock:
            self._state["done"], self._state["total"] = done, total

    def heartbeat(self):
        # re-stamp ts every second so the file stays fresh (and elapsed ticks) during silent
        # phases — a long compile may emit no lines for minutes.
        while self._alive:
            self.flush()
            time.sleep(1)

    def stop(self):
        self._alive = False
        try:
            os.remove(PROGRESS_FILE)
        except OSError:
            pass


def main(argv):
    label = "build"
    if argv and argv[0] == "--label":
        if len(argv) < 2:
            sys.exit("pbrun: --label needs a value")
        label, argv = argv[1], argv[2:]
    if argv and argv[0] == "--":
        argv = argv[1:]
    if not argv:
        sys.exit("usage: pbrun [--label L] -- <command> [args...]")

    prog = Progress(label)
    prog.flush()
    threading.Thread(target=prog.heartbeat, daemon=True).start()

    # Merge stderr into stdout so we catch markers from either stream (synapse streams to stderr),
    # and re-emit every line so the wrapped command still looks normal in the terminal.
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        for line in iter(proc.stdout.readline, b""):
            sys.stdout.buffer.write(line)
            sys.stdout.buffer.flush()
            last = None
            for last in MARKER.finditer(line):
                pass  # keep the LAST marker on the line
            if last is not None:
                prog.update(int(last.group(1)), int(last.group(2)))
        rc = proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        rc = 130
    finally:
        prog.stop()
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
