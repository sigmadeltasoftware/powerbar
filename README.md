# powerbar

A rich status line for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) that shows git info, context window usage, rate limits with pace tracking, and task progress — all in your terminal.

<p align="center">
  <img src="assets/preview.svg" alt="powerbar preview" width="720">
</p>

## What you get

- **Project & git** — branch, ahead/behind, diff stats, untracked files
- **Context window** — dot bar with gradient coloring (green → yellow → red)
- **Rate limits** — 5-hour and 7-day usage with pace-aware coloring (blue = under pace, green → red = over pace) and countdown to reset
- **Tasks** — completed / total count
- **Adaptive layout** — single line when minimal, two lines when rate limits or tasks are present

## Install

```bash
git clone https://github.com/sigmadeltasoftware/powerbar.git
cd powerbar
./install.sh
```

This copies `powerbar.py` to `~/.claude/` and configures the `statusLine` setting in `~/.claude/settings.json`. Restart Claude Code to activate.

### Manual install

```bash
cp powerbar.py ~/.claude/powerbar.py
```

Add to `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/powerbar.py"
  }
}
```

## Requirements

- Python 3.6+
- Git (for branch/diff info)
- A terminal with true color support (most modern terminals)

## How it works

Claude Code pipes JSON status data to the configured command via stdin. `powerbar.py` parses this and outputs ANSI-colored text. The dot bars use Unicode circles (`●` / `○`) with 24-bit color codes.

**Pace tracking**: Rate limit bars compare your current usage against where you *should* be given the time elapsed in the window. If you're under pace, the bar is blue. As you exceed pace, it shifts green → yellow → red.

## License

MIT
