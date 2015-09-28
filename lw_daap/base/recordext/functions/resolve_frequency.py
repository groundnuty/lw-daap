"""Resolve Frequency helper functions."""


def resolve_frequency(values, which):
    if not isinstance(values, list):
        values = [values]
    which_map = {
        'size': 0,
        'unit': -1,
    }
    return values[which_map.get(which, 0)] 
