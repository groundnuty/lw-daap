"""Resolve Period helper functions."""

import datetime
import time

def resolve_period(values, which):
    if not isinstance(values, list):
        values = [values]
    period = []
    for v in values:
        period.append(datetime.date(*(time.strptime(v or '', '%Y-%m-%d')[0:3])))
    if which == 'start':
        return period[0]
    elif which == 'end':
        return period[-1] 
