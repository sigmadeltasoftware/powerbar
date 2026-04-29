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


def calc_pace_pct(resets_epoch, window_secs, now=None):
    if now is None:
        now = time.time()
    if window_secs <= 0:
        return None
    window_start = resets_epoch - window_secs
    elapsed = now - window_start
    elapsed = max(0, min(elapsed, window_secs))
    return round(elapsed / window_secs * 100)


def format_countdown(epoch, now=None):
    if now is None:
        now = time.time()
    diff = int(epoch - now)
    if diff <= 0:
        return 'now'
    minutes = (diff + 59) // 60
    if minutes < 60:
        return f'{minutes}min'
    hours = minutes // 60
    mins = minutes % 60
    if hours < 24:
        return f'{hours}h {mins}min' if mins else f'{hours}h'
    days = hours // 24
    remaining_hours = hours % 24
    return f'{days}d {remaining_hours}h' if remaining_hours else f'{days}d'


def format_tasks(tasks_data):
    if not isinstance(tasks_data, list) or len(tasks_data) == 0:
        return None
    total = len(tasks_data)
    completed = sum(
        1 for t in tasks_data
        if isinstance(t, dict) and t.get('status') == 'completed'
    )
    return completed, total


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
