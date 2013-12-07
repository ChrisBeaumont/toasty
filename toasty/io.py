from PIL import Image
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
    Image.fromarray(array).save(pth)


def read_png(pth):
    """
    load a PNG image into an array

    Parameters
    ----------
    pth : str
       Path to write read
    """
    return np.asarray(Image.open(pth))
