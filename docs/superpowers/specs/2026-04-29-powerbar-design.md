# Powerbar — Claude Code Statusline

A minimal, adaptive statusline for Claude Code. Single Python script, no dependencies beyond Python 3 and git. Reads JSON from Claude Code's stdin, prints ANSI-formatted output.

## Segments

| Segment | Source | Display |
|---------|--------|---------|
| Directory | `workspace.current_dir` | Basename only, bold white. e.g. `powerbar` |
| Git | `git` CLI (shelled out using cwd) | `main ↑2 ↓1 +15 -3 ?4` — branch (green), ahead/behind (yellow), added/removed (cyan), untracked (dim). Only non-zero parts shown. |
| Model | `model.display_name` | Dimmed. e.g. `Opus 4.6` |
| Context | `context_window.used_percentage` | Dot bar + percentage. e.g. `ctx ●●●●○○○○○○ 42%` |
| 5-hour usage | `rate_limits.five_hour` | Dot bar + percentage + reset countdown. e.g. `5h ●●○○○○○○○○ 18% (2h 30min)` |
| 7-day usage | `rate_limits.seven_day` | Same format as 5-hour |
| Tasks | `tasks` field from stdin JSON | `tasks 3/7` — completed/total. Only shown when tasks exist. |

Separators: ` · ` (dimmed middle dot).

## Adaptive Layout

**Single line** — when only directory, git, model, and context are available:

```
powerbar · main ↑2 +15 -3 · Opus 4.6 · ctx ●●●●○○○○○○ 42%
```

**Two lines** — when rate limits OR tasks are present:

```
powerbar · main ↑2 +15 -3 · Opus 4.6
ctx ●●●●○○○○○○ 42% · 5h ●●○○○○○○○○ 18% (2h 30min) · 7d ●○○○○○○○○○ 5% · tasks 3/7
```

Rules:
- Line 1 always contains: directory, git, model
- Line 2 appears only when rate limits or tasks are present
- Single line mode: context bar joins line 1
- Two line mode: context bar moves to line 2 with other metrics
- Segments with no data are silently omitted

## Colors

| Element | Color |
|---------|-------|
| Directory | White, bold |
| Git branch | Green |
| Git ahead/behind | Yellow |
| Git added/removed | Cyan |
| Git untracked | Dim |
| Model | Dim |
| Separators | Dim |
| Labels (`ctx`, `5h`, `7d`, `tasks`) | Dim |
| Percentages | White |
| Reset countdowns | Dim |

## Dot Bars

All bars use 10 dots. Filled: `●`, empty: `○`.

**Context bar** — per-dot gradient by position:

| Position | Color |
|----------|-------|
| 0–49% | Green |
| 50–69% | Yellow |
| 70–89% | Orange |
| 90%+ | Red |

**Rate limit bars** — pace-based coloring (all filled dots same color):

| Pace delta | Color | Meaning |
|------------|-------|---------|
| Below pace | Blue | Healthy buffer |
| 0–20% above | Green | On track |
| 20–50% above | Yellow | Outpacing |
| 50%+ above | Red | Significantly outpacing |

**Empty dots** — always dim.

**Task segment** — no bar, just `tasks 3/7`. Green when all complete, white otherwise.

## Script Structure

Single file `powerbar.py`:

1. **Constants** — ANSI color codes
2. **`build_dot_bar(pct, width, pace_pct=None)`** — returns formatted dot string with gradient or pace-based coloring
3. **`get_git_info(cwd)`** — shells out to git, returns dict with branch/ahead/behind/added/removed/untracked
4. **`calc_pace_pct(resets_epoch, window_secs)`** — percentage of time elapsed in rate limit window
5. **`format_countdown(epoch)`** — human-readable time until reset (e.g. `2h 30min`, `45min`, `3d 2h`)
6. **`format_tasks(tasks_data)`** — returns `3/7` string or None
7. **`main()`** — reads stdin JSON, assembles segments, decides single/two-line layout, prints

## Installation

`install.sh` copies `powerbar.py` to `~/.claude/` and updates `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/powerbar.py"
  }
}
```

## Fallback Behavior

- Empty/missing stdin → print `Claude` and exit
- No git repo → skip git segment
- No rate limits → skip rate limit bars
- No tasks → skip task segment
- Invalid/missing JSON fields → silently omit, never crash
