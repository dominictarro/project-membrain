"""
Computer vision algorithms.
"""
import cv2
import numpy as np

def perceptual_hash(img: np.ndarray, hash_size: int = 8) -> int:
    """_summaComputes the perceptual hash of an image.ry_

    :param img: 3D array of integers to compute hash of
    :type img: np.ndarray
    :param hash_size: Number of bytes the hash should be, defaults to 8
    :type hash_size: int, optional
    :return: Image hash
    :rtype: int
    """
    _img: np.ndarray
    # to grayscale
    # opencv2 loads to BGR color space by default
    if img.shape[2] == 3:
        _img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    elif img.shape[2] > 3:
        # beware, black & transparent photos (e.g. silhoutte stock)
        # will produce an image hash of 0 every time
        _img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
    
    _img = cv2.resize(_img, (hash_size+1, hash_size))
    _img = _img[:, 1:] > _img[:, :-1]
    return sum([2 ** i for (i, v) in enumerate(_img.flatten()) if v])
