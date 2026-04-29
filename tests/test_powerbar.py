import re

def strip_ansi(s):
    return re.sub(r'\033\[[^m]*m', '', s)
