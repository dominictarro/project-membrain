"""
Transforms raw text into linguistic components.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Tuple

from project import models as m

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize

if TYPE_CHECKING:
    from project.result import Result

# some nltk functions use whole language name while others use abbreviations
NLTK_LANG = 'eng', 'english'
LANG_STOP_WORDS = stopwords.words(NLTK_LANG[1])
LEMMATIZER = WordNetLemmatizer()


def extract_word_features(result: Result, msentence: m.MemeSentence, pos_tags: List[str]):
    """Extracts words and their features from sentences and adds them to the result object.

    :param result: Meme container object
    :type result: Result
    :param msentence: Sentence to have word features extracted from
    :type msentence: m.MemeSentence
    :param pos_tags: Array of words w/ part-of-speech
    :type pos_tags: List[str]
    """
    # Stop words are excluded from the MemeWord set
    non_stop_word_tags = list(filter(lambda pos_tag: pos_tag[0] not in LANG_STOP_WORDS, pos_tags))
    for word, pos in non_stop_word_tags:
        lemma = LEMMATIZER.lemmatize(word)
        result.add_meme_word_from_args(msentence, word, pos, lemma)

def extract_chunk_features(result: Result, msentence: m.MemeSentence, pos_tags: List[Tuple[str]]):
    """Extracts chunks and their features from sentences and adds them to the result object.

    :param result: Meme container object
    :type result: Result
    :param msentence: Sentence to have chunk features extracted from
    :type msentence: MemeSentence
    :param pos_tags: Array of words w/ part-of-speech
    :type pos_tags: List[Tuple[str]]

    ## Extracted Features
        - Named Entity
    """
    for t in nltk.ne_chunk(pos_tags, binary=True):
        if hasattr(t, 'label') and t.label() == 'NE':
            result.add_meme_chunk_from_args(msentence, chunk=' '.join(i[0] for i in t), is_named_entity=True)

def extract_sentence_features(result: Result, mtext: m.MemeText):
    """Extracts sentences and their features from text blocks and adds them to the result object.

    :param result: Meme container object
    :type result: Result
    :param mtext: Text to have sentence features extracted from
    :type mtext: m.MemeText
    """
    tokens = sent_tokenize(mtext.body)
    for sentence in tokens:
        msentence = m.MemeSentence(sentence=sentence)
        result.add_meme_sentence(mtext, msentence)

        tokens: List[str] = word_tokenize(msentence.sentence)
        pos_tags: List[Tuple[str]] = nltk.pos_tag(tokens, lang=NLTK_LANG[0])

        extract_word_features(result, msentence, pos_tags)
        extract_chunk_features(result, msentence, pos_tags)


def extract_nltk_features(result: Result):
    """Extracts language features from a meme result.

    :param result: Meme container object
    :type result: Result
    """
    for mtext in result.meme.texts:
        extract_sentence_features(result, mtext)
