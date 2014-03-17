toasty
======

[![Coverage Status](https://coveralls.io/repos/ChrisBeaumont/toasty/badge.png)](https://coveralls.io/r/ChrisBeaumont/toasty)
[![Build Status](https://travis-ci.org/ChrisBeaumont/toasty.png?branch=master)](https://travis-ci.org/ChrisBeaumont/toasty)


Library to build WorldWide Telescope TOAST tiles.


### Dependencies
 * Required: python (2.6, 2.7, 3.2, or 3.3), numpy, cython, Pillow/PIL
 * Optional: astropy (for FITS IO), healpy (for HEALPIX data), pytest (for testing)

### Usage

```python
from toasty import toast
toast(sampler, depth, directory)
```

where:

  * **sampler** is a function that takes 2D arrays of (lon, lat) as input,
    samples a dataset at these locations, and returns the resampled image
  * **depth** is the depth of the tile pyramid to create (4^d tiles are
    created at a depth of d)
  * **directory** is the path to create the hierarchy at

Toasty provides a few basic sampler functions:

  * **healpix_sampler** for sampling from healpix arrays
  * **cartesian_sampler** for sampling from cartesian-projections
  * **normalizer** for applying an intensity normalization after sampling

### Examples

To toast an all-sky, Cartesian projection, 8 byte image:

```python
from toasty import toast, cartesian_sampler
from skimage.io import imread

data = imread('allsky.png')
sampler = cartesian_sampler(data)
output = 'toast'
depth = 8  # approximately 0.165"/pixel at highest resolution
toast(sampler, depth, output)
```

To apply a log-stretch to an all sky FITS image:

```python
from toasty import toast, cartesian_sampler, normalizer
from astropy.io import fits

data = fits.open('allsky.fits')[0].data
vmin, vmax = 100, 65535
scaling = 'log'
contrast = 1
sampler = normalizer(cartesian_sampler(data), vmin, vmax
                     scaling, bias, contrast)
output = 'toast'
depth = 8
toast(sampler, depth, output)
```

To perform a custom transformation

```python
from toasty import toast
from astropy.io import fits

data = fits.open('allsky.fits')[0].data

def sampler(x, y):
    """
    x and y are arrays, giving the RA/Dec centers
    for each pixel to extract
    """
    ... code to extract a tile from `data` here ...

output = 'toast'
depth = 8
toast(sampler, depth, output)
```


See ``toasty.tile`` for documentation on these functions.


### Using with WorldWide Telescope
To quickly preview a toast directory named `test`, navigate to the directory
where `test` exists and run

```
python -m toasty.viewer test
```

This will start a web server, probably at [http://0.0.0.0:8000](http://0.0.0:8000) (check the output for the actual address). Open this URL in a browser to get a quick look at the data.

For more information about using WorldWide Telescope with custom image data,
see [the official documentation](http://www.worldwidetelescope.org/Docs/worldwidetelescopedatafilesreference.html). The function `toasty.gen_wtml` can generate the wtml information for images generated with toasty.

For an example of tiles generated with Toasty (originally from [Aladin healpix images](http://alasky.u-strasbg.fr/cats/SIMBAD/)), see [The ADS All Sky Survey](http://adsass.org/wwt). The code used to generate these images is [here](https://github.com/ChrisBeaumont/adsass/blob/master/toast/toast.py).
