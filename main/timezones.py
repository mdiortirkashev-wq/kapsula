"""Butun dunyo vaqt mintaqalari ro'yxati (UTC siljishi bo'yicha saralangan)."""
from datetime import datetime, timezone as dt_timezone
from zoneinfo import ZoneInfo, available_timezones

_SKIP = {'Etc', 'posix', 'right', 'SystemV', 'US', 'Brazil', 'Canada', 'Chile', 'Mexico'}


def _utc_label(offset):
    minutes = int(offset.total_seconds() // 60)
    sign = '+' if minutes >= 0 else '-'
    h, m = divmod(abs(minutes), 60)
    return f"UTC{sign}{h:02d}:{m:02d}"


def build_choices():
    now = datetime.now(dt_timezone.utc)
    rows = []
    for name in available_timezones():
        if '/' not in name and name != 'UTC':
            continue
        if name.split('/')[0] in _SKIP:
            continue
        try:
            offset = now.astimezone(ZoneInfo(name)).utcoffset()
        except Exception:
            continue
        rows.append((offset, name))
    rows.sort(key=lambda r: (r[0], r[1]))
    return [(name, f"({_utc_label(off)}) {name.replace('_', ' ')}") for off, name in rows]


TZ_CHOICES = build_choices()
TZ_NAMES = {value for value, _ in TZ_CHOICES}
DEFAULT_TZ = 'Asia/Tashkent'