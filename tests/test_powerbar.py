import re

from powerbar import (
    build_dot_bar, calc_pace_pct, format_countdown, format_tasks, GREEN, YELLOW, ORANGE, RED, BLUE, DIM
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


def test_pace_pct_midway():
    assert calc_pace_pct(1000, 100, now=950) == 50


def test_pace_pct_start():
    assert calc_pace_pct(1000, 100, now=900) == 0


def test_pace_pct_end():
    assert calc_pace_pct(1000, 100, now=1000) == 100


def test_pace_pct_clamps_before_window():
    assert calc_pace_pct(1000, 100, now=800) == 0


def test_pace_pct_clamps_after_window():
    assert calc_pace_pct(1000, 100, now=1200) == 100


def test_pace_pct_invalid_window():
    assert calc_pace_pct(1000, 0) is None


def test_countdown_past():
    assert format_countdown(100, now=200) == 'now'


def test_countdown_minutes():
    assert format_countdown(1000, now=1000 - 2700) == '45min'


def test_countdown_one_minute():
    assert format_countdown(1000, now=1000 - 30) == '1min'


def test_countdown_hours_and_minutes():
    assert format_countdown(1000, now=1000 - 9000) == '2h 30min'


def test_countdown_exact_hours():
    assert format_countdown(1000, now=1000 - 10800) == '3h'


def test_countdown_days_and_hours():
    assert format_countdown(1000, now=1000 - 93600) == '1d 2h'


def test_countdown_exact_days():
    assert format_countdown(1000, now=1000 - 259200) == '3d'


def test_tasks_none():
    assert format_tasks(None) is None


def test_tasks_empty_list():
    assert format_tasks([]) is None


def test_tasks_with_mixed_statuses():
    tasks = [
        {'status': 'completed'},
        {'status': 'completed'},
        {'status': 'in_progress'},
        {'status': 'pending'},
    ]
    assert format_tasks(tasks) == (2, 4)


def test_tasks_all_complete():
    tasks = [{'status': 'completed'}, {'status': 'completed'}]
    assert format_tasks(tasks) == (2, 2)


def test_tasks_none_complete():
    tasks = [{'status': 'pending'}, {'status': 'in_progress'}]
    assert format_tasks(tasks) == (0, 2)


def test_tasks_non_list():
    assert format_tasks("not a list") is None


def test_tasks_malformed_items():
    tasks = [{'status': 'completed'}, {'no_status': True}, 'garbage']
    assert format_tasks(tasks) == (1, 3)
