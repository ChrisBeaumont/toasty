from libc.math cimport sin, cos, atan2, hypot
import numpy as np

cimport cython

cimport numpy as np

DTYPE = np.float
ctypedef np.float_t DTYPE_t

cdef struct Point:
    DTYPE_t x
    DTYPE_t y

cdef void _mid(Point a, Point b, Point *cen):
    """
    Return the midpoint of two points on a great circle arc

    Parameters
    ----------
    a, b: Point
    Two lon, lat pairs, in radians
    """
    cdef DTYPE_t dl, bx, by, b3, l3, outb, outl
    cdef Point out

    dl = b.x - a.x
    bx = cos(b.y) * cos(dl)
    by = cos(b.y) * sin(dl)
    outb = atan2(sin(a.y) + sin(b.y), hypot(cos(a.y) + bx, by))
    outl = a.x + atan2(by, cos(a.y) + bx)
    cen.x = outl
    cen.y = outb


def mid(a, b):
    cdef Point l = Point(a[0], a[1]), m = Point(b[0], b[1]), n
    _mid(l, m, &n)
    return n.x, n.y


@cython.boundscheck(False)
cdef void _subsample(Point ul, Point ur, Point lr, Point ll,
                    DTYPE_t [:, :] x,
                    DTYPE_t [:, :] y,
                    int increasing):
    """
    Given the corners of a toast tile, return the
    sky locations of a subsampled version

    Parameters
    ----------
    ul, ur, lr, ll: Points
        The (lon, lat) coordinates of the four corners of the toast
        tile to subdivide. In radians
    x, y : arrays
        The arrays in which to hold the subdivided locations
    increasing : int
         If 1, the shared edge of the toast tile's two sub-HTM
         trixels increases from left to right. Otherwise, it
         decreases from left to right
    n : int
        The number of pixels in x and y
    """
    cdef Point le, up, lo, ri, cen
    cdef int n = x.shape[0]
    cdef int n2 = n / 2

    _mid(ul, ur, &up)
    _mid(ul, ll, &le)
    _mid(ur, lr, &ri)
    _mid(ll, lr, &lo)

    if increasing:
        _mid(ll, ur, &cen)
    else:
        _mid(ul, lr, &cen)

    if n == 1:
        x[0] = cen.x
        y[0] = cen.y
        return

    _subsample(ul, up, cen, le, x[:n2, :n2], y[:n2, :n2], increasing)
    _subsample(up, ur, ri, cen, x[:n2, n2:], y[:n2, n2:], increasing)
    _subsample(le, cen, lo, ll, x[n2:, :n2], y[n2:, :n2], increasing)
    _subsample(cen, ri, lr, lo, x[n2:, n2:], y[n2:, n2:], increasing)


def subsample(ul, ur, lr, ll, npix, increasing):
    """Subdivide a toast quad, and return the pixel locations

    Parameters
    ----------
    ul, ur, lr, ll : array-like
        Two-element arrays giving the (lon, lat) position of each corner
        of the toast tile, in radians
    npix: int
        The pixel resolution of the subsampled image. Must be a power of 2
    increasing: bool
        Whether the two HTM trixels that define this toast tile are joined
        along the diagonal which increases from left to right


    Returns
    --------
    Two arrays, giving the lon/lat of each point in the subsampled image
    """
    if len(ul) != 2 or len(ur) != 2 or len(lr) != 2 or len(ll) != 2:
        raise ValueError("Toast corners must be two-element arrays")
    if 2 ** int(np.log2(npix)) != npix:
        raise ValueError("npix must be a power of 2: %i" % npix)

    cdef Point _ul, _ur, _lr, _ll
    cdef int _inc = (1 if increasing else 0)

    x = np.zeros((npix, npix), dtype=DTYPE)
    y = np.zeros((npix, npix), dtype=DTYPE)

    _ul = Point(DTYPE(ul[0]), DTYPE(ul[1]))
    _ur = Point(DTYPE(ur[0]), DTYPE(ur[1]))
    _lr = Point(DTYPE(lr[0]), DTYPE(lr[1]))
    _ll = Point(DTYPE(ll[0]), DTYPE(ll[1]))
    _subsample(_ul, _ur, _lr, _ll, x, y, increasing)
    return x, y
