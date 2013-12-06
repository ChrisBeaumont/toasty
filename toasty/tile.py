"""
Generate PNG tile directories
"""
import os
import numpy as np

from .util import subsample, mid
from skimage.io import imsave

level1 = map(np.radians, [[(0, -90), (90, 0), (0, 90), (180, 0)],
                          [(90, 0), (0, -90), (0, 0), (0, 90)],
                          [(0, 90), (0, 0), (0, -90), (270, 0)],
                          [(180, 0), (0, 90), (270, 0), (0, -90)]])


def div4(n, x, y, c, increasing):
    ul, ur, lr, ll = c
    to = mid(ul, ur)
    ri = mid(ur, lr)
    bo = mid(lr, ll)
    le = mid(ll, ul)
    ce = mid(ll, ur) if increasing else mid(ul, lr)

    return [(n + 1, 2 * x, 2 * y, (ul, to, ce, le), increasing),
            (n + 1, 2 * x + 1, 2 * y, (to, ur, ri, ce), increasing),
            (n + 1, 2 * x, 2 * y + 1, (le, ce, bo, ll), increasing),
            (n + 1, 2 * x + 1, 2 * y + 1, (ce, ri, lr, bo), increasing)]


def tile_directory(data, vec2pix, depth, outbase):
    todo = [(1, 0, 0, level1[0], True),
            (1, 0, 1, level1[1], False),
            (1, 1, 1, level1[2], True),
            (1, 1, 0, level1[3], False)]

    while len(todo):
        n, x, y, c, increasing = todo.pop()
        assert n <= depth

        direc = os.path.join(outbase, '%i' % n, '%i' % y)
        if not os.path.exists(direc):
            os.makedirs(direc)
        pth = os.path.join(direc, '%i_%i.png' % (x, y))

        x, y = subsample(c[0], c[1], c[2], c[3], 256, increasing)
        x, y = vec2pix(x, y)
        img = data[x, y]
        imsave(pth, img)

        if n == depth:
            continue

        todo.extend(div4(n, x, y, c, increasing))
