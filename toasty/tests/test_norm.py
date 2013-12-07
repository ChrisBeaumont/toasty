import numpy as np
import pytest

from ..norm import *


def test_log_warp():
    x = np.array([0, 1, 10, 100, 101])
    y = log_warp(x, 1, 100, .5, 1)
    yexp = np.array([0, 0, .654, 1, 1])
    np.testing.assert_array_almost_equal(y, yexp, 3)


def test_sqrt_warp():
    x = np.array([0, 1, 10, 100, 101])
    y = sqrt_warp(x, 1, 100, .5, 1)
    yexp = np.array([0, 0, .3015, 1, 1])
    np.testing.assert_array_almost_equal(y, yexp, 3)


def test_pow_warp():
    x = np.array([0, 1, 10, 100, 101])
    y = pow_warp(x, 1, 100, .5, 1)
    yexp = np.array([0, 0, .00087, 1, 1])
    np.testing.assert_array_almost_equal(y, yexp, 3)


def test_squared_warp():
    x = np.array([0, 1, 10, 100, 101])
    y = squared_warp(x, 1, 100, .5, 1)
    yexp = np.array([0, 0, .008264, 1, 1])
    np.testing.assert_array_almost_equal(y, yexp, 3)


def test_asinh_warp():
    x = np.array([0, 1, 10, 100, 101])
    y = asinh_warp(x, 1, 100, .5, 1)
    yexp = np.array([0, 0, .27187, 1, 1])
    np.testing.assert_array_almost_equal(y, yexp, 3)


def test_linear_warp():
    x = np.array([0, 1, 10, 100, 101])
    y = linear_warp(x, 1, 100, .5, 1)
    yexp = np.array([0, 0, 9. / 99., 1, 1])
    np.testing.assert_array_almost_equal(y, yexp, 3)


def test_bias():
    x = np.array([0, .4, .5, .6, 1])

    y = cscale(x.copy(), .5, 1)
    np.testing.assert_array_almost_equal(x, y)

    y = cscale(x.copy(), .5, 2)
    yexp = np.array([0, .3, .5, .7, 1])
    np.testing.assert_array_almost_equal(y, yexp)

    y = cscale(x.copy(), .5, 0)
    yexp = np.array([.5, .5, .5, .5, .5])
    np.testing.assert_array_almost_equal(y, yexp)

    y = cscale(x.copy(), .5, 0)
    yexp = np.array([.5, .5, .5, .5, .5])
    np.testing.assert_array_almost_equal(y, yexp)

    y = cscale(x.copy(), .4, 1)
    yexp = np.array([.1, .5, .6, .7, 1])
    np.testing.assert_array_almost_equal(y, yexp)

    y = cscale(x.copy(), .6, 1)
    yexp = np.array([0, .3, .4, .5, .9])
    np.testing.assert_array_almost_equal(y, yexp)


class TestNormalize(object):

    def test_input_unmodified(self):
        x = np.array([1, 2, 3])
        y = normalize(x, 1, 3, contrast=100)
        assert np.abs(x - y).max() > .1  #they are different
        np.testing.assert_array_almost_equal(x, [1, 2, 3]) # x is not

    def test_call_default(self):
        x = np.array([1, 2, 3])
        np.testing.assert_array_almost_equal(normalize(x, 1, 3), [0, 127, 255])

    def test_call_invert(self):
        x = np.array([1, 2, 3])
        y = normalize(x, vmin=3, vmax=1)
        np.testing.assert_array_almost_equal(y, [255, 127, 0])
