"""
Transforms meme images into linguistic and visual features.
"""
from __future__ import annotations
import logging
import sys
import traceback
from typing import TYPE_CHECKING

import cv2
import numpy as np
import os
import requests

if TYPE_CHECKING:
    from project.result import Result

logger = logging.getLogger(__name__)


def get_image(result: Result) -> np.ndarray:
    """Gets a meme's image from its url.

    :param result: Meme container object
    :type result: Result
    :return: Meme image
    :rtype: np.ndarray
    """
    r: requests.Response = requests.get(result.meme.url)
    r.raise_for_status()
    arr = np.asarray(bytearray(r.content), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)
    if img is None:
        logger.warning(f"Got an empty image from {result.meme.url}\narr: {arr.shape if arr is not None else 'empty'}")
    return img

def compute_perceptual_image_hash(img: np.ndarray) -> int:
    """Computes the perceptual hash of an image.

    :param img: Image to compute hash for
    :type img: np.ndarray
    :return: Perceptual hash
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
    
    _img = cv2.resize(_img, (9, 8))
    _img = _img[:, 1:] > _img[:, :-1]
    return sum([2 ** i for (i, v) in enumerate(_img.flatten()) if v])

def extract_image_meta_features(result: Result, img: np.ndarray):
    init_kwargs = dict()
    # resolution
    try:
        init_kwargs['height'] = img.shape[0]
        init_kwargs['width'] = img.shape[1]
        init_kwargs['channels'] = img.shape[2] if len(img.shape) > 2 else 1
    except: # TODO something, anything
        logger.warning(f"Failed to set resolution \nid: {result}\n shape: {img.shape}\n {traceback.format_exc()}")

    try:
        init_kwargs['format'] = os.path.splitext(result.meme.url)[-1]
    except: # TODO something, anything
        logger.warning(f"Failed to set format \nid: {result}\n shape: {img.shape}\n {traceback.format_exc()}")
    result.set_meme_image_from_args(**init_kwargs)

def extract_image_features(result: Result):
    try:
        img: np.ndarray = get_image(result)
        result.is_db_ready = True
    except:
        logger.warning(f"Errored while getting the image  \nid: {result}\n {traceback.format_exc()}")
        result.is_db_ready = False
        return
    
    try:
        result.meme.id = compute_perceptual_image_hash(img).to_bytes(64, sys.byteorder)
    except:
        logger.warning(f"Errored while setting the hash id  \nid: {result}\n {traceback.format_exc()}")
        result.is_db_ready = False
        return
    
    extract_image_meta_features(result, img)
    return result
