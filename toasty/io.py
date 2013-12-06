from skimage.io import imsave, imread
import numpy as np


def save_png(pth, array):
    """
    Save an array as a PNG image

    Parameters
    ----------
    pth : str
       Path to write to
    array : array-like
       Image to save
    """
    imsave(pth, array)


def read_png(pth):
    """
    load a PNG image into an array

    Parameters
    ----------
    pth : str
       Path to write read
    """
    return np.asarray(imread(pth))
