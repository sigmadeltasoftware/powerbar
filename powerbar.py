#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time

BLUE = '\033[38;2;0;153;255m'
GREEN = '\033[38;2;0;160;0m'
YELLOW = '\033[38;2;230;200;0m'
ORANGE = '\033[38;2;255;176;85m'
RED = '\033[38;2;255;85;85m'
CYAN = '\033[38;2;46;149;153m'
WHITE = '\033[38;2;220;220;220m'
BOLD = '\033[1m'
DIM = '\033[2m'
RESET = '\033[0m'

DOT_FILLED = '●'
DOT_EMPTY = '○'


def main():
    raw = sys.stdin.read()
    if not raw.strip():
        print('Claude', end='')
        return
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print('Claude', end='')
        return
    print('Claude', end='')


if __name__ == '__main__':
    main()
