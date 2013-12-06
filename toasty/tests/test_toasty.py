import os

import pytest
import numpy as np

from .. import iter_tiles, cartesian_sampler
from ..io import read_png, save_png
from ..util import mid

def mock_sampler(x, y):
    pass


@pytest.mark.parametrize('depth', (0, 1, 2))
def test_iter_tiles_path(depth):
    result = set(r[0] for r in iter_tiles(mock_sampler, depth))
    expected = set(['{n}/{y}/{y}_{x}.png'.format(n=n, x=x, y=y)
                    for n in range(depth+1)
                    for y in range(2 ** n)
                    for x in range(2 ** n)])
    assert result == expected


def test_mid():
    result = mid((0, 0), (np.pi / 2, 0))
    expected = np.pi / 4, 0
    np.testing.assert_array_almost_equal(result, expected)

    result = mid((0, 0), (0, 1))
    expected = 0, .5
    np.testing.assert_array_almost_equal(result, expected)


def fail_image(expected, actual, err_msg):
    from tempfile import mkstemp

    _, pth = mkstemp(suffix='.png')
    save_png(pth, np.hstack((expected, actual)))

    assert False, "%s. Saved to %s" % (err_msg, pth)


def test_wwt_compare_sky():
    """Assert that the toast tiling looks similar to the WWT tiles"""
    direc = os.path.split(os.path.abspath(__file__))[0]

    im = read_png(os.path.join(direc, 'test.png'))
    im = np.flipud(im)

    sampler = cartesian_sampler(im)

    for pth, result in iter_tiles(sampler, depth=1):
        expected = read_png(os.path.join(direc, 'test_sky', pth))
        expected = expected[:, :, :3]

        resid = np.abs(1. * result - expected)
        if np.median(resid) > 15:
            fail_image(expected, result, "Failed for %s" % pth)
