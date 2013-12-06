"""
Generate PNG tile directories
"""
import os
import numpy as np

from .util import subsample, mid
from .io import save_png
from .norm import normalize

level1 = [[np.radians(c) for c in row]
          for row in  [[(0, -90), (90, 0), (0, 90), (180, 0)],
                       [(90, 0), (0, -90), (0, 0), (0, 90)],
                       [(0, 90), (0, 0), (0, -90), (270, 0)],
                       [(180, 0), (0, 90), (270, 0), (0, -90)]]
                       ]

def _div4(n, x, y, c, increasing):
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


def iter_tiles(data_sampler, depth):
    """
    Create a hierarchy of toast tiles

    Parameters
    ----------
    data_sampler : function
       A function that takes two 2D numpy arrays of (lon, lat) as input,
       and returns an image of the original dataset sampled
       at these locations

    depth : int
      The maximum depth to tile to. A depth of N creates
      4^N pngs at the deepest level

    Yields
    ------
    (pth, tile) : str, ndarray
      pth is the relative path where the tile image should be saved
    """
    todo = [(1, 0, 0, level1[0], True),
            (1, 1, 0, level1[1], False),
            (1, 1, 1, level1[2], True),
            (1, 0, 1, level1[3], False)]
    lev1 = {}

    while len(todo):
        n, x, y, c, increasing = todo.pop()

        pth = os.path.join('%i' % n, '%i' % y, '%i_%i.png' % (y, x))

        l, b = subsample(c[0], c[1], c[2], c[3], 256, increasing)
        img = data_sampler(l, b)
        if n == 1:
            lev1[(x, y)] = img

        if depth != 0:
            yield pth, img

        if n < depth:
            todo .extend(_div4(n, x, y, c, increasing))

    # level 0 tile plays by special rules
    n0 = np.vstack((np.hstack((lev1[(0, 0)], lev1[(1, 0)])),
                    np.hstack((lev1[(0, 1)], lev1[(1, 1)]))))
    n0 = n0[::2, ::2]
    pth = os.path.join('0', '0', '0_0.png')
    yield pth, n0


def toast(data_sampler, depth, base_dir):
    """
    Build a directory of toast tiles

    Parameters
    ----------
    data_sampler : func
      A function of (lon, lat) that samples a dataset
      at the input 2D coordinate arrays
    depth : int
      The maximum depth to generate tiles for.
      4^n tiles are generated at each depth n
    base_dir : str
      The path to create the files at
    """

    for pth, tile in iter_tiles(data_sampler, depth):
        print pth
        pth = os.path.join(base_dir, pth)
        direc, _ = os.path.split(pth)
        if not os.path.exists(direc):
            os.makedirs(direc)
        save_png(pth, tile)


def _find_extension(pth):
    """
    Find the first HEALPIX extension in a fits file,
    and return the extension number. Else, raise an IndexError
    """
    for i, hdu in enumerate(pth):
        if hdu.header.get('PIXTYPE') == 'HEALPIX':
            return i
    else:
        raise IndexError("No HEALPIX extensions found in %s" % pth.filename())


def _guess_healpix(pth, extension=None):
    # try to guess healpix_sampler arguments from
    # a file

    from astropy.io import fits
    f = fits.open(pth)

    if extension is None:
        extension = _find_extension(f)

    data, hdr = f[extension].data, f[extension].header
    nest = hdr.get('ORDERING') == 'NESTED'
    coord = hdr.get('COORDSYS', 'C')

    return data, nest, coord


def healpix_sampler(data, nest=False, coord = 'C', interpolation='nearest'):
    """
    Build a sampler for Healpix images

    Parameters
    ----------
    data : array
      The healpix data
    nest : bool (default: False)
      Whether the data is ordered in the nested healpix style
    coord : 'C' | 'G'
      Whether the image is in Celestial (C) or Galactic (G) coordinates
    interpolation : 'nearest' | 'bilinear'
      What interpolation scheme to use.

      WARNING: bilinear uses healpy's get_interp_val,
               which seems prone to segfaults

    Returns
    -------
    A function which samples the healpix image, given arrays
    of (lon, lat)
    """
    from healpy import ang2pix, get_interp_val, npix2nside

    interp_opts = ['nearest', 'bilinear']
    if interpolation not in interp_opts:
        raise ValueError("Invalid interpolation %s. Must be one of %s" %
                         (interpolation, interp_opts))
    if coord.upper() not in 'CG':
        raise ValueError("Invalid coord %s. Must be 'C' or 'G'" % coord)

    #XXX Add support for G
    if coord.upper() == 'G':
        raise NotImplementedError("coord='G' not yet supported")

    interp = interpolation == 'bilinear'
    nside = npix2nside(data.size)

    def vec2pix(l, b):
        theta = np.pi / 2 - b
        phi = l

        if interp:
            return get_interp_val(data, theta, phi, nest=nest)

        return data[ang2pix(nside, theta, phi, nest=nest)]

    return vec2pix


def cartesian_sampler(data):
    """Return a sampler function for a dataset in the cartesian projection

    The image is assumed to be oriented with longitude increasing to the left,
    with (l,b) = (0,0) at the center pixel

    Parameters
    ----------
    data : array-like
      The map to sample
    """
    data = np.asarray(data)
    ny, nx = data.shape[0:2]

    if ny * 2 != nx:
        raise ValueError("Map must be twice as wide as it is tall")

    def vec2pix(l, b):
        l = l % (2 * np.pi)
        l[l < 0] += 2 * np.pi
        l = nx * (1 - l / (2 * np.pi))
        l = np.clip(l.astype(np.int), 0, nx - 1)
        b = ny * (1 - (b + np.pi/2) / np.pi)
        b = np.clip(b.astype(np.int), 0, ny - 1)
        return data[b, l]

    return vec2pix


def normalizer(sampler, vmin, vmax, scaling='linear',
               bias=0.5, contrast=1):
    """
    Apply an intensity scaling to a sampler function

    Parameters
    ----------
    sampler : function
       A function of (lon, lat) that samples a dataset

    vmin : float
      The data value to assign to black
    vmin : float
      The data value to assign to white
    bias : float between 0-1. Default=0.5
      Where to assign middle-grey, relative to (vmin, vmax).
    contrast : float, default=1
      How quickly to ramp from black to white. The default of 1
      ramps over a data range of (vmax - vmin)
    scaling : 'linear' | 'log' | 'arcsinh' | 'sqrt' | 'power'
      The type of intensity scaling to apply

    Returns
    -------
    A function of (lon, lat) that samples an image,
    scales the intensity, and returns an array of dtype=np.uint8
    """
    def result(x, y):
        raw = sampler(x, y)
        r = normalize(raw, vmin, vmax, bias, contrast, scaling)
        return r
    return result
