from __future__ import print_function

import os
from xml.dom.minidom import parseString

import pytest
import numpy as np

from .. import iter_tiles, cartesian_sampler, gen_wtml
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
