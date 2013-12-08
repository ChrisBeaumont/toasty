from setuptools import setup, Extension, find_packages
from Cython.Distutils import build_ext
import numpy as np

ext_modules = [Extension("toasty._libtoasty", ["toasty/_libtoasty.pyx"])]
setup(
        name = "toasty",
        version='0.0.1',
        description='Image pyramid generator for WorldWide Telescope',
        author='Chris Beaumont',
        author_email='cbeaumont@cfa.harvard.edu',
        classifiers=[
            'Intended Audience :: Science/Research',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.7',
            'Topic :: Scientific/Engineering :: Data Visualization'
            ],

        cmdclass = {'build_ext': build_ext},
        packages = find_packages(),
        include_dirs = [np.get_include()],
        ext_modules = ext_modules,
        install_requires=['cython', 'numpy', 'pillow'],
        package_data={'': ['*.png']}
        )
