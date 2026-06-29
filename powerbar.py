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


def _git(cwd, *args):
    try:
        r = subprocess.run(
            ['git', '-C', cwd] + list(args),
            capture_output=True, text=True, timeout=5
        )
        return r.stdout.strip() if r.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def get_git_info(cwd):
    if not cwd or not os.path.isabs(cwd):
        return None
    if _git(cwd, 'rev-parse', '--git-dir') is None:
        return None

    branch = _git(cwd, 'symbolic-ref', '--short', 'HEAD')
    if branch is None:
        branch = _git(cwd, 'rev-parse', '--short', 'HEAD')
    if branch is None:
        return None

    info = {
        'branch': branch,
        'ahead': 0, 'behind': 0,
        'added': 0, 'removed': 0,
        'untracked': 0,
    }

    counts = _git(cwd, 'rev-list', '--left-right', '--count', '@{upstream}...HEAD')
    if counts:
        parts = counts.split()
        if len(parts) == 2:
            info['behind'] = int(parts[0])
            info['ahead'] = int(parts[1])

    for diff_cmd in [('diff', '--numstat'), ('diff', '--cached', '--numstat')]:
        output = _git(cwd, *diff_cmd)
        if output:
            for line in output.splitlines():
                cols = line.split('\t')
                if len(cols) >= 2:
                    try:
                        info['added'] += int(cols[0])
                        info['removed'] += int(cols[1])
                    except ValueError:
                        pass

    untracked_out = _git(cwd, 'ls-files', '--others', '--exclude-standard')
    if untracked_out:
        info['untracked'] = len(untracked_out.splitlines())

    return info


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


def _safe_int(val):
    try:
        return max(0, min(100, int(float(val))))
    except (TypeError, ValueError):
        return 0


def _int0(val):
    try:
        return max(0, int(val))
    except (TypeError, ValueError):
        return 0


PROGRESS_FILE = os.path.expanduser('~/.claude/progress.json')
PROGRESS_TTL = 60  # seconds; a file not updated within this is a dead run, shown no more


def read_progress(now=None):
    """Live build/verify progress published by `pbrun` (or any producer) to PROGRESS_FILE
    as ``{label, done, total, started, ts}``. Returns the dict if present and fresh, else
    None — a finished run clears the file, a crashed one goes stale past PROGRESS_TTL."""
    now = time.time() if now is None else now
    try:
        with open(PROGRESS_FILE) as f:
            p = json.load(f)
    except (OSError, ValueError):
        return None
    ts = p.get('ts')
    if not isinstance(ts, (int, float)) or now - ts > PROGRESS_TTL:
        return None
    return p


def format_progress(p, now=None):
    """A live progress segment: `⚙ label ●●●●●○○○ 7/11 12s`. With no total (indeterminate
    build) it falls back to `⚙ label 12s`."""
    now = time.time() if now is None else now
    label = str(p.get('label') or 'build')[:24]
    done, total = _int0(p.get('done')), _int0(p.get('total'))
    started = p.get('started')
    elapsed = f' {DIM}{int(now - started)}s{RESET}' if isinstance(started, (int, float)) else ''
    head = f'{CYAN}⚙{RESET} {WHITE}{label}{RESET}'
    if total > 0:
        bar = build_dot_bar(done * 100 // total, width=8)
        return f'{head} {bar} {WHITE}{done}/{total}{RESET}{elapsed}'
    return f'{head}{elapsed}'


def format_statusline(data):
    sep = f' {DIM}·{RESET} '

    cwd = data.get('workspace', {}).get('current_dir') or data.get('cwd', '')
    if not isinstance(cwd, str) or not cwd.startswith('/'):
        cwd = ''
    model = data.get('model', {}).get('display_name', '')

    line1_parts = []
    if cwd:
        line1_parts.append(f'{BOLD}{WHITE}{os.path.basename(cwd)}{RESET}')

    git = get_git_info(cwd) if cwd else None
    if git:
        git_str = f'{GREEN}{git["branch"]}{RESET}'
        if git['ahead']:
            git_str += f' {YELLOW}↑{git["ahead"]}{RESET}'
        if git['behind']:
            git_str += f' {YELLOW}↓{git["behind"]}{RESET}'
        if git['added'] or git['removed']:
            git_str += f' {CYAN}+{git["added"]} -{git["removed"]}{RESET}'
        if git['untracked']:
            git_str += f' {DIM}?{git["untracked"]}{RESET}'
        line1_parts.append(git_str)

    if model:
        line1_parts.append(f'{DIM}{model}{RESET}')

    ctx_pct = _safe_int(data.get('context_window', {}).get('used_percentage', 0))
    ctx_segment = f'{DIM}ctx{RESET} {build_dot_bar(ctx_pct)} {WHITE}{ctx_pct}%{RESET}'

    metrics = [ctx_segment]

    prog = read_progress()
    has_progress = prog is not None
    if has_progress:
        metrics.append(format_progress(prog))

    has_rate_limits = False

    rate_limits = data.get('rate_limits', {})
    five = rate_limits.get('five_hour', {})
    if five.get('used_percentage') is not None:
        has_rate_limits = True
        five_pct = _safe_int(five['used_percentage'])
        five_resets = five.get('resets_at')
        five_pace = calc_pace_pct(five_resets, 18000) if isinstance(five_resets, (int, float)) else None
        five_seg = f'{DIM}5h{RESET} {build_dot_bar(five_pct, pace_pct=five_pace)} {WHITE}{five_pct}%{RESET}'
        if isinstance(five_resets, (int, float)):
            five_seg += f' {DIM}({format_countdown(five_resets)}){RESET}'
        metrics.append(five_seg)

    seven = rate_limits.get('seven_day', {})
    if seven.get('used_percentage') is not None:
        has_rate_limits = True
        seven_pct = _safe_int(seven['used_percentage'])
        seven_resets = seven.get('resets_at')
        seven_pace = calc_pace_pct(seven_resets, 604800) if isinstance(seven_resets, (int, float)) else None
        seven_seg = f'{DIM}7d{RESET} {build_dot_bar(seven_pct, pace_pct=seven_pace)} {WHITE}{seven_pct}%{RESET}'
        if isinstance(seven_resets, (int, float)):
            seven_seg += f' {DIM}({format_countdown(seven_resets)}){RESET}'
        metrics.append(seven_seg)

    task_result = format_tasks(data.get('tasks'))
    has_tasks = task_result is not None
    if task_result:
        completed, total = task_result
        color = GREEN if completed == total else WHITE
        metrics.append(f'{DIM}tasks{RESET} {color}{completed}/{total}{RESET}')

    if has_rate_limits or has_tasks or has_progress:
        return sep.join(line1_parts) + '\n' + sep.join(metrics)
    else:
        return sep.join(line1_parts + [ctx_segment])


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
    print(format_statusline(data), end='')


if __name__ == '__main__':
    main()
