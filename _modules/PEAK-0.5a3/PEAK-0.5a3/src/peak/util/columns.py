"""Utilities for columnar output"""

from __future__ import generators

def lsFormat(width, items, colsize=16, sort=True, reverse=False):
    """utility for things that want to print ls-like columnar output"""

    items = list(items) # don't modify the original list!

    if not items:
        return

    if sort:
        items.sort()

    if reverse:
        items.reverse()

    # Truncate items to available width
    items = [
        len(item) >= width and item[:width-4]+'...' or item
        for item in items
    ]

    maxlen = max([len(item) for item in items])+1
    maxlen = max(maxlen,colsize)
    cols, leftover = divmod(width,maxlen)
    cols = min(cols,len(items))
    colwidth,leftover = divmod(width,cols)
    rows,    leftover = divmod(len(items), cols)
    if leftover:
        rows += 1
        items.extend((cols-leftover)*[''])

    grid = []
    for i in range(cols):
        grid.append(items[i*rows:(i+1)*rows])

    grid = zip(*grid)
    for row in grid:
        yield ''.join([item.ljust(colwidth) for item in row]).rstrip()+'\n'


