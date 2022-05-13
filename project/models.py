"""
Database models.
"""
from __future__ import annotations
from typing import List, Type
import os

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    SmallInteger,
    String,
    Text,
    TIMESTAMP
)
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import aliased, declarative_base, relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func, join, text

try:
    POSTGRES_USER=os.environ['POSTGRES_USER']
except KeyError:
    print("Set a POSTGRES_USER value in .env")
    exit(1)

try:
    POSTGRES_PASSWORD=os.environ['POSTGRES_PASSWORD']
except KeyError:
    print("Set a POSTGRES_PASSWORD value in .env")
    exit(1)

try:
    POSTGRES_DB=os.environ['POSTGRES_DB']
except KeyError:
    print("Set a POSTGRES_DB value in .env")
    exit(1)

engine = create_engine(
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB}"
)
Session: sessionmaker = sessionmaker(engine)
Base = declarative_base(bind=engine)

def timestamped(cls: Type[Base]) -> Type[Base]:
    """Class wrapper to add timestamp fields to the model.
    
    :cls:   Model class to wrap

    Fields added
    ---

    :created_at:    When the row was created

    :last_modified: When the row was last edited
    """
    cls.created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )
    cls.last_modified = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )
    return cls


@timestamped
class Meme(Base):
    """
    Core type from which derived data relates. Kept to a low-column table for faster indexing & querying.

    :id:    Image Hamming distance hash acting as unique meme identifier

    :url:   URL to the meme image
    """
    __tablename__ = 'meme'
    id = Column(
        LargeBinary(64),
        primary_key=True,
        nullable=False
    )
    url = Column(
        String(2048),
        unique=True
    )

    # ORM relationships
    image: MemeImage = relationship('MemeImage', uselist=False)
    context: MemeContext = relationship('MemeContext', uselist=False)
    texts: List[MemeText] = relationship('MemeText')
    sentences: List[MemeSentence]
    chunks: List[MemeChunk]
    words: List[MemeWord]


class MemeImage(Base):
    """
    One-to-one content table with more information about the Meme's image & file properties.

    :width:     Width

    :height:    Height

    :channels:  Number of channels

    :size:      Size of the image in bytes

    :format:    Image's encoding format
    """
    __tablename__ = 'meme_image'
    id = Column(
        LargeBinary(64),
        ForeignKey('meme.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False
    )
    width = Column(SmallInteger)
    height = Column(SmallInteger)
    channels = Column(SmallInteger)
    format = Column(String(8))


class MemeContext(Base):
    """
    One-to-one content table that adds context and reference information for the Meme's source.

    :origin:    Source identifier

    :post_url:  URL to the original post containing the Meme

    """
    __tablename__ = 'meme_context'
    id = Column(
        LargeBinary(64),
        ForeignKey('meme.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False
    )
    origin = Column(String(16), nullable=False)
    post_url = Column(
        String(2048),
        nullable=False,
        unique=True
    )


class MemeText(Base):
    """
    A body of text that accompanied a Meme.

    :meme_id:       Meme this text is associated with

    :body:          The text

    :text_type:     The text's relationship to the Meme (title, description, in-image, comment, etc.)

    :confidence:    If text was machine-extracted, confidence in the text's accuracy. 1 otherwise
    """
    __tablename__ = 'meme_text'
    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )
    meme_id = Column(
        LargeBinary(64),
        ForeignKey('meme.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    body = Column(
        Text,
        nullable=False
    )
    text_type = Column(
        String(8),
        nullable=False,
        index=True
    )
    confidence = Column(
        Float,
        server_default=u'1.0',
        nullable=False
    )
    
    meme: Meme = relationship('Meme', back_populates='texts', uselist=False)
    sentences: List[MemeSentence] = relationship('MemeSentence', back_populates='text')


class MemeSentence(Base):
    """
    A sentence from a body of text.

    :text_id:       Text this sentence is contained within

    :sentence:      Sentence content
    """
    __tablename__ = 'meme_sentence'
    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )
    text_id = Column(
        BigInteger,
        ForeignKey('meme_text.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    sentence = Column(
        Text,
        nullable=False
    )

    text: MemeText = relationship('MemeText', back_populates='sentences', uselist=False)
    chunks: List[MemeChunk] = relationship('MemeChunk', back_populates='sentence')
    words: List[MemeWord] = relationship('MemeWord', back_populates='sentence')


class MemeChunk(Base):
    """
    A chunk from a sentence.

    :sentence_id:       Sentence this chunk is contained within

    :chunk:             Chunk content

    :is_named_entity:   The chunk refers to an NLTK [named entity](https://www.nltk.org/book/ch07.html#sec-ner)
    """
    __tablename__ = 'meme_chunk'
    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )
    sentence_id = Column(
        BigInteger,
        ForeignKey('meme_sentence.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    chunk = Column(
        Text,
        nullable=False
    )
    is_named_entity = Column(
        Boolean,
        nullable=False,
        server_default=u'0'
    )

    sentence: MemeSentence = relationship('MemeSentence', back_populates='chunks', uselist=False)


class MemeWord(Base):
    """
    A word from a sentence.

    :sentence_id:   Sentence this word is contained within

    :word:          Word

    :pos_tag:       The word's NLTK [part-of-speech](https://www.nltk.org/book/ch05.html#a-universal-part-of-speech-tagset)

    :lemma:         The [lemmatized](https://nlp.stanford.edu/IR-book/html/htmledition/stemming-and-lemmatization-1.html) form of `word`
    """
    __tablename__ = 'meme_word'
    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )
    sentence_id = Column(
        BigInteger,
        ForeignKey('meme_sentence.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    word = Column(
        String(64),
        nullable=False,
        index=True
    )
    pos_tag = Column(String(8), index=True)
    lemma = Column(String(64), index=True)

    sentence: MemeSentence = relationship('MemeSentence', back_populates='words', uselist=False)


# Relate Meme to MemeSentence
meme_sentence_join = join(
        MemeText, MemeSentence, MemeText.id == MemeSentence.text_id
    ).join(
        Meme, Meme.id == MemeText.meme_id
)
meme_sentence_via_text = aliased(MemeSentence, meme_sentence_join, flat=True)
Meme.sentences = relationship(meme_sentence_via_text, viewonly=True)

# Relate Meme to MemeChunk
meme_chunk_join = join(
        MemeChunk, MemeSentence, MemeSentence.id == MemeChunk.sentence_id
    ).join(
        MemeText, MemeText.id == MemeSentence.text_id
    ).join(
        Meme, Meme.id == MemeText.meme_id
)
meme_chunk_via_sentence_text = aliased(MemeChunk, meme_chunk_join, flat=True)
Meme.chunks = relationship(meme_chunk_via_sentence_text, viewonly=True)

# Relate Meme to MemeWord
meme_word_join = join(
        MemeWord, MemeSentence, MemeSentence.id == MemeWord.sentence_id
    ).join(
        MemeText, MemeText.id == MemeSentence.text_id
    ).join(
        Meme, Meme.id == MemeText.meme_id
)
meme_word_via_sentence_text = aliased(MemeSentence, meme_word_join, flat=True)
Meme.words = relationship(meme_word_via_sentence_text, viewonly=True)

Base.metadata.create_all()
