"""
Main schedule

"""
from __future__ import annotations
import logging
import os
import traceback
from typing import TYPE_CHECKING, Any, List, Optional, Tuple

from project.models import Session
from project.sources import reddit
from project.transforms.language import extract_nltk_features
from project.transforms.vision import extract_image_features

import prefect

if TYPE_CHECKING:
    from project.result import Result

    from sqlalchemy.orm.session import Session as _Session


@prefect.task
def get_reddit_hot(limit: int) -> list:
    return list(reddit.HotSource(limit=limit).extract())

@prefect.task
def get_reddit_rising(limit: int) -> list:
    return list(reddit.RisingSource(limit=limit).extract())

@prefect.task
def get_reddit_top(limit: int) -> list:
    return list(reddit.TopSource(limit=limit).extract())

@prefect.task
def nltk_transform(results: List[Result]) -> List[Result]:
    for r in results:
        extract_nltk_features(r)
    return results

@prefect.task
def cv2_transform(results: List[Result]) -> List[Result]:
    for r in results:
        extract_image_features(r)
    return results

@prefect.task
def db_load(results: List[Result], dependents: Optional[Tuple[Any]] = None):
    with Session() as s:
        s: _Session
        to_save = map(
            lambda r: r.meme, 
            filter(lambda r: r.is_db_ready, results)
        )
        loaded = 0
        for meme in to_save:
            try:
                s.add(meme)
                s.commit()
                loaded += 1
            except Exception:
                logging.error(f"Errored while inserting {meme}\n{traceback.format_exc()}")
        logging.info(f"loaded {loaded} / {len(results)}")

with prefect.Flow('test') as flow:
    reddit_limit = prefect.Parameter('reddit_limit', int(os.getenv('REDDIT_QUERY_SIZE', 100)))

    r_hot_0 = get_reddit_hot(reddit_limit)
    r_hot_1_a = nltk_transform(r_hot_0)
    r_hot_1_b = cv2_transform(r_hot_0)
    db_load(r_hot_0, dependents=(r_hot_1_a, r_hot_1_b))

    r_rising_0 = get_reddit_rising(reddit_limit)
    r_rising_1_a = nltk_transform(r_rising_0)
    r_rising_1_b = cv2_transform(r_rising_0)
    db_load(r_rising_0, dependents=(r_rising_1_a, r_rising_1_b))

    r_top_0 = get_reddit_top(reddit_limit)
    r_top_1_a = nltk_transform(r_top_0)
    r_top_1_b = cv2_transform(r_top_0)
    db_load(r_top_0, dependents=(r_top_1_a, r_top_1_b))


if __name__ == '__main__':
    flow.run({'reddit_limit': 5})
