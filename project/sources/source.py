"""
Abstract Source for method imposition.
"""
from __future__ import annotations
import abc
from typing import Iterator, TYPE_CHECKING

if TYPE_CHECKING:
    from project.result import Result


class Source(abc.ABC):

    @abc.abstractmethod
    def extract(self, *args, **kwds) -> Iterator[Result]:
        """Extracts and yields results.

        :yield: Resulting meme
        :rtype: Generator[Result]
        """
        ...
