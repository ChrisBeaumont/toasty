from skimage.io import imsave

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
