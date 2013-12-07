toasty
======

[![Coverage Status](https://coveralls.io/repos/ChrisBeaumont/toasty/badge.png)](https://coveralls.io/r/ChrisBeaumont/toasty)
[![Build Status](https://travis-ci.org/ChrisBeaumont/toasty.png?branch=master)](https://travis-ci.org/ChrisBeaumont/toasty)


Library to build WorldWide Telescope TOAST tiles


### Dependencies
 * Required: numpy, cython, PIL
 * Optional: astropy, healpy (for astronomy); pytest (for testing)

### Usage

```
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

See ``toasty.tile`` for documentation on these functions


### Using with WorldWide Telescope
To quickly preview a toast directory named `test`, navigate to the directory
where `test` exists and run

```
python -m toasty.view base_directory toasty.view
```

This will start a web server, probably at [http://0.0.0.0:8000](http://0.0.0:8000) (check the output for the actual address). Open this URL in a browser to get a quick look at the data.

For more information about using WorldWide Telescope with custom image data,
see [the official documentation](http://www.worldwidetelescope.org/Docs/worldwidetelescopedatafilesreference.html). The function `toasty.gen_wtml` can generate the wtml information for images generated with toasty.

