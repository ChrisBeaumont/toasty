from setuptools import setup, Extension, find_packages
from Cython.Distutils import build_ext
import numpy as np

ext_modules = [Extension("toasty/util", ["toasty/util.pyx"])]
setup(
        name = "toasty",
        cmdclass = {'build_ext': build_ext},
        packages = find_packages(),
        include_dirs = [np.get_include()],
        ext_modules = ext_modules
        )
