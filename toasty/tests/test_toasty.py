from __future__ import print_function

import os
from xml.dom.minidom import parseString
from tempfile import mkstemp, mkdtemp
from shutil import rmtree

import pytest
import numpy as np

try:
    import healpy as hp
    from astropy.io import fits
    HAS_ASTRO = True
except ImportError:
    HAS_ASTRO = False

from .. import tile
from .. import iter_tiles, cartesian_sampler, gen_wtml, toast, healpix_sampler
from ..io import read_png, save_png
from .._libtoasty import mid


def mock_sampler(x, y):
    return x


@pytest.mark.parametrize('depth', (0, 1, 2))
def test_iter_tiles_path(depth):
    result = set(r[0] for r in iter_tiles(mock_sampler, depth))
    expected = set(['{n}/{y}/{y}_{x}.png'.format(n=n, x=x, y=y)
                    for n in range(depth + 1)
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


def image_test(expected, actual, err_msg):
    resid = np.abs(1. * actual - expected)
    if np.median(resid) < 15:
        return

    _, pth = mkstemp(suffix='.png')
    save_png(pth, np.hstack((expected, actual)))

    pytest.fail("%s. Saved to %s" % (err_msg, pth))


def test_reference_wtml():
    ref = parseString(reference_wtml)
    opts = {'FolderName': 'ADS All Sky Survey',
            'Name': 'allSources_512',
            'Credits': 'ADS All Sky Survey',
            'CreditsUrl': 'adsass.org',
            'ThumbnailUrl': 'allSources_512.jpg'
            }
    wtml = gen_wtml('allSources_512', 3, **opts)
    val = parseString(wtml)

    assert ref.getElementsByTagName('Folder')[0].getAttribute('Name') == \
        val.getElementsByTagName('Folder')[0].getAttribute('Name')

    for n in ['Credits', 'CreditsUrl', 'ThumbnailUrl']:
        assert ref.getElementsByTagName(n)[0].childNodes[0].nodeValue == \
            val.getElementsByTagName(n)[0].childNodes[0].nodeValue

    ref = ref.getElementsByTagName('ImageSet')[0]
    val = val.getElementsByTagName('ImageSet')[0]
    for k in ref.attributes.keys():
        assert ref.getAttribute(k) == val.getAttribute(k)


def cwd():
    return os.path.split(os.path.abspath(__file__))[0]


def test_wwt_compare_sky():
    """Assert that the toast tiling looks similar to the WWT tiles"""
    direc = cwd()

    im = read_png(os.path.join(direc, 'test.png'))
    sampler = cartesian_sampler(im)

    for pth, result in iter_tiles(sampler, depth=1):
        expected = read_png(os.path.join(direc, 'test_sky', pth))
        expected = expected[:, :, :3]

        image_test(expected, result, "Failed for %s" % pth)


@pytest.mark.skipif('not HAS_ASTRO')
def test_healpix_sampler():

    direc = cwd()

    im = fits.open(os.path.join(direc, 'test.hpx'))[1].data['I']

    sampler = healpix_sampler(im, nest=True)

    for pth, result in iter_tiles(sampler, depth=1):
        expected = read_png(os.path.join(direc, 'test_sky', pth))
        expected = expected[:, :, 0]

        image_test(expected, result, "Failed for %s" % pth)


@pytest.mark.skipif('not HAS_ASTRO')
def test_healpix_sampler_galactic():

    direc = cwd()

    im = fits.open(os.path.join(direc, 'test_gal.hpx'))[1].data['I']

    sampler = healpix_sampler(im, nest=True, coord='G')

    for pth, result in iter_tiles(sampler, depth=1):
        expected = read_png(os.path.join(direc, 'test_sky', pth))
        expected = expected[:, :, 0]

        image_test(expected, result, "Failed for %s" % pth)


@pytest.mark.skipif('not HAS_ASTRO')
def test_guess_healpix():
    pth = os.path.join(cwd(), 'test.hpx')
    d, nest, coord = tile._guess_healpix(pth)
    assert nest is True
    assert coord == 'C'
    np.testing.assert_array_equal(d, fits.open(pth)[1].data['I'])


def test_merge():
    # test that merge function called on non-terminal nodes
    im = read_png(os.path.join(cwd(), 'test.png'))

    def null_merge(mosaic):
        return np.zeros((256, 256, 3), dtype=np.uint8)

    sampler = cartesian_sampler(im)

    for pth, im in iter_tiles(sampler, 2, null_merge):
        if pth[0] != '2':
            assert im.max() == 0
        else:
            assert im.max() != 0


class TestToaster(object):

    def setup_method(self, method):
        self.base = mkdtemp()
        self.cwd = cwd()

        im = read_png(os.path.join(self.cwd, 'test.png'))
        self.sampler = cartesian_sampler(im)

    def teardown_method(self, method):
        rmtree(self.base)

    def verify_toast(self):
        """ Zip the expected and actual tiles """
        for n, x, y in [(0, 0, 0), (1, 0, 0), (1, 0, 1),
                        (1, 1, 0), (1, 1, 1)]:
            subpth = os.path.join(str(n), str(y), "%i_%i.png" % (y, x))
            a = read_png(os.path.join(self.base, subpth))[:, :, :3]
            b = read_png(os.path.join(self.cwd, 'test_sky', subpth))[:, :, :3]
            image_test(b, a, 'Failed for %s' % subpth)

    def test_default(self):

        wtml = os.path.join(self.base, 'test.wtml')
        toast(self.sampler, 1, self.base, wtml_file=wtml)

        assert os.path.exists(wtml)
        self.verify_toast()

    def test_no_merge(self):
        toast(self.sampler, 1, self.base, merge=False)
        self.verify_toast()


reference_wtml = """
<Folder Name="ADS All Sky Survey">
<ImageSet Generic="False" DataSetType="Sky" BandPass="Visible" Name="allSources_512" Url="allSources_512/{1}/{3}/{3}_{2}.png" BaseTileLevel="0" TileLevels="3" BaseDegreesPerTile="180" FileType=".png" BottomsUp="False" Projection="Toast" QuadTreeMap="" CenterX="0" CenterY="0" OffsetX="0" OffsetY="0" Rotation="0" Sparse="False" ElevationModel="False">
<Credits> ADS All Sky Survey </Credits>
<CreditsUrl>adsass.org</CreditsUrl>
<ThumbnailUrl>allSources_512.jpg</ThumbnailUrl>
<Description/>
</ImageSet>
</Folder>
"""
