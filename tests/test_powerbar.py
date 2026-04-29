import re

from powerbar import (
    build_dot_bar, GREEN, YELLOW, ORANGE, RED, BLUE, DIM
)


def strip_ansi(s):
    return re.sub(r'\033\[[^m]*m', '', s)


def test_dot_bar_zero():
    result = build_dot_bar(0, 10)
    stripped = strip_ansi(result)
    assert stripped == '○' * 10


def test_dot_bar_full():
    result = build_dot_bar(100, 10)
    stripped = strip_ansi(result)
    assert stripped == '●' * 10


def test_dot_bar_half():
    result = build_dot_bar(50, 10)
    stripped = strip_ansi(result)
    assert stripped.count('●') == 5
    assert stripped.count('○') == 5


def test_dot_bar_clamps_negative():
    result = build_dot_bar(-10, 10)
    stripped = strip_ansi(result)
    assert stripped == '○' * 10


def test_dot_bar_clamps_over_100():
    result = build_dot_bar(150, 10)
    stripped = strip_ansi(result)
    assert stripped == '●' * 10


def test_dot_bar_gradient_has_green_and_red():
    result = build_dot_bar(100, 10)
    assert GREEN in result
    assert RED in result


def test_dot_bar_gradient_low_has_no_red():
    result = build_dot_bar(40, 10)
    assert RED not in result
    assert ORANGE not in result


def test_dot_bar_pace_below():
    result = build_dot_bar(30, 10, pace_pct=50)
    assert BLUE in result


def test_dot_bar_pace_on_track():
    result = build_dot_bar(50, 10, pace_pct=45)
    assert GREEN in result


def test_dot_bar_pace_outpacing():
    result = build_dot_bar(60, 10, pace_pct=30)
    assert YELLOW in result


def test_dot_bar_pace_critical():
    result = build_dot_bar(90, 10, pace_pct=20)
    assert RED in result


def test_dot_bar_empty_dots_always_dim():
    result = build_dot_bar(50, 10)
    empty_section = result.split('●')[-1]
    assert DIM in empty_section
