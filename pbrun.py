#!/usr/bin/env python3
"""pbrun — run a command, stream its output, and publish ``[done/total]`` progress to
``~/.claude/progress.json`` so powerbar can show a live bar in the status line.

Turns a silent multi-minute build/verify into a glance: instead of wondering "is it stuck or
working?", powerbar renders ``⚙ verify hydra-core ●●●●●○○○ 7/11 12s``.

It scans the wrapped command's output for ``[i/N]`` progress markers — the format
``synapse verify-proofs`` already streams (``[7/11] flow: invariant … (compiling+testing)``).
With no marker yet it still shows the label + elapsed time (an indeterminate spinner).

    pbrun --label "verify hydra-core" -- synapse verify-proofs --flow hydra-core --jobs 6
    pbrun -- cargo test -p hydra-core            # no [i/N] -> label + elapsed only

The file is written atomically and removed on exit; powerbar also ignores any file older than
its TTL, so a crashed run never leaves a phantom bar.
"""
import json
import os
import re
import subprocess
import sys
import time

PROGRESS_FILE = os.path.expanduser("~/.claude/progress.json")
MARKER = re.compile(rb"\[(\d+)/(\d+)\]")  # e.g. [7/11]


def _write(state):
    tmp = PROGRESS_FILE + ".tmp"
    try:
        os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
        with open(tmp, "w") as f:
            json.dump(state, f)
        os.replace(tmp, PROGRESS_FILE)  # atomic — powerbar never reads a half-written file
    except OSError:
        pass


def _clear():
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

    started = time.time()
    state = {"label": label, "done": 0, "total": 0, "started": started, "ts": started}
    _write(state)

    # Merge stderr into stdout so we see markers from either stream (synapse streams to stderr),
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
                state.update(done=int(last.group(1)), total=int(last.group(2)))
            state["ts"] = time.time()  # heartbeat so powerbar knows the run is alive
            _write(state)
        rc = proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        rc = 130
    finally:
        _clear()
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
