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


def build_dot_bar(pct, width=10, pace_pct=None):
    pct = max(0, min(100, int(pct)))
    filled = pct * width // 100
    empty = width - filled

    if pace_pct is not None:
        above_pace = pct - pace_pct
        if above_pace < 0:
            color = BLUE
        elif above_pace <= 20:
            color = GREEN
        elif above_pace <= 50:
            color = YELLOW
        else:
            color = RED
        filled_str = color + DOT_FILLED * filled
    else:
        filled_str = ''
        for i in range(filled):
            pos = (i + 1) * 100 // width
            if pos >= 90:
                c = RED
            elif pos >= 70:
                c = YELLOW
            elif pos >= 50:
                c = ORANGE
            else:
                c = GREEN
            filled_str += c + DOT_FILLED

    empty_str = DIM + DOT_EMPTY * empty
    return filled_str + empty_str + RESET


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
