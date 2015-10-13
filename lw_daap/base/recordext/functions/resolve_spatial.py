"""Resolve Frequency helper functions."""


def resolve_spatial(values, which):
    if not isinstance(values, list):
        values = [values]
    which_map = {
        'west': 0,
        'east': -1,
    }
    return values[which_map.get(which, 0)] 
