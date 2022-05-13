"""
Utilities for reading and writing image data.
"""
import logging
import os
from contextlib import contextmanager
import traceback
from typing import Iterator

import cv2
import imageio
import numpy as np
from pyparsing import Optional
import requests


@contextmanager
def temporary_file_from_web(url: str, temp_dir: str = '.') -> Iterator[str]:
    """Context manager to temporarily store a file from the web.

    :param url: Url to the file
    :type url: str
    :param temp_dir: Temporary directory's filepath, defaults to '.'
    :type temp_dir: str, optional
    :yield: Filepath to the temporary file
    :rtype: Generator[str]
    """
    r: requests.Response = requests.get(url)
    r.raise_for_status()
    tfp = os.path.join(temp_dir, os.path.basename(url))
    try:
        with open(tfp, 'wb+') as fo:
            fo.write(r.content)
        yield tfp
    except Exception:
        logging.error(traceback.format_exc())
    finally:
        if os.path.isfile(tfp):
            os.remove(tfp)

def get_any_image(url: str) -> np.ndarray:
    """Gets an image from a url and temporarily save it to 
    disk for more versatile loading operations.

    :param url: Url to the image
    :type url: str
    :return: Image
    :rtype: np.ndarray
    """
    with temporary_file_from_web(url) as tfp:
        # GIFs will only load the first frame
        return imageio.imread(tfp)

def get_static_image(url: str) -> np.ndarray:
    """Get an image from a url and read it from memory.

    :param url: Url to the image
    :type url: str
    :return: Image
    :rtype: np.ndarray
    """
    r: requests.Response = requests.get(url)
    r.raise_for_status()
    arr = np.asarray(bytearray(r.content), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)
    return img

FORMAT_HANDLERS={
    '.gif': get_any_image,
    '.png': get_static_image,
    '.jpg': get_static_image,
    '.jpeg': get_static_image,
    '.webm': get_any_image,
    '.tiff': get_any_image,
    '.bmp': get_static_image
}
def get_image(url: str) -> np.ndarray:
    """Gets a meme's image from its url.

    :param result: Meme container object
    :type result: Result
    :return: Meme image
    :rtype: np.ndarray
    """
    fmt = os.path.splitext(url)[1]
    handler = FORMAT_HANDLERS.get(fmt, get_any_image)
    return handler(url)
