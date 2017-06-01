#!/usr/bin/env python
# -*- coding: UTF-8 -*-

def flatten(d, parent_key='', sep='__'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, str(v) if isinstance(v, list) else v))
    return dict(items)


def unflatten(d, sep='__'):
    items = {}
    for k, v in d.items():
        i = k.split(sep)
        if len(i) == 1:
            items[k] = v
        elif len(i) == 2:
            t = items.get(i[0], {})
            t[i[1]] = v
            items[i[0]] = t
    return items
