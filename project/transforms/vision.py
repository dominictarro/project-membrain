"""
Transforms meme images into linguistic and visual features.
"""
from __future__ import annotations
import logging
import sys
import traceback
from typing import TYPE_CHECKING

from project.transforms._vision import image_io as iio
from project.transforms._vision import algorithms as ialg

import numpy as np
import os

if TYPE_CHECKING:
    from project.result import Result

logger = logging.getLogger(__name__)



def extract_image_meta_features(result: Result, img: np.ndarray):
    init_kwargs = dict()
    # resolution
    try:
        init_kwargs['height'] = img.shape[0]
        init_kwargs['width'] = img.shape[1]
        init_kwargs['channels'] = img.shape[2] if len(img.shape) > 2 else 1
    except Exception:
        logger.warning(f"Failed to set resolution \nid: {result}\n shape: {img.shape}\n {traceback.format_exc()}")

    try:
        init_kwargs['format'] = os.path.splitext(result.meme.url)[-1]
    except Exception:
        logger.warning(f"Failed to set format \nid: {result}\n shape: {img.shape}\n {traceback.format_exc()}")
    result.set_meme_image_from_args(**init_kwargs)

def extract_image_features(result: Result):
    try:
        img: np.ndarray = iio.get_image(result.meme.url)
        result.is_db_ready = True
    except Exception:
        logger.warning(f"Errored while getting the image  \nid: {result}\n {traceback.format_exc()}")
        result.is_db_ready = False
        return
    
    try:
        result.meme.id = ialg.perceptual_hash(img, hash_size=8).to_bytes(8, sys.byteorder)
    except Exception:
        logger.warning(f"Errored while setting the hash id  \nid: {result}\n {traceback.format_exc()}")
        result.is_db_ready = False
        return
    
    extract_image_meta_features(result, img)
    return result
