"""
Resample test.hpx into Galactic coordinates, and create test_gal.hpx
"""
import numpy as np
import healpy as hp
from astropy.coordinates import Galactic, FK5
import astropy.units as u

nest = True
map = hp.read_map('test.hpx', nest=nest)

theta, phi = hp.pix2ang(64, np.arange(map.size), nest)
l, b = phi, np.pi / 2 - theta

g = Galactic(l, b, unit=(u.rad, u.rad))
f = g.transform_to(FK5)
ra, dec = f.ra.rad, f.dec.rad

map = hp.get_interp_val(map, np.pi / 2 - dec, ra, nest)

hp.write_map('test_gal.hpx', map, nest=nest, coord='G',
             fits_IDL=False)
